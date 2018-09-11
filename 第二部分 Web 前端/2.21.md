# Canvas

## 支持性

由于浏览器对 Canvas 的支持标准不一致，所以通常 &lt;canvas&gt; 内部添加一些说明行的 HTML 代码，如果浏览器支持 Canvas，它将忽略 &lt;canvas&gt; 内部的 HTML，如果浏览器不支持 Canvas，它将显示 &lt;canvas&gt; 内部的HTML。

## 一、基础使用

使用 Canvas 前，用 canvas.getContext 来判断浏览器是否支持 Canvas

```
var canvas = document.getElementById("test-canvas");
if (canvas.getContext) {
    console.log("你的浏览器支持canvas");
} else {
    console.log("你的浏览器不支持canvas");
}
```

getContext\('2d'\) 方法拿到一个 CanvasRenderingContext2D 对象，所有的绘图操作都需要通过这个对象完成。

```
var ctx = canvas.getContext("2d");
```

如果需要绘制 3D图形，我们可以通过

```
var gl = canvas.getContext("webgl");
```

### 1、绘制形状

```
var ctx = canvas.getContext("2d");
ctx.fillStyle = "rgb(200,0,0)";
ctx.fillRect(10,10,50,50);

ctx.fillStyle = "rgba(0,0,200,0.5)";
ctx.fillRect(30,30,50,50);
```

![](/assets/canvas - 绘制图形1.png)

* #### 绘制矩形

不同于 SVG，Canvas 只提供了一种原生的图形绘制能力：矩形。 所有的其他图形的绘制都至少需要生成一条路径。

1. 绘制一个填充矩形 fillRect\(x,y,width,height\)
2. 绘制一个矩形的边框 strokeRect\(x,y,width,height\)
3. 清除矩形的指定区域 clearRect\(x,y,width,height\)

```
ctx.fillRect(20,20,160,160);
ctx.clearRect(30,30,140,140);
ctx.strokeRect(80,80,40,40);
```

![](/assets/canvas - 绘制图形2.png)

#### 2、绘制路径

图形的基本元素是路径，路径是通过不同颜色和宽度的线段或曲线相连形成的不同形状点的集合。一个路径，甚至一个子路径，都是闭合的。使用路径绘制图形需要一些额外的步骤。

* 首先你需要创建路径的起始点
* 然后使用画图命令去画出路径
* 之后把路径封闭
* 一旦路径生成，你就可以通过秒变或者填充路径区域来渲染图形了。

beginPath\(\)：新建一条路径，生成之后，图形绘制命令被只想到路径上生成路径。

closePath\(\):闭合路径之后图形绘制命令又重新指向到上下文中。

stroke\(\):通过线条来绘制图形轮廓。给图形描边。

fill\(\): 通过填充路径的内容区域生成实心的图形。

```
var ctx = canvas.getContext("2d");
ctx.beginPath();
ctx.moveTo(75,50);
ctx.lineTo(100,75);
ctx.lineTo(100,25);
ctx.fillStyle = "red";
ctx.fill();
```

























