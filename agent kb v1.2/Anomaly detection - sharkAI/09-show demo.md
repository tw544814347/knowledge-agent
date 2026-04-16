---
topic: shark-service-demo
relevance: partial
language: en
source: https://confluence.shopee.io/pages/viewpage.action?pageId=2561315743
last_reviewed: 2026-04-16
---

# show demo

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2561315743

### step:

env: [live](https://portal.fp-data.shopee.io/sharkService/metaManage) [test](https://portal.fp-data.test.shopee.io/sharkService/metaManage)

1. create job:

**demo sql:** 
```
sum(avg_over_time(kafka_server_BrokerTopicMetrics_OneMinuteRate{name="BytesInPerSec", topic=~"risk.shopeepay_acquiring_id_transaction_order_wide_tab__live|dwd_risk_id_spp_uws_order|dwd_spm_transaction_tab__id|wide_id_spm_payment_transaction|dwd_apm_transaction_tab__id|wide_id_apm_payment_transaction"}[5m]))
```

**metric store id:** shared-id / monitor-biz-credit-vn-main-vthl

1.1 query metric store id: 
https://space.shopee.io/observability/monitoring/platform/metric-stores

2. config grafana:
https://monitoring.infra.sz.shopee.io/grafana/d/7FMmYO4Hk/shark-service

3. preview data:
https://portal.fp-data.test.shopee.io/sharkService/metaPreview/208/monitor-k8s-biz-credit/ID-SPL-Payment_Count

4. release data:
https://portal.fp-data.test.shopee.io/sharkService/metaRelease/208/monitor-k8s-biz-credit/ID-SPL-Payment_Count

4.1 config alert

### remark

| 监控面板 | datasource | metrics store id | project |
| --- | --- | --- | --- |
| paredose | monitor-biz-risk-id-main-iddci | monitor-biz-risk-id-main-iddci | risk-sre |
| credit | monitor-biz-credit-id-main-iddci | monitor-k8s-biz-credit | credit |
| risk | monitor-biz-risk-id-main-iddci | monitor-biz-risk-id-main-iddci |  |
| shark | monitor-biz-data-latency-id | monitor-biz-data-latency-id |  |
