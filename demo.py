"""
拖拽功能演示脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_watermark_drag():
    """演示水印拖拽功能"""
    print("=" * 60)
    print("Watermark Studio - 拖拽功能演示")
    print("=" * 60)
    
    print("\n功能说明:")
    print("1. 文件拖拽导入:")
    print("   - 拖拽图片文件到程序窗口")
    print("   - 拖拽文件夹到程序窗口（批量导入）")
    print("   - 右键菜单选择导入选项")
    
    print("\n2. 水印拖拽调整:")
    print("   - 点击预览区域的水印")
    print("   - 拖拽水印到新位置")
    print("   - 实时预览效果")
    print("   - 点击'显示边界'查看水印区域")
    
    print("\n3. 操作提示:")
    print("   - 鼠标悬停在水印上时，光标变为手型")
    print("   - 状态栏显示当前操作状态")
    print("   - 拖拽时显示'正在拖拽水印...'")
    print("   - 释放后显示'水印位置已更新'")
    
    print("\n启动程序:")
    print("python main.py")
    
    print("\n使用技巧:")
    print("- 导入图片后，设置文本水印内容")
    print("- 点击'显示边界'按钮查看水印区域")
    print("- 在水印区域内点击并拖拽调整位置")
    print("- 使用九宫格预设快速定位")
    print("- 结合偏移滑块进行精细调整")
    
    print("\n" + "=" * 60)

def demo_file_operations():
    """演示文件操作"""
    print("\n文件操作演示:")
    print("1. 导入方式:")
    print("   - 工具栏'导入图片'按钮")
    print("   - 工具栏'导入文件夹'按钮") 
    print("   - 直接拖拽文件到窗口")
    print("   - 右键菜单选择")
    
    print("\n2. 支持格式:")
    print("   - JPEG (.jpg, .jpeg)")
    print("   - PNG (.png) - 支持透明")
    print("   - BMP (.bmp)")
    print("   - TIFF (.tiff, .tif)")
    
    print("\n3. 批量处理:")
    print("   - 支持同时导入多张图片")
    print("   - 支持整个文件夹导入")
    print("   - 自动生成缩略图")
    print("   - 显示导入统计信息")

def demo_watermark_features():
    """演示水印功能"""
    print("\n水印功能演示:")
    print("1. 文本水印:")
    print("   - 自定义文本内容")
    print("   - 字体、字号、颜色设置")
    print("   - 透明度调节")
    print("   - 实时预览")
    
    print("\n2. 图片水印:")
    print("   - 支持PNG透明图片")
    print("   - 缩放比例调节")
    print("   - 透明度控制")
    print("   - 位置调整")
    
    print("\n3. 位置控制:")
    print("   - 九宫格预设位置")
    print("   - 鼠标拖拽调整")
    print("   - 精确偏移设置")
    print("   - 旋转角度调节")
    
    print("\n4. 高级功能:")
    print("   - 模板保存/加载")
    print("   - 导出格式选择")
    print("   - 文件命名规则")
    print("   - JPEG质量调节")

if __name__ == "__main__":
    demo_watermark_drag()
    demo_file_operations()
    demo_watermark_features()
    
    print("\n快速开始:")
    print("1. 运行: python main.py")
    print("2. 导入图片文件")
    print("3. 设置水印内容")
    print("4. 点击'显示边界'查看水印区域")
    print("5. 拖拽水印调整位置")
    print("6. 导出处理后的图片")
    
    print("\n享受使用 Watermark Studio！")
