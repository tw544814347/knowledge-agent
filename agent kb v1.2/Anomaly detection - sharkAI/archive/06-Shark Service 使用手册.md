# Shark Service 使用手册

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2484782624

### 一、登陆元数据管理后端

| env | 地址 |
| --- | --- |
| test | https://portal.fp-data.test.shopee.io/sharkService/metaManage |
| live | https://portal.fp-data.shopee.io/sharkService/metaManage |

### 二、添加指标到异常监控服务

### 2.1 第一种：直接在后端添加对应的promql

点击create创建对应的元数据

| 参数 | 含义 | 默认值 | 说明 |
| --- | --- | --- | --- |
| MetricStoreName | 指标的数据源 |  | 可以在监控平台获取，需要填入MetricStore ID |
| PromqlName | 指标的逻辑定义，自定义（不支持修改） |  |  |
| Promql | promql语法 |  | 可以在监控平台获取 |
| CreateUser | 创建者 |  |  |
| Cron | 调度周期 | 0 0/1 * * * ? |  |
| AlgoParam | 算法参数 | {"algo_type":{"algos":["sarima"]}} |  |
| StartInterval | 历史数据范围 | 3 | 历史3小时数据用于预测数据 |

点击Edit可以修改对应的元数据

可以修改：

| 参数 | 含义 | 默认值 | 说明 |
| --- | --- | --- | --- |
| PromqlName | 指标的逻辑定义 |  |  |
| Promql | promql语法 |  |  |
| StartInterval | 用于训练算法预测的历史数据时间范围 | 24（单位小时） |  |
| Cron | 任务执行周期 | 0 0/1 * * * ? | 一分钟执行一次 |
| AlgoParam | 指定算法模型 | {"algo_type":{"algos":["holt_winters"]}} | 支持：holt_winters、sarima |
| CreateUser | 创建者 |  |  |

注意：参数修改可能会产生新的标签或者标签值发生变化会导致数据会重新初始化一次

### 2.2 第二种：直接拉取监控平台的规则到异常检测服务

通过点击LoadRule添加规则，规则ID从监控平台获取

1.本方法会把规则名称作为PromqlName  
2.本方法只会加载一次

### 三、数据展示

| env | prometheus地址 | 说明 |
| --- | --- | --- |
| test | monitoring grafana | 异常检测的数据推送到默认的地址 |
| live | 拉取数据的数据源中 | 异常检测的数据推送回拉取数据的metricstore中 |

提供的指标

| 指标 | 含义 |
| --- | --- |
| detect_y | 业务上报原始指标 |
| detect_yhat_future_lower | 业务指标预测下限值 |
| detect_yhat_future_upper | 业务指标预测上限值 |

标签

| 标签名 | 标签值 |
| --- | --- |
| shark_job | job id |
| detect_yhat_name | 参数PromqlName值 |
| detect_metric_store | 参数MetricStoreName值 |
| detect_algo | 参数AlgoParam中的算法 |
| shark_env | 生产：live，测试：test |

### 异常点剔除

发送post请求 `${host}/addAbnormal`

```json
{
  "metricStoreName": "monitor-biz-data-latency-id",
  "promqlName": "test_monitor_less_cnt_by_5m_bill_tab_test",
  "abnormalTime": "2024-10-17 16:05:00,2024-10-17 16:15:00"
}
```

### 算法回放/数据回补

添加任务：`${host}/playback/addPlayBack`

| 字段 | 含义 | 是否必须 |
| --- | --- | --- |
| aglo_param | 算法参数 | 否 |
| create_user | 操作者 | 否 |
| end_time | 回放结束时间（包含该时间戳） | 是 |
| metricstore_name | 数据源 | 是 |
| promql | promQL语法 | 否 |
| promql_name | 指标名称 | 是 |
| start_interval | 开始时间与当前时间间隔 | 否 |
| start_time | 回放开始时间（不包含该时间戳） | 是 |
| type | 操作类型（1：算法回放，2：回补数据） | 是 |

### 四、添加告警

告警请使用监控平台添加对应的告警规则

### 备注

| 监控面板 | datasource | metrics store id | remark |
| --- | --- | --- | --- |
| paredose | monitor-biz-risk-id-main-iddci |  |  |
| credit | monitor-biz-credit-id-main-iddci |  |  |
| risk | monitor-biz-risk-id-main-iddci |  | 场景id：10035 80022 |
