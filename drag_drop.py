"""
文件拖拽支持模块
"""

import tkinter as tk
from tkinter import ttk
import os
from typing import List, Callable, Optional


class DragDropHandler:
    """拖拽处理器"""
    
    def __init__(self, target_widget, callback: Callable[[List[str]], None]):
        self.target_widget = target_widget
        self.callback = callback
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """设置拖拽支持"""
        # 绑定拖拽进入事件
        self.target_widget.bind("<Enter>", self.on_drag_enter)
        self.target_widget.bind("<Leave>", self.on_drag_leave)
        
        # 尝试使用系统拖拽支持
        try:
            # Windows 拖拽支持
            if hasattr(self.target_widget, 'tk') and self.target_widget.tk.call('tk', 'windowingsystem') == 'win32':
                self.setup_windows_drag_drop()
        except:
            # 如果系统拖拽不可用，使用模拟拖拽
            self.setup_simulated_drag_drop()
    
    def setup_windows_drag_drop(self):
        """设置Windows拖拽支持"""
        try:
            # 注册拖拽目标
            self.target_widget.tk.call('tkdnd', 'drop_target', 'register', self.target_widget, 'DND_Files')
            self.target_widget.tk.call('tkdnd', 'bind', self.target_widget, '<<Drop>>', self.on_drop)
        except:
            # tkdnd 不可用，使用备用方案
            self.setup_simulated_drag_drop()
    
    def setup_simulated_drag_drop(self):
        """设置模拟拖拽支持"""
        # 绑定鼠标事件来模拟拖拽
        self.target_widget.bind("<Button-1>", self.on_click)
        self.target_widget.bind("<B1-Motion>", self.on_drag)
        self.target_widget.bind("<ButtonRelease-1>", self.on_release)
        
        # 显示拖拽提示
        self.show_drag_hint()
    
    def show_drag_hint(self):
        """显示拖拽提示"""
        # 在画布上显示拖拽提示
        if hasattr(self.target_widget, 'create_text'):
            self.target_widget.create_text(
                self.target_widget.winfo_width() // 2,
                self.target_widget.winfo_height() // 2,
                text="拖拽图片文件到此区域\n或使用工具栏导入",
                fill="gray",
                font=("Arial", 12),
                tags="drag_hint"
            )
    
    def hide_drag_hint(self):
        """隐藏拖拽提示"""
        if hasattr(self.target_widget, 'delete'):
            self.target_widget.delete("drag_hint")
    
    def on_drag_enter(self, event):
        """拖拽进入事件"""
        self.target_widget.configure(relief="raised", borderwidth=2)
    
    def on_drag_leave(self, event):
        """拖拽离开事件"""
        self.target_widget.configure(relief="flat", borderwidth=0)
    
    def on_drop(self, event):
        """拖拽释放事件"""
        try:
            files = event.data.split()
            file_paths = []
            
            for file_path in files:
                file_path = file_path.strip('{}')
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            if file_paths:
                self.callback(file_paths)
                
        except Exception as e:
            print(f"拖拽处理失败: {e}")
    
    def on_click(self, event):
        """鼠标点击事件"""
        # 记录点击位置
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag(self, event):
        """鼠标拖拽事件"""
        # 模拟拖拽效果
        pass
    
    def on_release(self, event):
        """鼠标释放事件"""
        # 模拟拖拽结束
        pass


class SimpleFileDialog:
    """简单的文件选择对话框"""
    
    @staticmethod
    def ask_files(parent=None, title="选择图片文件"):
        """选择多个文件"""
        from tkinter import filedialog
        
        file_paths = filedialog.askopenfilenames(
            parent=parent,
            title=title,
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )
        return file_paths if file_paths else []
    
    @staticmethod
    def ask_directory(parent=None, title="选择图片文件夹"):
        """选择文件夹"""
        from tkinter import filedialog
        
        dir_path = filedialog.askdirectory(parent=parent, title=title)
        return dir_path if dir_path else ""


def setup_drag_drop_for_window(window, callback: Callable[[List[str]], None]):
    """为窗口设置拖拽支持"""
    # 为整个窗口设置拖拽支持
    drag_handler = DragDropHandler(window, callback)
    
    # 添加右键菜单支持
    def show_context_menu(event):
        context_menu = tk.Menu(window, tearoff=0)
        context_menu.add_command(label="导入图片文件", command=lambda: callback(SimpleFileDialog.ask_files(window)))
        context_menu.add_command(label="导入图片文件夹", command=lambda: _import_folder())
        context_menu.tk_popup(event.x_root, event.y_root)
    
    def _import_folder():
        folder_path = SimpleFileDialog.ask_directory(window)
        if folder_path:
            callback([folder_path])
    
    # 绑定右键菜单
    window.bind("<Button-3>", show_context_menu)
    
    return drag_handler


def setup_drag_drop_for_canvas(canvas, callback: Callable[[List[str]], None]):
    """为画布设置拖拽支持"""
    drag_handler = DragDropHandler(canvas, callback)
    
    # 当有内容时隐藏拖拽提示
    def on_content_change():
        if canvas.find_all():
            drag_handler.hide_drag_hint()
        else:
            drag_handler.show_drag_hint()
    
    # 绑定画布内容变化事件
    canvas.bind("<Configure>", lambda e: on_content_change())
    
    return drag_handler
