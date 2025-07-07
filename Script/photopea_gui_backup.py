#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Photopea GUI - 鍥惧舰鐣岄潰宸ュ叿

杩欎釜鑴氭湰鎻愪緵浜嗕竴涓浘褰㈢晫闈紝鐢ㄤ簬浣跨敤 PhotopeaAPI 鐨勫悇绉嶅姛鑳姐€?
浣跨敤鏂规硶:
    python photopea_gui.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
from threading import Thread

# 瀵煎叆 PhotopeaAPI 绫?sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from photopea_api import PhotopeaAPI

# 榛樿 Photopea URL
DEFAULT_URL = "http://localhost:8888"

# 鍒涘缓杈撳嚭鐩綍
output_dir = Path(os.path.expanduser("~/photopea_output"))
output_dir.mkdir(exist_ok=True)


class PhotopeaGUI(tk.Tk):
    """Photopea GUI 搴旂敤绋嬪簭"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Photopea API GUI")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # 璁剧疆鍥炬爣锛堝鏋滄湁锛?        # self.iconbitmap("icon.ico")
        
        # 鍒濆鍖?API 涓?None
        self.api = None
        
        # 鍒涘缓涓绘鏋?        self.create_widgets()
        
        # 缁戝畾鍏抽棴浜嬩欢
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """鍒涘缓鐣岄潰缁勪欢"""
        # 鍒涘缓涓绘鏋?        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 鍒涘缓宸︿晶鍜屽彸渚ф鏋?        left_frame = ttk.Frame(main_frame, padding=5, relief=tk.GROOVE, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        right_frame = ttk.Frame(main_frame, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 鍒涘缓杩炴帴妗嗘灦
        connection_frame = ttk.LabelFrame(left_frame, text="杩炴帴璁剧疆", padding=5)
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL 杈撳叆
        ttk.Label(connection_frame, text="Photopea URL:").pack(anchor=tk.W, padx=5, pady=2)
        self.url_var = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(connection_frame, textvariable=self.url_var).pack(fill=tk.X, padx=5, pady=2)
        
        # 杩炴帴鎸夐挳
        ttk.Button(connection_frame, text="杩炴帴", command=self.connect).pack(fill=tk.X, padx=5, pady=5)
        
        # 鍒涘缓鍔熻兘妗嗘灦
        functions_frame = ttk.LabelFrame(left_frame, text="鍔熻兘", padding=5)
        functions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 鍒涘缓鍔熻兘鍒楄〃
        self.functions = [
            ("鎵撳紑 PSD 鏂囦欢", self.open_psd),
            ("鏄剧ず/闅愯棌鍥惧眰", self.show_hide_layer),
            ("婵€娲诲浘灞?, self.activate_layer),
            ("淇敼鍥惧眰鏂囧瓧", self.change_text_layer),
            ("鏇挎崲鍥惧眰鍥剧墖", self.replace_image_layer),
            ("瀵煎嚭涓哄浘鐗?, self.export_image),
            ("鍏抽棴鏂囨。", self.close_document),
            ("鍙﹀瓨涓?PSD", self.save_as_psd),
            ("鑾峰彇鎵€鏈夊浘灞傚悕", self.get_all_layer_names),
            ("鑾峰彇鍥惧眰鏂囧瓧", self.get_layer_text),
            ("璁剧疆鏂囧瓧鍥惧眰瀛椾綋", self.set_text_layer_font),
            ("鑾峰彇鍥惧眰鎵€灞炵粍", self.get_layer_group),
            ("閲嶅懡鍚嶅浘灞?, self.rename_layer),
            ("鍐呭璇嗗埆濉厖", self.content_aware_fill),
            ("淇敼棰滆壊濉厖鍥惧眰", self.change_fill_layer_color),
            ("璁剧疆褰㈢姸鍥惧眰鎻忚竟", self.set_shape_layer_stroke),
            ("瀵煎嚭鍥惧眰涓?PNG", self.export_layer_as_png),
            ("娣诲姞鍥剧墖鍥惧眰", self.add_image_layer),
            ("鍒犻櫎鍥惧眰", self.delete_layer),
            ("鑾峰彇鍥惧眰瀛椾綋淇℃伅", self.get_text_layer_font_info),
            ("婵€娲绘枃妗?, self.activate_document),
            ("鏇挎崲鍥炬", self.replace_frame),
            ("鐢绘澘鍒囧浘", self.export_artboard),
            ("鏇挎崲鍥惧眰鍥剧墖(鑷姩缂╂斁)", self.replace_image_layer_auto_scale),
            ("璁剧疆鏂囧瓧鍥惧眰鏍煎紡", self.set_text_layer_format),
        ]
        
        # 鍒涘缓鍔熻兘鎸夐挳
        for name, command in self.functions:
            ttk.Button(functions_frame, text=name, command=command).pack(fill=tk.X, padx=5, pady=2)
        
        # 鍒涘缓鏃ュ織妗嗘灦
        log_frame = ttk.LabelFrame(right_frame, text="鏃ュ織", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 鍒涘缓鏃ュ織鏂囨湰妗?        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=50, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 娣诲姞婊氬姩鏉?        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 璁剧疆鍙
        self.log_text.config(state=tk.DISABLED)
        
        # 鍒涘缓鐘舵€佹爮
        self.status_var = tk.StringVar(value="鏈繛鎺?)
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log(self, message):
        """娣诲姞鏃ュ織娑堟伅"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def connect(self):
        """杩炴帴鍒?Photopea"""
        url = self.url_var.get()
        
        # 濡傛灉宸茬粡杩炴帴锛屽厛鍏抽棴
        if self.api is not None:
            try:
                self.api.close()
            except Exception as e:
                self.log(f"鍏抽棴杩炴帴鏃跺嚭閿? {e}")
        
        # 鍒涘缓鏂拌繛鎺?        try:
            self.log(f"姝ｅ湪杩炴帴鍒?{url}...")
            self.api = PhotopeaAPI(url)
            self.status_var.set(f"宸茶繛鎺ュ埌 {url}")
            self.log(f"宸叉垚鍔熻繛鎺ュ埌 {url}")
        except Exception as e:
            self.status_var.set("杩炴帴澶辫触")
            self.log(f"杩炴帴澶辫触: {e}")
            messagebox.showerror("杩炴帴閿欒", f"鏃犳硶杩炴帴鍒?Photopea: {e}")
    
    def check_connection(self):
        """妫€鏌ユ槸鍚﹀凡杩炴帴"""
        if self.api is None:
            messagebox.showwarning("鏈繛鎺?, "璇峰厛杩炴帴鍒?Photopea")
            return False
        return True
    
    def run_in_thread(self, func, *args, **kwargs):
        """鍦ㄧ嚎绋嬩腑杩愯鍑芥暟"""
        if not self.check_connection():
            return
        
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.log(f"閿欒: {e}")
                messagebox.showerror("鎿嶄綔閿欒", str(e))
        
        Thread(target=wrapper).start()
    
    def open_psd(self):
        """鎵撳紑 PSD 鏂囦欢"""
        if not self.check_connection():
            return
        
        file_path = filedialog.askopenfilename(
            title="閫夋嫨 PSD 鏂囦欢",
            filetypes=[("Photoshop 鏂囦欢", "*.psd"), ("鎵€鏈夋枃浠?, "*.*")]
        )
        
        if not file_path:
            return
        
        # 杞崲涓?file:/// URL
        file_url = f"file:///{file_path.replace(os.path.sep, '/')}"
        
        self.log(f"姝ｅ湪鎵撳紑 PSD 鏂囦欢: {file_path}")
        self.run_in_thread(self.api.open_psd, file_url)
        self.log(f"宸叉墦寮€ PSD 鏂囦欢: {file_path}")
    
    def show_hide_layer(self):
        """鏄剧ず/闅愯棌鍥惧眰"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鏄剧ず/闅愯棌鍥惧眰")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 鏄剧ず/闅愯棌閫夐」
        show_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(dialog, text="鏄剧ず", variable=show_var, value=True).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(dialog, text="闅愯棌", variable=show_var, value=False).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            show = show_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            action = "鏄剧ず" if show else "闅愯棌"
            self.log(f"姝ｅ湪{action}鍥惧眰: {layer_name}")
            self.run_in_thread(self.api.show_hide_layer, layer_name, show)
            self.log(f"宸瞷action}鍥惧眰: {layer_name}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def activate_layer(self):
        """婵€娲诲浘灞?""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("婵€娲诲浘灞?)
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪婵€娲诲浘灞? {layer_name}")
            self.run_in_thread(self.api.activate_layer, layer_name)
            self.log(f"宸叉縺娲诲浘灞? {layer_name}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def change_text_layer(self):
        """淇敼鍥惧眰鏂囧瓧"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("淇敼鍥惧眰鏂囧瓧")
        dialog.geometry("400x200")
        dialog.resizable(True, True)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鏂版枃鏈唴瀹?").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        
        # 鏂囨湰妗?        text_frame = ttk.Frame(dialog)
        text_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=30, height=5)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            new_text = text_widget.get("1.0", tk.END).strip()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪淇敼鍥惧眰 '{layer_name}' 鐨勬枃鏈唴瀹?)
            self.run_in_thread(self.api.change_text_layer, layer_name, new_text)
            self.log(f"宸蹭慨鏀瑰浘灞?'{layer_name}' 鐨勬枃鏈唴瀹?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆琛屽垪鏉冮噸
        dialog.columnconfigure(1, weight=1)
        dialog.rowconfigure(1, weight=1)
    
    def replace_image_layer(self):
        """鏇挎崲鍥惧眰鍥剧墖"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鏇挎崲鍥惧眰鍥剧墖")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鍥剧墖璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_entry = ttk.Entry(dialog, textvariable=image_path_var)
        path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 娴忚鎸夐挳
        def browse_image():
            file_path = filedialog.askopenfilename(
                title="閫夋嫨鍥剧墖鏂囦欢",
                filetypes=[("鍥剧墖鏂囦欢", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("鎵€鏈夋枃浠?, "*.*")]
            )
            
            if file_path:
                # 杞崲涓?file:/// URL
                file_url = f"file:///{file_path.replace(os.path.sep, '/')}"
                image_path_var.set(file_url)
        
        ttk.Button(dialog, text="娴忚...", command=browse_image).grid(row=1, column=2, padx=5, pady=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not image_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨鍥剧墖鏂囦欢")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鏇挎崲鍥惧眰 '{layer_name}' 鐨勫浘鐗?)
            self.run_in_thread(self.api.replace_image_layer, layer_name, image_path)
            self.log(f"宸叉浛鎹㈠浘灞?'{layer_name}' 鐨勫浘鐗?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def export_image(self):
        """瀵煎嚭涓哄浘鐗?""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("瀵煎嚭涓哄浘鐗?)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="淇濆瓨璺緞:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar(value=str(output_dir / "output.png"))
        path_entry = ttk.Entry(dialog, textvariable=save_path_var)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 娴忚鎸夐挳
        def browse_save_path():
            file_path = filedialog.asksaveasfilename(
                title="淇濆瓨鍥剧墖",
                defaultextension=".png",
                filetypes=[("PNG 鍥剧墖", "*.png"), ("JPEG 鍥剧墖", "*.jpg"), ("鎵€鏈夋枃浠?, "*.*")]
            )
            
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(dialog, text="娴忚...", command=browse_save_path).grid(row=0, column=2, padx=5, pady=5)
        
        # 璐ㄩ噺閫夐」
        ttk.Label(dialog, text="璐ㄩ噺 (1-100):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quality_var = tk.IntVar(value=100)
        ttk.Spinbox(dialog, from_=1, to=100, textvariable=quality_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            save_path = save_path_var.get()
            quality = quality_var.get()
            
            if not save_path:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ヤ繚瀛樿矾寰?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪瀵煎嚭鍥剧墖鍒? {save_path}")
            self.run_in_thread(self.api.export_image, save_path, quality)
            self.log(f"宸插鍑哄浘鐗囧埌: {save_path}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def close_document(self):
        """鍏抽棴鏂囨。"""
        if not self.check_connection():
            return
        
        if messagebox.askyesno("纭", "纭畾瑕佸叧闂綋鍓嶆枃妗ｅ悧锛?):
            self.log("姝ｅ湪鍏抽棴褰撳墠鏂囨。")
            self.run_in_thread(self.api.close_document)
            self.log("宸插叧闂綋鍓嶆枃妗?)
    
    def save_as_psd(self):
        """鍙﹀瓨涓?PSD"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鍙﹀瓨涓?PSD")
        dialog.geometry("400x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="淇濆瓨璺緞:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar(value=str(output_dir / "output.psd"))
        path_entry = ttk.Entry(dialog, textvariable=save_path_var)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 娴忚鎸夐挳
        def browse_save_path():
            file_path = filedialog.asksaveasfilename(
                title="淇濆瓨 PSD 鏂囦欢",
                defaultextension=".psd",
                filetypes=[("Photoshop 鏂囦欢", "*.psd"), ("鎵€鏈夋枃浠?, "*.*")]
            )
            
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(dialog, text="娴忚...", command=browse_save_path).grid(row=0, column=2, padx=5, pady=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            save_path = save_path_var.get()
            
            if not save_path:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ヤ繚瀛樿矾寰?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鍙﹀瓨涓?PSD 鏂囦欢: {save_path}")
            self.run_in_thread(self.api.save_as_psd, save_path)
            self.log(f"宸插彟瀛樹负 PSD 鏂囦欢: {save_path}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=3, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def get_all_layer_names(self):
        """鑾峰彇鎵€鏈夊浘灞傚悕"""
        if not self.check_connection():
            return
        
        self.log("姝ｅ湪鑾峰彇鎵€鏈夊浘灞傚悕...")
        
        def get_names():
            try:
                layer_names = self.api.get_all_layer_names()
                self.log("鍥惧眰鍒楄〃:")
                for i, name in enumerate(layer_names, 1):
                    self.log(f"{i}. {name}")
            except Exception as e:
                self.log(f"閿欒: {e}")
                messagebox.showerror("鎿嶄綔閿欒", str(e))
        
        Thread(target=get_names).start()
    
    def get_layer_text(self):
        """鑾峰彇鍥惧眰鏂囧瓧"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鑾峰彇鍥惧眰鏂囧瓧")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鑾峰彇鍥惧眰 '{layer_name}' 鐨勬枃鏈唴瀹?..")
            
            def get_text():
                try:
                    text = self.api.get_layer_text(layer_name)
                    self.log(f"鍥惧眰 '{layer_name}' 鐨勬枃鏈唴瀹? {text}")
                except Exception as e:
                    self.log(f"閿欒: {e}")
                    messagebox.showerror("鎿嶄綔閿欒", str(e))
            
            Thread(target=get_text).start()
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def set_text_layer_font(self):
        """璁剧疆鏂囧瓧鍥惧眰瀛椾綋"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("璁剧疆鏂囧瓧鍥惧眰瀛椾綋")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="瀛椾綋鍚嶇О:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=font_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            font_name = font_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not font_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ瓧浣撳悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪璁剧疆鍥惧眰 '{layer_name}' 鐨勫瓧浣撲负: {font_name}")
            self.run_in_thread(self.api.set_text_layer_font, layer_name, font_name)
            self.log(f"宸茶缃浘灞?'{layer_name}' 鐨勫瓧浣撲负: {font_name}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def get_layer_group(self):
        """鑾峰彇鍥惧眰鎵€灞炵粍"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鑾峰彇鍥惧眰鎵€灞炵粍")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鑾峰彇鍥惧眰 '{layer_name}' 鐨勬墍灞炵粍...")
            
            def get_group():
                try:
                    group = self.api.get_layer_group(layer_name)
                    self.log(f"鍥惧眰 '{layer_name}' 鐨勬墍灞炵粍: {group}")
                except Exception as e:
                    self.log(f"閿欒: {e}")
                    messagebox.showerror("鎿嶄綔閿欒", str(e))
            
            Thread(target=get_group).start()
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def rename_layer(self):
        """閲嶅懡鍚嶅浘灞?""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("閲嶅懡鍚嶅浘灞?)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鏂板悕绉?").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        new_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=new_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            new_name = new_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not new_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ユ柊鍚嶇О")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪灏嗗浘灞?'{layer_name}' 閲嶅懡鍚嶄负: {new_name}")
            self.run_in_thread(self.api.rename_layer, layer_name, new_name)
            self.log(f"宸插皢鍥惧眰 '{layer_name}' 閲嶅懡鍚嶄负: {new_name}")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def content_aware_fill(self):
        """鍐呭璇嗗埆濉厖"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鍐呭璇嗗埆濉厖")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="閫夊尯鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        selection_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=selection_layer_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鐩爣鍥惧眰鍚嶇О:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        target_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=target_layer_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            selection_layer = selection_layer_var.get()
            target_layer = target_layer_var.get()
            
            if not selection_layer:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ラ€夊尯鍥惧眰鍚嶇О")
                return
            
            if not target_layer:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ョ洰鏍囧浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪瀵瑰浘灞?'{target_layer}' 浣跨敤閫夊尯 '{selection_layer}' 杩涜鍐呭璇嗗埆濉厖...")
            self.run_in_thread(self.api.content_aware_fill, selection_layer, target_layer)
            self.log(f"宸插畬鎴愬唴瀹硅瘑鍒～鍏?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def modify_color_fill(self):
        """淇敼棰滆壊濉厖鍥惧眰"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("淇敼棰滆壊濉厖鍥惧眰")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="棰滆壊 (R,G,B):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 鍒涘缓RGB杈撳叆妗?        rgb_frame = ttk.Frame(dialog)
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
        
        # 棰滆壊閫夋嫨鎸夐挳
        def choose_color():
            color = colorchooser.askcolor(title="閫夋嫨棰滆壊")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="閫夋嫨棰滆壊", command=choose_color).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤诲湪0-255涔嬮棿")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤讳负鏁存暟")
                return
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪淇敼鍥惧眰 '{layer_name}' 鐨勯鑹蹭负: RGB({r},{g},{b})")
            self.run_in_thread(self.api.modify_color_fill, layer_name, r, g, b)
            self.log(f"宸蹭慨鏀瑰浘灞?'{layer_name}' 鐨勯鑹?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def set_shape_stroke(self):
        """璁剧疆褰㈢姸鍥惧眰鎻忚竟"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("璁剧疆褰㈢姸鍥惧眰鎻忚竟")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鎻忚竟瀹藉害 (px):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        width_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=width_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="棰滆壊 (R,G,B):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 鍒涘缓RGB杈撳叆妗?        rgb_frame = ttk.Frame(dialog)
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
        
        # 棰滆壊閫夋嫨鎸夐挳
        def choose_color():
            color = colorchooser.askcolor(title="閫夋嫨棰滆壊")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="閫夋嫨棰滆壊", command=choose_color).grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            try:
                width = float(width_var.get())
                if width <= 0:
                    messagebox.showwarning("杈撳叆閿欒", "鎻忚竟瀹藉害蹇呴』澶т簬0")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "鎻忚竟瀹藉害蹇呴』涓烘暟瀛?)
                return
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤诲湪0-255涔嬮棿")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤讳负鏁存暟")
                return
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪璁剧疆鍥惧眰 '{layer_name}' 鐨勬弿杈? 瀹藉害 {width}px, 棰滆壊 RGB({r},{g},{b})")
            self.run_in_thread(self.api.set_shape_stroke, layer_name, width, r, g, b)
            self.log(f"宸茶缃浘灞?'{layer_name}' 鐨勬弿杈?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def export_layer_as_png(self):
        """瀵煎嚭鍥惧眰涓篜NG"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("瀵煎嚭鍥惧眰涓篜NG")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="淇濆瓨璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=save_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 娴忚鎸夐挳
        def browse_file():
            file_path = filedialog.asksaveasfilename(
                title="淇濆瓨PNG鏂囦欢",
                filetypes=[("PNG鏂囦欢", "*.png")],
                defaultextension=".png"
            )
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(path_frame, text="娴忚", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            save_path = save_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not save_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨淇濆瓨璺緞")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪瀵煎嚭鍥惧眰 '{layer_name}' 涓篜NG: {save_path}")
            
            def export_png():
                try:
                    self.api.export_layer_as_png(layer_name, save_path)
                    self.log(f"宸插鍑哄浘灞?'{layer_name}' 涓篜NG: {save_path}")
                    messagebox.showinfo("瀵煎嚭鎴愬姛", f"宸插鍑哄浘灞?'{layer_name}' 涓篜NG\n淇濆瓨璺緞: {save_path}")
                except Exception as e:
                    self.log(f"瀵煎嚭閿欒: {e}")
                    messagebox.showerror("瀵煎嚭閿欒", str(e))
            
            Thread(target=export_png).start()
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def add_image_layer(self):
        """娣诲姞鍥剧墖鍥惧眰"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("娣诲姞鍥剧墖鍥惧眰")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鍥剧墖璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 娴忚鎸夐挳
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="閫夋嫨鍥剧墖鏂囦欢",
                filetypes=[
                    ("鍥剧墖鏂囦欢", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("鎵€鏈夋枃浠?, "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="娴忚", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not image_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨鍥剧墖璺緞")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("杈撳叆閿欒", "鎵€閫夊浘鐗囨枃浠朵笉瀛樺湪")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪娣诲姞鍥剧墖鍥惧眰 '{layer_name}': {image_path}")
            self.run_in_thread(self.api.add_image_layer, layer_name, image_path)
            self.log(f"宸叉坊鍔犲浘鐗囧浘灞?'{layer_name}'")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def delete_layer(self):
        """鍒犻櫎鍥惧眰"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鍒犻櫎鍥惧眰")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            # 纭鍒犻櫎
            if not messagebox.askyesno("纭鍒犻櫎", f"纭畾瑕佸垹闄ゅ浘灞?'{layer_name}' 鍚楋紵\n姝ゆ搷浣滀笉鍙挙閿€锛?):
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鍒犻櫎鍥惧眰 '{layer_name}'...")
            self.run_in_thread(self.api.delete_layer, layer_name)
            self.log(f"宸插垹闄ゅ浘灞?'{layer_name}'")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def get_layer_font_info(self):
        """鑾峰彇鍥惧眰瀛椾綋淇℃伅"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鑾峰彇鍥惧眰瀛椾綋淇℃伅")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鑾峰彇鍥惧眰 '{layer_name}' 鐨勫瓧浣撲俊鎭?..")
            
            def get_font_info():
                try:
                    font_info = self.api.get_layer_font_info(layer_name)
                    self.log(f"鍥惧眰 '{layer_name}' 鐨勫瓧浣撲俊鎭? {font_info}")
                    
                    # 鏄剧ず璇︾粏淇℃伅
                    info_dialog = tk.Toplevel(self)
                    info_dialog.title(f"鍥惧眰 '{layer_name}' 鐨勫瓧浣撲俊鎭?)
                    info_dialog.geometry("400x300")
                    info_dialog.transient(self)
                    info_dialog.grab_set()
                    
                    # 鍒涘缓鏂囨湰妗嗘樉绀轰俊鎭?                    text_frame = ttk.Frame(info_dialog)
                    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    text_widget = tk.Text(text_frame, wrap=tk.WORD)
                    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    
                    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    
                    # 鏍煎紡鍖栧瓧浣撲俊鎭?                    formatted_info = "瀛椾綋淇℃伅:\n"
                    for key, value in font_info.items():
                        formatted_info += f"- {key}: {value}\n"
                    
                    text_widget.insert(tk.END, formatted_info)
                    text_widget.config(state=tk.DISABLED)  # 璁句负鍙
                    
                    # 鍏抽棴鎸夐挳
                    ttk.Button(info_dialog, text="鍏抽棴", command=info_dialog.destroy).pack(pady=10)
                    
                except Exception as e:
                    self.log(f"閿欒: {e}")
                    messagebox.showerror("鎿嶄綔閿欒", str(e))
            
            Thread(target=get_font_info).start()
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def activate_document(self):
        """婵€娲绘枃妗?""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("婵€娲绘枃妗?)
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鏂囨。绱㈠紩 (浠?寮€濮?:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        doc_index_var = tk.StringVar(value="0")
        ttk.Entry(dialog, textvariable=doc_index_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 纭畾鎸夐挳
        def on_ok():
            try:
                doc_index = int(doc_index_var.get())
                if doc_index < 0:
                    messagebox.showwarning("杈撳叆閿欒", "鏂囨。绱㈠紩蹇呴』澶т簬绛変簬0")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "鏂囨。绱㈠紩蹇呴』涓烘暣鏁?)
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪婵€娲绘枃妗?(绱㈠紩: {doc_index})...")
            self.run_in_thread(self.api.activate_document, doc_index)
            self.log(f"宸叉縺娲绘枃妗?(绱㈠紩: {doc_index})")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def replace_frame(self):
        """鏇挎崲鍥炬"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鏇挎崲鍥炬")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥炬鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        frame_layer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=frame_layer_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鍥剧墖璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 娴忚鎸夐挳
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="閫夋嫨鍥剧墖鏂囦欢",
                filetypes=[
                    ("鍥剧墖鏂囦欢", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("鎵€鏈夋枃浠?, "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="娴忚", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            frame_layer = frame_layer_var.get()
            image_path = image_path_var.get()
            
            if not frame_layer:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘妗嗗浘灞傚悕绉?)
                return
            
            if not image_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨鍥剧墖璺緞")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("杈撳叆閿欒", "鎵€閫夊浘鐗囨枃浠朵笉瀛樺湪")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鏇挎崲鍥炬 '{frame_layer}' 鐨勫浘鐗? {image_path}")
            self.run_in_thread(self.api.replace_frame, frame_layer, image_path)
            self.log(f"宸叉浛鎹㈠浘妗?'{frame_layer}' 鐨勫浘鐗?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def artboard_export(self):
        """鐢绘澘鍒囧浘"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鐢绘澘鍒囧浘")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鐢绘澘鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        artboard_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=artboard_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="淇濆瓨璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        save_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=save_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 娴忚鎸夐挳
        def browse_file():
            file_path = filedialog.asksaveasfilename(
                title="淇濆瓨PNG鏂囦欢",
                filetypes=[("PNG鏂囦欢", "*.png")],
                defaultextension=".png"
            )
            if file_path:
                save_path_var.set(file_path)
        
        ttk.Button(path_frame, text="娴忚", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            artboard_name = artboard_name_var.get()
            save_path = save_path_var.get()
            
            if not artboard_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ョ敾鏉垮悕绉?)
                return
            
            if not save_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨淇濆瓨璺緞")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪瀵煎嚭鐢绘澘 '{artboard_name}' 涓篜NG: {save_path}")
            
            def export_artboard():
                try:
                    self.api.artboard_export(artboard_name, save_path)
                    self.log(f"宸插鍑虹敾鏉?'{artboard_name}' 涓篜NG: {save_path}")
                    messagebox.showinfo("瀵煎嚭鎴愬姛", f"宸插鍑虹敾鏉?'{artboard_name}' 涓篜NG\n淇濆瓨璺緞: {save_path}")
                except Exception as e:
                    self.log(f"瀵煎嚭閿欒: {e}")
                    messagebox.showerror("瀵煎嚭閿欒", str(e))
            
            Thread(target=export_artboard).start()
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def replace_image_layer_auto_scale(self):
        """鏇挎崲鍥惧眰鍥剧墖(鑷姩缂╂斁)"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("鏇挎崲鍥惧眰鍥剧墖(鑷姩缂╂斁)")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="鍥剧墖璺緞:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(path_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 娴忚鎸夐挳
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="閫夋嫨鍥剧墖鏂囦欢",
                filetypes=[
                    ("鍥剧墖鏂囦欢", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                    ("鎵€鏈夋枃浠?, "*.*")
                ]
            )
            if file_path:
                image_path_var.set(file_path)
        
        ttk.Button(path_frame, text="娴忚", command=browse_file).pack(side=tk.RIGHT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            image_path = image_path_var.get()
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not image_path:
                messagebox.showwarning("杈撳叆閿欒", "璇烽€夋嫨鍥剧墖璺緞")
                return
            
            if not os.path.exists(image_path):
                messagebox.showwarning("杈撳叆閿欒", "鎵€閫夊浘鐗囨枃浠朵笉瀛樺湪")
                return
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪鏇挎崲鍥惧眰 '{layer_name}' 鐨勫浘鐗?鑷姩缂╂斁): {image_path}")
            self.run_in_thread(self.api.replace_image_layer_auto_scale, layer_name, image_path)
            self.log(f"宸叉浛鎹㈠浘灞?'{layer_name}' 鐨勫浘鐗?鑷姩缂╂斁)")
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
    
    def set_text_layer_format(self):
        """璁剧疆鏂囧瓧鍥惧眰鏍煎紡"""
        if not self.check_connection():
            return
        
        # 鍒涘缓瀵硅瘽妗?        dialog = tk.Toplevel(self)
        dialog.title("璁剧疆鏂囧瓧鍥惧眰鏍煎紡")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 鍒涘缓琛ㄥ崟
        ttk.Label(dialog, text="鍥惧眰鍚嶇О:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        layer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=layer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="瀛椾綋鍚嶇О:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=font_name_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="瀛椾綋澶у皬:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        font_size_var = tk.StringVar(value="12")
        ttk.Entry(dialog, textvariable=font_size_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="棰滆壊 (R,G,B):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 鍒涘缓RGB杈撳叆妗?        rgb_frame = ttk.Frame(dialog)
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
        
        # 棰滆壊閫夋嫨鎸夐挳
        def choose_color():
            color = colorchooser.askcolor(title="閫夋嫨棰滆壊")
            if color[0]:
                r, g, b = [int(c) for c in color[0]]
                r_var.set(str(r))
                g_var.set(str(g))
                b_var.set(str(b))
        
        ttk.Button(dialog, text="閫夋嫨棰滆壊", command=choose_color).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # 瀵归綈鏂瑰紡
        ttk.Label(dialog, text="瀵归綈鏂瑰紡:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        align_var = tk.StringVar(value="left")
        align_frame = ttk.Frame(dialog)
        align_frame.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Radiobutton(align_frame, text="宸﹀榻?, variable=align_var, value="left").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="灞呬腑", variable=align_var, value="center").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="鍙冲榻?, variable=align_var, value="right").pack(side=tk.LEFT, padx=5)
        
        # 纭畾鎸夐挳
        def on_ok():
            layer_name = layer_name_var.get()
            font_name = font_name_var.get()
            
            try:
                font_size = float(font_size_var.get())
                if font_size <= 0:
                    messagebox.showwarning("杈撳叆閿欒", "瀛椾綋澶у皬蹇呴』澶т簬0")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "瀛椾綋澶у皬蹇呴』涓烘暟瀛?)
                return
            
            try:
                r = int(r_var.get())
                g = int(g_var.get())
                b = int(b_var.get())
                
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤诲湪0-255涔嬮棿")
                    return
            except ValueError:
                messagebox.showwarning("杈撳叆閿欒", "RGB鍊煎繀椤讳负鏁存暟")
                return
            
            if not layer_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ浘灞傚悕绉?)
                return
            
            if not font_name:
                messagebox.showwarning("杈撳叆閿欒", "璇疯緭鍏ュ瓧浣撳悕绉?)
                return
            
            align = align_var.get()
            
            dialog.destroy()
            
            self.log(f"姝ｅ湪璁剧疆鍥惧眰 '{layer_name}' 鐨勬枃瀛楁牸寮?..")
            self.run_in_thread(self.api.set_text_layer_format, layer_name, font_name, font_size, r, g, b, align)
            self.log(f"宸茶缃浘灞?'{layer_name}' 鐨勬枃瀛楁牸寮?)
        
        ttk.Button(dialog, text="纭畾", command=on_ok).grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # 璁剧疆鍒楁潈閲?        dialog.columnconfigure(1, weight=1)
