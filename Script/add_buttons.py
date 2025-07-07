import os

# 定义要添加的按钮
new_buttons = """
        # 定义按钮
        buttons = [
            ("打开PSD", self.open_psd),
            ("显示/隐藏图层", self.show_hide_layer),
            ("激活图层", self.activate_layer),
            ("修改图层文字", self.change_text_layer),
            ("替换图层图片", self.replace_image_layer),
            ("导出为图片", self.export_image),
            ("关闭文档", self.close_document),
            ("另存为PSD", self.save_as_psd),
            ("获取所有图层名", self.get_all_layer_names),
            ("获取图层文字", self.get_layer_text),
            ("设置文字图层字体", self.set_text_layer_font),
            ("获取图层所属组", self.get_layer_group),
            ("重命名图层", self.rename_layer),
            ("内容识别填充", self.content_aware_fill),
            ("修改颜色填充图层", self.modify_color_fill),
            ("设置形状图层描边", self.set_shape_stroke),
            ("导出图层为PNG", self.export_layer_as_png),
            ("添加图片图层", self.add_image_layer),
            ("删除图层", self.delete_layer),
            ("获取图层字体信息", self.get_layer_font_info),
            ("激活文档", self.activate_document),
            ("替换图框", self.replace_frame),
            ("画板切图", self.artboard_export),
            ("替换图层图片(自动缩放)", self.replace_image_layer_auto_scale),
            ("设置文字图层格式", self.set_text_layer_format),
        ]
"""

# 打印按钮定义，可以复制粘贴到GUI文件中
print(new_buttons)