"""
配置文件 - 存储应用常量和默认设置
"""

import os
from typing import Dict, Any

# 支持的图片格式
SUPPORTED_FORMATS = {
    'input': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'],
    'output': ['JPEG', 'PNG']
}

# 默认设置
DEFAULT_SETTINGS = {
    'watermark': {
        'type': 'text',
        'text_content': 'Watermark',
        'font_family': 'Arial',
        'font_size': 24,
        'font_weight': 'normal',
        'font_style': 'normal',
        'color': '#000000',
        'opacity': 80,
        'position_preset': 'bottom_right',
        'offset_x': 20,
        'offset_y': 20,
        'padding': 10,
        'rotation': 0
    },
    'export': {
        'format': 'JPEG',
        'jpeg_quality': 85,
        'naming_rule': 'keep_original',
        'prefix': 'wm_',
        'suffix': '_watermarked',
        'output_dir': '',
        'avoid_overwrite_original': True
    },
    'ui': {
        'thumbnail_size': 120,
        'preview_size': 800,
        'theme': 'light'
    }
}

# 九宫格位置预设
POSITION_PRESETS = {
    'top_left': (0, 0),
    'top_center': (0.5, 0),
    'top_right': (1, 0),
    'center_left': (0, 0.5),
    'center': (0.5, 0.5),
    'center_right': (1, 0.5),
    'bottom_left': (0, 1),
    'bottom_center': (0.5, 1),
    'bottom_right': (1, 1)
}

# 应用路径
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, 'config.json')
TEMPLATES_DIR = os.path.join(APP_DIR, 'templates')
