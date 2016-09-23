# IXIA-test-automation
IXIA自动化跑流量
设计思路：
1、自动化执行逻辑，根据官方文档：tclsh vw_auto.tcl –f test1.tcl执行。
2、IXIA环境需要tcl8.4和python2.4.3可以安装进去作为环境使用，但不是作为平台框架的运行环境。
3、平台框架使用python2.7.8库比较多，使用PYQT4作为用户交互GUI部分与python开发框架主体。
4、框架设计思路：队列+线程控制用例的执行顺序。用例使用tcl格式方便IXIA调用。使用tk包调用tcl进行解析tcl文件。用例组织的用例树则使用elementtree解析xml+QTreeWget组合。run执行线程的队列元素为每个Case的关键信息，可根据关键信息查找到指定的用例。
5、配置主要分为：DUT配置：使用http拓展包requests配置，也可使用selenium进行WEB配置。IXIA配置：使用内部提供的tcl脚本配置，用WaveAPP配置完后生成的WML文件使用内置工具转化为tcl即可。Linux Server DUT的WAN口服务器配置，使用SSH进行配置。外设仪器配置：使用serial拓展包用串口进行配置。
外设仪器主要有：可调衰减仪、天线角度自动转盘。

备注：
本文仅提供一个设计思路与部分代码。

实际开发中需要对IXIA仪器的执行过程有一定了解，并修改几个厂家接口的配置tcl文件。
