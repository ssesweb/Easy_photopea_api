# Photopea 本地集成与自动化指南

本文介绍如何通过前端 JavaScript 和后端 Python 脚本，调用本地部署的 Photopea（运行在 `http://localhost:8887/` 或 `http://192.168.110.13:8887/`）进行图像处理。涵盖以下功能及示例：打开文件、图像编辑、图层插入、导出图像、PSD 内容修改，以及使用插件（内置或第三方）进行抠图、图像扩展等操作。文档结构清晰易读，每个功能均给出调用说明、关键参数说明，以及 JavaScript 和 Python 的示例代码。

## 环境与通信机制

* **Photopea 部署**：假设已在本地启动 Photopea 服务器，监听端口 `8887`。可通过 `http://localhost:8887/` 或本机 IP（如 `http://192.168.110.13:8887/`）访问。

* **集成方式**：将 Photopea 嵌入在网页的 `<iframe>` 中。上层环境（Outer Environment, OE）通过 `window.postMessage` 向 Photopea 发送命令。[photopea.com](https://www.photopea.com/api/live#:~:text=OE%20can%20send%20two%20kinds,of%20data%20to%20Photopea)Photopea 接受两种消息类型：**字符串脚本**（Photopea 执行的 JavaScript 代码）或 **ArrayBuffer 二进制**（用于加载文件）。初始化完成后，Photopea 会发送 `"done"` 消息表示就绪；每次执行完脚本，也会发送 `"done"`。例如：

  ```
  js
  复制编辑
  // 在父页面中监听 Photopea 消息
  window.addEventListener("message", e => {
    if (e.data === "done") { console.log("Photopea 执行完毕"); }
    else { /* 处理 ArrayBuffer 或字符串消息 */ }
  });
  // 向 Photopea iframe 发送脚本命令
  const iframe = document.getElementById("photopeaFrame");
  const script = "app.open('http://localhost:8887/images/img.png', '', false);";
  iframe.contentWindow.postMessage(script, "*");
  ```

  如上所示，通过 `iframe.contentWindow.postMessage(msg, "*")` 发送脚本即可[photopea.com](https://www.photopea.com/api/live#:~:text=OE%20can%20send%20two%20kinds,of%20data%20to%20Photopea)。

* **参数说明**：Photopea 通过全局 `app` 对象提供 Photoshop 式脚本接口[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Scripts%20allow%20you%20to%20access,to%20do%20the%20same%20task)。常用命令包括 `app.open(url, as, asSmart)`（加载图像）、`Document.saveToOE(format)`（将文档发送到外部）、`app.echoToOE(string)`（向外部发送字符串）等[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Document.saveToOE%28,optional%20parameters%20after%20the%20colon)。例如：`app.open("http://.../img.png", "", true);` 会将图片作为智能对象插入当前文档[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)。

* **脚本示例**：Live Messaging API 文档给出示例——向 Photopea 发送 `app.activeDocument.saveToOE("gif");` 可将当前文档以 GIF 格式的二进制发送给外部环境[photopea.com](https://www.photopea.com/api/live#:~:text=app.activeDocument.saveToOE%28)；调用 `app.echoToOE("Hello");` 则会向外部发送字符串[photopea.com](https://www.photopea.com/api/live#:~:text=It%20can%20also%20send%20any,inside%20a%20script)。这些命令常用于获取结果或状态。

* **Python 集成**：可以使用 Selenium、Pyppeteer 等浏览器自动化工具，在后台打开 Photopea 界面并执行相同的 postMessage 操作。例如，Selenium 示例：

  ```
  python
  复制编辑
  from selenium import webdriver
  driver = webdriver.Chrome()
  driver.get("http://localhost:8887")  # 打开 Photopea
  # 发送脚本到 Photopea
  driver.execute_script("""
    window.postMessage("app.open('http://localhost:8887/images/photo.psd', '', false);", "*");
  """)
  ```

  或使用 Pyppeteer：

  ```
  python
  复制编辑
  import asyncio
  from pyppeteer import launch
  async def run():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://localhost:8887')
    await page.evaluate('window.postMessage("app.open(\'/test.png\', \'\', true);", "*");')
  asyncio.get_event_loop().run_until_complete(run())
  ```

  *注意：* Selenium/pyppeteer 示例代码须在相应上下文执行，postMessage 需要在主文档作用域内调用。

下面按照功能逐项说明调用方法和示例。

## 1. 打开图像或 PSD 文件

**说明**：可以通过脚本命令或二进制方式在 Photopea 中打开本地或远程文件。常用的脚本命令是 `app.open(url, as, asSmart)`[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)。其中 `url` 可以是图片或 PSD 文件的网络地址，`asSmart=true` 表示将图像作为智能对象插入到当前文档。

**JavaScript 示例**：

```
js
复制编辑
// 通过 postMessage 打开远程图片
const script = "app.open('http://192.168.110.13:8887/images/photo.jpg', '', false);";
iframe.contentWindow.postMessage(script, "*");
// 若希望插入为当前文档的新图层，设置 asSmart: true
const script2 = "app.open('http://localhost:8887/insert.png', '', true);";
iframe.contentWindow.postMessage(script2, "*");
```

**Python 示例**（使用 Selenium）：

```
python
复制编辑
driver.execute_script("""
  window.postMessage(
    "app.open('http://192.168.110.13:8887/images/photo.jpg', '', false);", "*");
""")
```

或者先用 `requests` 获取图像二进制，再发送 ArrayBuffer（需在浏览器环境执行 JS）。例如：

```
python
复制编辑
import requests, numpy as np
img_data = requests.get("http://localhost:8887/pic.png").content
# 将二进制转换为 JavaScript 可读取的格式（Uint8Array）
arr = list(img_data)
driver.execute_script(f"""
  var array = new Uint8Array({arr});
  window.postMessage(array.buffer, "*");
""")
```

这样可以将图片数据直接发送给 Photopea，触发文件打开。

## 2. 修改图像

**说明**：利用 `app.activeDocument` 对象可以修改当前文档属性或调用各种变换、滤镜等。例如旋转、缩放、裁剪等。常用方法：`rotateCanvas(deg)`、`resizeImage(w,h)`、`resizeCanvas(w,h)`、`activeLayer.rotate(deg)` 等[photopea.com](https://www.photopea.com/learn/scripts#:~:text=,you%20must%20call%20resizeCanvas)[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)。

**JavaScript 示例**：

```
js
复制编辑
// 旋转画布 90 度
iframe.contentWindow.postMessage("app.activeDocument.rotateCanvas(90);", "*");
// 缩放画布到 800x600
iframe.contentWindow.postMessage("app.activeDocument.resizeCanvas(800, 600);", "*");
// 旋转当前选中图层 45 度
iframe.contentWindow.postMessage("app.activeDocument.activeLayer.rotate(45);", "*");
```

**Python 示例**（Selenium）：

```
python
复制编辑
driver.execute_script("""
  window.postMessage("app.activeDocument.rotateCanvas(90);", "*");
""")
driver.execute_script("""
  window.postMessage("app.activeDocument.resizeCanvas(1024, 768);", "*");
""")
```

完成修改后，可使用 `app.echoToOE(...)` 发送状态或结果到外部[photopea.com](https://www.photopea.com/api/live#:~:text=It%20can%20also%20send%20any,inside%20a%20script)。

## 3. 插入图像（作为新图层）

**说明**：在已有文档中插入新图层，可以使用 `app.open(url, as, asSmart)` 并将 `asSmart` 设为 `true`[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)。这样图像会作为智能对象插入到当前文档。若文档为空，效果同新建文档。

**JavaScript 示例**：

```
js
复制编辑
// 将远程图像插入为新图层（智能对象）
iframe.contentWindow.postMessage(
  "app.open('http://localhost:8887/assets/logo.png', '', true);", "*"
);
```

**Python 示例**（Selenium）：

```
python
复制编辑
driver.execute_script("""
  window.postMessage("app.open('http://192.168.110.13:8887/logo.jpg', '', true);", "*");
""")
```

插入后，可以在脚本中调整新图层的位置或样式。

## 4. 导出图像（PNG、JPG、PSD）

**说明**：Photopea 支持将当前文档导出为多种格式。通过脚本调用 `app.activeDocument.saveToOE(format)` 可以将图像（如 PNG、JPG、PSD）以二进制形式发送到外部[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Document.saveToOE%28,optional%20parameters%20after%20the%20colon)[photopea.com](https://www.photopea.com/api/live#:~:text=app.activeDocument.saveToOE%28)。参数 `format` 格式为 `"png"`、`"jpg:质量"` 或 `"psd:true"` 等。例如 `"jpg:0.8"` 表示 JPG 压缩质量为 80%。

**JavaScript 示例**：

```
js
复制编辑
// 导出为 PNG
iframe.contentWindow.postMessage("app.activeDocument.saveToOE('png');", "*");
// 导出为 JPG（质量 0.8）
iframe.contentWindow.postMessage("app.activeDocument.saveToOE('jpg:0.8');", "*");
// 导出为最小化 PSD
iframe.contentWindow.postMessage("app.activeDocument.saveToOE('psd:true');", "*");
```

执行上述命令后，Photopea 会向外部环境依次发送图像文件（二进制 ArrayBuffer）和 `"done"` 消息[photopea.com](https://www.photopea.com/api/live#:~:text=app.activeDocument.saveToOE%28)。在 JavaScript 环境中需通过 `window.addEventListener("message", ...)` 接收这些数据；在 Python 中可用 Selenium 等方式捕获返回的二进制并保存。

**Python 示例**（Selenium + requests）：

```
python
复制编辑
# 在 iframe 中调用导出
driver.execute_script("window.postMessage(\"app.activeDocument.saveToOE('png');\", '*');")
# 等待 Photopea 发送数据，并通过 window.addEventListener 获取。在此示例中，可在 JS 回调中存储到全局变量或通过 WebSocket 通道返回。
```

*提示：* 使用 `saveToOE` 需要在框架环境内收听消息。若需要直接下载文件，也可以用 `Document.exportDocument()` 方法（将结果打包为 ZIP 下载），或前述方式结合后端服务器保存图片[reddit.com](https://www.reddit.com/r/photopea/comments/idq39d/assistance_with_scripting_export/#:~:text=The%20saveToOE%20saves%20to%20the,com%2Fapi)。

## 5. 修改 PSD 内容（编辑图层、插入/替换图层、插入文字、复制图层等）

**说明**：Photopea 的脚本接口类似 Photoshop，允许修改图层属性和内容[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Scripts%20allow%20you%20to%20access,to%20do%20the%20same%20task)[photopea.com](https://www.photopea.com/tuts/edit-smart-objects-with-a-script/#:~:text=%2F%2F%20select%20a%20layer%20that,app.activeDocument.activeLayer%20%3D%20l)。常见操作包括选择图层、重命名、复制、修改文本、编辑智能对象等。

* **选择和操作图层**：

  ```
  js
  复制编辑
  // 选中名为 "Layer 1" 的图层
  iframe.contentWindow.postMessage("app.activeDocument.activeLayer = app.activeDocument.layers.getByName('Layer 1');", "*");
  ```

* **重命名图层**：

  ```
  js
  复制编辑
  // 重命名当前选中图层
  iframe.contentWindow.postMessage("app.activeDocument.activeLayer.name = 'NewName';", "*");
  ```

* **复制图层**：\
  Photopea 支持 `.duplicate()` 方法复制图层[reddit.com](https://www.reddit.com/r/photopea/comments/idq39d/assistance_with_scripting_export/#:~:text=app)。示例：

  ```
  js
  复制编辑
  // 复制当前选中图层
  iframe.contentWindow.postMessage("app.activeDocument.activeLayer.duplicate();", "*");
  ```

* **插入/替换图层内容**：\
  *插入*：可通过前面第3步 `app.open(..., asSmart=true)` 将图像作为新智能对象层插入。*替换*（特别是智能对象内容），可使用 Photoshop 的 Action 机制：例如 Edit Smart Objects with a Script 中给出，通过执行 `executeAction(stringIDToTypeID("placedLayerEditContents"))` 进入智能对象，再修改后保存[photopea.com](https://www.photopea.com/tuts/edit-smart-objects-with-a-script/#:~:text=%2F%2F%20select%20a%20layer%20that,app.activeDocument.activeLayer%20%3D%20l)。示例：

  ```
  js
  复制编辑
  // 编辑名为 "SmartObj" 的智能对象图层内容
  iframe.contentWindow.postMessage(
    `
    var layer = app.activeDocument.layers.getByName("SmartObj");
    app.activeDocument.activeLayer = layer;
    executeAction(stringIDToTypeID("placedLayerEditContents")); 
    app.activeDocument.activeLayer.rotate(30);
    app.activeDocument.save(); app.activeDocument.close();
    `,
    "*"
  );
  ```

* **插入文字**：Photopea 脚本可创建文本图层并设置内容样式。示例（创建文本后设置样式）：

  ```
  js
  复制编辑
  // 新建文本图层并设置文字
  iframe.contentWindow.postMessage(
    `
    var textLayer = app.activeDocument.createTextLayer(); 
    textLayer.textItem.contents = "示例文字";
    textLayer.textItem.size = 48; 
    textLayer.textItem.color.rgb.red = 255;
    `,
    "*"
  );
  ```

  (*注：示例仅用于说明，具体 API 可能需要根据 Photopea 版本调整。*)

## 6. 插件与高级操作

### 6.1 Photopea 插件（抠图、魔法工具）

Photopea 支持内置插件与第三方插件。通过脚本可以调用内置工具，如“Magic Cut”（魔术剪切）用于背景抠图。示例：

```
js
复制编辑
// 打开 Magic Cut 窗口
iframe.contentWindow.postMessage("app.showWindow('magiccut');", "*");
```

此命令会调出 Magic Cut 面板，让用户交互抠图。若配置了第三方服务（如 Dezgo 的“Remove BG”），可在加载 Photopea 时在环境配置里设置 API Key：

```
js
复制编辑
const env = { apis: { dezgo: "YOUR_API_KEY" } };
iframe.src = "http://localhost:8887/?json=" + encodeURIComponent(JSON.stringify({environment: env}));
```

这样在 Photopea 中就能使用“Remove BG”功能（调用 Dezgo API）[photopea.com](https://www.photopea.com/api/#:~:text=%2A%20%60apis%60%20,executed%20after%20loading%20each%20file)。插件可通过 `app.showWindow(...)` 调用，多数都有对应名称（参见 Photopea 插件列表）。

### 6.2 调用本地 ComfyUI API（抠图、扩展、图像修改）

如果本地部署了 ComfyUI（如 `http://192.168.110.13:8188/`），可以通过其 HTTP 接口进行 AI 图像处理。如背景移除、图像扩展（外推）等。ComfyUI 提供了 RESTful API 和 WebSocket，主要端点有[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=,sends%20status%20and%20executing%20messages)：

* `POST /prompt`：提交一个 Workflow（JSON 格式）到队列，返回 `prompt_id`[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=%2A%20%60%40routes.post%28,workflow%2C%20returns%20prompt_id%20or%20error)。

* `GET /history/{prompt_id}`：查询指定 `prompt_id` 的执行结果信息[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=%2A%20%60%40routes.post%28,workflow%2C%20returns%20prompt_id%20or%20error)。

* `GET /view?filename=...&subfolder=...&type=...`：下载生成的图像二进制[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=%2A%20%60%40routes.get%28,temp)[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=Retrieves%20an%20image%20from%20ComfyUI,returns%20the%20raw%20image%20data)。

* `POST /upload/image`：上传图片文件到 ComfyUI（指定类别 input/output/temp）[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=%2A%20%60%40routes.get%28,temp)[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=Upload%20Image)。

* `WS /ws?clientId=...`：WebSocket 连接，用于接收生成进度消息[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=,sends%20status%20and%20executing%20messages)。

**示例流程（Python）**：

1. **准备图像**：将当前 Photopea 文档导出并作为输入，或直接读取本地文件。例如使用 Selenium 在浏览器中执行：`app.activeDocument.saveToOE("png");` 收集 PNG 二进制。

2. **上传图片**：

   ```
   python
   复制编辑
   import requests
   files = {'image': open('input.png','rb')}
   requests.post("http://192.168.110.13:8188/upload/image", files=files)
   ```

3. **提交工作流**：准备一个 ComfyUI Workflow JSON（已包含背景移除或扩展节点），并调用 `/prompt`。

   ```
   python
   复制编辑
   import json, uuid
   prompt = json.loads(open('workflow.json').read())  # ComfyUI workflow
   client_id = str(uuid.uuid4())
   data = {'prompt': prompt, 'client_id': client_id}
   res = requests.post(f"http://192.168.110.13:8188/prompt", json=data)
   prompt_id = res.json()['prompt_id']
   ```

4. **获取结果**：持续查询或使用 WebSocket 监听任务完成。完成后通过 `/history` 和 `/view` 下载输出图像。

   ```
   python
   复制编辑
   # 等待生成完成（可使用 WebSocket 等待 'executing' 消息）
   import time
   while True:
       hist = requests.get(f"http://192.168.110.13:8188/history/{prompt_id}").json()
       if hist.get(prompt_id) and hist[prompt_id].get('outputs'):
           break
       time.sleep(1)
   # 假设有输出文件信息
   outputs = hist[prompt_id]['outputs']
   # 遍历输出节点，下载图片
   for node_id, out in outputs.items():
       if 'images' in out:
           for img in out['images']:
               data = {'filename': img['filename'], 'subfolder': img['subfolder'], 'type': img['type']}
               q = requests.get(f"http://192.168.110.13:8188/view", params=data)
               with open(img['filename'], 'wb') as f:
                   f.write(q.content)
   ```

   详细代码可参考 ComfyUI 官方博客[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=Get%20Image)和 Medium 教程[medium.com](https://medium.com/@next.trail.tech/how-to-use-comfyui-api-with-python-a-complete-guide-f786da157d37#:~:text=ComfyUI%20uses%20WebSocket%20to%20provide,receive%20preview%20images%20during%20generation)。

5. **反馈到 Photopea**：将处理结果再次通过 postMessage 或 `app.open` 载入 Photopea。例如使用 Selenium 调用：

   ```
   python
   复制编辑
   # 读取生成图像并发送到 Photopea
   with open('result.png','rb') as f:
       img_bytes = f.read()
   arr = list(img_bytes)
   driver.execute_script(f"""
     var img = new Uint8Array({arr}).buffer;
     window.postMessage(img, "*");
   """)
   ```

   Photopea 将收到二进制数组并自动打开为图层或文档。

### 6.3 插件开发/调用建议

Photopea 允许自定义插件，通过 JSON 配置注册，并在 UI 中添加按钮[photopea.com](https://www.photopea.com/api/plugins#:~:text=%7B%20,%7D)。例如，将插件配置添加到 `environment` 参数：

```
js
复制编辑
const config = {
  environment: {
    plugins: [
      { name: "MyPlugin", url: "http://localhost:8887/myplugin.html", icon: "http://localhost:8887/icon.png" }
    ]
  }
};
iframe.src = "http://localhost:8887/#" + encodeURIComponent(JSON.stringify(config));
```

用户点击插件按钮时，会在 Photopea 侧边打开指定 URL[photopea.com](https://www.photopea.com/api/plugins#:~:text=Image)。插件网页可以使用 `window.parent.postMessage(...)` 与 Photopea 通信[photopea.com](https://www.photopea.com/api/plugins#:~:text=The%20plugin%20can%20give%20files,which%20is%20your%20website)，执行脚本或传递文件。例如插件按钮触发 `window.parent.postMessage("app.activeDocument.rotateCanvas(180);", "*");`，即可在 Photopea 中旋转图像。开发插件时建议支持响应式布局，不指定固定宽高[photopea.com](https://www.photopea.com/api/plugins#:~:text=)。

## 参考资料

* Photopea Live Messaging API[photopea.com](https://www.photopea.com/api/live#:~:text=OE%20can%20send%20two%20kinds,of%20data%20to%20Photopea)[photopea.com](https://www.photopea.com/api/live#:~:text=app.activeDocument.saveToOE%28)

* Photopea 脚本文档[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Photopea%20extends%20the%20model%20of,by%20adding%20several%20new%20functions)[photopea.com](https://www.photopea.com/learn/scripts#:~:text=Document.saveToOE%28,optional%20parameters%20after%20the%20colon)

* Photopea 教程《Edit Smart Objects with a Script》[photopea.com](https://www.photopea.com/tuts/edit-smart-objects-with-a-script/#:~:text=%2F%2F%20select%20a%20layer%20that,app.activeDocument.activeLayer%20%3D%20l)

* ComfyUI HTTP 接口指南[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=,sends%20status%20and%20executing%20messages)[9elements.com](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/#:~:text=Retrieves%20an%20image%20from%20ComfyUI,returns%20the%20raw%20image%20data)

* Photopea 插件文档[photopea.com](https://www.photopea.com/api/plugins#:~:text=%7B%20,%7D)[photopea.com](https://www.photopea.com/api/plugins#:~:text=The%20plugin%20can%20give%20files,which%20is%20your%20website)

以上示例仅供参考，实际集成时可根据需求调整 URL、参数和工作流。通过 iframe+postMessage 机制，配合 Photopea 和 ComfyUI 的 API，可以实现强大的图像自动化处理流水线。
