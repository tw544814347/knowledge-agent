---
topic: chatbot-knowledge-base
relevance: core
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# Credit Mart SQL Standards

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462808

本文档定义在 **Credit Mart**（及关联 UC / 主题域表）上编写 **Presto SQL** 查询时的方言、格式、领域约定与质量要求，供 Credit Bot、分析师与数据开发统一引用。

---

## SQL Dialect Standard（方言标准）

- **默认方言**：**Presto SQL**（与 Hive 语法有差异；在 Data IDE / 查询引擎中执行前请确认引擎标签）。
- **避免混用**：不要在同一语句中混用仅 Hive 支持的函数或仅 Trino 新版本的语法；以平台文档与已验证样例为准。
- **类型意识**：对金额、利率、计数等字段显式 `CAST`，避免隐式类型提升导致的精度或比较问题。

---

## SQL Format Requirements（格式要求）

### 缩进与换行

- 使用 **2 或 4 空格** 缩进（团队内保持一致即可），**不使用 Tab**。
- `SELECT` 字段每行一个（字段较多时）；`JOIN` / `WHERE` 条件按逻辑块换行。
- 子查询、CTE 使用有意义的别名（`u`、`loan`、`repay` 等），避免 `t1`、`a`。

### 注释

- **文件/块级**：复杂逻辑用 `--` 说明业务口径、快照日期含义、与 Confluence 指标编号对应关系。
- **条件级**：对非显而易见的过滤（例如状态枚举、地区裁剪）加简短注释。
- **禁止**：大段复制粘贴无意义注释或过期口径（易误导 RAG / 读者）。

---

## Presto SQL Specific Rules（Presto 专项）

### GROUP BY / ORDER BY 与列序号

- 在 Presto 中 **`GROUP BY` / `ORDER BY` 可使用列序号**（如 `GROUP BY 1,2`），但 **推荐优先使用列名或别名**，可读性与重构更安全。
- 若使用序号，**修改 SELECT 列表顺序时必须同步检查** `GROUP BY` / `ORDER BY`。

### 日期运算：DATE_ADD，不用 DATE_SUB

- 使用 **`DATE_ADD('day', -1, date_col)`** 等形式表达“减一天”；**避免依赖 `DATE_SUB`**（方言差异大）。
- 周/月偏移统一用带单位的 `DATE_ADD` / `date_trunc` 组合，并在注释中写明业务日历（自然日 vs 工作日）。

### CAST 函数

- 显式转换：**`CAST(x AS BIGINT)`**、**`CAST(x AS DOUBLE)`**、**`CAST(x AS VARCHAR)`**、**`CAST(x AS DATE)`**。
- 字符串转日期优先 **`CAST(col AS DATE)`** 或 **`date_parse`**（格式固定时）；避免隐式转换。

### 字符串函数

- 常用：**`concat`**、**`substr` / `substring`**、**`trim`**、**`lower` / `upper`**、**`replace`**。
- 模糊匹配：**`LIKE`**；多值枚举优先 **`IN (...)`** 而非长链 `OR`。
- 注意 **VARCHAR 与 CHAR** 尾部空格行为；比较前必要时 `trim`。

---

## Credit Mart Specific Patterns（Credit Mart 领域模式）

### 按 grass_date 过滤

- 分区或业务快照字段 **`grass_date`**（或表约定的等价分区键）应作为 **首要过滤条件**，与 **`pt` / `bizdate`** 等工程分区字段区分清楚：业务口径以文档为准。
- 典型模式：`WHERE grass_date = DATE '${bizdate}'` 或 `WHERE grass_date BETWEEN ...`（区间分析时）。

### T-1 数据滞后

- **可查询的最新业务日通常为 T-1**（相对调度日或“今天”）；查询“截至昨日”的余额/状态类指标时，**显式约束** `grass_date` / `pt`，避免误用未闭合的 T 日数据。
- 需要“当日”实时或准实时能力时，**改查 ODS / 近实时视图**，勿与 T-1 离线宽表混用。

### 时间列处理

- **ODS** 常见为 **UTC0**；**Mart / 应用层** 可能为 **VARCHAR 本地时间** 或已转换时间戳——以表字典为准，**禁止混用时区不做转换**。
- 比较、聚合前统一：**先转同一时区或同一 DATE**，再 `JOIN` / `GROUP BY`。

### DPD 字段使用

- **`dpd`**：常用日切逾期天数口径（具体以表说明为准）。
- **`dpd_eod`**：**日终**口径，用于与财务/科目日结一致的场景。
- **`dpd_finance`**：**财务**口径，用于对账、拨备、损益相关分析。
- 同一分析中 **只选一个主口径**，并在注释中声明；跨表 `JOIN` 时核对是否同一快照与同一 DPD 定义。

### bill_status / loan_status

- **账单维度**用 **`bill_status`**（分期、账单级还款计划）。
- **借据/合同维度**用 **`loan_status`**（整笔借据生命周期）。
- 组合报表时 **避免混维度聚合**；需桥接时通过订单号/借据号关联并注明粒度。

---

## Performance Best Practices（性能）

1. **尽早过滤**：分区键（`grass_date`、`pt`、`region` 等）写在 **WHERE 最前路径**，减少扫描。
2. **限制结果集**：探索性查询 **`LIMIT`**；生产取数配合分区 + 谓词下推，避免无界全表扫。
3. **避免 `SELECT *`**：只选必要列，降低 IO 与下游脱敏风险。
4. **大表 JOIN**：保证 **JOIN 键类型一致**；小表在广播语义允许时可利用 hint（若平台支持）。
5. **预聚合**：重复使用的中间结果用 **CTE** 分层，避免重复扫描同一子查询。

---

## Common Pitfalls（常见陷阱）

| 问题 | 说明 |
|------|------|
| 混用 Hive 专属函数 | 如部分 `DATE_SUB`、旧版 UDF，在 Presto 报错或结果不一致 |
| 忽略 T-1 | 把未闭合当日数据当期末快照 |
| 时区混用 | UTC 与本地 VARCHAR 直接比较 |
| 多 DPD 字段混用 | 同一报表同时用 `dpd` 与 `dpd_finance` 未说明 |
| 状态枚举魔法值 | 未对照字典，遗漏 `NULL` / 历史枚举值 |
| `JOIN` 放大 | 一对多关系未去重导致金额翻倍 |
| 分区漏写 | 触发全分区扫描，任务超时 |

---

## SQL Quality Checklist（质量自检清单）

- [ ] 方言为 **Presto**，已在目标引擎验证。
- [ ] **`grass_date` / `pt` / 地区** 等分区与裁剪条件齐全。
- [ ] 业务日理解正确（**T-1** 或明确实时来源）。
- [ ] 时间列 **时区与类型** 与关联表一致。
- [ ] **DPD** 选用字段与口径在注释中说明。
- [ ] **`bill_status` vs `loan_status`** 维度正确。
- [ ] 无 **`SELECT *`**（探索查询除外且已 `LIMIT`）。
- [ ] `GROUP BY` / 窗口函数 **粒度** 与指标定义一致。
- [ ] 关键 `JOIN` 键 **无重复放大** 或已聚合。
- [ ] 注释包含 **指标名 / Confluence 链接或 pageId**（便于审计）。
