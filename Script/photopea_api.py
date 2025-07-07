# photopea_api.py
# 封装与本地 Photopea 实例交互的完整 API

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import base64
import json

class PhotopeaAPI:
    def __init__(self, photopea_url="http://192.168.110.13:8887"):
        """
        初始化 Photopea API 控制器
        
        Args:
            photopea_url: Photopea 本地服务器地址
        """
        self.photopea_url = photopea_url
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        # 可选：无头模式
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(photopea_url)
        time.sleep(2)

        # 自动点击"Start using Photopea"
        try:
            self.driver.find_element(By.CSS_SELECTOR, "a[href='#']").click()
            print("✅ 已自动点击 Start using Photopea")
        except Exception as e:
            print("⚠️ 未能点击启动按钮（可能已跳过）:", e)

        time.sleep(6)  # 等待主编辑器加载
        
        # 存储当前活动文档的信息
        self.active_document = None
        
    def send_script(self, script):
        """
        向 Photopea 发送 JavaScript 脚本
        
        Args:
            script: 要执行的 JavaScript 脚本
        """
        # 使用 JSON 字符串避免反引号与嵌套错误
        wrapped_script = f"window.postMessage({repr(script)}, '*');"
        self.driver.execute_script(wrapped_script)
        time.sleep(1)
        
    def execute_with_result(self, script):
        """
        执行脚本并获取返回结果
        
        Args:
            script: 要执行的 JavaScript 脚本，应当包含 app.echoToOE() 调用
            
        Returns:
            str: 脚本执行的结果
        """
        # 设置一个监听器来捕获 postMessage 事件
        setup_listener = """
        window.ppResult = null;
        window.addEventListener('message', function(e) {
            if (e.data !== 'done') {
                window.ppResult = e.data;
            }
        });
        """
        self.driver.execute_script(setup_listener)
        
        # 执行脚本
        self.send_script(script)
        
        # 获取结果
        time.sleep(1)  # 给予足够时间处理消息
        result = self.driver.execute_script("return window.ppResult;")
        return result
    
    # 1. 打开 PSD 文件
    def open_psd(self, url):
        """
        打开 PSD 文件
        
        Args:
            url: PSD 文件的 URL 或本地文件路径（需要以 file:/// 开头）
        """
        self.send_script(f"app.open('{url}', '', false);")
        time.sleep(3)  # 等待文件加载
    
    # 2. 显示/隐藏图层
    def show_hide_layer(self, layer_name, visible=True):
        """
        显示或隐藏指定名称的图层
        
        Args:
            layer_name: 图层名称
            visible: True 为显示，False 为隐藏
        """
        visibility = "true" if visible else "false"
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) layer.visible = {visibility};
        """
        self.send_script(script)
    
    # 3. 激活图层
    def activate_layer(self, layer_name):
        """
        激活指定名称的图层
        
        Args:
            layer_name: 图层名称
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) app.activeDocument.activeLayer = layer;
        """
        self.send_script(script)
    
    # 4. 修改图层文字
    def change_text_layer(self, layer_name, new_text):
        """
        修改文本图层的内容
        
        Args:
            layer_name: 文本图层名称
            new_text: 新的文本内容
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'textLayer') {{
            layer.textItem.contents = '{new_text}';
        }}
        """
        self.send_script(script)
    
    # 5. 替换图层图片
    def replace_image_layer(self, layer_name, image_url):
        """
        替换智能对象图层的图片
        
        Args:
            layer_name: 智能对象图层名称
            image_url: 新图片的 URL 或本地文件路径（需要以 file:/// 开头）
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'smartObject') {{
            app.activeDocument.activeLayer = layer;
            executeAction(stringIDToTypeID('placedLayerEditContents'));
            app.open('{image_url}', '', false);
            var imageLayer = app.activeDocument.layers[0];
            imageLayer.translate(-imageLayer.bounds[0] - imageLayer.bounds[2]/2 + app.activeDocument.width/2,
                                  -imageLayer.bounds[1] - imageLayer.bounds[3]/2 + app.activeDocument.height/2);
            app.activeDocument.flatten();
            app.activeDocument.save();
            app.activeDocument.close();
        }}
        """
        self.send_script(script)
    
    # 6. 导出为图片
    def export_image(self, output_path, format="png", quality=0.8):
        """
        将当前文档导出为图片
        
        Args:
            output_path: 输出文件路径
            format: 输出格式，支持 'png', 'jpg', 'webp' 等
            quality: 当格式为 jpg 时的质量参数 (0-1)
        
        Returns:
            bool: 是否成功导出
        """
        format_param = format
        if format.lower() == "jpg" or format.lower() == "jpeg":
            format_param = f"jpg:{quality}"
            
        # 设置监听器捕获二进制数据
        setup_listener = """
        window.imageData = null;
        window.addEventListener('message', function(e) {
            if (e.data instanceof ArrayBuffer) {
                window.imageData = e.data;
            }
        });
        """
        self.driver.execute_script(setup_listener)
        
        # 发送导出命令
        self.send_script(f"app.activeDocument.saveToOE('{format_param}');")
        
        # 等待数据返回
        time.sleep(2)
        
        # 获取二进制数据
        binary_data = self.driver.execute_script("return window.imageData;")
        if not binary_data:
            print("❌ 未能获取导出数据")
            return False
            
        # 将 ArrayBuffer 转换为 Python 字节并保存
        try:
            # 获取 ArrayBuffer 的 Uint8Array 视图
            bytes_data = self.driver.execute_script("""
            var buffer = window.imageData;
            var bytes = new Uint8Array(buffer);
            var binary = '';
            for (var i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
            """)
            
            # 解码 Base64 并写入文件
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(bytes_data))
            print(f"✅ 已导出图片到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 导出图片失败: {e}")
            return False
    
    # 7. 关闭 PSD 文件
    def close_document(self, save=False):
        """
        关闭当前活动的文档
        
        Args:
            save: 是否在关闭前保存
        """
        if save:
            self.send_script("app.activeDocument.save();")
        self.send_script("app.activeDocument.close();")
    
    # 8. 另存为 PSD 文件
    def save_as_psd(self, file_path):
        """
        将当前文档另存为 PSD 文件
        
        Args:
            file_path: 保存路径，需要是绝对路径
            
        Returns:
            bool: 是否成功保存
        """
        # 设置监听器捕获二进制数据
        setup_listener = """
        window.psdData = null;
        window.addEventListener('message', function(e) {
            if (e.data instanceof ArrayBuffer) {
                window.psdData = e.data;
            }
        });
        """
        self.driver.execute_script(setup_listener)
        
        # 发送保存命令
        self.send_script("app.activeDocument.saveToOE('psd:true');")
        
        # 等待数据返回
        time.sleep(3)
        
        # 获取二进制数据并保存
        try:
            bytes_data = self.driver.execute_script("""
            var buffer = window.psdData;
            var bytes = new Uint8Array(buffer);
            var binary = '';
            for (var i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
            """)
            
            # 解码 Base64 并写入文件
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(bytes_data))
            print(f"✅ 已保存 PSD 到: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 保存 PSD 失败: {e}")
            return False
    
    # 9. 获取所有图层名
    def get_all_layer_names(self):
        """
        获取当前文档中所有图层的名称
        
        Returns:
            list: 图层名称列表
        """
        script = """
        function getAllLayers(layers, result = []) {
            for (var i = 0; i < layers.length; i++) {
                var layer = layers[i];
                result.push(layer.name);
                if (layer.layers) {
                    getAllLayers(layer.layers, result);
                }
            }
            return result;
        }
        var layerNames = getAllLayers(app.activeDocument.layers);
        app.echoToOE(JSON.stringify(layerNames));
        """
        result = self.execute_with_result(script)
        if result:
            try:
                return json.loads(result)
            except:
                print("❌ 解析图层名称失败")
        return []
    
    # 10. 获取图层文字
    def get_layer_text(self, layer_name):
        """
        获取文本图层的内容
        
        Args:
            layer_name: 文本图层名称
            
        Returns:
            str: 文本内容，如果不是文本图层则返回 None
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'textLayer') {{
            app.echoToOE(layer.textItem.contents);
        }} else {{
            app.echoToOE('NOT_TEXT_LAYER');
        }}
        """
        result = self.execute_with_result(script)
        if result and result != "NOT_TEXT_LAYER":
            return result
        return None
    
    # 11. 设置文字图层字体
    def set_text_layer_font(self, layer_name, font_name):
        """
        设置文本图层的字体
        
        Args:
            layer_name: 文本图层名称
            font_name: 字体名称
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'textLayer') {{
            layer.textItem.font = '{font_name}';
        }}
        """
        self.send_script(script)
    
    # 12. 获取图层所属组
    def get_layer_group(self, layer_name):
        """
        获取图层所属的组名称
        
        Args:
            layer_name: 图层名称
            
        Returns:
            str: 组名称，如果不在组内则返回 None
        """
        script = f"""
        function findLayerGroup(layers, targetName, path = []) {{
            for (var i = 0; i < layers.length; i++) {{
                var layer = layers[i];
                if (layer.name === targetName) {{
                    return path.length > 0 ? path[path.length - 1] : null;
                }}
                if (layer.layers) {{
                    path.push(layer.name);
                    var result = findLayerGroup(layer.layers, targetName, path);
                    if (result !== null) {{
                        return result;
                    }}
                    path.pop();
                }}
            }}
            return null;
        }}
        var groupName = findLayerGroup(app.activeDocument.layers, '{layer_name}');
        app.echoToOE(groupName ? groupName : 'NO_GROUP');
        """
        result = self.execute_with_result(script)
        if result and result != "NO_GROUP":
            return result
        return None
    
    # 13. 重命名图层
    def rename_layer(self, old_name, new_name):
        """
        重命名图层
        
        Args:
            old_name: 原图层名称
            new_name: 新图层名称
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{old_name}');
        if(layer) layer.name = '{new_name}';
        """
        self.send_script(script)
    
    # 14. 内容识别填充
    def content_aware_fill(self, layer_name):
        """
        对指定图层应用内容识别填充
        
        Args:
            layer_name: 图层名称
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) {{
            app.activeDocument.activeLayer = layer;
            app.activeDocument.contentAwareFill();
        }}
        """
        self.send_script(script)
    
    # 15. 修改颜色填充图层
    def change_fill_layer_color(self, layer_name, r, g, b):
        """
        修改填充图层的颜色
        
        Args:
            layer_name: 填充图层名称
            r, g, b: RGB 颜色值 (0-255)
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'solidColorLayer') {{
            var color = new SolidColor();
            color.rgb.red = {r};
            color.rgb.green = {g};
            color.rgb.blue = {b};
            layer.fillColor = color;
        }}
        """
        self.send_script(script)
    
    # 16. 设置形状图层描边
    def set_shape_layer_stroke(self, layer_name, width, r, g, b):
        """
        设置形状图层的描边
        
        Args:
            layer_name: 形状图层名称
            width: 描边宽度（像素）
            r, g, b: RGB 颜色值 (0-255)
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'shapeLayer') {{
            var color = new SolidColor();
            color.rgb.red = {r};
            color.rgb.green = {g};
            color.rgb.blue = {b};
            
            var desc = new ActionDescriptor();
            var ref = new ActionReference();
            ref.putEnumerated(charIDToTypeID('Lyr '), charIDToTypeID('Ordn'), charIDToTypeID('Trgt'));
            desc.putReference(charIDToTypeID('null'), ref);
            
            var strokeDesc = new ActionDescriptor();
            strokeDesc.putUnitDouble(stringIDToTypeID('strokeStyleLineWidth'), charIDToTypeID('#Pxl'), {width});
            strokeDesc.putBoolean(stringIDToTypeID('strokeEnabled'), true);
            
            var colorDesc = new ActionDescriptor();
            colorDesc.putDouble(charIDToTypeID('Rd  '), {r});
            colorDesc.putDouble(charIDToTypeID('Grn '), {g});
            colorDesc.putDouble(charIDToTypeID('Bl  '), {b});
            strokeDesc.putObject(stringIDToTypeID('strokeStyleContent'), stringIDToTypeID('solidColorLayer'), colorDesc);
            
            desc.putObject(stringIDToTypeID('strokeStyle'), stringIDToTypeID('strokeStyle'), strokeDesc);
            executeAction(stringIDToTypeID('set'), desc, DialogModes.NO);
        }}
        """
        self.send_script(script)
    
    # 17. 导出图层为 PNG
    def export_layer_as_png(self, layer_name, output_path):
        """
        将指定图层导出为 PNG 文件
        
        Args:
            layer_name: 图层名称
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功导出
        """
        script = f"""
        // 保存当前可见状态
        var visibilityState = [];
        for(var i = 0; i < app.activeDocument.layers.length; i++) {{
            visibilityState.push(app.activeDocument.layers[i].visible);
            app.activeDocument.layers[i].visible = false;
        }}
        
        // 只显示目标图层
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) {{
            layer.visible = true;
            app.activeDocument.saveToOE('png');
        }}
        
        // 恢复可见状态
        for(var i = 0; i < app.activeDocument.layers.length; i++) {{
            app.activeDocument.layers[i].visible = visibilityState[i];
        }}
        """
        
        # 设置监听器捕获二进制数据
        setup_listener = """
        window.layerImageData = null;
        window.addEventListener('message', function(e) {
            if (e.data instanceof ArrayBuffer) {
                window.layerImageData = e.data;
            }
        });
        """
        self.driver.execute_script(setup_listener)
        
        # 发送导出命令
        self.send_script(script)
        
        # 等待数据返回
        time.sleep(2)
        
        # 获取二进制数据并保存
        try:
            bytes_data = self.driver.execute_script("""
            var buffer = window.layerImageData;
            var bytes = new Uint8Array(buffer);
            var binary = '';
            for (var i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
            """)
            
            if not bytes_data:
                print("❌ 未能获取图层导出数据")
                return False
                
            # 解码 Base64 并写入文件
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(bytes_data))
            print(f"✅ 已导出图层到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 导出图层失败: {e}")
            return False
    
    # 18. 添加图片图层
    def add_image_layer(self, image_url, as_smart_object=True):
        """
        添加图片作为新图层
        
        Args:
            image_url: 图片的 URL 或本地文件路径（需要以 file:/// 开头）
            as_smart_object: 是否作为智能对象添加
        """
        self.send_script(f"app.open('{image_url}', '', {str(as_smart_object).lower()});")
    
    # 19. 删除图层
    def delete_layer(self, layer_name):
        """
        删除指定名称的图层
        
        Args:
            layer_name: 图层名称
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) {{
            app.activeDocument.activeLayer = layer;
            app.activeDocument.activeLayer.remove();
        }}
        """
        self.send_script(script)
    
    # 20. 获取图层字体信息
    def get_text_layer_font_info(self, layer_name):
        """
        获取文本图层的字体信息
        
        Args:
            layer_name: 文本图层名称
            
        Returns:
            dict: 包含字体名称、大小、颜色等信息的字典，如果不是文本图层则返回 None
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'textLayer') {{
            var info = {{
                font: layer.textItem.font,
                size: layer.textItem.size,
                color: {{
                    r: layer.textItem.color.rgb.red,
                    g: layer.textItem.color.rgb.green,
                    b: layer.textItem.color.rgb.blue
                }},
                bold: layer.textItem.fauxBold,
                italic: layer.textItem.fauxItalic,
                underline: layer.textItem.underline,
                justification: layer.textItem.justification
            }};
            app.echoToOE(JSON.stringify(info));
        }} else {{
            app.echoToOE('NOT_TEXT_LAYER');
        }}
        """
        result = self.execute_with_result(script)
        if result and result != "NOT_TEXT_LAYER":
            try:
                return json.loads(result)
            except:
                print("❌ 解析字体信息失败")
        return None
    
    # 21. 激活文档
    def activate_document(self, document_index=0):
        """
        激活指定索引的文档
        
        Args:
            document_index: 文档索引（从0开始）
        """
        script = f"app.activeDocument = app.documents[{document_index}];"
        self.send_script(script)
    
    # 22. 替换图框
    def replace_frame(self, frame_layer_name, image_url):
        """
        替换图框中的图片
        
        Args:
            frame_layer_name: 图框图层名称
            image_url: 新图片的 URL 或本地文件路径（需要以 file:/// 开头）
        """
        script = f"""
        var frameLayer = app.activeDocument.layers.getByName('{frame_layer_name}');
        if(frameLayer) {{
            app.activeDocument.activeLayer = frameLayer;
            // 检查是否是图框
            if(frameLayer.kind === 'smartObject' || frameLayer.isBackgroundLayer) {{
                // 创建一个临时图层组
                var tempGroup = app.activeDocument.layerSets.add();
                tempGroup.name = 'TempFrameGroup';
                
                // 复制当前图层到组
                frameLayer.duplicate(tempGroup, ElementPlacement.INSIDE);
                
                // 打开新图像
                app.open('{image_url}', '', false);
                
                // 复制新图像到原文档
                app.activeDocument.activeLayer.duplicate(tempGroup, ElementPlacement.INSIDE);
                app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
                
                // 创建剪贴蒙版
                var newLayer = tempGroup.layers[0];
                var frameLayerCopy = tempGroup.layers[1];
                newLayer.move(frameLayerCopy, ElementPlacement.PLACEBEFORE);
                newLayer.grouped = true;
                
                // 将组内容移回原位置
                newLayer.duplicate(frameLayer, ElementPlacement.PLACEBEFORE);
                frameLayerCopy.duplicate(frameLayer, ElementPlacement.PLACEBEFORE);
                
                // 删除原图层和临时组
                frameLayer.remove();
                tempGroup.remove();
            }}
        }}
        """
        self.send_script(script)
    
    # 23. 画板切图
    def export_artboard(self, artboard_name, output_path, format="png"):
        """
        导出指定画板为图片
        
        Args:
            artboard_name: 画板名称
            output_path: 输出文件路径
            format: 输出格式，支持 'png', 'jpg' 等
            
        Returns:
            bool: 是否成功导出
        """
        script = f"""
        var artboard = app.activeDocument.layers.getByName('{artboard_name}');
        if(artboard && artboard.kind === 'artboardSection') {{
            // 保存当前选择
            var currentActiveLayer = app.activeDocument.activeLayer;
            
            // 选择画板
            app.activeDocument.activeLayer = artboard;
            
            // 获取画板边界
            var bounds = artboard.bounds;
            
            // 创建选区
            app.activeDocument.selection.select([
                [bounds[0], bounds[1]],
                [bounds[2], bounds[1]],
                [bounds[2], bounds[3]],
                [bounds[0], bounds[3]]
            ]);
            
            // 复制选区
            app.activeDocument.selection.copy(true);
            
            // 创建新文档
            var width = bounds[2] - bounds[0];
            var height = bounds[3] - bounds[1];
            app.documents.add(width, height, 72, 'ArtboardExport', NewDocumentMode.RGB);
            
            // 粘贴
            app.activeDocument.paste();
            
            // 导出
            app.activeDocument.saveToOE('{format}');
            
            // 关闭临时文档
            app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
            
            // 恢复选择
            app.activeDocument.activeLayer = currentActiveLayer;
        }}
        """
        
        # 设置监听器捕获二进制数据
        setup_listener = """
        window.artboardData = null;
        window.addEventListener('message', function(e) {
            if (e.data instanceof ArrayBuffer) {
                window.artboardData = e.data;
            }
        });
        """
        self.driver.execute_script(setup_listener)
        
        # 发送导出命令
        self.send_script(script)
        
        # 等待数据返回
        time.sleep(3)
        
        # 获取二进制数据并保存
        try:
            bytes_data = self.driver.execute_script("""
            var buffer = window.artboardData;
            var bytes = new Uint8Array(buffer);
            var binary = '';
            for (var i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
            """)
            
            if not bytes_data:
                print("❌ 未能获取画板导出数据")
                return False
                
            # 解码 Base64 并写入文件
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(bytes_data))
            print(f"✅ 已导出画板到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 导出画板失败: {e}")
            return False
    
    # 24. 替换图层图片(自动缩放)
    def replace_image_layer_auto_scale(self, layer_name, image_url):
        """
        替换智能对象图层的图片并自动缩放以适应原尺寸
        
        Args:
            layer_name: 智能对象图层名称
            image_url: 新图片的 URL 或本地文件路径（需要以 file:/// 开头）
        """
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'smartObject') {{
            // 保存原始尺寸
            var originalWidth = layer.bounds[2] - layer.bounds[0];
            var originalHeight = layer.bounds[3] - layer.bounds[1];
            var originalLeft = layer.bounds[0];
            var originalTop = layer.bounds[1];
            
            app.activeDocument.activeLayer = layer;
            executeAction(stringIDToTypeID('placedLayerEditContents'));
            app.open('{image_url}', '', false);
            
            // 调整新图像大小以适应原始尺寸
            app.activeDocument.resizeImage(originalWidth, originalHeight, 72, ResampleMethod.BICUBIC);
            
            app.activeDocument.flatten();
            app.activeDocument.save();
            app.activeDocument.close();
            
            // 确保位置正确
            layer = app.activeDocument.layers.getByName('{layer_name}');
            if(layer) {{
                var newLeft = layer.bounds[0];
                var newTop = layer.bounds[1];
                var dx = originalLeft - newLeft;
                var dy = originalTop - newTop;
                if(dx !== 0 || dy !== 0) {{
                    layer.translate(dx, dy);
                }}
            }}
        }}
        """
        self.send_script(script)
    
    # 25. 设置文字图层格式
    def set_text_layer_format(self, layer_name, properties):
        """
        设置文本图层的格式属性
        
        Args:
            layer_name: 文本图层名称
            properties: 包含格式属性的字典，可包含以下键：
                - font: 字体名称
                - size: 字体大小
                - color: RGB颜色元组 (r,g,b)
                - bold: 是否粗体
                - italic: 是否斜体
                - underline: 是否下划线
                - justification: 对齐方式 ('left', 'center', 'right')
        """
        # 构建脚本
        script_parts = [f"var layer = app.activeDocument.layers.getByName('{layer_name}');"]
        script_parts.append("if(layer && layer.kind === 'textLayer') {")
        
        # 添加各属性设置
        if 'font' in properties:
            script_parts.append(f"    layer.textItem.font = '{properties['font']}';")
        
        if 'size' in properties:
            script_parts.append(f"    layer.textItem.size = {properties['size']};")
        
        if 'color' in properties:
            r, g, b = properties['color']
            script_parts.append(f"    layer.textItem.color.rgb.red = {r};")
            script_parts.append(f"    layer.textItem.color.rgb.green = {g};")
            script_parts.append(f"    layer.textItem.color.rgb.blue = {b};")
        
        if 'bold' in properties:
            script_parts.append(f"    layer.textItem.fauxBold = {str(properties['bold']).lower()};")
        
        if 'italic' in properties:
            script_parts.append(f"    layer.textItem.fauxItalic = {str(properties['italic']).lower()};")
        
        if 'underline' in properties:
            script_parts.append(f"    layer.textItem.underline = {str(properties['underline']).lower()};")
        
        if 'justification' in properties:
            just_map = {'left': 'Justification.LEFT', 'center': 'Justification.CENTER', 'right': 'Justification.RIGHT'}
            if properties['justification'] in just_map:
                script_parts.append(f"    layer.textItem.justification = {just_map[properties['justification']]};")
        
        script_parts.append("}")
        
        # 执行脚本
        self.send_script("\n".join(script_parts))
    
    def close(self):
        """
        关闭浏览器并清理资源
        """
        self.driver.quit()

# 示例用法
if __name__ == '__main__':
    api = PhotopeaAPI("http://192.168.110.13:8887")
    psd_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/%E5%93%81%E7%89%8C%E5%BA%97%E7%9B%92%E5%AD%90.psd"
    image_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/image_263.png"

    # 打开 PSD 文件
    api.open_psd(psd_path)
    
    # 获取所有图层名
    layer_names = api.get_all_layer_names()
    print("图层列表:", layer_names)
    
    # 替换图层图片
    api.replace_image_layer("产品图片", image_path)
    
    # 修改文本图层
    api.change_text_layer("产品型号", "NPG45")
    
    # 导出为 PNG
    api.export_image("C:/Users/Adminstor/Downloads/Easy_photopea_api/output/output.png")
    
    # 关闭
    api.close()