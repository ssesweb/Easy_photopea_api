# examples.py
# PhotopeaAPI 使用示例

import os
import sys
import time
from pathlib import Path

# 导入 PhotopeaAPI 类
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from photopea_api import PhotopeaAPI

# 创建输出目录
output_dir = Path("C:/Users/Adminstor/Downloads/Easy_photopea_api/output")
output_dir.mkdir(exist_ok=True)

# 初始化 API
def run_examples():
    # 初始化 PhotopeaAPI
    api = PhotopeaAPI("http://192.168.110.13:8887")
    
    # 设置文件路径
    psd_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/%E5%93%81%E7%89%8C%E5%BA%97%E7%9B%92%E5%AD%90.psd"
    image_path = "file:///C:/Users/Adminstor/Downloads/Easy_photopea_api/input/image_263.png"
    
    try:
        # 1. 打开 PSD 文件
        print("\n1. 打开 PSD 文件")
        api.open_psd(psd_path)
        time.sleep(2)
        
        # 2. 显示/隐藏图层
        print("\n2. 显示/隐藏图层")
        # 假设有一个名为"背景"的图层
        api.show_hide_layer("背景", False)  # 隐藏
        time.sleep(1)
        api.show_hide_layer("背景", True)   # 显示
        time.sleep(1)
        
        # 3. 激活图层
        print("\n3. 激活图层")
        api.activate_layer("产品图片")
        time.sleep(1)
        
        # 4. 修改图层文字
        print("\n4. 修改图层文字")
        api.change_text_layer("产品型号", "NPG45")
        time.sleep(1)
        
        # 5. 替换图层图片
        print("\n5. 替换图层图片")
        api.replace_image_layer("产品图片", image_path)
        time.sleep(2)
        
        # 6. 导出为图片
        print("\n6. 导出为图片")
        api.export_image(str(output_dir / "output.png"))
        time.sleep(1)
        
        # 7. 关闭 PSD 文件 (先不关闭，继续演示其他功能)
        # print("\n7. 关闭 PSD 文件")
        # api.close_document()
        
        # 8. 另存为 PSD 文件
        print("\n8. 另存为 PSD 文件")
        api.save_as_psd(str(output_dir / "saved.psd"))
        time.sleep(1)
        
        # 9. 获取所有图层名
        print("\n9. 获取所有图层名")
        layer_names = api.get_all_layer_names()
        print(f"图层列表: {layer_names}")
        time.sleep(1)
        
        # 10. 获取图层文字
        print("\n10. 获取图层文字")
        text_content = api.get_layer_text("产品型号")
        print(f"文本内容: {text_content}")
        time.sleep(1)
        
        # 11. 设置文字图层字体
        print("\n11. 设置文字图层字体")
        api.set_text_layer_font("产品型号", "Arial")
        time.sleep(1)
        
        # 12. 获取图层所属组
        print("\n12. 获取图层所属组")
        group_name = api.get_layer_group("产品图片")
        print(f"所属组: {group_name}")
        time.sleep(1)
        
        # 13. 重命名图层
        print("\n13. 重命名图层")
        api.rename_layer("产品型号", "产品型号-已修改")
        time.sleep(1)
        
        # 14. 内容识别填充 (需要先选择区域，此处仅演示API)
        print("\n14. 内容识别填充 (仅演示API)")
        # api.content_aware_fill("背景")
        
        # 15. 修改颜色填充图层 (假设有一个颜色填充图层)
        print("\n15. 修改颜色填充图层 (仅演示API)")
        # api.change_fill_layer_color("颜色填充", 255, 0, 0)  # 红色
        
        # 16. 设置形状图层描边 (假设有一个形状图层)
        print("\n16. 设置形状图层描边 (仅演示API)")
        # api.set_shape_layer_stroke("形状图层", 2, 0, 0, 255)  # 2像素蓝色描边
        
        # 17. 导出图层为 PNG
        print("\n17. 导出图层为 PNG")
        api.export_layer_as_png("产品图片", str(output_dir / "layer.png"))
        time.sleep(1)
        
        # 18. 添加图片图层
        print("\n18. 添加图片图层")
        api.add_image_layer(image_path)
        time.sleep(2)
        
        # 19. 删除图层 (先不删除，继续演示其他功能)
        # print("\n19. 删除图层")
        # api.delete_layer("新添加的图层")
        
        # 20. 获取图层字体信息
        print("\n20. 获取图层字体信息")
        font_info = api.get_text_layer_font_info("产品型号-已修改")
        print(f"字体信息: {font_info}")
        time.sleep(1)
        
        # 21. 激活文档 (如果有多个文档)
        print("\n21. 激活文档")
        api.activate_document(0)
        time.sleep(1)
        
        # 22. 替换图框 (假设有一个图框图层)
        print("\n22. 替换图框 (仅演示API)")
        # api.replace_frame("图框图层", image_path)
        
        # 23. 画板切图 (假设有一个画板)
        print("\n23. 画板切图 (仅演示API)")
        # api.export_artboard("画板1", str(output_dir / "artboard.png"))
        
        # 24. 替换图层图片(自动缩放)
        print("\n24. 替换图层图片(自动缩放)")
        api.replace_image_layer_auto_scale("产品图片", image_path)
        time.sleep(2)
        
        # 25. 设置文字图层格式
        print("\n25. 设置文字图层格式")
        api.set_text_layer_format("产品型号-已修改", {
            'size': 24,
            'color': (255, 0, 0),  # 红色
            'bold': True,
            'justification': 'center'
        })
        time.sleep(1)
        
        # 导出最终结果
        print("\n导出最终结果")
        api.export_image(str(output_dir / "final_result.png"))
        
        # 7. 关闭 PSD 文件
        print("\n7. 关闭 PSD 文件")
        api.close_document()
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭浏览器
        api.close()
        print("\n示例运行完成，浏览器已关闭")

if __name__ == "__main__":
    run_examples()