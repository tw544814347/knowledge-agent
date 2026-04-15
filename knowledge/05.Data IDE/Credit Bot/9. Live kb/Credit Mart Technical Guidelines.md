# Credit Mart Technical Guidelines

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462810

本文档汇总 Credit 数据集市（Credit Mart）相关的 **时效、时区、分区、逾期、MOB、状态、数仓分层、重组贷款与命名** 等技术约定，与 SQL 标准、术语表配合使用。

---

## Data Timeliness（T-1 Data）

- 离线宽表与主题汇总表通常按调度日产出，**业务可依赖的“完整一日”数据为 T-1**（相对数据可用日或分析基准日）。
- 报表默认 **`grass_date = 业务日`** 且该业务日 ≤ 已闭合的最大分区；若需当日进度，需切换 **ODS / 近实时** 数据源并单独说明口径。

---

## Time Zone Handling（时区）

| 层级 | 常见约定 | 注意 |
|------|----------|------|
| **ODS** | 时间戳多为 **UTC0** | `JOIN`、逾期起算需转业务地区本地日历 |
| **Mart / 应用宽表** | 可能为 **VARCHAR 本地时间** 或已转本地 TIMESTAMP | 以数据字典为准；禁止与 UTC 裸比较 |
| **分析实践** | 统一转 **DATE（业务日）** 或统一时区后再比较 | 跨区汇总时按 **region** 分别处理再合并 |

---

## Partition Key Convention（grass_date）

- **`grass_date`**：Credit Mart 系列表中广泛使用的 **业务日期分区 / 快照键**，表示“数据所对应的业务日”。
- 查询 **必须** 带 `grass_date`（或表规定的等价分区）谓词，避免全表扫描。
- 与 **`pt`**（跑批分区）、**`bizdate`**（调度变量）同时出现时，在 SQL 注释中写明映射关系。

---

## DPD Fields（dpd, dpd_eod, dpd_finance）

| 字段 | 典型用途 |
|------|----------|
| **dpd** | 通用分析、策略、运营看板（日切逾期天数） |
| **dpd_eod** | 日终快照、与 EOD 批次一致的对账与监控 |
| **dpd_finance** | 财务、拨备、科目对齐场景 |

同一需求 **固定一个主字段**；跨系统对比时核对是否同一 cut-off。

---

## MOB Grouping（账龄分组）

- **MOB**（Month on Book）：在账月份 / 账龄分组，用于 **vintage、迁徙、核销后表现** 等分析。
- 分组边界（M0、M1、…）以 **产品/报表规范** 为准；落表时常为离散桶或序号。
- 与 **`grass_date`**、借据起息日组合计算 MOB 时，注意 **30/360 与自然月** 的产品差异。

---

## Bill_status / Loan_status Conventions

- **bill_status**：账单/期次粒度状态（如出账、结清、逾期中）。
- **loan_status**：借据/合同粒度状态（如放款成功、正常、结清、核销）。
- 分析 **还款计划** 时用账单维度；分析 **合同级风险敞口** 时用借据维度；**禁止跨粒度直接 SUM** 不做说明。

---

## Data Layer Definitions（ODS, DWD, DWM, DWS, ADS, DIM, VIEW）

| 层级 | 英文 | 含义（Credit 域内） |
|------|------|---------------------|
| **ODS** | Operational Data Store | 贴源层，近原始事件与快照，UTC、变更频繁 |
| **DWD** | Data Warehouse Detail | 明细建模，清洗、统一编码、主题关联 |
| **DWM** | Data Warehouse Middle | 中间汇总，轻度聚合、宽表准备 |
| **DWS** | Data Warehouse Summary | 按主题/维度汇总（用户、借据、日等） |
| **ADS** | Application Data Service | 应用层指标表，面向报表与 API |
| **DIM** | Dimension | 维度表（产品、地区、码表） |
| **VIEW** | View | 逻辑视图，可能跨层封装；注意性能与权限 |

---

## Restructured Loans Business Guidelines（重组贷款）

- **识别**：通过重组标识、原借据与新借据关联、或产品事件表识别（具体字段以 Mart 文档为准）。
- **DPD / 余额**：重组后可能 **重置 DPD** 或 **继承敞口**，不同报表口径不同；分析时需 **按监管/财务/运营** 选择对应字段。
- **Vintage**：重组借据是否纳入原 cohort 以 **业务定义** 为准，并在需求中冻结。

---

## Table Naming Conventions（表命名）

常见模式（示例，非穷举）：

- **库.schema**：`credit_mart`、`credit_uc` 等。
- **层级前缀**：`dwd_`、`dws_`、`ads_` 等。
- **产品/域片段**：`bcl`、`spl`、`scl`、`cl` 等。
- **地区占位**：`_<region>_` 或 `${region}`，如 `dws_bcl_id_loan_df`。
- **后缀**：`_df` 日表、`_mf` 月表等（以平台规范为准）。

新建中间表时 **沿用同产品同粒度命名**，便于检索与权限继承。
