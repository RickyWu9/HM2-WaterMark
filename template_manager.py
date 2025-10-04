"""
模板管理模块
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import TEMPLATES_DIR
from utils import ensure_templates_dir, show_error, show_info


class TemplateManager:
    """模板管理器类"""
    
    def __init__(self):
        ensure_templates_dir()
        self.templates_dir = TEMPLATES_DIR
        
    def save_template(self, name: str, watermark_config: Dict[str, Any], 
                     export_config: Dict[str, Any], description: str = "") -> bool:
        """保存模板"""
        try:
            template_data = {
                'name': name,
                'description': description,
                'created_time': datetime.now().isoformat(),
                'watermark_config': watermark_config,
                'export_config': export_config,
                'version': '1.0'
            }
            
            # 生成文件名（安全的文件名）
            safe_name = self._make_safe_filename(name)
            template_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            # 检查是否已存在
            if os.path.exists(template_file):
                from utils import ask_yes_no
                if not ask_yes_no(f"模板 '{name}' 已存在，是否覆盖？", "确认覆盖"):
                    return False
            
            # 保存文件
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            show_error(f"保存模板失败: {e}")
            return False
    
    def load_template(self, template_file: str) -> Optional[Dict[str, Any]]:
        """加载模板"""
        try:
            template_path = os.path.join(self.templates_dir, template_file)
            if not os.path.exists(template_path):
                show_error(f"模板文件不存在: {template_file}")
                return None
                
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            # 验证模板数据
            if not self._validate_template(template_data):
                show_error("模板文件格式无效")
                return None
                
            return template_data
            
        except Exception as e:
            show_error(f"加载模板失败: {e}")
            return None
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """获取模板列表"""
        templates = []
        
        try:
            if not os.path.exists(self.templates_dir):
                return templates
                
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_path = os.path.join(self.templates_dir, filename)
                    try:
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            
                        if self._validate_template(template_data):
                            template_info = {
                                'filename': filename,
                                'name': template_data.get('name', filename[:-5]),
                                'description': template_data.get('description', ''),
                                'created_time': template_data.get('created_time', ''),
                                'version': template_data.get('version', '1.0')
                            }
                            templates.append(template_info)
                            
                    except Exception as e:
                        print(f"读取模板文件失败 {filename}: {e}")
                        
        except Exception as e:
            print(f"获取模板列表失败: {e}")
            
        # 按创建时间排序
        templates.sort(key=lambda x: x.get('created_time', ''), reverse=True)
        return templates
    
    def delete_template(self, template_file: str) -> bool:
        """删除模板"""
        try:
            template_path = os.path.join(self.templates_dir, template_file)
            if os.path.exists(template_path):
                os.remove(template_path)
                return True
            else:
                show_error("模板文件不存在")
                return False
                
        except Exception as e:
            show_error(f"删除模板失败: {e}")
            return False
    
    def rename_template(self, old_file: str, new_name: str) -> bool:
        """重命名模板"""
        try:
            # 加载原模板
            template_data = self.load_template(old_file)
            if not template_data:
                return False
                
            # 更新名称
            template_data['name'] = new_name
            template_data['modified_time'] = datetime.now().isoformat()
            
            # 生成新文件名
            safe_name = self._make_safe_filename(new_name)
            new_file = f"{safe_name}.json"
            
            # 检查新文件名是否已存在
            new_path = os.path.join(self.templates_dir, new_file)
            if os.path.exists(new_path) and new_file != old_file:
                from utils import ask_yes_no
                if not ask_yes_no(f"模板 '{new_name}' 已存在，是否覆盖？", "确认覆盖"):
                    return False
            
            # 保存新文件
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            # 删除旧文件（如果文件名不同）
            if new_file != old_file:
                old_path = os.path.join(self.templates_dir, old_file)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    
            return True
            
        except Exception as e:
            show_error(f"重命名模板失败: {e}")
            return False
    
    def export_template(self, template_file: str, export_path: str) -> bool:
        """导出模板到指定路径"""
        try:
            template_path = os.path.join(self.templates_dir, template_file)
            if not os.path.exists(template_path):
                show_error("模板文件不存在")
                return False
                
            # 复制文件
            import shutil
            shutil.copy2(template_path, export_path)
            return True
            
        except Exception as e:
            show_error(f"导出模板失败: {e}")
            return False
    
    def import_template(self, import_path: str) -> bool:
        """从指定路径导入模板"""
        try:
            if not os.path.exists(import_path):
                show_error("导入文件不存在")
                return False
                
            # 验证模板文件
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            if not self._validate_template(template_data):
                show_error("模板文件格式无效")
                return False
            
            # 生成目标文件名
            template_name = template_data.get('name', 'imported_template')
            safe_name = self._make_safe_filename(template_name)
            target_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            # 检查是否已存在
            if os.path.exists(target_file):
                from utils import ask_yes_no
                if not ask_yes_no(f"模板 '{template_name}' 已存在，是否覆盖？", "确认覆盖"):
                    return False
            
            # 复制文件
            import shutil
            shutil.copy2(import_path, target_file)
            return True
            
        except Exception as e:
            show_error(f"导入模板失败: {e}")
            return False
    
    def get_default_template(self) -> Dict[str, Any]:
        """获取默认模板"""
        from config import DEFAULT_SETTINGS
        
        return {
            'name': '默认模板',
            'description': '系统默认设置',
            'created_time': datetime.now().isoformat(),
            'watermark_config': DEFAULT_SETTINGS['watermark'].copy(),
            'export_config': DEFAULT_SETTINGS['export'].copy(),
            'version': '1.0'
        }
    
    def create_default_templates(self):
        """创建默认模板"""
        # 文本水印模板
        text_template = {
            'name': '文本水印模板',
            'description': '简单的文本水印，位于右下角',
            'created_time': datetime.now().isoformat(),
            'watermark_config': {
                'type': 'text',
                'text_content': 'Copyright © 2024',
                'font_family': 'Arial',
                'font_size': 24,
                'color': '#FFFFFF',
                'opacity': 80,
                'position_preset': 'bottom_right',
                'offset_x': 20,
                'offset_y': 20,
                'padding': 10,
                'rotation': 0
            },
            'export_config': {
                'format': 'JPEG',
                'jpeg_quality': 85,
                'naming_rule': 'suffix',
                'prefix': 'wm_',
                'suffix': '_watermarked',
                'output_dir': ''
            },
            'version': '1.0'
        }
        
        # Logo水印模板
        logo_template = {
            'name': 'Logo水印模板',
            'description': '透明Logo水印，位于右下角',
            'created_time': datetime.now().isoformat(),
            'watermark_config': {
                'type': 'image',
                'image_path': '',
                'scale': 0.3,
                'opacity': 60,
                'position_preset': 'bottom_right',
                'offset_x': 20,
                'offset_y': 20,
                'padding': 10,
                'rotation': 0
            },
            'export_config': {
                'format': 'PNG',
                'jpeg_quality': 85,
                'naming_rule': 'prefix',
                'prefix': 'logo_',
                'suffix': '_watermarked',
                'output_dir': ''
            },
            'version': '1.0'
        }
        
        # 保存默认模板
        templates = [text_template, logo_template]
        for template in templates:
            safe_name = self._make_safe_filename(template['name'])
            template_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            # 只在不存在时创建
            if not os.path.exists(template_file):
                try:
                    with open(template_file, 'w', encoding='utf-8') as f:
                        json.dump(template, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"创建默认模板失败 {template['name']}: {e}")
    
    def _validate_template(self, template_data: Dict[str, Any]) -> bool:
        """验证模板数据格式"""
        try:
            # 检查必需字段
            required_fields = ['watermark_config', 'export_config']
            for field in required_fields:
                if field not in template_data:
                    return False
            
            # 检查水印配置
            watermark_config = template_data['watermark_config']
            if 'type' not in watermark_config:
                return False
                
            # 检查导出配置
            export_config = template_data['export_config']
            if 'format' not in export_config:
                return False
                
            return True
            
        except Exception:
            return False
    
    def _make_safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_name = name
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
            
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
            
        # 确保不为空
        if not safe_name.strip():
            safe_name = 'template'
            
        return safe_name.strip()
    
    def get_template_preview(self, template_file: str) -> Optional[str]:
        """获取模板预览信息"""
        template_data = self.load_template(template_file)
        if not template_data:
            return None
            
        try:
            watermark_config = template_data['watermark_config']
            export_config = template_data['export_config']
            
            preview_lines = []
            preview_lines.append(f"名称: {template_data.get('name', '未知')}")
            preview_lines.append(f"描述: {template_data.get('description', '无')}")
            preview_lines.append("")
            
            # 水印信息
            if watermark_config['type'] == 'text':
                preview_lines.append("水印类型: 文本")
                preview_lines.append(f"文本内容: {watermark_config.get('text_content', '')}")
                preview_lines.append(f"字体: {watermark_config.get('font_family', 'Arial')}")
                preview_lines.append(f"字号: {watermark_config.get('font_size', 24)}")
                preview_lines.append(f"颜色: {watermark_config.get('color', '#000000')}")
            else:
                preview_lines.append("水印类型: 图片")
                preview_lines.append(f"缩放: {watermark_config.get('scale', 1.0)}")
            
            preview_lines.append(f"透明度: {watermark_config.get('opacity', 100)}%")
            preview_lines.append(f"位置: {watermark_config.get('position_preset', 'bottom_right')}")
            preview_lines.append("")
            
            # 导出信息
            preview_lines.append(f"输出格式: {export_config.get('format', 'JPEG')}")
            if export_config.get('format') == 'JPEG':
                preview_lines.append(f"JPEG质量: {export_config.get('jpeg_quality', 85)}")
            preview_lines.append(f"命名规则: {export_config.get('naming_rule', 'keep_original')}")
            
            return "\n".join(preview_lines)
            
        except Exception as e:
            return f"预览生成失败: {e}"
