# Photopea API Python 封装

这个项目提供了一个 Python 封装的 Photopea API，使您能够通过 Python 代码轻松控制 Photopea 进行各种图像编辑操作。

## 功能特点

该 API 封装了 Photopea 的主要功能，包括：

1. 打开 PSD 文件
2. 显示/隐藏图层
3. 激活图层
4. 修改图层文字
5. 替换图层图片
6. 导出为图片
7. 关闭 PSD 文件
8. 另存为 PSD 文件
9. 获取所有图层名
10. 获取图层文字
11. 设置文字图层字体
12. 获取图层所属组
13. 重命名图层
14. 内容识别填充
15. 修改颜色填充图层
16. 设置形状图层描边
17. 导出图层为 PNG
18. 添加图片图层
19. 删除图层
20. 获取图层字体信息
21. 激活文档
22. 替换图框
23. 画板切图
24. 替换图层图片(自动缩放)
25. 设置文字图层格式

## 安装依赖

```bash
pip install selenium webdriver-manager
```

## 使用方法

### 基本用法

```python
from photopea_api import PhotopeaAPI

# 初始化 API (传入 Photopea 实例的 URL)
api = PhotopeaAPI("http://localhost:8888")

# 打开 PSD 文件
api.open_psd("file:///path/to/your/file.psd")

# 修改文本图层
api.change_text_layer("文本图层名称", "新文本内容")

# 替换图片图层
api.replace_image_layer("图片图层名称", "file:///path/to/new/image.png")

# 导出为图片
api.export_image("output.png")

# 关闭浏览器
api.close()
```

### 示例脚本

查看 `examples.py` 文件获取完整的使用示例。

## API 参考

### 初始化

```python
api = PhotopeaAPI(url="http://localhost:8888")
```

- `url`: Photopea 实例的 URL

### 文件操作

```python
# 打开 PSD 文件
api.open_psd(file_path)

# 关闭当前文档
api.close_document()

# 另存为 PSD
api.save_as_psd(save_path)

# 导出为图片
api.export_image(save_path, quality=100)

# 激活文档 (当有多个文档打开时)
api.activate_document(index)
```

### 图层操作

```python
# 显示/隐藏图层
api.show_hide_layer(layer_name, show=True)

# 激活图层
api.activate_layer(layer_name)

# 修改文本图层
api.change_text_layer(layer_name, new_text)

# 替换图片图层
api.replace_image_layer(layer_name, image_path)

# 替换图片图层 (自动缩放)
api.replace_image_layer_auto_scale(layer_name, image_path)

# 获取所有图层名
names = api.get_all_layer_names()

# 获取图层文字
text = api.get_layer_text(layer_name)

# 设置文字图层字体
api.set_text_layer_font(layer_name, font_name)

# 获取图层所属组
group = api.get_layer_group(layer_name)

# 重命名图层
api.rename_layer(layer_name, new_name)

# 内容识别填充
api.content_aware_fill(layer_name)

# 修改颜色填充图层
api.change_fill_layer_color(layer_name, r, g, b)

# 设置形状图层描边
api.set_shape_layer_stroke(layer_name, width, r, g, b)

# 导出图层为 PNG
api.export_layer_as_png(layer_name, save_path)

# 添加图片图层
api.add_image_layer(image_path)

# 删除图层
api.delete_layer(layer_name)

# 获取图层字体信息
font_info = api.get_text_layer_font_info(layer_name)

# 替换图框
api.replace_frame(layer_name, image_path)

# 画板切图
api.export_artboard(artboard_name, save_path)

# 设置文字图层格式
api.set_text_layer_format(layer_name, format_options)
```

## 注意事项

1. 确保您有一个运行中的 Photopea 实例，并且 URL 正确。
2. 图层名称必须与 Photopea 中的图层名称完全匹配。
3. 文件路径可以是本地路径（使用 `file:///` 前缀）或远程 URL。
4. 某些操作可能需要先激活相应的图层。

## 许可证

此项目基于 MIT 许可证。