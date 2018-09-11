# H5页面保存页面为图片

方案：有个github的js库可以将html转换为canvas，然后canvas可以转换为图片，然后图片可以下载，所以基本路线就是：

* html2canvas.js ：将htmldom转为canvas （[https://github.com/niklasvh/html2canvas](https://github.com/niklasvh/html2canvas "html2canvas")）
* canvasAPI： toDataUrl\(\)将canvas转为base64格式
* 图片下载

具体描述：https://juejin.im/post/5a17c5e26fb9a04527254689

