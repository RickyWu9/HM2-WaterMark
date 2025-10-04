"""
应用测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        import config
        print("+ config 模块导入成功")
    except Exception as e:
        print(f"- config 模块导入失败: {e}")
        return False
    
    try:
        import utils
        print("+ utils 模块导入成功")
    except Exception as e:
        print(f"- utils 模块导入失败: {e}")
        return False
    
    try:
        import image_manager
        print("+ image_manager 模块导入成功")
    except Exception as e:
        print(f"- image_manager 模块导入失败: {e}")
        return False
    
    try:
        import watermark_engine
        print("+ watermark_engine 模块导入成功")
    except Exception as e:
        print(f"- watermark_engine 模块导入失败: {e}")
        return False
    
    try:
        import template_manager
        print("+ template_manager 模块导入成功")
    except Exception as e:
        print(f"- template_manager 模块导入失败: {e}")
        return False
    
    try:
        import main_window
        print("+ main_window 模块导入成功")
    except Exception as e:
        print(f"- main_window 模块导入失败: {e}")
        return False
    
    return True

def test_dependencies():
    """测试依赖库"""
    print("\n测试依赖库...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageTk
        print("+ Pillow 库可用")
    except ImportError as e:
        print(f"- Pillow 库不可用: {e}")
        return False
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("+ Tkinter 库可用")
    except ImportError as e:
        print(f"- Tkinter 库不可用: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        from image_manager import ImageManager
        from watermark_engine import WatermarkEngine
        from template_manager import TemplateManager
        
        # 测试图片管理器
        img_manager = ImageManager()
        print("+ ImageManager 创建成功")
        
        # 测试水印引擎
        watermark_engine = WatermarkEngine()
        print("+ WatermarkEngine 创建成功")
        
        # 测试模板管理器
        template_manager = TemplateManager()
        print("+ TemplateManager 创建成功")
        
        # 测试文本水印创建
        text_watermark = watermark_engine.create_text_watermark(
            "Test Watermark", "Arial", 24, "#000000", 80
        )
        if text_watermark:
            print("+ 文本水印创建成功")
        else:
            print("- 文本水印创建失败")
            
        return True
        
    except Exception as e:
        print(f"- 基本功能测试失败: {e}")
        return False

def test_config():
    """测试配置功能"""
    print("\n测试配置功能...")
    
    try:
        from utils import load_config, save_config
        from config import DEFAULT_SETTINGS
        
        # 测试加载配置
        config = load_config()
        print("+ 配置加载成功")
        
        # 测试保存配置
        if save_config(DEFAULT_SETTINGS):
            print("+ 配置保存成功")
        else:
            print("- 配置保存失败")
            
        return True
        
    except Exception as e:
        print(f"- 配置功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Watermark Studio 应用测试")
    print("=" * 50)
    
    all_passed = True
    
    # 测试依赖库
    if not test_dependencies():
        all_passed = False
        print("\n请安装必要的依赖库:")
        print("pip install -r requirements.txt")
        return
    
    # 测试模块导入
    if not test_imports():
        all_passed = False
    
    # 测试基本功能
    if not test_basic_functionality():
        all_passed = False
    
    # 测试配置功能
    if not test_config():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("+ 所有测试通过！应用可以正常运行。")
        print("\n启动应用:")
        print("python main.py")
    else:
        print("- 部分测试失败，请检查错误信息。")
    print("=" * 50)

if __name__ == "__main__":
    main()
