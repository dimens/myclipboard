# MyClipboard - macOS 剪贴板增强工具

MyClipboard 是一个简单但功能强大的 macOS 剪贴板管理工具，它可以帮助您记录和管理剪贴板历史，提高工作效率。

## 功能特点

- 自动记录剪贴板历史
- 支持文本和图片内容
- 支持文件复制记录
- 快速访问历史记录
- 可自定义最大记录数量（1-100条）
- 支持开机自动启动
- 支持清除单条或所有历史记录

## 系统要求

- macOS 10.10 或更高版本
- 约 10MB 磁盘空间

## 安装说明

1. 下载 MyClipboard.dmg 文件
2. 打开 DMG 文件
3. 将 MyClipboard.app 拖到 Applications（应用程序）文件夹
4. 首次运行时，可能需要在"系统偏好设置 > 安全性与隐私"中允许运行

## 使用说明

### 基本使用
1. 运行 MyClipboard 后，菜单栏会出现一个剪贴板图标
2. 复制任何内容后，都会自动记录到历史中
3. 点击菜单栏图标可查看剪贴板历史
4. 点击任何历史记录可快速复制该内容

### 历史记录管理
- 将鼠标悬停在历史记录上可以看到"复制"和"删除"选项
- 点击"清除所有"可以清空所有历史记录

### 设置选项
点击"设置"可以进行以下配置：
1. 开机自动启动：选择是否在系统启动时自动运行
2. 最大记录数：设置保留的最大历史记录数量（1-100条）

## 注意事项

- 图片内容暂不支持持久化存储，重启应用后会丢失
- 为保护隐私，建议定期清理不需要的历史记录
- 如果遇到权限问题，请检查系统安全设置

## 卸载方法

1. 退出 MyClipboard 应用
2. 从应用程序文件夹删除 MyClipboard.app
3. （可选）删除配置文件：
   ```bash
   rm -rf ~/Library/Application\ Support/MyPST
   ```

## 常见问题

Q: 为什么有些复制的内容没有显示在历史记录中？
A: 程序会自动去重，相同的内容不会重复记录。

Q: 如何快速清空所有历史记录？
A: 点击菜单中的"清除所有"选项即可。

Q: 设置了开机自启动但没有生效？
A: 请检查系统偏好设置中的登录项是否允许 MyClipboard 自启动。


## 版权信息

© 2025 MyClipboard。保留所有权利。

## 开发说明

### 环境配置
```bash
# 创建虚拟环境
python3.11 -m venv pst_env

# 激活虚拟环境
source pst_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 构建应用
```bash
# 清理之前的构建
rm -rf build dist

# 构建应用
python setup.py py2app
```

### 贡献代码
1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request