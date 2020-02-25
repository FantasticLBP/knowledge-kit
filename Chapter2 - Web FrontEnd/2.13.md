# webpack-dev-server 的配置和使用



> webpack-dev-server是一个小型的`Node.js Express`服务器,它使用`webpack-dev-middleware`来服务于webpack的包,除此自外，它还有一个通过[Sock.js](http://sockjs.org/)来连接到服务器的微型运行时.
>
> 说人话就是可以极大的提高开发效率。这么好的东西那就用起来





1、看看 webpack.config.js 

```
module.exports = {
    target:"web",   //编译平台 web
    entry:path.join(__dirname,"src/index.js"),     //应用程序的主入口
    output:{
        filename:"bundle.js",       //输出文件名
        path: path.join(__dirname, "dist")
    },
    module:{
        rules:[
            {
                test:/\.vue$/,
                loader:"vue-loader"
            },
            {
                test:/\.css$/,
                use:[
                    "style-loader",
                    "css-loader"
                ]
            },
            {
                test:/\.(gif|jpg|jpeg|png|svg)$/,
                use:[
                    {
                        loader:"url-loader",
                        options:{
                            limit:1024,
                            name:'[name]-lbp.[ext]' //甚至可以加一些名字处理规则 '[name]-lbp.[ext]'
                        }
                    }
                ]
            }
        ]
    },
    /*
    在 plugins 中写 webpack.DefinePlugin 是为了在 webpack 打包的时候选择源代码的版本。当在 dev 的时候会打包开发所需要的所有东西，比如警告信息
    */
    plugins:[
         new webpack.DefinePlugin({
             'process.env':{
                 NODE_ENV: isDev ? '"development"' : '"production"'
             }
         }),
        new HTMLPlugin()
    ]
}
```



配置文件提供1个入口和一个出口，webpack 根据这个文件来执行 js 的打包和编译。webpack-dev-server 其中的部分功能就克服了上面2个问题。 webpack-dev-server 主要启动了1个使用 express 的 HTTP 服务器（资源文件）。由于这个 HTTP 服务器和 client 使用了 websocket 通讯协议，原始文件作出了改动，webpack-dev-server 会实时编译，但是最后编译的文件并没有输出到目标文件夹

## 一些截图



![](/assets/todo-20180226-1.png)



![](/assets/todo-20180226-2.png)



![](/assets/todo-20180226-3.png)





![](/assets/todo-20180226-4.png)



![](/assets/todo-20180226-5.png)



完整的 webpack.config.js

```
const path = require("path");
const HTMLPlugin = require("html-webpack-plugin")
const webpack = require("webpack")


//process.env 是读取系统环境。比如在启动服务的时候会通过 npm run build/dev 运行，其真实入口是在 webpack.config.js ，然后我们在 webpack.config.js设置为 production 或 development。那么就可以通过 process.env.NODE_ENV 获取
const isDev = process.env.NODE_ENV === 'developement'



//webpack 会将文件打包为 bundle.js
//需要为 .vue 文件声明一个类型， 因为 webpack 只识别 .js 且支持的语法为 ES5
//增加一个 module 模块，一个键为 rules ，值可以是多个数组。检测文件以 .vue 结尾的话就以 vue-loader 解析
//vue-loader 为 webpack 解析 .vue



/*
查看 dist 文件夹下的 bundle.js 文件
最顶部都是 webpack 处理包的代码
其次是 vue 代码 
webpack 做的事情就是将不同类型的静态资源打包成 JS，然后在 HTML 中引入 JS 就可以减小 HTTP 请求。
以 css 结尾的文件使用 css-loader。
css-loader:从css文件中将内容读了出来。
style-loader：判断将css代码插入到html还是写到一个新的文件中

在写图片的读取规则的时候，用到了use，use数组里面是一个个对象，loader 可以配置一些选项
url-loader 可以将图片转换为 base64 字符串直接写到 JS 内容里面而不用生成一个图片，这对于一些小的图片是比较有利的，这样子可以减小 http 请求。
url-loader 封装了 file-loader：读取了文件内容并做一些简单操作，再把图片换个名称存在一个地方
            limit选项：如果图片小于1024就可以转义成 base64
            name选项： 可以处理图片的名字

配置完之后则需要安装相应的模块，npm install 


配置环境变量：
1、MAC 平台：NODE_ENV=production
2、Window 平台 SET NODE_ENV=production
3、为了配置开发环境和正式环境，需要安装： cross-env包。需要修改package.json 文件中的 scripts-> build 和 dev


*/
const config = {
    target:"web",   //编译平台 web
    entry:path.join(__dirname,"src/index.js"),     //应用程序的主入口
    output:{
        filename:"bundle.js",       //输出文件名
        path: path.join(__dirname, "dist")
    },
    module:{
        rules:[
            {
                test:/\.vue$/,
                loader:"vue-loader"
            },
            {
                test:/\.css$/,
                use:[
                    "style-loader",
                    "css-loader"
                ]
            },
            {
                test:/\.(gif|jpg|jpeg|png|svg)$/,
                use:[
                    {
                        loader:"url-loader",
                        options:{
                            limit:1024,
                            name:'[name]-lbp.[ext]' //甚至可以加一些名字处理规则 '[name]-lbp.[ext]'
                        }
                    }
                ]
            }
        ]
    },
    /*
    在 plugins 中写 webpack.DefinePlugin 是为了在 webpack 打包的时候选择源代码的版本。当在 dev 的时候会打包开发所需要的所有东西，比如警告信息
    */
    plugins:[
         new webpack.DefinePlugin({
             'process.env':{
                 NODE_ENV: isDev ? '"development"' : '"production"'
             }
         }),
        new HTMLPlugin()
    ]
}


//为了判断是开发环境还是生成环境，判断了  isDEV
/*
webpack 2.0 以后增加了 devSever。用来处理开发环境的配置
0.0.0.0:可以通过 localhost 和本地电脑 ip 访问项目
overlay：在 webpack 编译的时候如果有错误显示在网页上。errors:true 
*/
if (isDev) {
    config.devtool = "#cheap-module-eval-source-map"
    config.devServer = {
        port:8000,
        host:'0.0.0.0',
        overlay:{
            errors:true
        },
        hot:true
    }
    config.plugins.push(
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoEmitOnErrorsPlugin()
    )
}

module.exports = config 
```













