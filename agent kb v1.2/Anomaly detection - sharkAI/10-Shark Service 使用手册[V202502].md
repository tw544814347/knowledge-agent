---
topic: shark-service-user-manual-v202502
relevance: core
language: zh
source: https://confluence.shopee.io/pages/viewpage.action?pageId=2619933046
last_reviewed: 2026-04-16
---

# Shark Service 使用手册 [V202502]

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2619933046

## 1.首页

首页按照业务的一二级展示，用户点击相应图标即可进入对应业务的告警列。如Credit-SPL，即为一级业务为Credit，二级业务为SPL。**如需添加新的业务，请联系我们**

![image2026-1-9_17-1-1.png](https://confluence.shopee.io/download/attachments/2619933046/image2026-1-9_17-1-1.png)

[shark service home page](https://portal.fp-data.test.shopee.io/sharkService/home)

## 2.列表页

用户首次通过首页进入列表页面

![image2026-1-6_17-50-28.png](https://confluence.shopee.io/download/attachments/2619933046/image2026-1-6_17-50-28.png)

### 2.1）Create页

| Name | Description | Remark |
| --- | --- | --- |
| Region | 地区名 |  |
| Business Folder | 业务一二级 |  |
| Rule Name | 告警的名字，每个告警数据源下保持唯一 |  |
| MetricStore ID | 告警数据源ID，公司监控平台的数据源（注意不要混淆metric store name和metric store id） |  |
| Monitor Metric | 监控指标，普罗米修斯的SQL（暂不支持带变量的SQL语句；暂不支持过多维度，只支持单维度且基数不超过10） |  |
| Tag | 标签 |  |

### 2.2）Preview页

- Edit按钮：修改配置
- Next按钮：进入preview预览页面，展示设定时间范围内原始数据的时序图和维度配置信息

### 2.3）Release页

#### 2.3.1）Anomaly Detection

异常特征配置选项：

| Name | Description | Remark |
| --- | --- | --- |
| TimeRange | 图表展示时间 |  |
| Rule Type | Thresholds（原始时序+预测上下限）或 Original（仅原始数据） |  |
| Rule condition | Rising（高于上限告警）和/或 Falling（低于下限告警） |  |
| Alert After (Minutes) | 告警连续触发大于此时间才触发告警 |  |
| Threshold Range | 模型系数factor（0-2），调整上下限宽度。默认值=1 |  |
| Anomaly Features | 异常检测特征，如Steep Drop（陡降特征） |  |

#### Anomaly List

连续period周期内超过上下限的点，标为异常红点，展示Time、Alert After、Threshold Range、Upper、Lower、Value等信息

#### Metrics And Alerts

- False Alarm Rate: 误报率
- False Omission Rate: 漏报率

## 3.用户案例分析

**案例一：通过调整Alert After来减少误告**  
数据量激增导致预测值偏高时，增大Alert After可以避免短暂波动触发告警

**案例二：通过调整Threshold Range来减少误告**  
增大Threshold Range（如1→1.5）可以扩大上下限范围

**案例三：通过勾选Steep Drop来减少误告**  
勾选Steep Drop后，不符合陡降特征的点都不会告警

## 参考

- shark测试环境：https://portal.fp-data.test.shopee.io/sharkService/home
- shark正式环境：https://portal.fp-data.shopee.io/sharkService/home
- 公司监控平台：https://space.shopee.io/observability/monitoring/platform/metric-stores
