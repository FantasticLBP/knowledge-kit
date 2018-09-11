## Promise

## 一、基础使用

举个例子：

```
//方式一
function test(resolve, reject) {
    var timeout = Math.random() * 2;
    console.log("开始尝试promise");
    setTimeout(function() {
        if (timeout < 1) {
            resolve(timeout);
        } else {
            reject(timeout);
        }
    }, 1000);
}

function resolve(time) {
    console.log("小于1的数字" + time);
}

function reject(time) {
    console.log("不小于1的数字" + time);
}
var p1 = new Promise(test);
var p2 = p1.then(function(result) {
    console.log("成功" + result);
});
var p3 = p1.catch(function(reason) {
    console.log("失败" + reason);
});

// 方式二
new Promise(test).then(function(result) {
    console.log("成功" + result);
}).catch(function(reason) {
    console.log("失败" + reason);
});


//方式三
<div id="test-promise-log">

</div>


var logging = document.getElementById("test-promise-log");
while (logging.children.length > 1) {
    logging.removeChild(logging.children[logging.children.length - 1]);
}

function log(s) {
    var p = document.createElement("p");
    p.innerHTML = s;
    logging.appendChild(p);
}


new Promise(function(resolve, reject) {
    log("start new Promise...");
    var timeout = Math.random() * 2;
    log('set timeout to: ' + timeout + 'seconds.');
    setTimeout(function() {
        if (timeout < 1) {
            log('call resolve()...');
            resolve('200 OK');
        } else {
            log('call reject()...');
            reject('timeout in ' + timeout + 'sconds.');
        }
    }, timeout * 1000);

}).then(function(result) {
    log('Done: ' + result);
}).catch(function(reason) {
    log("Failed: " + reason);
});


------------

start new Promise...

set timeout to: 1.6579586637257697seconds.

call reject()...

Failed: timeout in 1.6579586637257697sconds.
```

可见 Promise 的最大好处就是在异步执行的流程中，将执行代码和处理结果的代码清晰地分离了。

## 二、串行执行

比如有若干个异步任务，需要先做任务1，如果任务1成功后执行任务2...，任何一个环节中的任务失败则不再继续执行错误处理函数。

要完成这个需求，传统写法需要一层一层的嵌套代码有了 Promise ，就可以

```
task1.then(task2).then(task3).catch(erroeHandler);
```

举个例子

```
function add(num) {
    return new Promise(function(resolve, reject) {
        log(num + " + " + num + "...");
        setTimeout(resolve, 500, num + num);
    });
}

function mul(num) {
    return new Promise(function(resolve, reject) {
        log(num + " x " + num + "...");
        setTimeout(resolve, 500, num * num);
    });
}

new Promise(function(resolve, reject) {
    resolve(100);
}).then(add).then(mul).then(add).then(mul).then(function(result) {
    log("the result is " + result);
});


---------------------
100 + 100...

200 x 200...

40000 + 40000...

80000 x 80000...

the result is 6400000000
```

## 三、并行执行

```
    var p1 = new Promise(function(resolve, reject) {
        setTimeout(resolve, 500, "p1 success");
    });

    var p2 = new Promise(function(resolve, reject) {
        setTimeout(resolve, 500, "p2 success");
    });
    Promise.all([p1, p2]).then(function(results) {
        console.log(results)
    });
```

多个 任务需要同时进行也就是并行执行，那么就可以使用 Promise.all\(\) 实现



## 四、容错处理，只需要拿到先返回的结果。

```
var p1 = new Promise(function(resolve, reject) {
    setTimeout(resolve, 500, "p1 success");
});

var p2 = new Promise(function(resolve, reject) {
    setTimeout(resolve, 500, "p2 success");
});


//使用第一个返回的结果
Promise.race([p1, p2]).then(function(result) {
    console.log("结果是： " + result);
});
```



