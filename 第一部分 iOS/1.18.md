* 对于不能调节高度的控件比如 UISlider、UISwitch、UIProgressView 等控件的宽高可以用 \(仿射变化\)transform 属性控制高度。

```
myswitch.transform = CGAffineTransformMakeScale(1,5);
```



