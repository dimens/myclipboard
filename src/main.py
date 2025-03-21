import AppKit
import ServiceManagement
from AppKit import NSImage, NSStatusBar, NSMenuItem, NSScreen
from Foundation import NSObject, NSLog, NSTimer
import objc
import time
import json
import os

class SettingsManager(NSObject):
    def init(self):
        self = objc.super(SettingsManager, self).init()
        self.defaults = AppKit.NSUserDefaults.standardUserDefaults()
        return self
    
    @objc.signature(b'B@:')
    def autoStart(self):
        return self.defaults.boolForKey_('autoStart')
    
    def setAutoStart_(self, value):
        self.defaults.setBool_forKey_(value, 'autoStart')
        # 注册登录启动项
        ServiceManagement.SMLoginItemSetEnabled('com.mypst.launcher', value)
        self.defaults.synchronize()
    
    def maxHistoryCount(self):
        # 获取最大历史记录数，默认为 10
        count = self.defaults.integerForKey_('maxHistoryCount')
        return count if count > 0 else 10
    
    def setMaxHistoryCount_(self, value):
        # 确保值在 1-100 之间
        value = max(1, min(100, value))
        self.defaults.setInteger_forKey_(value, 'maxHistoryCount')
        self.defaults.synchronize()

class ClipboardManager(NSObject):
    def init(self):
        self = objc.super(ClipboardManager, self).init()
        if self is None:
            return None
        
        self.history = []
        self.max_history = 10
        self.last_change_count = 0
        self.settings_window = None
        self.settings_window_controller = None
        self.app = AppKit.NSApplication.sharedApplication()  # 保存应用程序实例引用
        
        # 初始化状态栏图标
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(AppKit.NSVariableStatusItemLength)
        self.status_item.setImage_(NSImage.imageNamed_("NSTouchBarHistoryTemplate"))
        self.status_item.setHighlightMode_(True)
        
        # 创建菜单
        self.menu = AppKit.NSMenu.alloc().init()
        self.status_item.setMenu_(self.menu)
        
        # 初始化设置管理器
        self.settings_manager = SettingsManager.alloc().init()
        
        # 加载历史记录
        self.load_history()
        
        # 首次加载菜单
        self.update_menu()
        
        # 启动剪贴板监听
        self.start_monitor()
        return self
    
    def start_monitor(self):
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.5, self, 'checkClipboard:', None, True
        )
    
    def checkClipboard_(self, timer):
        pasteboard = AppKit.NSPasteboard.generalPasteboard()
        change_count = pasteboard.changeCount()
        
        if change_count != self.last_change_count:
            self.last_change_count = change_count
            self.store_clipboard_content(pasteboard)
    
    def store_clipboard_content(self, pasteboard):
        content = {'timestamp': time.time()}
        
        # 检查所有可用的类型
        available_types = pasteboard.types()
        
        if AppKit.NSFilenamesPboardType in available_types:
            # 处理文件
            filenames = pasteboard.propertyListForType_(AppKit.NSFilenamesPboardType)
            if filenames and len(filenames) > 0:
                content.update({
                    'type': 'file',
                    'data': filenames,
                    'display_name': os.path.basename(filenames[0])
                })
        
        elif AppKit.NSPasteboardTypePNG in available_types:
            # 处理图片
            image_data = pasteboard.dataForType_(AppKit.NSPasteboardTypePNG)
            if image_data:
                image = NSImage.alloc().initWithData_(image_data)
                if image:
                    content.update({
                        'type': 'image',
                        'data': image
                    })
        
        elif AppKit.NSPasteboardTypeString in available_types:
            # 处理文本
            text = pasteboard.stringForType_(AppKit.NSPasteboardTypeString)
            if text:
                content.update({
                    'type': 'text',
                    'data': text.strip()
                })
        
        if 'type' in content:
            # 去重逻辑
            is_duplicate = False
            if content['type'] == 'text':
                is_duplicate = any(item.get('type') == 'text' and item.get('data') == content['data'] for item in self.history)
            elif content['type'] == 'file':
                is_duplicate = any(item.get('type') == 'file' and item.get('data') == content['data'] for item in self.history)
            elif content['type'] == 'image':
                content_hash = hash(content['data'].TIFFRepresentation())
                is_duplicate = any(item.get('type') == 'image' and hash(item['data'].TIFFRepresentation()) == content_hash for item in self.history)
            
            if not is_duplicate:
                self.history.insert(0, content)
                # 使用设置中的最大记录数
                max_count = self.settings_manager.maxHistoryCount()
                while len(self.history) > max_count:
                    self.history.pop()
                self.update_menu()
                self.save_history()
    
    def update_menu(self):
        self.menu.removeAllItems()
        
        # 添加历史记录项
        for idx, item in enumerate(self.history):
            if item['type'] == 'text':
                text = item['data']
                if len(text) > 30:
                    text = text[:30] + '...'
                title = f"{idx+1}. {text}"
            elif item['type'] == 'file':
                title = f"{idx+1}. 文件: {item['display_name']}"
            else:
                title = f"{idx+1}. 图片 ({time.strftime('%H:%M', time.localtime(item['timestamp']))})"
            
            # 创建子菜单
            submenu = AppKit.NSMenu.alloc().init()
            
            # 添加复制选项
            copy_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                '复制', 'selectItem:', ''
            )
            copy_item.setRepresentedObject_(item)
            copy_item.setTarget_(self)
            submenu.addItem_(copy_item)
            
            # 添加删除选项
            delete_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                '删除', 'deleteItem:', ''
            )
            delete_item.setRepresentedObject_(item)
            delete_item.setTarget_(self)
            submenu.addItem_(delete_item)
            
            # 创建主菜单项并设置子菜单
            menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                title, None, ''
            )
            menu_item.setSubmenu_(submenu)
            self.menu.addItem_(menu_item)
        
        if not self.history:
            empty_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                '暂无记录', None, ''
            )
            self.menu.addItem_(empty_item)
        
        # 添加分隔线
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # 添加清除所有选项
        clear_all_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            '清除所有', 'clearAllItems:', ''
        )
        clear_all_item.setTarget_(self)
        self.menu.addItem_(clear_all_item)
        
        # 添加分隔线
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # 设置菜单项
        settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            '设置', 'openSettings:', ''
        )
        settings_item.setTarget_(self)
        self.menu.addItem_(settings_item)
        
        # 退出菜单项
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            '退出', 'terminateApp:', ''
        )
        quit_item.setTarget_(self)
        self.menu.addItem_(quit_item)
    
    @objc.signature(b'v@:@')
    def openSettings_(self, sender):
        NSLog("Opening settings window...")
        
        if self.settings_window is not None:
            self.settings_window.makeKeyAndOrderFront_(None)
            return
        
        # 获取屏幕尺寸
        screen = AppKit.NSScreen.mainScreen()
        screen_rect = screen.frame()
        window_width = 300
        window_height = 200  # 增加窗口高度
        x = (screen_rect.size.width - window_width) / 2
        y = (screen_rect.size.height - window_height) / 2
        
        # 创建窗口
        self.settings_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(x, y, window_width, window_height),
            AppKit.NSWindowStyleMaskTitled |
            AppKit.NSWindowStyleMaskClosable,
            AppKit.NSBackingStoreBuffered,
            False
        )
        self.settings_window.setTitle_('设置')
        self.settings_window.setReleasedWhenClosed_(False)
        
        # 创建内容视图
        content_view = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, window_width, window_height)
        )
        self.settings_window.setContentView_(content_view)
        
        # 创建自动启动复选框
        checkbox = AppKit.NSButton.alloc().initWithFrame_(AppKit.NSMakeRect(20, 150, 200, 30))
        checkbox.setButtonType_(AppKit.NSButtonTypeSwitch)
        checkbox.setTitle_('开机自动启动')
        checkbox.setState_(AppKit.NSOnState if self.settings_manager.autoStart() else AppKit.NSOffState)
        checkbox.setTarget_(self)
        checkbox.setAction_(objc.selector(self.toggleAutoStart_, signature=b'v@:@'))
        
        # 创建最大记录数标签
        label = AppKit.NSTextField.alloc().initWithFrame_(AppKit.NSMakeRect(20, 110, 150, 20))
        label.setStringValue_('最大记录数:')
        label.setEditable_(False)
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        
        # 创建最大记录数输入框
        self.max_count_field = AppKit.NSTextField.alloc().initWithFrame_(AppKit.NSMakeRect(170, 110, 50, 20))
        self.max_count_field.setStringValue_(str(self.settings_manager.maxHistoryCount()))
        self.max_count_field.setDelegate_(self)
        
        # 添加控件到内容视图
        content_view.addSubview_(checkbox)
        content_view.addSubview_(label)
        content_view.addSubview_(self.max_count_field)
        
        # 设置窗口代理
        self.settings_window.setDelegate_(self)
        
        # 显示窗口
        self.settings_window.setLevel_(AppKit.NSFloatingWindowLevel)
        self.settings_window.makeKeyAndOrderFront_(None)
        self.app.activateIgnoringOtherApps_(True)
    
    @objc.signature(b'v@:@')
    def windowWillClose_(self, notification):
        NSLog("Window is closing")  # 添加日志
        self.settings_window = None
    
    @objc.signature(b'v@:@')
    def toggleAutoStart_(self, sender):
        is_on = sender.state() == AppKit.NSOnState
        self.settings_manager.setAutoStart_(is_on)
        NSLog(f"Auto start setting changed to: {is_on}")  # 添加日志
    
    def terminateApp_(self, sender):
        AppKit.NSApplication.sharedApplication().terminate_(self)
    
    def selectItem_(self, sender):
        selected_item = sender.representedObject()
        pasteboard = AppKit.NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        
        if selected_item['type'] == 'text':
            pasteboard.setString_forType_(selected_item['data'], AppKit.NSPasteboardTypeString)
        elif selected_item['type'] == 'file':
            # 处理文件
            pasteboard.setPropertyList_forType_(selected_item['data'], AppKit.NSFilenamesPboardType)
        else:
            # 处理图片
            image = selected_item['data']
            # 设置 TIFF 格式
            tiff_data = image.TIFFRepresentation()
            if tiff_data:
                pasteboard.setData_forType_(tiff_data, AppKit.NSPasteboardTypeTIFF)
            
            # 设置 PNG 格式
            if image.representations():
                png_data = AppKit.NSBitmapImageRep.representationOfImageRepsInArray_usingType_properties_(
                    image.representations(), AppKit.NSBitmapImageFileTypePNG, None
                )
                if png_data:
                    pasteboard.setData_forType_(png_data, AppKit.NSPasteboardTypePNG)
    
    def save_history(self):
        try:
            history_path = os.path.expanduser('~/Library/Application Support/MyPST')
            if not os.path.exists(history_path):
                os.makedirs(history_path)
            
            serializable = []
            for item in self.history:
                base_item = {
                    'type': item['type'],
                    'timestamp': item['timestamp']
                }
                
                if item['type'] == 'text':
                    base_item['data'] = item['data']
                elif item['type'] == 'file':
                    # 将 NSArray 转换为 Python 列表
                    if isinstance(item['data'], (list, tuple)):
                        base_item['data'] = list(item['data'])
                    else:
                        # 处理 NSArray 类型
                        base_item['data'] = [str(item['data'].objectAtIndex_(i)) 
                                           for i in range(item['data'].count())]
                    base_item['display_name'] = item['display_name']
                # 图片类型不保存
                else:
                    continue
                
                serializable.append(base_item)
            
            # 使用临时文件来确保写入完整
            temp_path = os.path.join(history_path, 'history.json.tmp')
            final_path = os.path.join(history_path, 'history.json')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            
            # 如果写入成功，替换原文件
            os.replace(temp_path, final_path)
            
        except Exception as e:
            NSLog(f"Error saving history: {str(e)}")
            # 如果发生错误，尝试删除临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def load_history(self):
        try:
            history_path = os.path.expanduser('~/Library/Application Support/MyPST/history.json')
            if not os.path.exists(history_path):
                self.history = []
                return
            
            with open(history_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.history = []
                    
                    if not isinstance(data, list):
                        raise ValueError("Invalid history format")
                        
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                            
                        if 'type' not in item or 'data' not in item:
                            continue
                            
                        if item['type'] == 'text':
                            if isinstance(item.get('data'), str):
                                self.history.append(item)
                        elif item['type'] == 'file':
                            if isinstance(item.get('data'), list):
                                self.history.append(item)
                            
                except json.JSONDecodeError as e:
                    NSLog(f"JSON decode error: {str(e)}")
                    self.history = []
                    # 如果文件损坏，备份并创建新的
                    backup_path = history_path + '.bak'
                    try:
                        os.rename(history_path, backup_path)
                    except:
                        pass
                    
        except Exception as e:
            NSLog(f"Error loading history: {str(e)}")
            self.history = []

    @objc.signature(b'v@:@')
    def deleteItem_(self, sender):
        item = sender.representedObject()
        if item in self.history:
            self.history.remove(item)
            self.update_menu()
            self.save_history()

    @objc.signature(b'v@:@')
    def clearAllItems_(self, sender):
        self.history.clear()
        self.update_menu()
        self.save_history()

    @objc.signature(b'B@:@@')
    def control_textShouldEndEditing_(self, control, fieldEditor):
        if control == self.max_count_field:
            try:
                value = int(fieldEditor.string())  # 使用 fieldEditor 获取文本值
                value = max(1, min(100, value))
                self.settings_manager.setMaxHistoryCount_(value)
                self.max_count_field.setStringValue_(str(value))
                
                # 更新历史记录长度
                while len(self.history) > value:
                    self.history.pop()
                self.update_menu()
                self.save_history()
                
            except ValueError:
                # 如果输入无效，恢复原值
                self.max_count_field.setStringValue_(str(self.settings_manager.maxHistoryCount()))
        return True

def main():
    app = AppKit.NSApplication.sharedApplication()
    clipboard_manager = ClipboardManager.alloc().init()
    app.run()

if __name__ == '__main__':
    main()