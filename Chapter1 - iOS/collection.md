

# APM

内存泄露检测
各家都是基于 Facebook 的 FBRetainCycleDetector 实现，有：
腾讯 MLeaksFinder
https://github.com/Tencent/MLeaksFinder
PLeakSniffer
https://github.com/music4kid/PLeakSniffer
LeaksMonitor
https://github.com/tripleCC/Laboratory/tree/master/LeaksMonitor

ANR 检测
ANR 检测相对比较简单，各家原理基本相同。新建一个 thread 在 threshold 的间隔时间内（一般 200 - 400毫秒）循环等待一个 semaphore，并从主线程 async dispatch  semaphore 的 signal 函数，如果超时则报卡顿。
1. https://gist.github.com/leilee/3275b94c381114332242978fc4366591
2. https://gist.github.com/Adlai-Holler/ea7e3e98333b3b84f13d19b169ccf989
1. https://gist.github.com/mikeash/5172803 这个是纯 GCD 的实现
2. https://gist.github.com/steipete/5664345  PFPDFKit 里用的是这个
3. https://gist.github.com/jspahrsummers/419266f5231832602bec GitHub 客户端里用的
4. https://github.com/wojteklu/Watchdog 这个有用 atomic_store 和 atomic_load 实现死锁回调
5. DoKit
8. https://github.com/ming1016/study/wiki/检测iOS的APP性能的一些方法
启动优化
《Reducing Your App's Launch Time》- Apple
https://developer.apple.com/documentation/xcode/improving_your_app_s_performance/reducing_your_app_s_launch_time
《抖音研发实践：基于二进制文件重排的解决方案 APP启动速度提升超15%》
https://mp.weixin.qq.com/s?__biz=MzI1MzYzMjE0MQ==&mid=2247485101&idx=1&sn=abbbb6da1aba37a04047fc210363bcc9&scene=21#wechat_redirect
// 这种纬度的启动时间优化对小公司来说 ROI 太低 
《美团外卖 iOS App 冷启动治理》
https://tech.meituan.com/2018/12/06/waimai-ios-optimizing-startup.html

测量进程的 uptime
https://github.com/tripleCC/Laboratory/blob/master/ProcessStartTime/ProcessStartTime/main.m
https://stackoverflow.com/questions/40649964/ios-get-self-process-start-time-after-the-fact/40677286

滴滴出行 DoraemonKit
https://github.com/didi/DoraemonKit
功能非常多，感觉侧重了 UI 的运行时调试。APM 的部分主要依赖第三方库，如 MLeakFinder。有提供问题上报机制，所以会有不少额外的网络请求发送到 dokit 的API。

腾讯 Matrix
https://github.com/tencent/matrix
功能精简，只有 ANR 和内存检测。

美图秀秀 MTHawkeye
https://github.com/meitu/MTHawkeye/tree/develop/MTHawkeye
监控项目比 DoKit 多，ANR 中能看到主线程堆栈信息，网络层有做一些基本优化指标的监控。

阿里巴巴 GodEye
https://github.com/zixun/GodEye
项目已经三年没有维护，不过作者的小专栏有提供整体思路，值得参考学习。https://xiaozhuanlan.com/godeye





# 技术博客

AloneMonkey http://www.alonemonkey.com/ https://github.com/AloneMonkey #ios #re
yulingtianxia https://yulingtianxia.com/ https://github.com/yulingtianxia #ios #ml
SatanWoo http://satanwoo.github.io/ https://github.com/SatanWoo #ios #ml
Naville Zhang https://mayuyu.io/ https://github.com/Naville #ios #re #llvm
Cocoa Oikawa https://blog.0xbbc.com/ https://github.com/BlueCocoa #ios
jmpews https://jmpews.github.io https://github.com/jmpews #ios #re
kov4l3nko https://kov4l3nko.github.io https://github.com/kov4l3nko #ios
mikeash https://www.mikeash.com/pyblog/ #ios
NSBLOGGING https://kandelvijaya.com/post/ #ios
4ch12dy http://4ch12dy.site/ https://github.com/4ch12dy
ibireme https://blog.ibireme.com/ https://github.com/ibireme/ #ios
bang http://blog.cnbang.net/ https://github.com/bang590 #ios
everettjf https://everettjf.github.io/ https://github.com/everettjf #ios #re
Gityuan http://gityuan.com/ #android #flutter
Meituan https://tech.meituan.com/ #ios #android #company
draveness https://draveness.me/ #ios #golang
chy305chy https://chy305chy.github.io/ #ios
Urinx https://urinx.github.io/v6/ https://github.com/Urinx #ios #re
bdunagan http://bdunagan.com/ #ios
la0s https://la0s.github.io/ #re #ios
caijinglong https://www.kikt.top/ #flutter
weishu http://weishu.me/ https://github.com/tiann #android #re
zixia https://github.com/huan #ml #re
xelz https://github.com/xelzmm http://xelz.info/ #re
ChiChou https://github.com/ChiChou https://blog.chichou.me/ #re



# 学习

# 资料
* 经典WWDC视频
        [WWDC2016:Optimizing App Startup Time](https://developer.apple.com/videos/play/wwdc2016/406)
        [WWDC2016:Optimizing I/O for Performance and Battery Life](https://developer.apple.com/videos/play/wwdc2016/719/)
        [WWDC2017:App Startup Time: Past, Present, and Future](https://developer.apple.com/videos/play/wwdc2017/413/)
* 图片的加载过程
        [Core Image: Performance, Prototyping, and Python](https://developer.apple.com/videos/play/wwdc2018/719/)
* Facebook的二进制优化，开拓思路
        [通过优化二进制布局提升iOS启动性能](https://www.bilibili.com/video/BV1NJ411w7hv) 


# 文章
[如何对 iOS 启动阶段耗时进行分析](https://ming1016.github.io/2019/12/07/how-to-analyze-startup-time-cost-in-ios/)
[objc_msgSend Hook 精简学习过程](https://linux.ctolib.com/czqasngit-objc_msgSend_hook.html)
[如何对 iOS 启动阶段耗时进行分析](http://www.starming.com/2019/12/07/how-to-analyze-startup-time-cost-in-ios/)
[App 启动速度怎么做优化与监控？](https://time.geekbang.org/column/article/85331)
[监控所有的OC方法耗时](https://juejin.im/post/5d146490f265da1bc37f2065)
[Hook objc_msgSend to hotfix](https://www.dazhuanlan.com/2019/10/18/5da8a4b2a7da7/)

[iOS App启动优化（一）—— 了解App的启动流程](https://juejin.im/post/5da830a4e51d457805049817)
[iOS App启动优化（二）—— 使用“Time Profiler”工具监控App的启动耗时](https://juejin.im/post/5dad6bfb6fb9a04de818fcb8)
[iOS App启动优化（三）—— 自己做一个工具监控App的启动耗时](https://juejin.im/post/5de501e0e51d4540a15879ff)


* facebook的启动优化（2015年的老文章）
[Optimizing Facebook for iOS start time](https://engineering.fb.com/ios/optimizing-facebook-for-ios-start-time/)

[优化 App 的启动时间](http://yulingtianxia.com/blog/2016/10/30/Optimizing-App-Startup-Time/#%E5%AE%89%E5%85%A8)
[深入理解App的启动过程](https://github.com/LeoMobileDeveloper/Blogs/blob/master/iOS/What%20happened%20at%20startup%20time.md)
[iOS启动速度优化](https://github.com/BiBoyang/BoyangBlog/blob/master/File/iOS_APM_03.md)
[iOS app启动速度研究实践](https://zhuanlan.zhihu.com/p/38183046?from=1086193010&wm=3333_2001&weiboauthoruid=1690182120)
[iOS Dynamic Framework 对App启动时间影响实测](https://www.jianshu.com/p/3263009e9228)
[iOS App 启动性能优化](https://mp.weixin.qq.com/s/Kf3EbDIUuf0aWVT-UCEmbA)
[今日头条iOS客户端启动速度优化](https://juejin.im/entry/5b6061bef265da0f574dfd21)
[如何精确度量 iOS App 的启动时间](https://www.jianshu.com/p/c14987eee107)
[ iOS App冷启动治理：来自美团外卖的实践 ](https://mp.weixin.qq.com/s/jN3jaNrvXczZoYIRCWZs7w)