"""
主窗口界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
from typing import Dict, Any, Optional
from PIL import Image, ImageTk
import threading
import json

from config import DEFAULT_SETTINGS, POSITION_PRESETS
from image_manager import ImageManager
from watermark_engine import WatermarkEngine
from template_manager import TemplateManager
from utils import (
    load_config, save_config, get_available_fonts, 
    show_error, show_info, ask_yes_no, generate_output_filename,
    ensure_unique_filename
)


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Watermark Studio - 批量图片水印工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 核心组件
        self.image_manager = ImageManager()
        self.watermark_engine = WatermarkEngine()
        self.template_manager = TemplateManager()
        
        # 配置
        self.config = load_config()
        
        # UI变量
        self.setup_variables()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
        # 加载配置
        self.load_settings()
        
        # 预览相关
        self.preview_image = None
        self.preview_photo = None
        
        # 拖拽相关
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.watermark_position = None  # 存储当前水印在预览中的位置
        self.canvas_scale = 1.0  # 画布缩放比例
        self.show_watermark_bounds = False  # 是否显示水印边界
        
    def setup_variables(self):
        """设置UI变量"""
        # 水印设置
        self.watermark_type = tk.StringVar(value=self.config['watermark']['type'])
        self.text_content = tk.StringVar(value=self.config['watermark']['text_content'])
        self.font_family = tk.StringVar(value=self.config['watermark']['font_family'])
        self.font_size = tk.IntVar(value=self.config['watermark']['font_size'])
        self.font_color = tk.StringVar(value=self.config['watermark']['color'])
        self.opacity = tk.IntVar(value=self.config['watermark']['opacity'])
        self.position_preset = tk.StringVar(value=self.config['watermark']['position_preset'])
        self.offset_x = tk.IntVar(value=self.config['watermark']['offset_x'])
        self.offset_y = tk.IntVar(value=self.config['watermark']['offset_y'])
        self.rotation = tk.IntVar(value=self.config['watermark']['rotation'])
        
        # 导出设置
        self.export_format = tk.StringVar(value=self.config['export']['format'])
        self.jpeg_quality = tk.IntVar(value=self.config['export']['jpeg_quality'])
        self.naming_rule = tk.StringVar(value=self.config['export']['naming_rule'])
        self.prefix_text = tk.StringVar(value=self.config['export']['prefix'])
        self.suffix_text = tk.StringVar(value=self.config['export']['suffix'])
        self.output_dir = tk.StringVar(value=self.config['export']['output_dir'])
        
        # 图片水印设置
        self.image_watermark_path = tk.StringVar()
        self.image_scale = tk.DoubleVar(value=1.0)
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        self.create_main_frame()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建左侧图片列表
        self.create_image_list()
        
        # 创建中央预览区
        self.create_preview_area()
        
        # 创建右侧设置面板
        self.create_settings_panel()
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_main_frame(self):
        """创建主框架"""
        # 主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建PanedWindow用于分割界面
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # 导入按钮
        ttk.Button(toolbar, text="导入图片", command=self.import_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="导入文件夹", command=self.import_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 模板按钮
        ttk.Button(toolbar, text="保存模板", command=self.save_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="加载模板", command=self.load_template).pack(side=tk.LEFT, padx=(0, 5))
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 导出按钮
        ttk.Button(toolbar, text="开始导出", command=self.start_export, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
    def create_image_list(self):
        """创建图片列表"""
        # 左侧框架
        left_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(left_frame, weight=0)
        
        # 标题
        ttk.Label(left_frame, text="图片列表", font=("", 12, "bold")).pack(pady=(0, 5))
        
        # 操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_frame, text="清空", command=self.clear_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="删除选中", command=self.remove_selected).pack(side=tk.LEFT)
        
        # 列表框架
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        self.image_tree = ttk.Treeview(list_frame, columns=("size",), show="tree headings", height=15)
        self.image_tree.heading("#0", text="文件名")
        self.image_tree.heading("size", text="尺寸")
        self.image_tree.column("#0", width=150)
        self.image_tree.column("size", width=80)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_tree.bind("<<TreeviewSelect>>", self.on_image_select)
        
    def create_preview_area(self):
        """创建预览区域"""
        # 中央框架
        center_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(center_frame, weight=1)
        
        # 标题
        ttk.Label(center_frame, text="预览", font=("", 12, "bold")).pack(pady=(0, 5))
        
        # 预览画布框架
        canvas_frame = ttk.Frame(center_frame, relief=tk.SUNKEN, borderwidth=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建画布和滚动条
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white")
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # 布局
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 预览控制
        control_frame = ttk.Frame(center_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(control_frame, text="适应窗口", command=self.fit_to_window).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="原始尺寸", command=self.actual_size).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="刷新预览", command=self.refresh_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="显示边界", command=self.toggle_watermark_bounds).pack(side=tk.LEFT)
        
    def create_settings_panel(self):
        """创建设置面板"""
        # 右侧框架
        right_frame = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(right_frame, weight=0)
        
        # 创建Notebook
        self.settings_notebook = ttk.Notebook(right_frame)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 水印设置页
        self.create_watermark_tab()
        
        # 布局设置页
        self.create_layout_tab()
        
        # 导出设置页
        self.create_export_tab()
        
    def create_watermark_tab(self):
        """创建水印设置标签页"""
        watermark_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(watermark_frame, text="水印")
        
        # 创建滚动区域
        canvas = tk.Canvas(watermark_frame)
        scrollbar = ttk.Scrollbar(watermark_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 水印类型
        type_frame = ttk.LabelFrame(scrollable_frame, text="水印类型", padding=10)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type, 
                       value="text", command=self.on_watermark_type_change).pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                       value="image", command=self.on_watermark_type_change).pack(anchor=tk.W)
        
        # 文本水印设置
        self.text_frame = ttk.LabelFrame(scrollable_frame, text="文本设置", padding=10)
        self.text_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.text_frame, text="文本内容:").pack(anchor=tk.W)
        text_entry = ttk.Entry(self.text_frame, textvariable=self.text_content, width=30)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', lambda e: self.refresh_preview())
        
        # 字体设置
        font_frame = ttk.Frame(self.text_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="字体:").pack(anchor=tk.W)
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family, 
                                 values=get_available_fonts(), state="readonly")
        font_combo.pack(fill=tk.X, pady=(0, 5))
        font_combo.bind('<<ComboboxSelected>>', self.on_font_family_change)
        
        ttk.Label(font_frame, text="字号:").pack(anchor=tk.W)
        size_frame = ttk.Frame(font_frame)
        size_frame.pack(fill=tk.X)
        
        # 字体大小滑块
        font_scale = ttk.Scale(size_frame, from_=8, to=100, variable=self.font_size, 
                              orient=tk.HORIZONTAL, command=self.on_font_size_change)
        font_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 字体大小显示标签
        size_label = ttk.Label(size_frame, textvariable=self.font_size, width=3)
        size_label.pack(side=tk.RIGHT)
        
        # 字体大小输入框
        size_entry = ttk.Entry(size_frame, textvariable=self.font_size, width=5)
        size_entry.pack(side=tk.RIGHT, padx=(0, 5))
        size_entry.bind('<Return>', lambda e: self.on_font_size_change())
        
        # 颜色设置
        color_frame = ttk.Frame(self.text_frame)
        color_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, text="选择颜色", 
                                     command=self.choose_color, width=10)
        self.color_button.pack(side=tk.RIGHT)
        
        # 图片水印设置
        self.image_frame = ttk.LabelFrame(scrollable_frame, text="图片设置", padding=10)
        self.image_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(self.image_frame, text="选择图片", 
                  command=self.choose_watermark_image).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.image_frame, text="缩放比例:").pack(anchor=tk.W)
        scale_frame = ttk.Frame(self.image_frame)
        scale_frame.pack(fill=tk.X)
        ttk.Scale(scale_frame, from_=0.1, to=2.0, variable=self.image_scale, 
                 orient=tk.HORIZONTAL, command=lambda v: self.refresh_preview()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(scale_frame, textvariable=self.image_scale, width=5).pack(side=tk.RIGHT)
        
        # 透明度设置
        opacity_frame = ttk.LabelFrame(scrollable_frame, text="透明度", padding=10)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        opacity_scale_frame = ttk.Frame(opacity_frame)
        opacity_scale_frame.pack(fill=tk.X)
        ttk.Scale(opacity_scale_frame, from_=0, to=100, variable=self.opacity, 
                 orient=tk.HORIZONTAL, command=lambda v: self.refresh_preview()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(opacity_scale_frame, textvariable=self.opacity, width=3).pack(side=tk.RIGHT)
        ttk.Label(opacity_scale_frame, text="%").pack(side=tk.RIGHT)
        
        # 布局滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 初始状态
        self.on_watermark_type_change()
        
    def create_layout_tab(self):
        """创建布局设置标签页"""
        layout_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(layout_frame, text="布局")
        
        # 位置预设
        position_frame = ttk.LabelFrame(layout_frame, text="位置预设", padding=10)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 九宫格按钮
        grid_frame = ttk.Frame(position_frame)
        grid_frame.pack()
        
        positions = [
            ('top_left', 'top_center', 'top_right'),
            ('center_left', 'center', 'center_right'),
            ('bottom_left', 'bottom_center', 'bottom_right')
        ]
        
        for row, pos_row in enumerate(positions):
            for col, pos in enumerate(pos_row):
                btn = ttk.Radiobutton(grid_frame, text="●", variable=self.position_preset, 
                                     value=pos, command=self.refresh_preview)
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # 偏移设置
        offset_frame = ttk.LabelFrame(layout_frame, text="偏移调整", padding=10)
        offset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(offset_frame, text="水平偏移:").pack(anchor=tk.W)
        x_frame = ttk.Frame(offset_frame)
        x_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Scale(x_frame, from_=-100, to=100, variable=self.offset_x, 
                 orient=tk.HORIZONTAL, command=lambda v: self.refresh_preview()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(x_frame, textvariable=self.offset_x, width=4).pack(side=tk.RIGHT)
        
        ttk.Label(offset_frame, text="垂直偏移:").pack(anchor=tk.W)
        y_frame = ttk.Frame(offset_frame)
        y_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Scale(y_frame, from_=-100, to=100, variable=self.offset_y, 
                 orient=tk.HORIZONTAL, command=lambda v: self.refresh_preview()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(y_frame, textvariable=self.offset_y, width=4).pack(side=tk.RIGHT)
        
        # 旋转设置
        rotation_frame = ttk.LabelFrame(layout_frame, text="旋转", padding=10)
        rotation_frame.pack(fill=tk.X, pady=(0, 10))
        
        rot_frame = ttk.Frame(rotation_frame)
        rot_frame.pack(fill=tk.X)
        ttk.Scale(rot_frame, from_=-180, to=180, variable=self.rotation, 
                 orient=tk.HORIZONTAL, command=lambda v: self.refresh_preview()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(rot_frame, textvariable=self.rotation, width=4).pack(side=tk.RIGHT)
        ttk.Label(rot_frame, text="°").pack(side=tk.RIGHT)
        
    def create_export_tab(self):
        """创建导出设置标签页"""
        export_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(export_frame, text="导出")
        
        # 输出格式
        format_frame = ttk.LabelFrame(export_frame, text="输出格式", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.export_format, 
                       value="JPEG", command=self.on_format_change).pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.export_format, 
                       value="PNG", command=self.on_format_change).pack(anchor=tk.W)
        
        # JPEG质量
        self.quality_frame = ttk.LabelFrame(export_frame, text="JPEG质量", padding=10)
        self.quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        quality_scale_frame = ttk.Frame(self.quality_frame)
        quality_scale_frame.pack(fill=tk.X)
        ttk.Scale(quality_scale_frame, from_=1, to=100, variable=self.jpeg_quality, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(quality_scale_frame, textvariable=self.jpeg_quality, width=3).pack(side=tk.RIGHT)
        
        # 文件命名
        naming_frame = ttk.LabelFrame(export_frame, text="文件命名", padding=10)
        naming_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(naming_frame, text="保留原文件名", variable=self.naming_rule, 
                       value="keep_original", command=self.on_naming_change).pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.naming_rule, 
                       value="prefix", command=self.on_naming_change).pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.naming_rule, 
                       value="suffix", command=self.on_naming_change).pack(anchor=tk.W)
        
        self.prefix_entry = ttk.Entry(naming_frame, textvariable=self.prefix_text, width=20)
        self.suffix_entry = ttk.Entry(naming_frame, textvariable=self.suffix_text, width=20)
        
        # 输出目录
        dir_frame = ttk.LabelFrame(export_frame, text="输出目录", padding=10)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill=tk.X)
        
        ttk.Entry(dir_select_frame, textvariable=self.output_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_select_frame, text="浏览", command=self.choose_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 初始状态
        self.on_format_change()
        self.on_naming_change()
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var, 
                                          length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定拖拽事件到预览画布
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.preview_canvas.bind("<Motion>", self.on_canvas_motion)  # 绑定鼠标移动事件
        
        # 文件拖拽支持
        self.setup_file_drag_drop()
        
        # 拖拽功能已移除，只保留水印拖拽
    
    def setup_file_drag_drop(self):
        """设置文件拖拽支持（已移除）"""
        # 文件拖拽功能已移除
        pass
        
    def load_settings(self):
        """加载设置"""
        # 更新颜色按钮
        self.update_color_button()
        
    def on_watermark_type_change(self):
        """水印类型改变事件"""
        if self.watermark_type.get() == "text":
            self.text_frame.pack(fill=tk.X, pady=(0, 10))
            self.image_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.refresh_preview()
        
    def on_format_change(self):
        """输出格式改变事件"""
        if self.export_format.get() == "JPEG":
            self.quality_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.quality_frame.pack_forget()
            
    def on_naming_change(self):
        """命名规则改变事件"""
        # 隐藏所有输入框
        self.prefix_entry.pack_forget()
        self.suffix_entry.pack_forget()
        
        # 根据选择显示对应输入框
        if self.naming_rule.get() == "prefix":
            self.prefix_entry.pack(fill=tk.X, pady=(5, 0))
        elif self.naming_rule.get() == "suffix":
            self.suffix_entry.pack(fill=tk.X, pady=(5, 0))
    
    def on_font_size_change(self, value=None):
        """字体大小改变事件"""
        try:
            # 确保字体大小在合理范围内
            size = int(self.font_size.get())
            if size < 8:
                size = 8
                self.font_size.set(8)
            elif size > 100:
                size = 100
                self.font_size.set(100)
            
            print(f"字体大小改变为: {size}")  # 调试信息
            
            # 清空字体缓存以确保新字体大小生效
            self.watermark_engine.clear_font_cache()
            
            # 刷新预览
            self.refresh_preview()
        except ValueError:
            # 如果输入无效，重置为默认值
            self.font_size.set(24)
            self.watermark_engine.clear_font_cache()
            self.refresh_preview()
    
    def on_font_family_change(self, event=None):
        """字体族改变事件"""
        # 清空字体缓存以确保新字体生效
        self.watermark_engine.clear_font_cache()
        # 刷新预览
        self.refresh_preview()
            
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(initialcolor=self.font_color.get())
        if color[1]:
            self.font_color.set(color[1])
            self.update_color_button()
            self.refresh_preview()
            
    def update_color_button(self):
        """更新颜色按钮"""
        try:
            self.color_button.configure(bg=self.font_color.get())
        except:
            pass
            
    def choose_watermark_image(self):
        """选择水印图片"""
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if file_path:
            self.image_watermark_path.set(file_path)
            self.refresh_preview()
            
    def choose_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)
            
    def import_images(self):
        """导入图片"""
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )
        
        if file_paths:
            success, error = self.image_manager.add_images(list(file_paths))
            self.update_image_list()
            self.update_status(f"导入完成: 成功 {success} 张，失败 {error} 张")
            
    def import_folder(self):
        """导入文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            # 询问是否递归
            recursive = ask_yes_no("是否包含子文件夹？", "导入选项")
            success, error = self.image_manager.add_folder(folder_path, recursive)
            self.update_image_list()
            self.update_status(f"导入完成: 成功 {success} 张，失败 {error} 张")
            
    def clear_images(self):
        """清空图片列表"""
        if ask_yes_no("确定要清空所有图片吗？", "确认清空"):
            self.image_manager.clear_all()
            self.update_image_list()
            self.clear_preview()
            self.update_status("已清空图片列表")
            
    def remove_selected(self):
        """删除选中图片"""
        count = self.image_manager.remove_selected()
        if count > 0:
            self.update_image_list()
            self.update_status(f"已删除 {count} 张图片")
            
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_tree.selection()
        if selection:
            item = selection[0]
            index = int(self.image_tree.item(item)['tags'][0])
            self.image_manager.select_image(index)
            self.refresh_preview()
            
    def update_image_list(self):
        """更新图片列表"""
        # 清空现有项目
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
            
        # 添加图片项目
        for i, img_item in enumerate(self.image_manager.images):
            self.image_tree.insert("", "end", 
                                  text=img_item.get_display_name(),
                                  values=(img_item.get_size_text(),),
                                  tags=(str(i),))
                                  
    def refresh_preview(self):
        """刷新预览"""
        current_image = self.image_manager.get_current_image()
        if not current_image:
            self.clear_preview()
            return
            
        try:
            # 在后台线程中生成预览
            threading.Thread(target=self._generate_preview, 
                           args=(current_image,), daemon=True).start()
        except Exception as e:
            print(f"预览失败: {e}")
            
    def _generate_preview(self, image_item):
        """生成预览（后台线程）"""
        try:
            # 打开原始图片
            with Image.open(image_item.file_path) as img:
                # 转换为RGBA以支持水印
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 获取水印配置
                watermark_config = self.get_watermark_config()
                
                # 创建水印
                watermark = None
                if watermark_config['type'] == 'text' and watermark_config['text_content']:
                    print(f"创建文本水印: 内容='{watermark_config['text_content']}', 字体='{watermark_config['font_family']}', 大小={watermark_config['font_size']}")  # 调试信息
                    watermark = self.watermark_engine.create_text_watermark(
                        watermark_config['text_content'],
                        watermark_config['font_family'],
                        watermark_config['font_size'],
                        watermark_config['color'],
                        watermark_config['opacity'],
                        watermark_config.get('font_weight', 'normal'),
                        watermark_config.get('font_style', 'normal')
                    )
                elif watermark_config['type'] == 'image' and watermark_config.get('image_path'):
                    if os.path.exists(watermark_config['image_path']):
                        watermark = self.watermark_engine.create_image_watermark(
                            watermark_config['image_path'],
                            watermark_config.get('scale', 1.0),
                            watermark_config['opacity']
                        )
                
                # 应用水印并记录位置
                if watermark:
                    # 计算水印在原始图片上的位置
                    watermark_pos = self._calculate_watermark_position(
                        img.size, watermark.size, watermark_config
                    )
                    
                    img = self.watermark_engine.apply_watermark(
                        img, watermark,
                        watermark_config['position_preset'],
                        watermark_config['offset_x'],
                        watermark_config['offset_y'],
                        watermark_config.get('padding', 10),
                        watermark_config.get('rotation', 0)
                    )
                else:
                    watermark_pos = None
                
                # 转换为RGB用于显示
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # 缩放以适应预览区域
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
                
                # 转换为PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # 在主线程中更新UI
                self.root.after(0, self._update_preview_ui, photo, img.size, watermark_pos)
                
        except Exception as e:
            print(f"生成预览失败: {e}")
            self.root.after(0, self.clear_preview)
            
    def _update_preview_ui(self, photo, size, watermark_pos=None):
        """更新预览UI（主线程）"""
        self.preview_photo = photo
        self.preview_canvas.delete("all")
        
        # 计算居中位置
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        x = max(0, (canvas_width - size[0]) // 2)
        y = max(0, (canvas_height - size[1]) // 2)
        
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)
        
        # 如果有水印位置信息，记录到画布坐标中
        if watermark_pos:
            # 计算缩放比例
            scale_x = size[0] / self.image_manager.get_current_image().image_info['size'][0]
            scale_y = size[1] / self.image_manager.get_current_image().image_info['size'][1]
            self.canvas_scale = min(scale_x, scale_y)
            
            # 转换水印位置到画布坐标
            wx, wy, ww, wh = watermark_pos
            canvas_wx = x + wx * self.canvas_scale
            canvas_wy = y + wy * self.canvas_scale
            canvas_ww = ww * self.canvas_scale
            canvas_wh = wh * self.canvas_scale
            
            self.watermark_position = (canvas_wx, canvas_wy, canvas_ww, canvas_wh)
            
            # 绘制水印区域边框（如果启用）
            if self.show_watermark_bounds:
                # 绘制水印边界
                self.preview_canvas.create_rectangle(canvas_wx, canvas_wy, 
                                                   canvas_wx + canvas_ww, canvas_wy + canvas_wh,
                                                   outline="red", width=2, dash=(5, 5), tags="watermark_bounds")
                
                # 绘制拖拽检测区域
                margin = 10
                self.preview_canvas.create_rectangle(canvas_wx - margin, canvas_wy - margin, 
                                                   canvas_wx + canvas_ww + margin, canvas_wy + canvas_wh + margin,
                                                   outline="blue", width=1, dash=(2, 2), tags="drag_bounds")
                
                # 添加提示文本
                self.preview_canvas.create_text(canvas_wx + canvas_ww/2, canvas_wy - 20,
                                               text="可拖拽区域", fill="blue", font=("Arial", 10),
                                               tags="drag_hint")
        else:
            self.watermark_position = None
        
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        
    def clear_preview(self):
        """清空预览"""
        self.preview_canvas.delete("all")
        self.preview_photo = None
        
    def fit_to_window(self):
        """适应窗口"""
        self.refresh_preview()
        
    def actual_size(self):
        """原始尺寸"""
        # TODO: 实现原始尺寸显示
        pass
    
    def toggle_watermark_bounds(self):
        """切换水印边界显示"""
        self.show_watermark_bounds = not self.show_watermark_bounds
        self.refresh_preview()
        
        if self.show_watermark_bounds:
            self.update_status("已显示水印边界")
        else:
            self.update_status("已隐藏水印边界")
        
    def get_watermark_config(self) -> Dict[str, Any]:
        """获取水印配置"""
        config = {
            'type': self.watermark_type.get(),
            'text_content': self.text_content.get(),
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'color': self.font_color.get(),
            'opacity': self.opacity.get(),
            'position_preset': self.position_preset.get(),
            'offset_x': self.offset_x.get(),
            'offset_y': self.offset_y.get(),
            'padding': 10,
            'rotation': self.rotation.get()
        }
        
        if self.watermark_type.get() == 'image':
            config.update({
                'image_path': self.image_watermark_path.get(),
                'scale': self.image_scale.get()
            })
            
        return config
        
    def get_export_config(self) -> Dict[str, Any]:
        """获取导出配置"""
        return {
            'format': self.export_format.get(),
            'jpeg_quality': self.jpeg_quality.get(),
            'naming_rule': self.naming_rule.get(),
            'prefix': self.prefix_text.get(),
            'suffix': self.suffix_text.get(),
            'output_dir': self.output_dir.get()
        }
        
    def save_template(self):
        """保存模板"""
        from tkinter import simpledialog
        
        name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if name:
            description = simpledialog.askstring("保存模板", "请输入模板描述（可选）:", initialvalue="")
            
            watermark_config = self.get_watermark_config()
            export_config = self.get_export_config()
            
            if self.template_manager.save_template(name, watermark_config, export_config, description or ""):
                show_info(f"模板 '{name}' 保存成功！")
            else:
                show_error("模板保存失败")
        
    def load_template(self):
        """加载模板"""
        templates = self.template_manager.get_template_list()
        if not templates:
            show_info("没有可用的模板")
            return
            
        # 创建模板选择对话框
        self._show_template_dialog(templates)
    
    def _show_template_dialog(self, templates):
        """显示模板选择对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择模板")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 模板列表
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="可用模板:", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # 列表框
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        listbox = tk.Listbox(listbox_frame, height=10)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        for template in templates:
            listbox.insert(tk.END, template['name'])
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(frame, text="预览", padding=5)
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        preview_text = tk.Text(preview_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        preview_text.pack(fill=tk.X)
        
        def on_select(event):
            selection = listbox.curselection()
            if selection:
                template = templates[selection[0]]
                preview_info = self.template_manager.get_template_preview(template['filename'])
                preview_text.configure(state=tk.NORMAL)
                preview_text.delete(1.0, tk.END)
                preview_text.insert(1.0, preview_info or "预览信息不可用")
                preview_text.configure(state=tk.DISABLED)
        
        listbox.bind('<<ListboxSelect>>', on_select)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                template = templates[selection[0]]
                self._apply_template(template['filename'])
                dialog.destroy()
            else:
                show_error("请选择一个模板")
        
        ttk.Button(button_frame, text="加载", command=load_selected).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # 选中第一个模板
        if templates:
            listbox.selection_set(0)
            on_select(None)
    
    def _apply_template(self, template_file):
        """应用模板"""
        template_data = self.template_manager.load_template(template_file)
        if not template_data:
            return
            
        try:
            watermark_config = template_data['watermark_config']
            export_config = template_data['export_config']
            
            # 应用水印配置
            self.watermark_type.set(watermark_config.get('type', 'text'))
            self.text_content.set(watermark_config.get('text_content', ''))
            self.font_family.set(watermark_config.get('font_family', 'Arial'))
            self.font_size.set(watermark_config.get('font_size', 24))
            self.font_color.set(watermark_config.get('color', '#000000'))
            self.opacity.set(watermark_config.get('opacity', 80))
            self.position_preset.set(watermark_config.get('position_preset', 'bottom_right'))
            self.offset_x.set(watermark_config.get('offset_x', 20))
            self.offset_y.set(watermark_config.get('offset_y', 20))
            self.rotation.set(watermark_config.get('rotation', 0))
            
            if watermark_config.get('type') == 'image':
                self.image_watermark_path.set(watermark_config.get('image_path', ''))
                self.image_scale.set(watermark_config.get('scale', 1.0))
            
            # 应用导出配置
            self.export_format.set(export_config.get('format', 'JPEG'))
            self.jpeg_quality.set(export_config.get('jpeg_quality', 85))
            self.naming_rule.set(export_config.get('naming_rule', 'keep_original'))
            self.prefix_text.set(export_config.get('prefix', 'wm_'))
            self.suffix_text.set(export_config.get('suffix', '_watermarked'))
            
            # 更新UI状态
            self.on_watermark_type_change()
            self.on_format_change()
            self.on_naming_change()
            self.update_color_button()
            self.refresh_preview()
            
            show_info(f"模板 '{template_data.get('name', '未知')}' 加载成功！")
            
        except Exception as e:
            show_error(f"应用模板失败: {e}")
        
    def start_export(self):
        """开始导出"""
        if not self.image_manager.images:
            show_error("请先导入图片")
            return
            
        if not self.output_dir.get():
            show_error("请选择输出目录")
            return
            
        # 在后台线程中执行导出
        threading.Thread(target=self._export_images, daemon=True).start()
        
    def _export_images(self):
        """导出图片（后台线程）"""
        try:
            print("开始导出图片...")
            watermark_config = self.get_watermark_config()
            export_config = self.get_export_config()
            
            # 验证输出目录
            output_dir = export_config.get('output_dir', '')
            if not output_dir:
                print("输出目录未设置")
                self.root.after(0, lambda: show_error("请选择输出目录"))
                return
                
            if not os.path.exists(output_dir):
                print(f"输出目录不存在: {output_dir}")
                self.root.after(0, lambda: show_error("输出目录不存在，请重新选择"))
                return
                
            if not os.access(output_dir, os.W_OK):
                print(f"输出目录没有写权限: {output_dir}")
                self.root.after(0, lambda: show_error("输出目录没有写权限，请选择其他目录"))
                return
            
            print(f"导出配置: {export_config}")
            print(f"水印配置: {watermark_config}")
            
            total = len(self.image_manager.images)
            success_count = 0
            error_count = 0
            
            print(f"总共需要处理 {total} 张图片")
            
            for i, img_item in enumerate(self.image_manager.images):
                try:
                    print(f"处理第 {i+1}/{total} 张图片: {img_item.file_path}")
                    
                    # 生成输出文件名
                    output_filename = generate_output_filename(
                        img_item.file_path,
                        export_config['naming_rule'],
                        export_config['prefix'],
                        export_config['suffix']
                    )
                    print(f"生成文件名: {output_filename}")
                    
                    # 确保文件名唯一
                    output_filename = ensure_unique_filename(
                        export_config['output_dir'], output_filename
                    )
                    print(f"确保文件名唯一后: {output_filename}")
                    
                    output_path = os.path.join(export_config['output_dir'], output_filename)
                    print(f"完整输出路径: {output_path}")
                    
                    # 处理图片
                    result = self.watermark_engine.process_image(
                        img_item.file_path, watermark_config, output_path, export_config
                    )
                    
                    if result:
                        print(f"图片导出成功: {output_path}")
                        success_count += 1
                    else:
                        print(f"图片导出失败: {img_item.file_path}")
                        error_count += 1
                        
                except Exception as e:
                    print(f"导出失败 {img_item.file_path}: {e}")
                    import traceback
                    traceback.print_exc()
                    error_count += 1
                
                # 更新进度
                progress = (i + 1) / total * 100
                print(f"进度: {progress:.1f}% ({i+1}/{total})")
                self.root.after(0, self._update_progress, progress, i + 1, total)
                
            # 导出完成
            print(f"导出完成: 成功 {success_count} 张，失败 {error_count} 张")
            self.root.after(0, self._export_complete, success_count, error_count)
            
        except Exception as e:
            print(f"导出过程出错: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: show_error(f"导出过程出错: {e}"))
            
    def _update_progress(self, progress, current, total):
        """更新进度（主线程）"""
        self.progress_var.set(progress)
        self.update_status(f"正在导出: {current}/{total}")
        
    def _export_complete(self, success, error):
        """导出完成（主线程）"""
        self.progress_var.set(0)
        self.update_status(f"导出完成: 成功 {success} 张，失败 {error} 张")
        show_info(f"导出完成！\n成功: {success} 张\n失败: {error} 张")
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.configure(text=message)
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
        
        # 保存拖拽开始时的偏移值
        self.drag_start_offset_x = self.offset_x.get()
        self.drag_start_offset_y = self.offset_y.get()
        
        # 检查是否点击在水印区域
        if self.watermark_position and self.is_point_in_watermark(event.x, event.y):
            self.update_status("点击水印区域，可以拖拽调整位置")
            self.preview_canvas.configure(cursor="hand2")
        else:
            self.update_status("点击图片其他区域")
            self.preview_canvas.configure(cursor="crosshair")
            
    def on_canvas_motion(self, event):
        """画布鼠标移动事件 - 改变光标样式以提高用户体验"""
        if self.watermark_position and self.is_point_in_watermark(event.x, event.y):
            # 鼠标在水印区域时显示手型光标
            if self.preview_canvas.cget("cursor") != "hand2":
                self.preview_canvas.configure(cursor="hand2")
        else:
            # 鼠标不在水印区域时显示十字光标
            if self.preview_canvas.cget("cursor") != "crosshair":
                self.preview_canvas.configure(cursor="crosshair")
        
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if not self.image_manager.get_current_image():
            return
        
        # 检查是否应该开始拖拽（基于初始点击位置）
        if (self.watermark_position and 
            self.is_point_in_watermark(self.drag_start_x, self.drag_start_y)):
            
            if not self.is_dragging:
                self.is_dragging = True
                self.preview_canvas.configure(cursor="hand2")
                self.update_status("正在拖拽水印...")
            
            # 计算相对于拖拽起始点的偏移（转换为实际图片坐标）
            dx = (event.x - self.drag_start_x) / self.canvas_scale
            dy = (event.y - self.drag_start_y) / self.canvas_scale
            
            # 基于拖拽起始时的偏移值计算新的偏移值
            new_x = self.drag_start_offset_x + int(dx)
            new_y = self.drag_start_offset_y + int(dy)
            
            # 扩大偏移范围，允许更大的拖拽区域
            new_x = max(-1000, min(1000, new_x))  # 从-200~200扩大到-1000~1000
            new_y = max(-1000, min(1000, new_y))  # 从-200~200扩大到-1000~1000
            
            # 更新UI变量
            self.offset_x.set(new_x)
            self.offset_y.set(new_y)
            
            # 取消之前的刷新定时器以避免累积延迟
            self._cancel_refresh_timer()
            
            # 立即刷新预览以提高响应性
            # 使用更短的时间间隔来减少延迟感
            self._refresh_timer = self.root.after(30, self._delayed_refresh)  # 从100ms减少到30ms
    
    def on_canvas_release(self, event):
        """画布释放事件"""
        if self.is_dragging:
            # 拖拽结束，保存位置到配置
            self._save_dragged_position()
            self.preview_canvas.configure(cursor="crosshair")
            self.update_status("水印位置已更新")
            
            # 立即刷新预览以显示最终位置
            self._cancel_refresh_timer()
            self.refresh_preview()
        self.is_dragging = False
    
    def on_canvas_enter(self, event):
        """鼠标进入画布"""
        self.preview_canvas.configure(cursor="crosshair")
    
    def on_canvas_leave(self, event):
        """鼠标离开画布"""
        self.preview_canvas.configure(cursor="")
    
    def on_tree_click(self, event):
        """图片列表点击事件"""
        # 让默认的树形控件处理选择
        pass
    
    # 文件拖拽功能已移除
    
    def is_point_in_watermark(self, x, y):
        """检查点是否在水印区域内"""
        if not self.watermark_position:
            return False
        
        wx, wy, ww, wh = self.watermark_position
        
        # 扩大检测区域，使拖拽更容易
        margin = 30  # 从10增加到30，使拖拽区域更大
        return (wx - margin <= x <= wx + ww + margin and 
                wy - margin <= y <= wy + wh + margin)
    

    
    def _save_dragged_position(self):
        """保存拖拽后的位置"""
        # 位置已经通过UI变量更新，这里可以添加额外的保存逻辑
        pass
    
    def _delayed_refresh(self):
        """延迟刷新预览"""
        self._refresh_timer = None
        self.refresh_preview()
        
    def _cancel_refresh_timer(self):
        """取消刷新定时器"""
        if hasattr(self, '_refresh_timer') and self._refresh_timer is not None:
            self.root.after_cancel(self._refresh_timer)
            self._refresh_timer = None
    
    def _calculate_watermark_position(self, image_size, watermark_size, watermark_config):
        """计算水印在图片中的位置和尺寸"""
        from utils import calculate_watermark_position
        
        # 计算水印位置
        pos_x, pos_y = calculate_watermark_position(
            image_size,
            watermark_size,
            watermark_config['position_preset'],
            watermark_config['offset_x'],
            watermark_config['offset_y'],
            watermark_config.get('padding', 10)
        )
        
        return (pos_x, pos_y, watermark_size[0], watermark_size[1])
            
    def on_closing(self):
        """窗口关闭事件"""
        # 保存当前配置
        current_config = {
            'watermark': self.get_watermark_config(),
            'export': self.get_export_config(),
            'ui': self.config.get('ui', {})
        }
        save_config(current_config)
        
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()