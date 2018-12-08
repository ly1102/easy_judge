
# easy_judge
用爬虫和网站技术大大简化了对网站的操作，实现了兼容新浏览器，直接查看图片等功能



# 简介
因为老版的德育审批网站已经很难适应现在这么复杂的需求

但是去找教务处、学生处更新网站又太费周章

所以决定直接给辅导员需要用的核心功能进行一次升级

每年一个辅导员要审批接近1000份的活动申请，这是一个让人非常痛苦的事情


## 原网站
- 无法在一个页面上完成审批(需要进入二级页面查看具体申请内容)
- 如果申请的分数需要更改，必须点击保存，页面刷新了再点通过才能生效
- 无论打回、保存、通过申请，页面都会刷新，并且在点击了alert弹窗内容才会显示网页正文
- 查看申请照片，点击后会在新网页打开图片，图片各种角度都有，无法放缩，看起来脖子非常痛苦
- 返回申请列表页面，会直接回到第一页，无法记住之前的过滤条件


## 改造后的网站
- 登录后通过多线程立即下载最新的申请到本地
- 所有的操作在一个页面完成，把不重要的信息通过鼠标滑过显示来降低影响
- 德育分、智育分的通过字体粗细、颜色来区分
- 更改分数、直接通过、打回等操作，页面都不会刷新，通过异步操作完成
- 图片直接显示，点击就在当前页面放大，支持放大缩小左右旋转，切换上下图片
- 一键通过或打回
- 导出审批内容到excel表格，方便让同学查看申请被打回的原因
- 多账号登录，学生申请不会串到一起，只会显示自己账号的

简书地址：
https://www.jianshu.com/p/f6708e8431e9

效果展示：

![审批主界面展示](https://github.com/ly1102/easy_judge/blob/master/teacher_manage/image/example_pic/apply_list.png)

![申请材料图片在当前页面放大缩小翻转都支持](https://github.com/ly1102/easy_judge/tree/master/teacher_manage/image/example_pic)


