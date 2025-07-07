#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Photopea CLI - 命令行工具

这个脚本提供了一个命令行界面，用于使用 PhotopeaAPI 的各种功能。

使用方法:
    python photopea_cli.py [命令] [参数...]

示例:
    python photopea_cli.py open file:///path/to/file.psd
    python photopea_cli.py change-text "图层名称" "新文本内容"
    python photopea_cli.py export output.png
"""

import os
import sys
import argparse
from pathlib import Path
from photopea_api import PhotopeaAPI

# 默认 Photopea URL
DEFAULT_URL = "http://localhost:8888"

# 创建输出目录
output_dir = Path(os.path.expanduser("~/photopea_output"))
output_dir.mkdir(exist_ok=True)


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description="Photopea 命令行工具")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"Photopea 实例的 URL (默认: {DEFAULT_URL})")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 打开 PSD 文件
    open_parser = subparsers.add_parser("open", help="打开 PSD 文件")
    open_parser.add_argument("file_path", help="PSD 文件路径 (使用 file:/// 前缀)")
    
    # 显示/隐藏图层
    show_hide_parser = subparsers.add_parser("show-hide", help="显示或隐藏图层")
    show_hide_parser.add_argument("layer_name", help="图层名称")
    show_hide_parser.add_argument("--hide", action="store_true", help="隐藏图层 (默认为显示)")
    
    # 激活图层
    activate_parser = subparsers.add_parser("activate", help="激活图层")
    activate_parser.add_argument("layer_name", help="图层名称")
    
    # 修改文本图层
    change_text_parser = subparsers.add_parser("change-text", help="修改文本图层")
    change_text_parser.add_argument("layer_name", help="文本图层名称")
    change_text_parser.add_argument("new_text", help="新文本内容")
    
    # 替换图片图层
    replace_image_parser = subparsers.add_parser("replace-image", help="替换图片图层")
    replace_image_parser.add_argument("layer_name", help="图片图层名称")
    replace_image_parser.add_argument("image_path", help="新图片路径 (使用 file:/// 前缀)")
    replace_image_parser.add_argument("--auto-scale", action="store_true", help="自动缩放图片")
    
    # 导出为图片
    export_parser = subparsers.add_parser("export", help="导出为图片")
    export_parser.add_argument("save_path", help="保存路径")
    export_parser.add_argument("--quality", type=int, default=100, help="导出质量 (1-100)")
    
    # 关闭文档
    subparsers.add_parser("close", help="关闭当前文档")
    
    # 另存为 PSD
    save_as_parser = subparsers.add_parser("save-as", help="另存为 PSD 文件")
    save_as_parser.add_argument("save_path", help="保存路径")
    
    # 获取所有图层名
    subparsers.add_parser("list-layers", help="获取所有图层名")
    
    # 获取图层文字
    get_text_parser = subparsers.add_parser("get-text", help="获取图层文字")
    get_text_parser.add_argument("layer_name", help="文本图层名称")
    
    # 设置文字图层字体
    set_font_parser = subparsers.add_parser("set-font", help="设置文字图层字体")
    set_font_parser.add_argument("layer_name", help="文本图层名称")
    set_font_parser.add_argument("font_name", help="字体名称")
    
    # 获取图层所属组
    get_group_parser = subparsers.add_parser("get-group", help="获取图层所属组")
    get_group_parser.add_argument("layer_name", help="图层名称")
    
    # 重命名图层
    rename_parser = subparsers.add_parser("rename", help="重命名图层")
    rename_parser.add_argument("layer_name", help="图层名称")
    rename_parser.add_argument("new_name", help="新名称")
    
    # 内容识别填充
    content_aware_parser = subparsers.add_parser("content-aware-fill", help="内容识别填充")
    content_aware_parser.add_argument("layer_name", help="图层名称")
    
    # 修改颜色填充图层
    change_color_parser = subparsers.add_parser("change-color", help="修改颜色填充图层")
    change_color_parser.add_argument("layer_name", help="颜色填充图层名称")
    change_color_parser.add_argument("r", type=int, help="红色 (0-255)")
    change_color_parser.add_argument("g", type=int, help="绿色 (0-255)")
    change_color_parser.add_argument("b", type=int, help="蓝色 (0-255)")
    
    # 设置形状图层描边
    set_stroke_parser = subparsers.add_parser("set-stroke", help="设置形状图层描边")
    set_stroke_parser.add_argument("layer_name", help="形状图层名称")
    set_stroke_parser.add_argument("width", type=int, help="描边宽度")
    set_stroke_parser.add_argument("r", type=int, help="红色 (0-255)")
    set_stroke_parser.add_argument("g", type=int, help="绿色 (0-255)")
    set_stroke_parser.add_argument("b", type=int, help="蓝色 (0-255)")
    
    # 导出图层为 PNG
    export_layer_parser = subparsers.add_parser("export-layer", help="导出图层为 PNG")
    export_layer_parser.add_argument("layer_name", help="图层名称")
    export_layer_parser.add_argument("save_path", help="保存路径")
    
    # 添加图片图层
    add_image_parser = subparsers.add_parser("add-image", help="添加图片图层")
    add_image_parser.add_argument("image_path", help="图片路径 (使用 file:/// 前缀)")
    
    # 删除图层
    delete_parser = subparsers.add_parser("delete-layer", help="删除图层")
    delete_parser.add_argument("layer_name", help="图层名称")
    
    # 获取图层字体信息
    get_font_info_parser = subparsers.add_parser("get-font-info", help="获取图层字体信息")
    get_font_info_parser.add_argument("layer_name", help="文本图层名称")
    
    # 激活文档
    activate_doc_parser = subparsers.add_parser("activate-doc", help="激活文档")
    activate_doc_parser.add_argument("index", type=int, help="文档索引")
    
    # 替换图框
    replace_frame_parser = subparsers.add_parser("replace-frame", help="替换图框")
    replace_frame_parser.add_argument("layer_name", help="图框图层名称")
    replace_frame_parser.add_argument("image_path", help="图片路径 (使用 file:/// 前缀)")
    
    # 画板切图
    export_artboard_parser = subparsers.add_parser("export-artboard", help="画板切图")
    export_artboard_parser.add_argument("artboard_name", help="画板名称")
    export_artboard_parser.add_argument("save_path", help="保存路径")
    
    # 设置文字图层格式
    set_text_format_parser = subparsers.add_parser("set-text-format", help="设置文字图层格式")
    set_text_format_parser.add_argument("layer_name", help="文本图层名称")
    set_text_format_parser.add_argument("--size", type=int, help="字体大小")
    set_text_format_parser.add_argument("--color", nargs=3, type=int, metavar=("R", "G", "B"), help="字体颜色 (RGB)")
    set_text_format_parser.add_argument("--bold", action="store_true", help="粗体")
    set_text_format_parser.add_argument("--italic", action="store_true", help="斜体")
    set_text_format_parser.add_argument("--justification", choices=["left", "center", "right"], help="对齐方式")
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化 API
    api = PhotopeaAPI(args.url)
    
    try:
        # 执行命令
        if args.command == "open":
            api.open_psd(args.file_path)
            print(f"已打开 PSD 文件: {args.file_path}")
            
        elif args.command == "show-hide":
            api.show_hide_layer(args.layer_name, not args.hide)
            status = "隐藏" if args.hide else "显示"
            print(f"已{status}图层: {args.layer_name}")
            
        elif args.command == "activate":
            api.activate_layer(args.layer_name)
            print(f"已激活图层: {args.layer_name}")
            
        elif args.command == "change-text":
            api.change_text_layer(args.layer_name, args.new_text)
            print(f"已修改文本图层 '{args.layer_name}' 的内容为: {args.new_text}")
            
        elif args.command == "replace-image":
            if args.auto_scale:
                api.replace_image_layer_auto_scale(args.layer_name, args.image_path)
            else:
                api.replace_image_layer(args.layer_name, args.image_path)
            print(f"已替换图片图层 '{args.layer_name}' 的图片为: {args.image_path}")
            
        elif args.command == "export":
            api.export_image(args.save_path, args.quality)
            print(f"已导出图片到: {args.save_path}")
            
        elif args.command == "close":
            api.close_document()
            print("已关闭当前文档")
            
        elif args.command == "save-as":
            api.save_as_psd(args.save_path)
            print(f"已另存为 PSD 文件: {args.save_path}")
            
        elif args.command == "list-layers":
            layer_names = api.get_all_layer_names()
            print("图层列表:")
            for i, name in enumerate(layer_names, 1):
                print(f"{i}. {name}")
            
        elif args.command == "get-text":
            text = api.get_layer_text(args.layer_name)
            print(f"图层 '{args.layer_name}' 的文本内容: {text}")
            
        elif args.command == "set-font":
            api.set_text_layer_font(args.layer_name, args.font_name)
            print(f"已设置图层 '{args.layer_name}' 的字体为: {args.font_name}")
            
        elif args.command == "get-group":
            group = api.get_layer_group(args.layer_name)
            print(f"图层 '{args.layer_name}' 所属组: {group}")
            
        elif args.command == "rename":
            api.rename_layer(args.layer_name, args.new_name)
            print(f"已将图层 '{args.layer_name}' 重命名为: {args.new_name}")
            
        elif args.command == "content-aware-fill":
            api.content_aware_fill(args.layer_name)
            print(f"已对图层 '{args.layer_name}' 进行内容识别填充")
            
        elif args.command == "change-color":
            api.change_fill_layer_color(args.layer_name, args.r, args.g, args.b)
            print(f"已修改颜色填充图层 '{args.layer_name}' 的颜色为: RGB({args.r}, {args.g}, {args.b})")
            
        elif args.command == "set-stroke":
            api.set_shape_layer_stroke(args.layer_name, args.width, args.r, args.g, args.b)
            print(f"已设置形状图层 '{args.layer_name}' 的描边为: {args.width}px RGB({args.r}, {args.g}, {args.b})")
            
        elif args.command == "export-layer":
            api.export_layer_as_png(args.layer_name, args.save_path)
            print(f"已导出图层 '{args.layer_name}' 为 PNG: {args.save_path}")
            
        elif args.command == "add-image":
            api.add_image_layer(args.image_path)
            print(f"已添加图片图层: {args.image_path}")
            
        elif args.command == "delete-layer":
            api.delete_layer(args.layer_name)
            print(f"已删除图层: {args.layer_name}")
            
        elif args.command == "get-font-info":
            font_info = api.get_text_layer_font_info(args.layer_name)
            print(f"图层 '{args.layer_name}' 的字体信息:")
            for key, value in font_info.items():
                print(f"  {key}: {value}")
            
        elif args.command == "activate-doc":
            api.activate_document(args.index)
            print(f"已激活文档索引: {args.index}")
            
        elif args.command == "replace-frame":
            api.replace_frame(args.layer_name, args.image_path)
            print(f"已替换图框 '{args.layer_name}' 的图片为: {args.image_path}")
            
        elif args.command == "export-artboard":
            api.export_artboard(args.artboard_name, args.save_path)
            print(f"已导出画板 '{args.artboard_name}' 为: {args.save_path}")
            
        elif args.command == "set-text-format":
            format_options = {}
            if args.size is not None:
                format_options["size"] = args.size
            if args.color is not None:
                format_options["color"] = tuple(args.color)
            if args.bold:
                format_options["bold"] = True
            if args.italic:
                format_options["italic"] = True
            if args.justification:
                format_options["justification"] = args.justification
                
            api.set_text_layer_format(args.layer_name, format_options)
            print(f"已设置文字图层 '{args.layer_name}' 的格式")
            
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭浏览器
        api.close()


if __name__ == "__main__":
    main()