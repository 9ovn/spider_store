# 微博评论爬虫  
该爬虫主要用来爬取指定微博的全部评论
## 1、cookies池
目前cookies正在重新编写
## 2、ip池
使用ip抓取脚本自行抓取
## 3、关于url的问题
以 https://weibo.cn/comment/hot/`Hx1gulh4A`?rl=1&`oid=4378696905070520`&page=1 为例<br>`Hx1gulh4A`: 是用户的uid，在网页端打开你想要抓取的评论如 https://weibo.com/6180213612/IcXPQzdtu 跟在数字后面的一串字母就是你需要的。<br>`oid`:这个则是微博的mid，在上一步的的url中寻找类似hroot_comment_id=4430900089883346这样的字符串然后将数字取出来。两个拼接在一起这样我们就得到 <br>https://weibo.com/6180213612/IcXPQzdtu?filter=hot&root_comment_id=4430900089883346&type=comment<br>在weibo.cn上的链接https://weibo.cn/comment/hot/IcXPQzdtu?rl=1&`oid=4430900089883346&page=1
