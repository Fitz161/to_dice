<div align="center">

# ToDice

基于[ OneBot ](https://github.com/howmanybots/onebot)标准以及[ go-cqhttp ](https://github.com/Mrs4s/go-cqhttp)开发的的QQ跑团娱乐机器人

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![OneBot Version](https://img.shields.io/badge/OneBot-v11-green)
![LICENSE](https://img.shields.io/github/license/Fitz161/to_dice?color=red)

</div>
</br>

## 安装使用
安装依赖的包 `pip insatll -r requirments.txt `
 
## 已实现功能
指令中[]为必需参数，()为可选参数

### 娱乐模块
* 签到功能  ` 签到 打卡  .dk`
* 今日人品  ` 运势  .jrrp`
* 抽卡功能  `单抽 十连 百连 [卡包编号]`
* 点歌功能  ` 点歌 /点歌 .点歌 网易云 [歌名]`    ` 已实现QQ音乐，网易云音乐点歌`
* 搜索功能  ` 百度 搜索[1-4] [关键词]`    ` 已实现百度百科，wekipedia，萌娘百科，touhouwiki搜索`
* 翻译功能  `翻译成 [语言] [文本] `
* 搜图功能  ` 搜图 [关键字]  取图[编号]`
* 热榜功能  ` 热榜`  ` 默认返回知乎热榜前九条` 
* 词云图生成  ` 词云图[模式] (字体类型) ([文本])`
* 网易云热评  ` 热评[条数](编号) [歌名]`

</br>

### 跑团模块
根据[ Dice ](https://github.com/Dice-Developer-Team/Dice)!2.4.1版本用户手册规定编写开发
</br>
.和。均可视为指令前缀符，指令不分大小写

#### 掷骰功能
* 掷骰指令  `.rhs3#d+3d20k2-p2*b3/2x3 `  `奖惩骰，暗骰，省略骰，多轮骰均开发完毕 `
* 旁观模式  `.ob (list exit clr on off)`
* 默认骰设置  `.set (默认骰子面数)`
* 随机昵称  `.name (cn/jp/en/enzh)(生成数量) `
* 设置昵称  `.nn [昵称] / .nn / .nnn (cn/jp/en/enzh) `
* 人物作成  ` .coc (生成数量)`
* 属性录入   ` .st (del/clr/show) .st[属性名](:)(运算符)[属性值/修正值]`  `支持通过四则运算符和修正值对属性直接修改 `
* 检定指令  ` .ra/rc ([检定轮数]#)[属性名] (运算符) ([成功率/修正值])`  `支持通过四则运算计算成功率`
* 设置默认房规  ` .setcoc (房规)`
* 日志记录  ` .log (new on off end)`  ` 日志记录完成后自动上传到服务器`
* 理智检定  ` .sc[成功损失]/[失败损失] ([当前san值])`

### 管理模块
* 发送消息  ` .send`
* Bot开关  ` .bot on .bot off`
* 退群指令  ` .dismiss .leave`

### 其他功能
* 帮助文档  ` .help [指令]`  ` 支持模糊匹配`
* 要礼物
* 冷知识
* 黑白名单
* 相量计算
* av BV转换
* 入群自动欢迎
* 每日自动备份数据
* 定时向指定群发送消息
