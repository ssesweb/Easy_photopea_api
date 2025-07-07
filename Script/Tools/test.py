# photopea_controller.py
# 封装与本地 Photopea 实例交互的控制器

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

class PhotopeaController:
    def __init__(self, photopea_url="http://192.168.110.13:8887"):
        self.photopea_url = photopea_url
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(photopea_url)
        time.sleep(2)

        # 自动点击“Start using Photopea”
        try:
            self.driver.find_element("css selector", "a[href='#']").click()
            print("✅ 已自动点击 Start using Photopea")
        except Exception as e:
            print("⚠️ 未能点击启动按钮（可能已跳过）:", e)

        time.sleep(6)  # 等待主编辑器加载

    def send_script(self, script):
        # 使用 JSON 字符串避免反引号与嵌套错误
        wrapped_script = f"window.postMessage({repr(script)}, '*');"
        self.driver.execute_script(wrapped_script)
        time.sleep(1)

    def open_psd(self, url):
        self.send_script(f"app.open('{url}', '', false);")

    def show_hide_layer(self, layer_name, visible=True):
        visibility = "true" if visible else "false"
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer) layer.visible = {visibility};
        """
        self.send_script(script)

    def change_text_layer(self, layer_name, new_text):
        script = f"""
        var layer = app.activeDocument.layers.getByName('{layer_name}');
        if(layer && layer.kind === 'textLayer') {{
            layer.textItem.contents = '{new_text}';
        }}
        """
        self.send_script(script)

    def rename_layer(self, old_name, new_name):
        script = f"""
        var layer = app.activeDocument.layers.getByName('{old_name}');
        if(layer) layer.name = '{new_name}';
        """
        self.send_script(script)

    def replace_image_layer(self, layer_name, image_url):
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

    def export_png(self, output_path):
        self.send_script("app.activeDocument.saveToOE('png');")
        # TODO: 捕获导出数据并写入文件

    def close(self):
        self.driver.quit()

# 示例用法
if __name__ == '__main__':
    controller = PhotopeaController("http://192.168.110.13:8887")
    psd_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/%E5%93%81%E7%89%8C%E5%BA%97%E7%9B%92%E5%AD%90.psd"
    image_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/image_263.png"

    controller.open_psd(psd_path)
    controller.replace_image_layer("产品图片", image_path)
    controller.change_text_layer("产品型号", "NPG45")
    controller.close()