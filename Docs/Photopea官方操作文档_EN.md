# Passing data to Photopea

<!--<p>* * * You can also use <a href="https://www.photopea.com/api/live">Live Messaging</a> to get files to and from Photopea.</p>-->

Photopea can be configured using a parameter after a hash sign.

```
https://www.photopea.com#STRING_VALUE
```

Such URL can be opened directly, or used as a `src` of an `iframe`. String value is encoded into the URL using classic encoding of query parameters (space as %20 etc.). It corresponds to **encodeURIComponent()** in Javascript or **urlencode()** in PHP. This string contains a JSON object.

### JSON configuration object

JSON object must have the following structure:

```
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
	"apis"   : { "dezgo": "d4e5f6"  },
	"script" : "app.activeDocument.rotateCanvas(90);"
}
```

All parameters are optional. Data URIs can be used - file can be passed inside a request ([test](//www.photopea.com#%7B%22files%22:%5B%22data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==%22%5D%7D)).

### Parameters

* `files` - array of files, that are loaded when Photopea starts

* `resources` - array of resources (gradients, brushes, fonts ...)

* `server` - parameters for saving documents back to a server

  * `version` - the version of the API
  * `url` - URL address of a server
  * `formats` - formats, in which a document should be sent to a server. The string format corresponds to [saveToOE](https://www.photopea.com/learn/scripts).

* `environment` - parameters of the environment, see [Environment](/api/environment)

* `apis` - some features are done by third parties. Enter your own API keys to use them.
  * `dezgo` - unlock the [Magic Replace](//www.youtube.com/watch?v=X_jRqH0eKtE) and "Remove BG" with [Dezgo](//dev.dezgo.com/pricing/sd1/)

* `script` - the [script](/learn/scripts), that should be executed after loading each file (can be long)

## Saving to server

When `server` parameter is specified in a request to Photopea.com, every document opened in Photopea will have the `File - Save` option. After a user clicks it, document data are sent to your server in a HTTP request using POST method.

Photopea will send binary data (a sequence of bytes) to your server, which has two parts:

* 2000 Bytes - JSON data
* the rest - one or more image files

The JSON will have a following structure:

```
{
	"source" : "https://www.mysite.com/images/button.png",
	"versions" : [
		{"format":"psd", "start":      0, "size": 700000 },
		{"format":"jpg", "start": 700000, "size": 100000 },
		...
	]
}
```

* `source` - if the file was loaded from your server, the value is the URL of this document. Otherwise (opening a local file, creating an empty file), it contains `"local,X,NAME"`, where X is the integer ID of the document, and NAME is the name of the document

* `versions` different versions of your document

  * `format` - format of the file, exported from Photopea
  * `start, size` - file offset and the size (relative, from the end of JSON)

Here is a short PHP example, which accepts files from Photopea.

```
$fi = fopen("php://input", "rb");  $p = JSON_decode(fread($fi, 2000));
// getting file name from "source"
$fname = substr ($p->source, strrpos($p->source,"/")+1);  
$fo = fopen("img/".$fname,"wb");  while($buf=fread($fi,50000)) fwrite($fo,$buf);
fclose($fi);  fclose($fo);
```

<!--<pre>$p = json_decode( $_POST["p"] );	// parse JSON
  // getting file name from "source";
  $fname = substr ($p->source, strrpos($p->source,"/")+1);	
  file_put_contents("images/".$fname, base64_decode( $p->versions[0]->data ));</pre>-->

### Your Response

After the server receives a file, it can send back a JSON response with optional String parameters:

* `message` - when specified, will be displayed to the user for a moment
* `script` - when specified, will be executed (e.g. you can call `app.echoToOE("saved");`)
* `newSource` - when specified, will be used as a new value of "source" for saving to a server in the future (can be useful, when a file was created within Photopea: "source" was "local,...")

## Cross-Origin Resource Sharing

For security reasons, webapps can access only files from the same domain. In order to let Photopea load your file, the response of your server must contain the following header:

```
Access-Control-Allow-Origin: *
```

Find out more at [CORS specification](http://www.w3.org/TR/cors/) or at [enable-cors.org](http://enable-cors.org/).

## Prices

Usage of Photopea API is completely free. Keep in mind, that PP is in early stages of development and there may be critical bugs. We do not take any responsibility for documents edited or generated by Photopea.

If you want to hide advertisement and "colorful buttons", and use a **whitelabel mode**, look at [Distributor account](https://www.photopea.com/api/accounts#distributors).

# Environment

The look of the editor can be customized by the `environment` property of the JSON.

```
{
	...
	"environment" : {          
		"theme"     : 2,         "lang"     : "es",    
		"vmode"     : 0,         "intro"    : true,
		"eparams"   : { "guides" :true, "grid" : true, "gsize": 8,   
		                                "paths": true, "pgrid": true },
		"customIO"  : { "open": "app.echoToOE(\"Open\");", "exportAs":true },
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

Each parameter is optional. They have the following meaning:

* <!--
      				<li><code>fcolor</code> - foreground color</li>
      				<li><code>bcolor</code> - background color</li>
      				<li><code>rulers</code> - rulers enabled</li>-->
  `theme` - theme (0, 1, 2, ...)
* `lang` - language
* `vmode` - view mode. 0: regular, 1: panels are collapsed, 2: hide all panels
* `intro` - when no documents are open, show introduction panel (with buttons etc.)
* `eparams` - extras: enable or disable guides, grid, paths, pixel grid ...
* <!--<li><code>showbranding</code> - show / hide Log In, Social media links etc.</li>-->
  `customIO` - redefine the behavior of File - Open, Save etc. and run a custom script instead. Possible properties: `"new", "open", "openFromURL", "takePic", "showTemplates", "save", "saveAsPSD", "publishOnline", "exportLayers"`.\
  `"exportAs"`: if true, clicking "Save" in the "Save for Web" window will send the ArrayBuffer with a file to the OE. Use the first bytes of data to determine the format.
* `localsave` - enable / disable "Save as PSD", "Save for Web" and "Publish Online"
* `autosave` - with a value X, Photopea will execute "File - Save" each X seconds
* `showtools` - show only following tools (see tool IDs below)
* `menus` - specify the structure of File, Edit, Image ... menus with **0/1 flags**. Each element of an array is either 0: hide the item, 1: show the item with a standard content, or an array of flags for sub-items (works recursively). If your array is shorter than required, zeros will be added to the end. See the current menu structure of Photopea to find the right values. E.g. \[1,1] as the first element means, that the "File" menu will be shown with "New" and "Open" items only.
* <!--<li><code>showpanels</code> - allows you to hide elements on the right side.
      					There are two <b>columns</b>, which contain <b>panel blocks</b>, which contain one or more <b>panels</b>.
      					Each element of an array is either 0: hide the column, 1: show the column with all standard items, 
      					or an array of indices of panel blocks, that should be displayed.</li>-->
  `panels` - what panels should be shown in a sidebar. Use following IDs:\
  0: HISTORY, 1: SWATCHES, 2: LAYERS, 3: INFO, 4: HISTOGRAM, 5: PROPERTIES, 6: CSS, 7: BRUSH, 8: LAYERCOMPS, 9: CHARACTER, 10: PARAGRAPH, 11: ACTIONS, 12: NAVIGATOR, 13: COLOR, 14: TPRESET, 15: GUIDEGUY, 16: CHANNELS, 17: PATHS, 18: ADJUST, 19: GLYPHS, 20: MEMORY, 21: STYLE, 22: NOTES .
* `phrases` - allows you to replace any phrase inside Photopea with your own. The aray has the form `[ ID1, W1, ID2, W2, ... ]`, where IDx is the ID of some phrase and Wx is a new phrase, that should be used instead.\
  Some useful IDs: \[1,2]: Save (File menu), \[2,0]: Step Forward, \[2,1]: Step Backward. To discover IDs of other phrases, get familiar with [OpenWord table structure](https://github.com/photopea/OpenWord) and find your phrase in [a current phrase database](https://www.photopea.com/code/dbs/DBS.js) (var LNG ...), or just write us an email to support\@photopea.com.
* `topt` - tool options. Lets you change the settings of each tool. Keys are "tXY", where XY is the tool ID. Each tool has its own format (see below).
* `tmnu` - tool menu. Lets you specify the structure of the top menu for each tool. Keys are "tXY", where XY is the tool ID. Each tool has its own format (see below).
* `icons` - custom icons. Each icon has an icon ID (key) and the image URL (value). You can find icon IDs [here](//www.photopea.com/code/dbs/DBS.js) (var PIMG ...). E.g. the Crop Tool has an ID "tools/crop". On the introduction screen, the logo is "logo", the bottom part is "bottom".
* `plugins` - described [here](/api/plugins)

## Tool options and menus

### Move Tool

Options: `[1,0,null]`. Three values mean Auto-Select, Transformation controls and Distances. 1 means enabled, 0: disabled, null: not specified.

Menu: `[1,1,1,1,1,1]`. Six flags to show / hide six items: Auto-Select, Transformation controls, Distances, Quick Save (Get PNG...), Vertical Align, Horizontal Align.

### Magic Wand

Options: `[0,0,[16,true,true]]` - Combining operation, Feather, Select options: Tolerance, Anti-alias, Contiguous.

## Tool IDs

* 0: Move Tool
* 70: Artboard Tool
* 1: Rectangle Select
* 2: Ellipse Select
* 5: Lasso Select
* 6: Polygonal Lasso Select
* 7: Magnetic Lasso Select
* 9: Magic Wand
* 8: Quick Selection
* 3: Object Selection
* 10: Crop Tool
* 11: Perspective Crop
* 12: Slice Tool
* 13: Slice Select Tool
* 14: Eyedropper
* 15: Color Sampler
* 16: Ruler
* 18: Spot Healing Brush Tool
* 19: Healing Brush Tool
* 90: Magic Replace
* 20: Patch Tool
* 21: Content-Aware Move Tool
* 22: Red Eye Tool
* 23: Brush Tool
* 24: Pencil Tool
* 25: Color Replacement
* 27: Clone Tool
* 31: Eraser Tool
* 32: Background Eraser
* 33: Magic Eraser
* 34: Gradient Tool
* 35: Paint Bucket Tool
* 36: Blur Tool
* 37: Sharpen Tool
* 38: Smudge Tool
* 39: Dodge Tool
* 40: Burn Tool
* 41: Sponge Tool
* 47: Type Tool
* 48: Vertical Type Tool
* 42: Pen
* 43: Free Pen
* 44: Curvature Pen
* 45: Add Anchor Point
* 46: Delete Anchor Point
* 72: Convert Point
* 51: Path Select
* 52: Direct Select
* 54: Rectangle
* 55: Ellipse
* 57: Line
* 56: Parametric Shape
* 58: Custom Shape
* 59: Hand Tool
* 60: Rotate View
* 61: Zoom Tool

# Live Messaging

You can insert Photopea into a webpage (using a frame). Let's call such webpage the **Outer Environment (OE)**. OE can communicate with Photopea through [Web Messaging](http://web.archive.org/web/20150331203017/http://www.w3.org/TR/webmessaging/).

```
window.addEventListener("message", function(e) { alert(e.data); });
var wnd = document.getElementById("pp").contentWindow;
wnd.postMessage(msg, "*");
```

OE can send **two kinds of data** to Photopea:

* **String** - contains a script, which will be executed by Photopea
* **ArrayBuffer** - a binary file: psd, svg, jpg, ... fonts, brushes, ...

When Photopea is initialized and ready to accept commands, it sends the message `"done"`. After your message is processed, Photopea also sends back the message `"done"`.

Some demos of live messsaging in Photopea: [Demo 1](//www.vectorpea.com/pp_api_demo/demo1.html) [Demo 2](//www.vectorpea.com/pp_api_demo/demo2.html) [Demo 3](//www.vectorpea.com/pp_api_demo/demo3.html)

## Retrieving data from Photopea

Photopea can send the current image to OE using the following command (inside a script):

```
app.activeDocument.saveToOE("gif");
```

After you run the script above, PP will send a message with an ArrayBuffer of a GIF image, followed by a message with a String `"done"` (processing the script has finished).

It can also send any String to OE using the following command (inside a script):

```
app.echoToOE("Hello");
```

The full description at [/learn/scripts](https://www.photopea.com/learn/scripts).

## Examples of usage

This API can replace the main API. Instad of letting Photopea communicate with your server directly, you can load files inside your progrm and transfer them to and from Photopea in a clients device.<!--E.g. you can recreate the autosave feature (by calling <code>saveToOE()</code> in regular intervals).-->

You can use Photopea as a "module", hide its UI and use only the messaging. You can create a batch-processor of images (resizing images, adding watermarks, converting between formats). You can make scripts, that would export each layer of the document as a PNG. You can make scripts, that would replace the text in each text layer by data from your user (to create a generator of business cards, etc.).

## Example: Integrating with a custom storage

We can redefine the default behaviour of File - Open and File - Save.

* We can send Photopea any image in a message as ArrayBuffer
* We can call `app.activeDocument.saveToOE("psd");` to send the current file to OE.
* We can call `app.echoToOE("Hello");` to send any string to OE.
* We can read and write `app.activeDocument.source` String to identify files.
* We can set custom scripts to run after pressing Open or Save: [customIO : open, save](https://www.photopea.com/api/environment)

Now, we can do following:

* Set custom scripts to `app.echoToOE("Open" / "Save");` to be notified, when the user presses the buttons.
* When the user wants to Open a file, show him your own file input (you can even let the user draw something, or take a picture of him).
* Once you have the image (ArrayBuffer), send it to Photopea and set the source: `app.activeDocument.source="myID2353"`.
* When the user wants to Save a file, read the file (`app.activeDocument.saveToOE("psd");`) and its source `app.echoToOE(app.activeDocument.source);`, and save the new version into your storage.

# Plugins

Create Plugins for Photopea and provide them to your users through a configuration JSON.

```
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

* `name` - plugin name
* `url` - plugin URL
* `icon` - plugin icon (optional)
* `w, h` - plugin width, height (optional)

\*\*\* We strongly suggest not specifying "w" and "h", and make your plugin work at any size.

For each plugin, a button will be added to the right side, below the current buttons.

![](//i.imgur.com/8tPgmho.png)

After the user clicks the plugin button, the panel is opened with a website `url`.

Users can drag-and-drop images from your website to Photopea (as Photopea supports dropping images from any website, opened by a browser).

Your website can connect with Photopea using [Live Messaging](/api/live) (your website acts as the OE). It allows your plugin to execute scripts (e.g. to change foreground color, to move a layer, etc.).

The plugin can give files (send ArrayBuffers) to Photopea (images: psd, jpg, svg ... or resources: brushes, patterns, fonts ...), or request the current file in a specific format. All this can be controlled e.g. by buttons in your plugin (which is your website).

```
window.parent.postMessage("...script...", "*");
window.parent.postMessage(ArrayBuffer, "*");
```

## Publish your Plugins

You can save your plugin as a .JSON file and upload it into a public plugin gallery. Go to [Photopea.com](//www.photopea.com) and press Window - Plugins. Then, press "Add Plugin" at the top.

Changing your plugin or its icon in the future doesn't require going to Photopea.com, as long as the plugin and the icon remain at the same URL.

## Examples of usage

**Photo Store**. Let users browse your database of images. They can search the database by a keyword. You can add a button "Open" next to each image, which would open that image in Photopea.

**Font Gallery**. Let users browse your database of fonts. The font will be loaded after clicking the button. You can integrate a payment gateway into the plugin, too (as it is your website, you have full control over it).

You can make your plugin "commercial" - let users pay for them monthly. The sign-in and the payment interface could still be in the same "iframe" of your plugin, inside Photopea (or you could open a new window and then, come back to Photopea).

## Icon URL

To make an icon similar to Photopea icons, make the icon backgorund transparent, and the icon itself black. Also, add the "===" before the icon URL. Photopea will adapt the color of your icon to the current color theme (white for dark themes, dark for bright themes).

Photopea will display your icon as a multiple of 20x20 screen pixels (20x20, 40x40, 60x60, ...). So if you want sharp vertical stripes, make an icon e.g. 160x160 pixels, and a stripe 8 pixels wide. 9-pixel stripes would look blurry in such case.
