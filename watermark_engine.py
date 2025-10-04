"""
水印处理引擎
"""

import os
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from utils import calculate_watermark_position, get_available_fonts


class WatermarkEngine:
    """水印处理引擎类"""
    
    def __init__(self):
        self.font_cache = {}
    
    def get_font(self, font_family: str, font_size: int, font_weight: str = 'normal', font_style: str = 'normal') -> Optional[ImageFont.FreeTypeFont]:
        """获取字体对象，带缓存"""
        cache_key = f"{font_family}_{font_size}_{font_weight}_{font_style}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype(font_family, font_size)
            self.font_cache[cache_key] = font
            return font
        except Exception:
            try:
                # 回退到默认字体
                font = ImageFont.load_default()
                self.font_cache[cache_key] = font
                return font
            except Exception:
                return None
    
    def create_text_watermark(
        self, 
        text: str, 
        font_family: str, 
        font_size: int, 
        color: str, 
        opacity: int,
        font_weight: str = 'normal',
        font_style: str = 'normal',
        shadow: Optional[Dict[str, Any]] = None,
        stroke: Optional[Dict[str, Any]] = None
    ) -> Optional[Image.Image]:
        """创建文本水印"""
        if not text.strip():
            return None
        
        try:
            font = self.get_font(font_family, font_size, font_weight, font_style)
            if font is None:
                return None
            
            # 计算文本尺寸
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 添加阴影和描边所需的额外空间
            extra_width = 0
            extra_height = 0
            if shadow:
                extra_width += shadow.get('offset_x', 0) + shadow.get('blur', 0)
                extra_height += shadow.get('offset_y', 0) + shadow.get('blur', 0)
            if stroke:
                stroke_width = stroke.get('width', 0)
                extra_width += stroke_width * 2
                extra_height += stroke_width * 2
            
            # 创建水印图像
            watermark = Image.new('RGBA', (text_width + extra_width, text_height + extra_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 绘制阴影
            if shadow:
                shadow_color = shadow.get('color', '#000000')
                shadow_opacity = shadow.get('opacity', 50)
                shadow_offset_x = shadow.get('offset_x', 2)
                shadow_offset_y = shadow.get('offset_y', 2)
                
                # 简化阴影实现（实际应用中可能需要更复杂的模糊效果）
                shadow_pos = (shadow_offset_x, shadow_offset_y)
                shadow_alpha = int(255 * shadow_opacity / 100)
                shadow_rgba = self._hex_to_rgba(shadow_color, shadow_alpha)
                draw.text(shadow_pos, text, font=font, fill=shadow_rgba)
            
            # 绘制描边
            if stroke:
                stroke_color = stroke.get('color', '#FFFFFF')
                stroke_width = stroke.get('width', 1)
                stroke_opacity = stroke.get('opacity', 100)
                stroke_alpha = int(255 * stroke_opacity / 100)
                stroke_rgba = self._hex_to_rgba(stroke_color, stroke_alpha)
                
                # 绘制描边（简化实现）
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((dx, dy), text, font=font, fill=stroke_rgba)
            
            # 绘制主文本
            text_pos = (stroke.get('width', 0) if stroke else 0, 
                       stroke.get('width', 0) if stroke else 0)
            text_alpha = int(255 * opacity / 100)
            text_rgba = self._hex_to_rgba(color, text_alpha)
            draw.text(text_pos, text, font=font, fill=text_rgba)
            
            return watermark
            
        except Exception as e:
            print(f"创建文本水印失败: {e}")
            return None
    
    def create_image_watermark(self, image_path: str, scale: float = 1.0, opacity: int = 80) -> Optional[Image.Image]:
        """创建图片水印"""
        try:
            with Image.open(image_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 缩放
                if scale != 1.0:
                    new_size = (int(img.width * scale), int(img.height * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 调整透明度
                if opacity != 100:
                    alpha = img.split()[-1]  # 获取alpha通道
                    alpha = alpha.point(lambda x: int(x * opacity / 100))
                    img.putalpha(alpha)
                
                return img
                
        except Exception as e:
            print(f"创建图片水印失败: {e}")
            return None
    
    def apply_watermark(
        self, 
        image: Image.Image, 
        watermark: Image.Image, 
        position_preset: str, 
        offset_x: int, 
        offset_y: int,
        padding: int,
        rotation: float = 0
    ) -> Image.Image:
        """将水印应用到图片上"""
        try:
            # 旋转水印
            if rotation != 0:
                watermark = watermark.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
            
            # 计算位置
            position = calculate_watermark_position(
                image.size, watermark.size, position_preset, offset_x, offset_y, padding
            )
            
            # 创建输出图像
            if image.mode != 'RGBA':
                output = image.convert('RGBA')
            else:
                output = image.copy()
            
            # 粘贴水印
            output.paste(watermark, position, watermark)
            
            return output
            
        except Exception as e:
            print(f"应用水印失败: {e}")
            return image
    
    def process_image(
        self, 
        image_path: str, 
        watermark_config: Dict[str, Any], 
        output_path: str,
        export_config: Dict[str, Any]
    ) -> bool:
        """处理单张图片"""
        try:
            # 打开原始图片
            with Image.open(image_path) as image:
                # 转换为RGB模式（用于JPEG输出）
                if export_config.get('format') == 'JPEG' and image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image)
                    image = background
                elif export_config.get('format') == 'PNG' and image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # 创建水印
                watermark = None
                if watermark_config.get('type') == 'text':
                    watermark = self.create_text_watermark(
                        watermark_config.get('text_content', ''),
                        watermark_config.get('font_family', 'Arial'),
                        watermark_config.get('font_size', 24),
                        watermark_config.get('color', '#000000'),
                        watermark_config.get('opacity', 80),
                        watermark_config.get('font_weight', 'normal'),
                        watermark_config.get('font_style', 'normal'),
                        watermark_config.get('shadow'),
                        watermark_config.get('stroke')
                    )
                elif watermark_config.get('type') == 'image':
                    image_watermark_path = watermark_config.get('image_path')
                    if image_watermark_path and os.path.exists(image_watermark_path):
                        watermark = self.create_image_watermark(
                            image_watermark_path,
                            watermark_config.get('scale', 1.0),
                            watermark_config.get('opacity', 80)
                        )
                
                # 应用水印
                if watermark:
                    image = self.apply_watermark(
                        image, watermark,
                        watermark_config.get('position_preset', 'bottom_right'),
                        watermark_config.get('offset_x', 20),
                        watermark_config.get('offset_y', 20),
                        watermark_config.get('padding', 10),
                        watermark_config.get('rotation', 0)
                    )
                
                # 保存图片
                save_kwargs = {}
                if export_config.get('format') == 'JPEG':
                    save_kwargs['quality'] = export_config.get('jpeg_quality', 85)
                    save_kwargs['optimize'] = True
                elif export_config.get('format') == 'PNG':
                    save_kwargs['optimize'] = True
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                image.save(output_path, export_config.get('format'), **save_kwargs)
                return True
                
        except Exception as e:
            print(f"处理图片失败 {image_path}: {e}")
            return False
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """将十六进制颜色转换为RGBA元组"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, alpha)
        return (0, 0, 0, alpha)
