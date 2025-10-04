"""
图片管理模块
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
from utils import (
    is_supported_image, get_file_hash, create_thumbnail, 
    get_image_files_from_folder, show_error
)


class ImageItem:
    """图片项类"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_hash = get_file_hash(file_path)
        self.thumbnail = None
        self.image_info = None
        self.status = 'pending'  # pending, loaded, error
        self.error_message = ''
        
        # 加载图片信息
        self._load_image_info()
    
    def _load_image_info(self):
        """加载图片基本信息"""
        try:
            if is_supported_image(self.file_path):
                with Image.open(self.file_path) as img:
                    self.image_info = {
                        'size': img.size,
                        'mode': img.mode,
                        'format': img.format
                    }
                self.status = 'loaded'
            else:
                self.status = 'error'
                self.error_message = '不支持的格式'
        except Exception as e:
            self.status = 'error'
            self.error_message = str(e)
    
    def generate_thumbnail(self, size: Tuple[int, int] = (120, 120)) -> bool:
        """生成缩略图"""
        try:
            self.thumbnail = create_thumbnail(self.file_path, size)
            return self.thumbnail is not None
        except Exception as e:
            print(f"生成缩略图失败 {self.file_path}: {e}")
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.file_name
    
    def get_size_text(self) -> str:
        """获取尺寸文本"""
        if self.image_info:
            width, height = self.image_info['size']
            return f"{width}×{height}"
        return "未知"


class ImageManager:
    """图片管理器类"""
    
    def __init__(self):
        self.images: List[ImageItem] = []
        self.selected_indices: set = set()
        self.current_index: int = -1
        self.thumbnail_size = (120, 120)
    
    def add_image(self, file_path: str) -> bool:
        """添加单张图片"""
        if not os.path.exists(file_path):
            return False
        
        # 检查是否已存在（基于文件路径）
        for img_item in self.images:
            if img_item.file_path == file_path:
                return False
        
        img_item = ImageItem(file_path)
        if img_item.status == 'loaded':
            img_item.generate_thumbnail(self.thumbnail_size)
            self.images.append(img_item)
            return True
        return False
    
    def add_images(self, file_paths: List[str]) -> Tuple[int, int]:
        """批量添加图片"""
        success_count = 0
        error_count = 0
        
        for file_path in file_paths:
            if self.add_image(file_path):
                success_count += 1
            else:
                error_count += 1
        
        return success_count, error_count
    
    def add_folder(self, folder_path: str, recursive: bool = False) -> Tuple[int, int]:
        """添加文件夹中的图片"""
        if not os.path.exists(folder_path):
            return 0, 0
        
        image_files = get_image_files_from_folder(folder_path, recursive)
        return self.add_images(image_files)
    
    def remove_image(self, index: int) -> bool:
        """移除指定索引的图片"""
        if 0 <= index < len(self.images):
            self.images.pop(index)
            # 更新选中状态
            self.selected_indices = {i for i in self.selected_indices if i != index}
            # 调整大于被删除索引的选中项
            self.selected_indices = {i-1 if i > index else i for i in self.selected_indices}
            # 更新当前索引
            if self.current_index == index:
                self.current_index = -1
            elif self.current_index > index:
                self.current_index -= 1
            return True
        return False
    
    def remove_selected(self) -> int:
        """移除选中的图片"""
        if not self.selected_indices:
            return 0
        
        # 按索引从大到小排序，避免删除时索引变化
        sorted_indices = sorted(self.selected_indices, reverse=True)
        removed_count = 0
        
        for index in sorted_indices:
            if self.remove_image(index):
                removed_count += 1
        
        self.selected_indices.clear()
        return removed_count
    
    def clear_all(self):
        """清空所有图片"""
        self.images.clear()
        self.selected_indices.clear()
        self.current_index = -1
    
    def select_image(self, index: int, multi_select: bool = False):
        """选择图片"""
        if not (0 <= index < len(self.images)):
            return
        
        if multi_select:
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                self.selected_indices.add(index)
        else:
            self.selected_indices.clear()
            self.selected_indices.add(index)
        
        self.current_index = index
    
    def get_current_image(self) -> Optional[ImageItem]:
        """获取当前图片"""
        if 0 <= self.current_index < len(self.images):
            return self.images[self.current_index]
        return None
    
    def get_selected_images(self) -> List[ImageItem]:
        """获取选中的图片"""
        return [self.images[i] for i in self.selected_indices if 0 <= i < len(self.images)]
    
    def get_image_count(self) -> int:
        """获取图片总数"""
        return len(self.images)
    
    def get_loaded_count(self) -> int:
        """获取成功加载的图片数量"""
        return sum(1 for img in self.images if img.status == 'loaded')
    
    def get_error_count(self) -> int:
        """获取加载失败的图片数量"""
        return sum(1 for img in self.images if img.status == 'error')
    
    def get_error_messages(self) -> List[str]:
        """获取错误信息列表"""
        return [f"{img.file_name}: {img.error_message}" for img in self.images if img.status == 'error']
    
    def set_thumbnail_size(self, size: Tuple[int, int]):
        """设置缩略图尺寸"""
        self.thumbnail_size = size
        # 重新生成所有缩略图
        for img_item in self.images:
            img_item.generate_thumbnail(size)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.images)
        loaded = self.get_loaded_count()
        error = self.get_error_count()
        
        return {
            'total': total,
            'loaded': loaded,
            'error': error,
            'selected': len(self.selected_indices),
            'current_index': self.current_index
        }
