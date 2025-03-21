from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'LSUIElement': True,  # 使应用程序在 Dock 中不显示图标
        'CFBundleName': 'MyClipboard',
        'CFBundleDisplayName': 'MyClipboard',
        'CFBundleIdentifier': 'com.mypst.clipboard',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2024',
        'LSMinimumSystemVersion': '10.10',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'AppKit', 
        'Foundation', 
        'objc', 
        'ServiceManagement',
    ],
    'includes': [
        'AppKit', 
        'Foundation', 
        'objc', 
        'ServiceManagement',
    ],
    'resources': [],
    'strip': False,  # 禁用 strip 以保留调试信息
    'arch': None,  # 让 py2app 自动检测架构
    'semi_standalone': False,  # 改为 False
    'site_packages': True,
}

setup(
    name='MyClipboard',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 