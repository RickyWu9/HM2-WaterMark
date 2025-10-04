"""
工具函数模块
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, messagebox
from config import SUPPORTED_FORMATS, DEFAULT_SETTINGS, CONFIG_FILE, TEMPLATES_DIR


def get_file_hash(file_path: str) -> str:
    """获取文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def is_supported_image(file_path: str) -> bool:
    """检查文件是否为支持的图片格式"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS['input']


def get_image_files_from_folder(folder_path: str, recursive: bool = False) -> List[str]:
    """从文件夹获取所有图片文件"""
    image_files = []
    
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_supported_image(file_path):
                    image_files.append(file_path)
    else:
        try:
            files = os.listdir(folder_path)
            for file in files:
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and is_supported_image(file_path):
                    image_files.append(file_path)
        except Exception:
            pass
    
    return image_files


def create_thumbnail(image_path: str, size: Tuple[int, int] = (120, 120)) -> Optional[Image.Image]:
    """创建图片缩略图"""
    try:
        with Image.open(image_path) as img:
            # 保持宽高比
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img.copy()
    except Exception:
        return None


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def ensure_templates_dir():
    """确保模板目录存在"""
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)


def get_available_fonts() -> List[str]:
    """获取系统可用字体"""
    try:
        import tkinter.font as tkFont
        return list(tkFont.families())
    except Exception:
        return ['Arial', 'Times New Roman', 'Courier New', 'Helvetica']


def calculate_watermark_position(
    image_size: Tuple[int, int], 
    watermark_size: Tuple[int, int], 
    position_preset: str, 
    offset_x: int, 
    offset_y: int,
    padding: int
) -> Tuple[int, int]:
    """计算水印位置"""
    from config import POSITION_PRESETS
    
    img_width, img_height = image_size
    wm_width, wm_height = watermark_size
    
    if position_preset not in POSITION_PRESETS:
        position_preset = 'bottom_right'
    
    preset_x, preset_y = POSITION_PRESETS[position_preset]
    
    # 计算基础位置
    base_x = int(preset_x * (img_width - wm_width))
    base_y = int(preset_y * (img_height - wm_height))
    
    # 添加偏移和边距
    final_x = max(padding, min(img_width - wm_width - padding, base_x + offset_x))
    final_y = max(padding, min(img_height - wm_height - padding, base_y + offset_y))
    
    return final_x, final_y


def generate_output_filename(original_path: str, naming_rule: str, prefix: str = '', suffix: str = '') -> str:
    """生成输出文件名"""
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    ext = os.path.splitext(original_path)[1]
    
    if naming_rule == 'prefix':
        return f"{prefix}{base_name}{ext}"
    elif naming_rule == 'suffix':
        return f"{base_name}{suffix}{ext}"
    else:  # keep_original
        return f"{base_name}{ext}"


def ensure_unique_filename(output_dir: str, filename: str) -> str:
    """确保文件名唯一，避免覆盖"""
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        return filename
    
    base_name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{base_name}_{counter}{ext}"
        new_path = os.path.join(output_dir, new_filename)
        if not os.path.exists(new_path):
            return new_filename
        counter += 1


def show_error(message: str, title: str = "错误"):
    """显示错误对话框"""
    messagebox.showerror(title, message)


def show_info(message: str, title: str = "信息"):
    """显示信息对话框"""
    messagebox.showinfo(title, message)


def show_warning(message: str, title: str = "警告"):
    """显示警告对话框"""
    messagebox.showwarning(title, message)


def ask_yes_no(message: str, title: str = "确认") -> bool:
    """显示是/否确认对话框"""
    return messagebox.askyesno(title, message)
