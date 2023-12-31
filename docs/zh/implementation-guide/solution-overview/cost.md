# 费用预估

!!! Important "重要"

    本节中描述的成本估算只是示例，可能会因您的环境而异。


您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。影响解决方案成本的主要因素包括：

- 选择的实例类型和购买方式
- 生成的图片量
- 弹性伸缩配置

以512x512, steps=16，文生图任务为例，使用美国东部（弗吉尼亚北部）AWS 区域的g5.xlarge实例，单张图像平均生成速度约为1.5s/张。根据[亚马逊云科技官方页面](https://aws.amazon.com/cn/ec2/instance-types/g5/) 按需计价模式下费用为1.006USD/h, 平均每千张图推理计算成本为0.42 USD.如果选择1 年期 ISP（0.604 USD/h），平均每千张图推理计算成本为0.25 USD.如果选择3 年期 ISP （0.402 USD/h），平均每千张图推理计算成本可低至0.17 USD。

此外，方案其他运行成本还包括存储成本，无服务器服务按需运行成本，以及网络数据流量成本。具体价格计算公式可参考[价格计算器](https://docs.aws.amazon.com/zh_cn/pricing-calculator/latest/userguide/getting-started.html)。
