---
topic: domain-knowledge
relevance: partial
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# Collection Terminology

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462819

催收域 **缩写、分桶、风险与系统词、外呼话术字段、业务指标** 速查表，与 **Collection Biz Knowledge.md** 搭配使用。

---

## Business Abbreviations（业务缩写）

| 缩写 | 英文 / 中文 |
|------|-------------|
| **DPD** | Days Past Due，逾期天数 |
| **BKT / Bucket** | 逾期分桶 |
| **WO** | Write-off，核销 |
| **PTP** | Promise to pay，承诺还款 |
| **RPC** | Right party contact，有效联系人接通 |
| **PTD** | 承诺日期（若与 PTP 并存，以字典为准） |
| **FPD** | First payment default 等首逾类（上下文区分） |
| **CURE** | 从逾期恢复至正常 |
| **ROLL** | 桶间迁徙 |

---

## Bucket Abbreviations（分桶缩写）

> 具体边界（天数）以 **地区产品 + 策略版本** 为准；下表为示例。

| 缩写 / 标签 | 含义方向 |
|-------------|----------|
| **M0 / Current** | 正常或宽限内 |
| **S1 / M1** | 短期逾期低桶 |
| **S2 / M2+** | 中高额逾期桶 |
| **Charge-off** | 核销桶（会计或运营口径） |

Mart 中可能以 **`dpd_bucket`**、**`overdue_stage`** 等字段呈现，枚举值需查维表。

---

## Risk & System Terms（风险与系统）

| 术语 | 说明 |
|------|------|
| **Strategy ID** | 催收策略版本标识 |
| **Queue** | 分案队列 |
| **Dialer** | 外呼平台 / 预测式拨号 |
| **Disposition** | 通话结束码 / 结果Disposition |
| **List / Campaign** | 外呼名单与活动批次 |
| **Compliance** | 拨打时段、频次、禁拨名单 |

---

## Calling Terms（外呼与通话）

| 术语 | 说明 |
|------|------|
| **Attempt** | 拨号尝试 |
| **Connect** | 接通 |
| **AHT** | Average handle time，平均处理时长 |
| **ACW** | After call work |
| **Abandon rate** | 弃呼率（预测外呼场景） |
| **Recording** | 录音与质检 |
| **IVR** | 交互式语音应答 |

---

## Business Metrics Tables（业务指标表）

### 过程指标

| 指标 | 定义要点 |
|------|----------|
| **接触率** | 触达用户 / 分母案件 |
| **接通率** | 接通次数 / 拨号次数 |
| **本人接通率** | RPC 相关分子分母以报表为准 |
| **行动覆盖率** | 至少一次有效行动的案件占比 |

### 结果指标

| 指标 | 定义要点 |
|------|----------|
| **当日回收金额** | 催收回款流水 |
| **PTP 履约率** | 承诺后实际还款比例 |
| **7/30 内回收率** | 观察窗内回收占逾期本金比 |
| **迁徙率** | 桶间流入流出 |

### 效率指标

| 指标 | 定义要点 |
|------|----------|
| **人均案件量** | 坐席负载 |
| **单案成本** | 费用 / 回收金额 |

---

## Data Join Hints（数据关联提示）

- 催收事实表常 **`loan_id` / `case_id` / `grass_date`** 与借据日表关联。
- 同一用户多借据时注意 **粒度**：案件级 vs 借据级 vs 用户级。
