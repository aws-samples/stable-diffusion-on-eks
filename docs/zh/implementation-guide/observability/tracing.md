# 查看跟踪

您可以从X-Ray中查看个别请求在每个阶段的耗时，实现链路跟踪。

## 服务总览图

=== "AWS 管理控制台"
    * 打开 [Amazon CloudWatch 控制台](https://console.aws.amazon.com/cloudwatch/)。
    * 在左侧导航窗格中，选择 **X-Ray traces** - **Service map**。
    * 在服务图中会列出该解决方案的相关组件，您可以点击某个组件以显示该组件的指标（含延迟，请求数和错误数）

## 查看请求详细信息

    * 在左侧导航窗格中，选择 **X-Ray traces** - **Traces**。
    * 在下方的**Traces**中，会列出每条请求的详细信息，选择个别请求可以显示在每个步骤的详细用时。