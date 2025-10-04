"""
使用cx_Freeze打包水印程序的setup脚本
"""

import sys
import os
from cx_Freeze import setup, Executable

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加需要包含的文件
include_files = [
    ('templates', 'templates'),
    ('config.json', 'config.json'),
]

# 包含的模块
includes = [
    'tkinter',
    'PIL',
    'PIL._tkinter_finder',
]

# 排除的模块
excludes = [
    'unittest',
    'pydoc',
    'email',
    'http',
    'urllib',
    'xml',
    'bz2',
    'lzma',
]

# 构建选项
build_exe_options = {
    "packages": ["tkinter", "PIL"],
    "includes": includes,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,
}

# 基础设置（Windows GUI应用）
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 不显示控制台窗口

# 可执行文件配置
executables = [
    Executable(
        script="main.py",
        target_name="watermark_app.exe",
        base=base,
        icon=None,  # 如果有图标文件可以在这里指定
    )
]

# 设置
setup(
    name="WatermarkApp",
    version="1.0",
    description="水印添加工具",
    options={"build_exe": build_exe_options},
    executables=executables,
)