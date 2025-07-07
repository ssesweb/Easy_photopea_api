<!---->

# 一、API Spec - API 规格（Photopea API 文档翻译）<!----><!---->

[用户7715287681873](/user/2384215747860557/posts)

<!---->

<!---->

<!---->

2022-08-25  3,253  阅读3分钟

专栏： 

photopea

<!---->

关注

<!---->

<!---->

<!---->

![](https://p3-piu.byteimg.com/tos-cn-i-8jisjyls3a/796c19f610c146ffac65db71d7329490~tplv-8jisjyls3a-2:0:0:q75.image)

* API Spec 规格

  * Environment 环境
  * Live Messaging 即时通讯
  * Plugins 插件

* Playground

* Accounts

# 向 Photopea 传送数据

Photopea可以使用哈希符号后面的参数进行配置。

```bash
bash
 体验AI代码助手
 代码解读
复制代码
https://www.photopea.com#STRING_VALUE
```

这样的 URL 可以直接打开，也可以用作 iframe 的 src。字符串值使用查询参数的经典编码(空格为% 20等)编码到 URL 中。它对应于 Javascript 中的 encodeURI ()或 PHP 中的 urlencode ()。这个字符串包含一个 JSON 对象。

## JSON 配置对象

JSON 对象必须具有以下结构:

```json
json
 体验AI代码助手
 代码解读
复制代码
{
	"files" : [
		"https://www.mysite.com/images/design.psd",
		"https://www.mysite.com/images/button.png",
		"data:image/png;base64,iVBORw0KGgoAAAAN..."
	],
	"resources" : [
		"https://www.xyz.com/brushes/Nature.ABR",
		"https://www.xyz.com/grads/Gradients.GRD",
		"https://www.xyz.com/fonts/NewFont.otf"
	],
	"server" : {
		"version" : 1,
		"url"     : "https://www.myserver.com/saveImage.php",
		"formats" : [ "psd:true", "png", "jpg:0.5" ]
	},
	"environment" : {...},
	"script" : "app.activeDocument.rotateCanvas(90);"
}
```

所有参数都是可选的。可以使用数据 URI -- 文件可以在请求中传递([测试](//www.photopea.com#%7B%22files%22:%5B%22data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==%22%5D%7D "//www.photopea.com#%7B%22files%22:%5B%22data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==%22%5D%7D"))。

## 参数

* `Files`-文件数组，在 Photopea 启动时加载

* `Resources`-资源数组(渐变、画笔、字体... ...)

* `Server`- 参数，用于将文档保存回服务器

  * `version`-API 的版本
  * `url`-服务器的地址
  * `formats`-应该被发送到服务器的文档的格式。字符串格式对应于 \[saveToOE]\([Photopea - Scripts](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Flearn%2Fscripts "https://www.photopea.com/learn/scripts"))

* `Environment`-环境的参数，请参见 \[Environment]\([Photopea API](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fapi%2Fenvironment "https://www.photopea.com/api/environment"))

* `Script`- [脚本](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Flearn%2Fscripts "https://www.photopea.com/learn/scripts")，应该在加载每个文件之后执行(可以很长)

# 保存到服务器

如果在对 Photopea.com 的请求中指定了 server 参数，那么在 Photopea 打开的每个文档都会有 File-Save 选项。用户单击文档数据后，文档数据将通过 HTTP 请求（使用 POST 方法的http请求）发送到服务器。

Photopea 将向您的服务器发送二进制数据(字节序列) ，该服务器由两部分组成:

* 2000字节 - JSON 数据
* 其余 - 一个或多个图像文件

JSON 的结构如下:

```json
json
 体验AI代码助手
 代码解读
复制代码
{
	"source" : "https://www.mysite.com/images/button.png",
	"versions" : [
		{"format":"psd", "start":      0, "size": 700000 },
		{"format":"jpg", "start": 700000, "size": 100000 },
		...
	]
}
```

* `Source`- 如果文件是从服务器加载的，则该值是此文档的 URL。否则(打开本地文件，创建一个空文件) ，它包含`“ local，X，NAME”`，其中 X 是文档的整数 ID，NAME 是文档的名称

* `versions` 文档的不同版本

  * `format` - 文件格式，从Photopea导出
  * `Start、 size` - 文件偏移量和 size (relative，从JSON末尾开始)

下面是一个简短的 PHP 示例，它接受来自 Photopea 的文件。

```ini
ini
 体验AI代码助手
 代码解读
复制代码
$fi = fopen("php://input", "rb");  
$p = JSON_decode(fread($fi, 2000));
// getting file name from "source"

$fname = substr ($p->source, strrpos($p->source,"/")+1);  
$fo = fopen("img/".$fname,"wb");

while($buf=fread($fi,50000)) 
fwrite($fo,$buf);
fclose($fi);  
fclose($fo);
```

## 你的回应

在服务器接收到文件之后，它可以发回 JSON 响应（这个JSON 是带有可选 String 参数的）:

* `message`- 指定后，将向用户显示片刻
* `script`- 当指定时，将被执行（例如，您可以调用`app.echoToOE("saved");`)
* `newSource`- 指定后，将用作“source”的新值，以便将来保存到服务器（当在Photopea中创建文件时：“source”是“local,...” 可能很有用）

# 跨域资源共享

出于安全原因，web应用只能访问来自同一域的文件。为了让 Photopea 加载你的文件，你的服务器的响应必须包含以下标头:

```makefile
makefile
 体验AI代码助手
 代码解读
复制代码
Access-Control-Allow-Origin: *
```

有关详细信息，请参阅 [CORS 规范](https://link.juejin.cn?target=http%3A%2F%2Fwww.w3.org%2FTR%2Fcors%2F "http://www.w3.org/TR/cors/")或 [enable-cors.org](https://link.juejin.cn?target=http%3A%2F%2Fenable-cors.org%2F "http://enable-cors.org/")。

# 价格

Photopea API的使用是完全免费的。请记住，PP处于开发的早期阶段，可能存在严重的错误。对于Photopea编辑或生成的文档，我们不承担任何责任。

如果要隐藏广告和“彩色按钮”，并使用**白标模式**，请查看[分销商帐户](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fapi%2Faccounts%23distributors "https://www.photopea.com/api/accounts#distributors")。

<!---->

标签：

[产品](/tag/%E4%BA%A7%E5%93%81)

<!---->

本文收录于以下专栏

<!---->

![cover](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/95414745836549ce9143753e2a30facd~tplv-k3u1fbpfcp-jj:80:60:0:0:q75.avis)

photopea

专栏目录

<!---->

photopea 文档翻译

1 订阅

·

4 篇文章

<!---->

<!---->

订阅

<!---->

下一篇

二、API Spec - Environment 环境（Photopea API 文档翻译）

评论 0

![avatar](//lf-web-assets.juejin.cn/obj/juejin-web/xitu_juejin_web/58aaf1326ac763d8a1054056f3b7f2ef.svg)

<!---->

<!---->

<!---->

<!---->

0 / 1000

标点符号、链接等不计算在有效字数内

Ctrl + Enter

发送

登录 / 注册 即可发布评论！

<!---->

<!---->

暂无评论数据

<!---->

<!---->

<!---->

![](//lf-web-assets.juejin.cn/obj/juejin-web/xitu_juejin_web/c12d6646efb2245fa4e88f0e1a9565b7.svg) 点赞

![](//lf-web-assets.juejin.cn/obj/juejin-web/xitu_juejin_web/336af4d1fafabcca3b770c8ad7a50781.svg) 评论

![](//lf-web-assets.juejin.cn/obj/juejin-web/xitu_juejin_web/3d482c7a948bac826e155953b2a28a9e.svg) 收藏

加个关注，精彩更新不错过\~ **

![avatar](https://p6-passport.byteacctimg.com/img/mosaic-legacy/3795/3044413937~40x40.awebp)

关注

<!---->

<!---->

# 二、API Spec - Environment 环境（Photopea API 文档翻译）<!----><!---->

[用户7715287681873](/user/2384215747860557/posts)

<!---->

<!---->

<!---->

2022-08-25  139  阅读4分钟

专栏： 

photopea

<!---->

关注

<!---->

<!---->

<!---->

![](https://p3-piu.byteimg.com/tos-cn-i-8jisjyls3a/796c19f610c146ffac65db71d7329490~tplv-8jisjyls3a-2:0:0:q75.image)

编辑器的外观可以通过 JSON属性`environment`进行自定义。

```sql
sql
 体验AI代码助手
 代码解读
复制代码
{
	...
	"environment" : {          
		"theme"     : 2,         "lang"     : "es",    
		"vmode"     : 0,         "intro"    : true,
		"eparams"   : { "guides" :true, "grid" : true, "gsize": 8,   
		                                "paths": true, "pgrid": true },
		"customIO"  : { "open": "app.echoToOE("Open");" },
		"localsave" : false,     "autosave" : 120,    
		"showtools" : [0,5,9],   "menus"    : [ [1,1,0,1], 1, 0, 1, [0] ],
		"panels"    : [0, 2],
		
		"phrases"   : [ [1,0], "Open Design", [1,2], "Save Design" ],
		
		"topt"  : {  "t0": ...,  "t1": ...,  ... },
		"tmnu"  : {  "t0": ...,  "t1": ...,  ... },
		"icons" : {  "tools/crop": "https://www.me.com/img/crop.png",  ... },
		"plugins":[ ... ]
	}
}
```

每个参数都是可选的。它们具有以下含义：

* `theme`- 主题 （0， 1， 2， ...）

* `lang`- 语言

* `vmode`- 视图模式。0：常规，1：面板折叠，2：隐藏所有面板

* `intro`- 当没有打开文档时，显示介绍面板（带按钮等）

* `eparams`- 附加功能：启用或禁用指南，网格，路径，像素网格...

* `customIO`- 重新定义File-Open、 Save等，并运行自定义脚本。可能的属性：。`"new", "open", "openFromURL", "takePic", "showTemplates", "save", "saveAsPSD", "publishOnline", "exportLayers"`

* `localsave`- 启用/禁用“另存为PSD”，“保存为web”和“在线发布”

* `autosave`- 如果值为 X，Photopea将每X秒执行“File-Save”

* `showtools`- 仅显示以下工具（请参阅下面的工具 ID）

* `menus`- 指定具有0/1标志的文件、编辑、图像... 菜单的结构。\
  数组的每个元素要么是 0：隐藏项目，\
  要么是 1：显示具有标准内容的项目，\
  要么是子元素的标志数组（递归工作）。\
  如果数组短于要求，则末尾将添加零。查看Photopea的当前菜单结构，找到正确的值。例如，\
  \[1，1]作为第一个元素，“File”菜单将仅显示“New”和“Open”项目。

* `panels`- 哪些面板应该显示在侧边栏中。使用以下 ID：\
  0：历史记录，1：色板，2：图层，3：信息，4：直方图，5：属性，6：CSS，7：画笔，8：图层组合，9：字符，10：段落，11：操作，12：导航器，13：颜色，14：TPRESET，15：GUIDEGUY，16：通道，17：路径，18：调整，19：字形，20：内存，21：样式，22：注释。

* `phrases`- 允许你用自己的短语替换 Photopea 境内的任何短语。这个数组的格式为` [ ID1，W1，ID2，W2，... ]`，其中 IDx 是某个短语的 ID，Wx 是一个（用来替换的 ）新短语。\
  一些有用的 ID：\
  \[1，2]：保存（文件菜单），\
  \[2，0]：前进一步，\
  \[2，1]：后退。\
  要发现其他短语的ID，请熟悉[OpenWord表结构](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fphotopea%2FOpenWord "https://github.com/photopea/OpenWord")并在[当前短语数据库中](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fcode%2Fdbs%2FDBS.js "https://www.photopea.com/code/dbs/DBS.js")查找您的短语（var LNG ...），或者只是给我们写一封电子邮件以 [support@photopea.com](https://link.juejin.cn?target=mailto%3Asupport%40photopea.com "mailto:support@photopea.com")。

* `topt`- 工具选项。用于更改每个工具的设置。键为“tXY”，其中 XY 是工具 ID。每个工具都有自己的格式（见下文）。

* `tmnu`- 工具菜单。用于指定每个工具的顶部菜单的结构。键为“tXY”，其中 XY 是工具 ID。每个工具都有自己的格式（见下文）。

* `icons`- 自定义图标。每个图标都有一个图标 ID（key）和图像 URL（value## 工具选项和菜单）。你可以[在这里](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fcode%2Fdbs%2FDBS.js "https://www.photopea.com/code/dbs/DBS.js")找到图标ID（var PIMG ...）。例如，裁剪工具有一个ID“工具/裁剪”。在介绍屏幕上，徽标是“徽标”，底部是“底部”。

* `plugins`- [描述这里](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fapi%2Fplugins "https://www.photopea.com/api/plugins")

# 工具选项和菜单

## 移动工具

选项：`[1,0,null]`。三个值表示自动选择、变换控制和距离。1 表示已启用，0：已禁用，空：未指定。

菜单：`[1,1,1,1,1,1]`。显示/隐藏六个项目的六个标志: 自动选择，转换控件，距离，快速保存（获取PNG...），垂直对齐，水平对齐。

## 魔棒 Magic Wand

选项：`[0,0,[16,true,true]]` - 组合操作、羽化、选择选项：容差、消除锯齿、连续。

# 工具ID

* 0：移动工具
* 1：矩形选择
* 2：椭圆选择
* 5： 套索选择
* 6：多边形套索选择
* 7：磁性套索选择
* 8：快速选择
* 9： 魔杖
* 10：裁剪工具
* 14： 吸管
* 16： 标尺
* 18： 斑点修复刷工具
* 19： 修复画笔工具
* 20： 补丁工具
* 23： 画笔工具
* 24： 铅笔工具
* 27：克隆工具
* 31： 橡皮擦工具
* 34： 渐变工具
* 35： 油漆桶工具
* 36：模糊工具
* 37： 锐化工具
* 38： 涂抹工具
* 39： 减淡工具
* 40： 刻录工具
* 41： 海绵工具
* 47： 打字工具
* 42： 钢笔
* 43：免费笔
* 51：路径选择
* 52：直接选择
* 54： 矩形
* 55： 椭圆
* 57： 线
* 56： 参数化形状
* 58： 自定义形状
* 59： 手动工具
* 61： 缩放工具

<!---->

# 三、API Spec - Live Messaging 即时通讯（Photopea API 文档翻译）<!----><!---->

[用户7715287681873](/user/2384215747860557/posts)

<!---->

<!---->

<!---->

2022-08-25  196  阅读2分钟

专栏： 

photopea

<!---->

关注

<!---->

<!---->

<!---->

![](https://p3-piu.byteimg.com/tos-cn-i-8jisjyls3a/796c19f610c146ffac65db71d7329490~tplv-8jisjyls3a-2:0:0:q75.image)

您可以将Photopea插入网页（using a frame）。让我们将这样的网页称为**外部环境（OE）。** OE可以通过[Web消息传递](https://link.juejin.cn?target=http%3A%2F%2Fweb.archive.org%2Fweb%2F20150331203017%2Fhttp%3A%2F%2Fwww.w3.org%2FTR%2Fwebmessaging%2F "http://web.archive.org/web/20150331203017/http://www.w3.org/TR/webmessaging/")与Photopea进行通信。

```javascript
javascript
 体验AI代码助手
 代码解读
复制代码
window.addEventListener("message", function(e) { alert(e.data); });
var wnd = document.getElementById("pp").contentWindow;
wnd.postMessage(msg, "*");
```

OE可以向Photopea发送**两种数据**：

* **字符串** - 包含一个脚本，该脚本将由Photopea执行
* **ArrayBuffer** - 一个二进制文件： psd， svg， jpg， ...字体、画笔等

当Photopea初始化并准备接受命令时，它会发送消息 `"done"`。处理完您的消息后，Photopea 还会发回`"done"`消息。

[一些在Photopea 的即时通讯演示](https://link.juejin.cn?target=https%3A%2F%2Fphotopea-api-demo.glitch.me%2F "https://photopea-api-demo.glitch.me/")

# 从Photopea检索数据

Photopea可以使用以下命令（在脚本中）将当前图像发送到OE：

```arduino
arduino
 体验AI代码助手
 代码解读
复制代码
app.activeDocument.saveToOE("gif");
```

运行上述脚本后，PP 将发送一条带有GIF 图像的 ArrayBuffer消息，后跟一条带有 String `“ done”`的消息（脚本处理已完成）。

它还可以使用以下命令（在脚本中）将任何字符串发送到 OE：

```arduino
arduino
 体验AI代码助手
 代码解读
复制代码
app.echoToOE("Hello");
```

[/learn/scripts](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Flearn%2Fscripts "https://www.photopea.com/learn/scripts") 中的完整说明。

# 用法示例

此 API 可以替换主 API。与其让 Photopea 直接与您的服务器通信，倒不如在程序中加载文件，并在客户端设备中将它们传输到Photopea。

您可以使用Photopea作为“模块”，隐藏其用户界面，只使用消息。您可以创建图像的批处理处理器（调整图像大小，添加水印，在格式之间转换）。您可以创建脚本，将文档的每个图层导出为 PNG。您可以创建脚本，该脚本用户的数据替换每个文本层中的文本(以创建名片生成器等)。

# 示例：与自定义存储集成

我们可以重新定义“File - Open”和“File - Save”的默认行为。

* 我们可以将Photopea消息中的任何图像作为ArrayBuffer发送
* 我们可以调用`app.activeDocument.saveToOE("psd");` 将当前文件发送到 OE。
* 我们可以调用`app.echoToOE("Hello");`将任何字符串发送到 OE。
* 我们可以读写`app.activeDocument.source` String 来标识文件。
* 我们可以在按 Open 或 Save 键后设置运行自定义脚本:[customIO : open, save](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fapi%2Fenvironment "https://www.photopea.com/api/environment")

现在，我们可以执行以下操作：

* 将自定义脚本设置为`app.echoToOE("Open" / "Save");` 在用户按下按钮时收到通知。
* 当用户想要打开文件时，向他显示您自己的文件输入（您甚至可以让用户画一些东西，或者为他拍照）。
* 获得图像（ArrayBuffer）后，将其发送到Photopea并设置source：。`app.activeDocument.source="myID2353"`
* 当用户想要保存文件时，读取该文件 （`app.activeDocument.saveToOE("psd");`） 及其source `app.echoToOE(app.activeDocument.source);`，然后将新版本保存到存储中。

# 四、API Spec - Plugins 插件（Photopea API 文档翻译）<!----><!---->

为Photopea创建插件，并通过配置 JSON 将它们提供给用户。

```json
json
 体验AI代码助手
 代码解读
复制代码
{ "environment": {
	"plugins" : [ 
		{
			"name"  : "Wikipedia",
			"url"   : "https://en.wikipedia.org",
			"icon"  : "https://en.wikipedia.org/static/favicon/wikipedia.ico"
		}
	]
} }
```

* `name`- 插件名称
* `url`- 插件网址
* `icon`- 插件图标（可选）

对于每个插件，按钮将添加到右侧当前按钮下方。

用户单击插件按钮后，面板会打开一个网站地址。

用户可以将图像从您的网站拖放到Photopea（因为Photopea支持从任何网站拖放图像，由浏览器打开）。

您的网站可以使用[实时消息传递](https://link.juejin.cn?target=https%3A%2F%2Fwww.photopea.com%2Fapi%2Flive "https://www.photopea.com/api/live")（您的网站充当OE）与Photopea连接。它允许您的插件执行脚本（例如，更改前景色，移动图层等）。

该插件可以将文件提供给Photopea（图像：psd，jpg，svg ...或资源：画笔，图案，字体...），或以特定格式请求当前文件。所有这些都可以通过插件（网站）中的按钮进行控制。

```javascript
javascript
 体验AI代码助手
 代码解读
复制代码
window.parent.postMessage("...script...", "*");
window.parent.postMessage(ArrayBuffer, "*");
```

# 用法示例

**照片商店**。允许用户浏览您的图像数据库。他们可以通过关键字搜索数据库。您可以在每个图像旁边添加一个“Open”按钮，这将在Photopea中打开该图像。

**字体库**。允许用户浏览字体数据库。单击按钮后将加载字体。您也可以将支付网关集成到插件中（因为它是您的网站，因此您可以完全控制它）。

您可以将插件设置为“商业” - 让用户每月为它们付费。登录和支付界面仍可能位于Photopea内部插件的同一“iframe”中（或者您可以打开一个新窗口，然后返回到Photopea）。

# 图标网址

要制作一个类似于Photopea图标，需要将图标背景设置为透明，图标本身为黑色。此外，在图标 URL 之前添加“===”。Photopea 会根据当前的颜色主题调整图标的颜色(白色表示深色主题，暗色表示明亮主题)。

Photopea会将您的图标显示为20x20屏幕像素（20x20，40x40，60x60等）的倍数。因此，如果您想要清晰的垂直条纹，请制作一个图标，例如160x160像素，以及一个8px宽的条纹。在这种情况下，9px的条纹看起来很模糊。
