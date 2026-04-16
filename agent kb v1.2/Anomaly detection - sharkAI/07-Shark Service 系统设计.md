---
topic: shark-service-system-design
relevance: core
language: zh
source: https://confluence.shopee.io/pages/viewpage.action?pageId=2485750769
last_reviewed: 2026-04-16
---

# Shark Service 系统设计

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2485750769

### 一、背景

目前公司内部监控平台每天都会产生基于规则的告警，由于业务是变化的，所以部分规则可能会随着业务的变化没有更好的适配。我们基于业务历史数据，使用算法预测未来业务数据的走向，业务可以比较当前值与预测值判断是否告警。

使用的数据模式：连续产生的，并且不会断流的数据。

### 二、架构

shark service交互的数据方有，业务上报的metricstore，对接算法模型。

* 业务上报的metricstore：获取业务的数据，并把预测数据推回到原来的数据源
* 算法模型：使用的业务历史数据，对接算法，获取业务的预测数据
* meta manager：管理用户配置的基本数据，数据回放，数据回补等元数据
* quartz scheduler：分布式任务调度器

![image2024-9-13_18-1-48.png](https://confluence.shopee.io/download/attachments/2366363749/image2024-9-13_18-1-48.png)

test aimos: https://aimos.fp-data.test.shopee.io/shark/anomaly/detect  
live aimos: https://aimos.fp-data.shopee.io/shark/anomaly/detect

### 三、元数据管理

1. quartz scheduler：quartz调度器的默认mysql表
2. 业务配置的监控任务的元数据：

库表：shopee_smd_shark_ai_db.shark_service_meta_param_tab

| 字段 | 描述 | 默认值 | 是否必填 | 例子 |
| --- | --- | --- | --- | --- |
| metricstore_name | 监控平台metricstore id |  | required，主键 | monitor-biz-data-latency-id |
| promql_name | 检测任务的逻辑名称 |  | required，主键 | monitor_less_cnt_by_5m |
| promql | promQL |  | required | sum(...) by (region,topic_name) |
| start_interval | 开始时间与当前时间间隔，单位小时 | 24 |  |  |
| cron | 任务执行的周期 | 0 0/1 * * * ? |  |  |
| algo_param | 异常检测的算法 | {"algo_type":{"algos":["prophet"]}} |  |  |
| create_user | 指标创建者 |  |  |  |
| update_time | 更新时间 |  |  |  |
| alert_rule_id | 添加的告警规则id |  |  |  |

3. 增量查询prometheus数据：已拉取的数据会持久化到服务内部，下次只拉取最新时间的数据即可。

### 四、数据回写

通过antlr解析用户的promql，获取用户by的标签，同时会写入promql_name，metricstore_name

系统构建默认标签：
* job = "shark-monitor"
* detect_metric_store = "${metricstore_name}"
* detect_yhat_name = "${promql_name}"
* detect_algo = "${algo}"

回写的指标

| metric | 描述 |
| --- | --- |
| detect_y | 业务上报原始指标 |
| detect_yhat_future_lower | 业务指标预测下限值 |
| detect_yhat_future_upper | 业务指标预测上限值 |

使用influxDB写入带有时间戳的数据指标。

### 五、后端管理

后端管理的前端使用LCP构建：https://space.shopee.io/lc/console/projectDetail?id=217

test: https://portal.fp-data.test.shopee.io/sharkService/metaManage  
live: https://portal.fp-data.shopee.io/sharkService/metaManage

两种添加指标方式：
1. 直接在后端添加promql
2. 通过监控平台的规则添加任务

### 六、剔除异常点

标记异常数据范围，存放在基础元数据表中(shark_service_meta_param_tab)，新增 abnormal_time 列

对于标记的异常点时间，通过与最后一条数据的时间计算要去除的时间位置，剔除后再发送到模型进行预测。

风险点说明：
1. 缺失值本身不参与预测，不要添加到异常时间范围内
2. 缺失值左侧的数据，如果要添加需要加上缺失值时间范围
3. 缺失值右侧的数据可以正常添加

### 七、算法数据回放与数据回补

算法回放：使用一段时间范围内的业务数据并指定算法，输出新的预测值  
数据回补：当生产服务宕机或者写入失败时，使用历史数据重新回填预测数据

回放提供新的三种指标：

| 指标 | 含义 |
| --- | --- |
| playback_y | 业务上报原始指标 |
| playback_yhat_future_lower | 业务指标预测下限值 |
| playback_yhat_future_upper | 业务指标预测上限值 |

新增版本标签 version（每次自增1）
