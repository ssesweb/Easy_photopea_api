#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Photopea GUI - 图形界面工具

这个脚本提供了一个图形界面，用于使用 PhotopeaAPI 的各种功能。

使用方法:
    python photopea_gui.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
from threading import Thread

# 导入 PhotopeaAPI 类
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from photopea_api import PhotopeaAPI

# 默认 Photopea URL
DEFAULT_URL = "http://localhost:8888"

# 创建输出目录
output_dir = Path(os.path.expanduser("~/photopea_output"))
output_dir.mkdir(exist_ok=True)


class PhotopeaGUI(tk.Tk):
    """Photopea GUI 应用程序"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Photopea API GUI")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # 设置图标（如果有）
        # self.iconbitmap("icon.ico")
        
        # 初始化 API 为 None
        self.api = None
        
        # 创建主框架
        self.create_widgets()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧和右侧框架
        left_frame = ttk.Frame(main_frame, padding=5, relief=tk.GROOVE, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        right_frame = ttk.Frame(main_frame, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建连接框架
        connection_frame = ttk.LabelFrame(left_frame, text="连接设置", padding=5)
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL 输入
        ttk.Label(connection_frame, text="Photopea URL:").pack(anchor=tk.W, padx=5, pady=2)
        self.url_var = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(connection_frame, textvariable=self.url_var).pack(fill=tk.X, padx=5, pady=2)
        
        # 连接按钮
        ttk.Button(connection_frame, text="连接", command=self.connect).pack(fill=tk.X, padx=5, pady=5)
        
        # 创建功能框架
        functions_frame = ttk.LabelFrame(left_frame, text="功能", padding=5)
        functions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建功能列表
        self.functions = [
            ("打开 PSD 文件", self.open_psd),
            ("显示/隐藏图层", self.show_hide_layer),
            ("激活图层", self.activate_layer),
            ("修改图层文字", self.change_text_layer),
            ("替换图层图片", self.replace_image_layer),
            ("导出为图片", self.export_image),
            ("关闭文档", self.close_document),
            ("另存为 PSD", self.save_as_psd),
            ("获取所有图层名", self.get_all_layer_names),
            ("获取图层文字", self.get_layer_text),
            ("设置文字图层字体", self.set_text_layer_font),
            ("获取图层所属组", self.get_layer_group),
            ("重命名图层", self.rename_layer),
            ("内容识别填充", self.content_aware_fill),
            ("修改颜色填充图层", self.change_fill_layer_color),
            ("设置形状图层描边", self.set_shape_layer_stroke),
            ("导出图层为 PNG", self.export_layer_as_png),
            ("添加图片图层", self.add_image_layer),
            ("删除图层", self.delete_layer),
            ("获取图层字体信息", self.get_text_layer_font_info),
            ("激活文档", self.activate_document),
            ("替换图框", self.replace_frame),
            ("画板切图", self.export_artboard),
            ("替换图层图片(自动缩放)", self.replace_image_layer_auto_scale),
            ("设置文字图层格式", self.set_text_layer_format),
        ]
        
        # 创建功能按钮
        for name, command in self.functions:
            ttk.Button(functions_frame, text=name, command=command).pack(fill=tk.X, padx=5, pady=2)
        
        # 创建日志框架
        log_frame = ttk.LabelFrame(right_frame, text="日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建日志文本框
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=50, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 设置只读
        self.log_text.config(state=tk.DISABLED)
        
        # 创建状态栏
        self.status_var = tk.StringVar(value="未连接")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log(self, message):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def connect(self):
        """连接到 Photopea"""
        url = self.url_var.get()
        
        # 如果已经连接，先关闭
        if self.api is not None:
            try:
                self.api.close()
            except Exception as e:
                self.log(f"关闭连接时出错: {e}")
        
        # 创建新连接
        try:
            self.log(f"正在连接到 {url}...")
            self.api = PhotopeaAPI(url)
            self.status_var.set(f"已连接到 {url}")
            self.log(f"已成功连接到 {url}")
        except Exception as e:
            self.status_var.set("连接失败")
            self.log(f"连接失败: {e}")
            messagebox.showerror("连接错误", f"无法连接到 Photopea: {e}")
    
    def check_connection(self):
        """检查是否已连接"""
        if self.api is None:
            messagebox.showwarning("未连接", "请先连接到 Photopea")
            return False
        return True
    
    def run_in_thread(self, func, *args, **kwargs):
        """在线程中运行函数"""
        if not self.check_connection():
            return
        
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.log(f"错误: {e}")
                messagebox.showerror("操作错误", str(e))
        
        Thread(target=wrapper).start()
    
    def open_psd(self):
        """打开 PSD 文件"""
        if not self.check_connection():
            return
        
        file_path = filedialog.askopenfilename(
            title="选择 PSD 文件",
            filetypes=[("Photoshop 文件", "*.psd"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        # 转换为 file:/// URL
        file_url = f"file:///{file_path.replace(os.path.sep, '/')}"
        
        self.log(f"正在打开 PSD 文件: {file_path}")
        self.run_in_thread(self.api.open_psd, file_url)
        self.log(f"已打开 PSD 文件: {file_path}")
    
    def show_hide_layer(self):
        """显示/隐藏图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("显示/隐藏图层")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 显示/隐藏选项
        show_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(dialog, text="显示", variable=show_var, value=True).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(dialog, text="隐藏", variable=show_var, value=False).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            show = show_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            action = "显示" if show else "隐藏"
            self.log(f"正在{action}图层: {layer_name}")
            self.run_in_thread(self.api.show_hide_layer, layer_name, show)
            self.log(f"已{action}图层: {layer_name}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def activate_layer(self):
        """激活图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("激活图层")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在激活图层: {layer_name}")
            self.run_in_thread(self.api.activate_layer, layer_name)
            self.log(f"已激活图层: {layer_name}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def change_text_layer(self):
        """修改图层文字"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("修改图层文字")
        dialog.geometry("400x200")
        dialog.resizable(True, True)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="新文本内容:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        
        # 文本框
        text_frame = ttk.Frame(dialog)
        text_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=30, height=5)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            new_text = text_widget.get("1.0", tk.END).strip()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在修改图层 '{layer_name}' 的文本内容")
            self.run_in_thread(self.api.change_text_layer, layer_name, new_text)
            self.log(f"已修改图层 '{layer_name}' 的文本内容")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置行列权重
        dialog.columnconfigure(1, weight=1)
        dialog.rowconfigure(1, weight=1)
    
    def replace_image_layer(self):
        """替换图层图片"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("替换图层图片")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="图片路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_entry = ttk.Entry(dialog, textvariable=image_path_var)
        path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 浏览按钮
        def browse_image():
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("所有文件", "*.*")]
            )
            
            if file_path:
                # 转换为 file:/// URL
                file_url = f"file:///{file_path.replace(os.path.sep, '/')}"
                image_path_var.set(file_url)
        
        ttk.Button(dialog, text="浏览...", command=browse_image).grid(row=1, column=2, padx=5, pady=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not image_path:
                messagebox.showwarning("输入错误", "请选择图片文件")
                return
            
            dialog.destroy()
            
            self.log(f"正在替换图层 '{layer_name}' 的图片")
            self.run_in_thread(self.api.replace_image_layer, layer_name, image_path)
            self.log(f"已替换图层 '{layer_name}' 的图片")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def export_image(self):
        """导出为图片"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("导出为图片")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="保存路径:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar(value=str(output_dir / "output.png"))
        path_entry = ttk.Entry(dialog, textvariable=save_path_var)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 浏览按钮
        def browse_save_path():
            file_path = filedialog.asksaveasfilename(
                title="保存图片",
                defaultextension=".png",
                filetypes=[("PNG 图片", "*.png"), ("JPEG 图片", "*.jpg"), ("所有文件", "*.*")]
            )
            
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(dialog, text="浏览...", command=browse_save_path).grid(row=0, column=2, padx=5, pady=5)
        
        # 质量选项
        ttk.Label(dialog, text="质量 (1-100):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quality_var = tk.IntVar(value=100)
        ttk.Spinbox(dialog, from_=1, to=100, textvariable=quality_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            save_path = save_path_var.get()
            quality = quality_var.get()
            
            if not save_path:
                messagebox.showwarning("输入错误", "请输入保存路径")
                return
            
            dialog.destroy()
            
            self.log(f"正在导出图片到: {save_path}")
            self.run_in_thread(self.api.export_image, save_path, quality)
            self.log(f"已导出图片到: {save_path}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def close_document(self):
        """关闭文档"""
        if not self.check_connection():
            return
        
        if messagebox.askyesno("确认", "确定要关闭当前文档吗？"):
            self.log("正在关闭当前文档")
            self.run_in_thread(self.api.close_document)
            self.log("已关闭当前文档")
    
    def save_as_psd(self):
        """另存为 PSD"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("另存为 PSD")
        dialog.geometry("400x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="保存路径:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar(value=str(output_dir / "output.psd"))
        path_entry = ttk.Entry(dialog, textvariable=save_path_var)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 浏览按钮
        def browse_save_path():
            file_path = filedialog.asksaveasfilename(
                title="保存 PSD 文件",
                defaultextension=".psd",
                filetypes=[("Photoshop 文件", "*.psd"), ("所有文件", "*.*")]
            )
            
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(dialog, text="浏览...", command=browse_save_path).grid(row=0, column=2, padx=5, pady=5)
        
        # 确定按钮
        def on_ok():
            save_path = save_path_var.get()
            
            if not save_path:
                messagebox.showwarning("输入错误", "请输入保存路径")
                return
            
            dialog.destroy()
            
            self.log(f"正在另存为 PSD 文件: {save_path}")
            self.run_in_thread(self.api.save_as_psd, save_path)
            self.log(f"已另存为 PSD 文件: {save_path}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=3, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def get_all_layer_names(self):
        """获取所有图层名"""
        if not self.check_connection():
            return
        
        self.log("正在获取所有图层名...")
        
        def get_names():
            try:
                layer_names = self.api.get_all_layer_names()
                self.log("图层列表:")
                for i, name in enumerate(layer_names, 1):
                    self.log(f"{i}. {name}")
            except Exception as e:
                self.log(f"错误: {e}")
                messagebox.showerror("操作错误", str(e))
        
        Thread(target=get_names).start()
    
    def get_layer_text(self):
        """获取图层文字"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("获取图层文字")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在获取图层 '{layer_name}' 的文本内容...")
            
            def get_text():
                try:
                    text = self.api.get_layer_text(layer_name)
                    self.log(f"图层 '{layer_name}' 的文本内容: {text}")
                except Exception as e:
                    self.log(f"错误: {e}")
                    messagebox.showerror("操作错误", str(e))
            
            Thread(target=get_text).start()
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def set_text_layer_font(self):
        """设置文字图层字体"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("设置文字图层字体")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="字体名称:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=font_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            font_name = font_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not font_name:
                messagebox.showwarning("输入错误", "请输入字体名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在设置图层 '{layer_name}' 的字体为: {font_name}")
            self.run_in_thread(self.api.set_text_layer_font, layer_name, font_name)
            self.log(f"已设置图层 '{layer_name}' 的字体为: {font_name}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def get_layer_group(self):
        """获取图层所属组"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("获取图层所属组")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在获取图层 '{layer_name}' 的所属组...")
            
            def get_group():
                try:
                    group = self.api.get_layer_group(layer_name)
                    self.log(f"图层 '{layer_name}' 的所属组: {group}")
                except Exception as e:
                    self.log(f"错误: {e}")
                    messagebox.showerror("操作错误", str(e))
            
            Thread(target=get_group).start()
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def rename_layer(self):
        """重命名图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("重命名图层")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="新名称:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        new_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=new_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            new_name = new_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not new_name:
                messagebox.showwarning("输入错误", "请输入新名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在将图层 '{layer_name}' 重命名为: {new_name}")
            self.run_in_thread(self.api.rename_layer, layer_name, new_name)
            self.log(f"已将图层 '{layer_name}' 重命名为: {new_name}")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def content_aware_fill(self):
        """内容识别填充"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("内容识别填充")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="选区图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        selection_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=selection_layer_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="目标图层名称:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        target_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=target_layer_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            selection_layer = selection_layer_var.get()
            target_layer = target_layer_var.get()
            
            if not selection_layer:
                messagebox.showwarning("输入错误", "请输入选区图层名称")
                return
            
            if not target_layer:
                messagebox.showwarning("输入错误", "请输入目标图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在对图层 '{target_layer}' 使用选区 '{selection_layer}' 进行内容识别填充...")
            self.run_in_thread(self.api.content_aware_fill, selection_layer, target_layer)
            self.log(f"已完成内容识别填充")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def modify_color_fill(self):
        """修改颜色填充图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("修改颜色填充图层")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="颜色 (R,G,B):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 创建RGB输入框
        rgb_frame = ttk.Frame(dialog)
        rgb_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        r_var = tk.StringVar(value="0")
        g_var = tk.StringVar(value="0")
        b_var = tk.StringVar(value="0")
        
        ttk.Label(rgb_frame, text="R:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=r_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="G:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=g_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="B:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=b_var, width=4).pack(side=tk.LEFT, padx=2)
        
        # 颜色选择按钮
        def choose_color():
            color = colorchooser.askcolor(title="选择颜色")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="选择颜色", command=choose_color).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("输入错误", "RGB值必须在0-255之间")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "RGB值必须为整数")
                return
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在修改图层 '{layer_name}' 的颜色为: RGB({r},{g},{b})")
            self.run_in_thread(self.api.modify_color_fill, layer_name, r, g, b)
            self.log(f"已修改图层 '{layer_name}' 的颜色")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def set_shape_stroke(self):
        """设置形状图层描边"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("设置形状图层描边")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="描边宽度 (px):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        width_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=width_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="颜色 (R,G,B):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 创建RGB输入框
        rgb_frame = ttk.Frame(dialog)
        rgb_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        r_var = tk.StringVar(value="0")
        g_var = tk.StringVar(value="0")
        b_var = tk.StringVar(value="0")
        
        ttk.Label(rgb_frame, text="R:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=r_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="G:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=g_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="B:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=b_var, width=4).pack(side=tk.LEFT, padx=2)
        
        # 颜色选择按钮
        def choose_color():
            color = colorchooser.askcolor(title="选择颜色")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="选择颜色", command=choose_color).grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            try:
                width = float(width_var.get())
                if width <= 0:
                    messagebox.showwarning("输入错误", "描边宽度必须大于0")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "描边宽度必须为数字")
                return
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("输入错误", "RGB值必须在0-255之间")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "RGB值必须为整数")
                return
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在设置图层 '{layer_name}' 的描边: 宽度 {width}px, 颜色 RGB({r},{g},{b})")
            self.run_in_thread(self.api.set_shape_stroke, layer_name, width, r, g, b)
            self.log(f"已设置图层 '{layer_name}' 的描边")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def export_layer_as_png(self):
        """导出图层为PNG"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("导出图层为PNG")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="保存路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=save_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.asksaveasfilename(
                title="保存PNG文件",
                filetypes=[("PNG文件", "*.png")],
                defaultextension=".png"
            )
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            save_path = save_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not save_path:
                messagebox.showwarning("输入错误", "请选择保存路径")
                return
            
            dialog.destroy()
            
            self.log(f"正在导出图层 '{layer_name}' 为PNG: {save_path}")
            
            def export_png():
                try:
                    self.api.export_layer_as_png(layer_name, save_path)
                    self.log(f"已导出图层 '{layer_name}' 为PNG: {save_path}")
                    messagebox.showinfo("导出成功", f"已导出图层 '{layer_name}' 为PNG\n保存路径: {save_path}")
                except Exception as e:
                    self.log(f"导出错误: {e}")
                    messagebox.showerror("导出错误", str(e))
            
            Thread(target=export_png).start()
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def add_image_layer(self):
        """添加图片图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("添加图片图层")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="图片路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not image_path:
                messagebox.showwarning("输入错误", "请选择图片路径")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("输入错误", "所选图片文件不存在")
                return
            
            dialog.destroy()
            
            self.log(f"正在添加图片图层 '{layer_name}': {image_path}")
            self.run_in_thread(self.api.add_image_layer, layer_name, image_path)
            self.log(f"已添加图片图层 '{layer_name}'")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def delete_layer(self):
        """删除图层"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("删除图层")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除图层 '{layer_name}' 吗？\n此操作不可撤销！"):
                return
            
            dialog.destroy()
            
            self.log(f"正在删除图层 '{layer_name}'...")
            self.run_in_thread(self.api.delete_layer, layer_name)
            self.log(f"已删除图层 '{layer_name}'")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def get_layer_font_info(self):
        """获取图层字体信息"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("获取图层字体信息")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            dialog.destroy()
            
            self.log(f"正在获取图层 '{layer_name}' 的字体信息...")
            
            def get_font_info():
                try:
                    font_info = self.api.get_layer_font_info(layer_name)
                    self.log(f"图层 '{layer_name}' 的字体信息: {font_info}")
                    
                    # 显示详细信息
                    info_dialog = tk.Toplevel(self)
                    info_dialog.title(f"图层 '{layer_name}' 的字体信息")
                    info_dialog.geometry("400x300")
                    info_dialog.transient(self)
                    info_dialog.grab_set()
                    
                    # 创建文本框显示信息
                    text_frame = ttk.Frame(info_dialog)
                    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    text_widget = tk.Text(text_frame, wrap=tk.WORD)
                    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    
                    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    
                    # 格式化字体信息
                    formatted_info = "字体信息:\n"
                    for key, value in font_info.items():
                        formatted_info += f"- {key}: {value}\n"
                    
                    text_widget.insert(tk.END, formatted_info)
                    text_widget.config(state=tk.DISABLED)  # 设为只读
                    
                    # 关闭按钮
                    ttk.Button(info_dialog, text="关闭", command=info_dialog.destroy).pack(pady=10)
                    
                except Exception as e:
                    self.log(f"错误: {e}")
                    messagebox.showerror("操作错误", str(e))
            
            Thread(target=get_font_info).start()
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def activate_document(self):
        """激活文档"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("激活文档")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="文档索引 (从0开始):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        doc_index_var = tk.StringVar(value="0")
        ttk.Entry(dialog, textvariable=doc_index_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 确定按钮
        def on_ok():
            try:
                doc_index = int(doc_index_var.get())
                if doc_index < 0:
                    messagebox.showwarning("输入错误", "文档索引必须大于等于0")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "文档索引必须为整数")
                return
            
            dialog.destroy()
            
            self.log(f"正在激活文档 (索引: {doc_index})...")
            self.run_in_thread(self.api.activate_document, doc_index)
            self.log(f"已激活文档 (索引: {doc_index})")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def replace_frame(self):
        """替换图框"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("替换图框")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图框图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        frame_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=frame_layer_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="图片路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        def on_ok():
            frame_layer = frame_layer_var.get()
            image_path = image_path_var.get()
            
            if not frame_layer:
                messagebox.showwarning("输入错误", "请输入图框图层名称")
                return
            
            if not image_path:
                messagebox.showwarning("输入错误", "请选择图片路径")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("输入错误", "所选图片文件不存在")
                return
            
            dialog.destroy()
            
            self.log(f"正在替换图框 '{frame_layer}' 的图片: {image_path}")
            self.run_in_thread(self.api.replace_frame, frame_layer, image_path)
            self.log(f"已替换图框 '{frame_layer}' 的图片")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def artboard_export(self):
        """画板切图"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("画板切图")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="画板名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        artboard_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=artboard_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="保存路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=save_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.asksaveasfilename(
                title="保存PNG文件",
                filetypes=[("PNG文件", "*.png")],
                defaultextension=".png"
            )
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        def on_ok():
            artboard_name = artboard_name_var.get()
            save_path = save_path_var.get()
            
            if not artboard_name:
                messagebox.showwarning("输入错误", "请输入画板名称")
                return
            
            if not save_path:
                messagebox.showwarning("输入错误", "请选择保存路径")
                return
            
            dialog.destroy()
            
            self.log(f"正在导出画板 '{artboard_name}' 为PNG: {save_path}")
            
            def export_artboard():
                try:
                    self.api.artboard_export(artboard_name, save_path)
                    self.log(f"已导出画板 '{artboard_name}' 为PNG: {save_path}")
                    messagebox.showinfo("导出成功", f"已导出画板 '{artboard_name}' 为PNG\n保存路径: {save_path}")
                except Exception as e:
                    self.log(f"导出错误: {e}")
                    messagebox.showerror("导出错误", str(e))
            
            Thread(target=export_artboard).start()
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def replace_image_layer_auto_scale(self):
        """替换图层图片(自动缩放)"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("替换图层图片(自动缩放)")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="图片路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not image_path:
                messagebox.showwarning("输入错误", "请选择图片路径")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("输入错误", "所选图片文件不存在")
                return
            
            dialog.destroy()
            
            self.log(f"正在替换图层 '{layer_name}' 的图片(自动缩放): {image_path}")
            self.run_in_thread(self.api.replace_image_layer_auto_scale, layer_name, image_path)
            self.log(f"已替换图层 '{layer_name}' 的图片(自动缩放)")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
    
    def set_text_layer_format(self):
        """设置文字图层格式"""
        if not self.check_connection():
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("设置文字图层格式")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        ttk.Label(dialog, text="图层名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="字体名称:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=font_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="字体大小:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        font_size_var = tk.StringVar(value="12")
        ttk.Entry(dialog, textvariable=font_size_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="颜色 (R,G,B):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 创建RGB输入框
        rgb_frame = ttk.Frame(dialog)
        rgb_frame.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        r_var = tk.StringVar(value="0")
        g_var = tk.StringVar(value="0")
        b_var = tk.StringVar(value="0")
        
        ttk.Label(rgb_frame, text="R:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=r_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="G:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=g_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(rgb_frame, text="B:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(rgb_frame, textvariable=b_var, width=4).pack(side=tk.LEFT, padx=2)
        
        # 颜色选择按钮
        def choose_color():
            color = colorchooser.askcolor(title="选择颜色")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="选择颜色", command=choose_color).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # 对齐方式
        ttk.Label(dialog, text="对齐方式:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        align_var = tk.StringVar(value="left")
        align_frame = ttk.Frame(dialog)
        align_frame.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Radiobutton(align_frame, text="左对齐", variable=align_var, value="left").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="居中", variable=align_var, value="center").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="右对齐", variable=align_var, value="right").pack(side=tk.LEFT, padx=5)
        
        # 确定按钮
        def on_ok():
            layer_name = layer_name_var.get()
            font_name = font_name_var.get()
            
            try:
                font_size = float(font_size_var.get())
                if font_size <= 0:
                    messagebox.showwarning("输入错误", "字体大小必须大于0")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "字体大小必须为数字")
                return
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("输入错误", "RGB值必须在0-255之间")
                    return
            except ValueError:
                messagebox.showwarning("输入错误", "RGB值必须为整数")
                return
            
            if not layer_name:
                messagebox.showwarning("输入错误", "请输入图层名称")
                return
            
            if not font_name:
                messagebox.showwarning("输入错误", "请输入字体名称")
                return
            
            align = align_var.get()
            
            dialog.destroy()
            
            self.log(f"正在设置图层 '{layer_name}' 的文字格式...")
            self.run_in_thread(self.api.set_text_layer_format, layer_name, font_name, font_size, r, g, b, align)
            self.log(f"已设置图层 '{layer_name}' 的文字格式")
        
        ttk.Button(dialog, text="确定", command=on_ok).grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)