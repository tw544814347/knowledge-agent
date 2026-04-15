# DE Developing Common Sense（数据开发常识）

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462826

面向 **数据开发（DE）** 在 Credit 域建模与取数时的 **高频约定**：T-1、时区、分区、DPD、MOB、状态、分层与近实时视图，与 **Credit Mart Technical Guidelines** 互补。

---

## T-1 Data

- 离线日批表 **默认可用日为 T-1**；调度参数 **`${bizdate}`** 常与 **分区 pt / grass_date** 对齐。
- 做 **日环比、周环比** 时注意 **节假日与数据闭合**；未闭合日不写死为“昨日”。

---

## Timezone Handling

- **ODS**：时间戳多 **UTC0**；落 Hive/Presto 后转本地需 **`AT TIME ZONE`** 或应用层转换（依引擎）。
- **Mart**：可能是 **DATE**、**TIMESTAMP** 或 **VARCHAR 本地时间**；**禁止** 未转换的跨层比较。
- **建议**：明细层统一 **业务地区本地日历 DATE** 再往上汇总。

---

## Partition Optimization

- **首列过滤**：`grass_date`、`pt`、`region`、`biz_type`。
- **避免**：无分区裁剪的全表扫；大区间 `OR` 可改写为 `BETWEEN` 或分段 `UNION ALL`。
- **动态分区**：写入时注意不要 **小文件爆炸**（控制并行度与 bucket）。

---

## DPD Fields

- **`dpd`**：通用分析。
- **`dpd_eod`**：日终批次一致。
- **`dpd_finance`**：财务口径。
- 同一张结果表 **不要混用多个 DPD** 而不加列名区分。

---

## MOB Grouping

- 从 **起息日 / 放款月** 到观察月的 MOB 序号；与 **核销日、cure 日** 联合定义 cohort。
- Vintage 宽表常预计算 **`mob`** 或 **`mob_bucket`**，优先 **直接引用** 减少重复逻辑。

---

## Bill / Loan Status

- **账单级** vs **借据级** 状态字段分离；汇总敞口时以 **借据+日期** 粒度为主。
- 状态流转画 **有向图** 再写 SQL，避免非法跳转被计入。

---

## Data Layer Definitions（数据分层）

| 层级 | DE 关注点 |
|------|-----------|
| **ODS** | 保真、延迟、主键唯一性 |
| **DWD** | 维度退化、缓慢变化、统一枚举 |
| **DWM** | 中间聚合可复用、控制冗余 |
| **DWS** | 主题一致、分区键稳定 |
| **ADS** | 面向应用，字段稳定、文档化 |
| **DIM** | 版本生效区间、scd 类型 |
| **VIEW** | 不下沉大计算、不藏隐式过滤 |

---

## Near Real-time Views（近实时视图）

- **用途**：当日放款、还款监控、催收实时队列（若存在）。
- **注意**：与 T-1 离线 **口径可能不一致**；看板需 **双口径说明**。
- **实践**：近实时层 **独立 schema** 或 `_rt` 后缀；任务 SLA 与补数策略文档化。

---

## Quick Checklist for DE

- [ ] 分区与 **grass_date** 设计一致  
- [ ] 时区与 **地区** 成对处理  
- [ ] DPD / 状态 **粒度** 与需求一致  
- [ ] 离线 vs 实时 **不同源** 已标注  
- [ ] 表注释与 **Confluence pageId** 可溯源  
