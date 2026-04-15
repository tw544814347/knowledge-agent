# Collection Business Knowledge

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462817

本文档描述 **催收（Collection）** 业务域：逾期管理、阶段划分、组织与渠道、流程、核心指标与外呼术语，便于与 Mart 字段及策略文档对齐。

---

## Business Domain Overview（业务域概述）

- **目标**：在合规前提下 **提升回款率、降低损失**，管理 **逾期资产** 的生命周期。
- **范围**：覆盖 **贷后预警、早期提醒、逾期催收、诉讼/委外（若适用）、结清与核销衔接**。
- **数据**：与 **`dpd`**、**`bill_status` / `loan_status`**、催收行动表、通话记录等关联。

---

## Core Concepts（核心概念）

### DPD（Days Past Due）

- **逾期天数**：自 **应还日次日** 或合同定义 cut-off 起算（以产品为准）。
- 与 Mart 中 **`dpd` / `dpd_eod` / `dpd_finance`** 对齐使用，见技术指南。

### Overdue（逾期）

- 未在到期日 **足额** 偿还应还金额；可能部分还款后仍逾期。
- 分析时明确 **本金逾期 vs 息费逾期** 是否区分（报表口径）。

### Pre-due（到期前）

- **到期日前** 的提醒与客户经营，降低入逾概率。
- 指标：提醒覆盖率、接通率、到期前还款率等。

### Post-due（到期后）

- **入逾后** 的催收动作与回收结果。
- 与 **bucket / stage** 强相关。

---

## Collection Stage Definitions（催收阶段）

典型阶段（名称因地区与组织而异）：

| 阶段 | 描述 |
|------|------|
| **Early / Soft** | 刚逾期，短信/App 提醒为主 |
| **In-house** | 内催，电催与短信组合 |
| **Late / Hard** | 高账龄，加强频次与升级策略 |
| **Legal / Agency** | 法催或委外（若业务存在） |

阶段常与 **DPD 桶** 映射；落表时以 **stage_code** 或策略版本为准。

---

## Organizational Terms（组织相关）

- **Queue / Skill group**：按产品、地区、账龄、额度拆分的作业队列。
- **Collector / Agent**：催收员坐席。
- **Team / Site**：团队与职场（内包/外包）。
- **Vendor**：委外供应商（若使用）。

---

## Collection Channels（催收渠道）

| 渠道 | 说明 |
|------|------|
| **Voice** | 电话外呼 |
| **SMS** | 短信模板，需合规审核 |
| **App Push / In-app** | 应用内消息 |
| **Email** | 部分地区使用 |
| **Field** | 上门（若合规允许） |

---

## Business Process（业务流程，简图）

```text
入逾识别 → 分案 / 入队 → 策略路由 → 渠道执行 → 结果回写
    → 承诺还款（PTP）跟踪 → 回款销账 → 升级或出队
```

- **分案规则**：额度、DPD、历史还款、风险分等。
- **行动代码**：每次联系记录 **action_code / result_code**（以 ODS/DWD 字典为准）。

---

## Core Metrics & Calling Terms（核心指标与外呼术语）

### 核心指标

| 指标 | 含义方向 |
|------|----------|
| **RPC / PTP rate** | 有效联系、承诺还款占比 |
| **Cure rate** | 经催收后回到正常状态的比例 |
| **Roll rate** | 桶间恶化或改善 |
| **Recovery amount** | 催回金额 |
| **Cost per dollar recovered** | 催回单位成本 |

### 外呼 / 通话相关

| 术语 | 说明 |
|------|------|
| **Dial / Connect** | 拨号 / 接通 |
| **ACW** | After call work，话后整理 |
| **PTP** | Promise to pay，承诺还款日与金额 |
| **RPC** | Right party contact，本人或有效第三方接通 |
| **PTD** | Promise to date（与 PTP 类似，以内部定义为准） |

更全缩写见 **Collection Terminology.md**。
