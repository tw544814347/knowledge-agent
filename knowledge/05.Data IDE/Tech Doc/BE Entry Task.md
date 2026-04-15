# BE Entry Task

> **Page ID**: 1337865469
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=1337865469

Entry Task

目的

时间

内容要求 功能

开发环境 设计要求

交付

验收标准 参考资料

目的

* 让团队更好地了解新人对技能的掌握情况
* 熟悉简单的Web API后台架构
* 熟悉使用Go/Java实现HTTP API(JSON、文件)
* 熟悉使用Go/Java实现基于TCP的RPC框架
* 熟悉基于Auth Token的鉴权机制和流程
* 熟悉使用Go/Java对MySQL、Redis进行基本操作
* 对任务进度和时间有所意识
* 对代码规范、测试、文档、性能调优需要有所意识

  时间

  ■ 有Go/Java经验的，5个工作日完成  
  ■ 无Go/Java经验的，7个工作日完成  
  ■ 入职第二天开始，期间需要参加培训课程，不影响最后期限

  内容要求  
  功能 实现一个用户管理系统，用户可以登录、拉取和编辑他们的profiles。

用户可以通过在Web页面输入username和password登录，backend系统负责校验用户身份。成功登录 后，页面需要展示用户的相关信息;否则页面展示相关错误。

成功登录后，用户可以编辑以下内容: 1. 上传profile picture

2. 修改nickname(需要支持Unicode字符集，utf-8编码) 用户信息包括:

1. username(不可更改)
2. nickname
3. profile picture

需要提前将初始用户数据插入数据库用于测试。确保测试数据库中包含10,000,000条用户账号信息。 开发环境

Server: 个人工作PC/Mac中的虚拟机

OS: CentOS 7 x64 or Ubuntu 14.04 above

DB: MySQL 5.5 or above

Client: Chrome and Firefox

注:如果对虚拟机不熟悉，可以直接在工作PC/Mac上开发;如果熟悉vagrant，可以直接使ubuntu-dev 。

设计要求

* 分别实现HTTP server和TCP server，主要的功能逻辑放在TCP server实现
* Backend鉴权逻辑需要在TCP server实现
* 用户账号信息必须存储在MySQL数据库。通过MySQL client连接数据库
* 使用基于Auth/Session Token的鉴权机制
* TCP server需要提供RPC，RPC机制希望自己设计实现
* HTTP server不允许直连MySQL。所有RPC请求只处理API和用户输入，具体的功能逻辑和数据

  库操作，需要通过RPC请求TCP server完成
* 尽可能使用Go/Java标准库
* 安全性
* 鲁棒性
* 性能

  交付

■ 源代码  
■ 设计文档  
■ 部署、运维文档 ■ 性能测试报告 ■ 总结文档  
■ 现场演示

代码必须上传到[git.garena.com](http://git.garena.com)。 文档尽可能使用Markdown和代码一起上传[git.garena.com](http://git.garena.com)，或者使用google docs。

验收标准 时间:

■ 尽可能在规定时间内完成  
■ 提前让mentor/team leader review代码

正确性:  
■ 必须完整实现相关API，不能有明显BUG

■ 实现细节必须满足设计要求，从而达到Entry Task的目的 安全性:

■ 不能有安全问题 鲁棒性:

* 服务不能因为客户端请求crash 性能:
* 数据库必须有10,000,000条用户账号信息
* 200并发(固定用户)情况下，HTTP API QPS大于3000
* 200并发(随机用户)情况下，HTTP API QPS大于1000
* 2000并发(固定用户)情况下，HTTP API QPS大于1500
* 2000并发(随机用户)情况下，HTTP API QPS大于800

  代码规范:

* 通过golint
* 通过go vet
* 尽可能遵循Effective Go
* 阿里Java规范
* 代码质量:

  ■ 易读  
  ■ 依赖清晰 ■ 尽量解耦

* 尽可能覆盖单元测试 文档:
* 交付的文档尽可能详细 其中，时间、正确性、安全性、性能是必须要达到要求的。其余几项在时间期限后，根据实际情况可以放

  宽要求。

  参考资料

* Go: <http://golang.org>
* Coding style: <https://github.com/golang/go/wiki/CodeReviewComments>
* Testing: <https://golang.org/pkg/testing/>
* Profiling: <http://blog.golang.org/profiling-go-programs>
* Go Web application example: <https://golang.org/doc/articles/wiki/>
* Go editor/IDE

  ■ <https://github.com/fatih/vim-go>  
  ■ <https://github.com/dominikh/go-mode.el>  
  ■ <https://github.com/DisposaBoy/GoSublime>  
  ■ <https://github.com/visualfc/liteide>  
  ■ <https://marketplace.visualstudio.com/items?itemName=lukehoban.Go>
* MySQL client: <https://github.com/go-sql-driver/mysql>
* Redis: <http://redis.io>
* Redis Client: <https://github.com/go-redis/redis>
* <https://blog.csdn.net/weixin_70730532/article/details/125201463>（参考阿里巴巴Java开发手册）
