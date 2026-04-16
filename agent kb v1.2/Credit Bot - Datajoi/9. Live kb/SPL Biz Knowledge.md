---
topic: domain-knowledge
relevance: partial
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# SPL Business Knowledge

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462874

**SPL（卖家侧先买后付 / Shop PayLater 类）** 业务：产品概览、地区、入口激活、支付与放款、退款还款展期、系统架构、**订单生命周期**、业务场景、产品变体与 **Mart 核心表**。

---

## Product Overview（产品概览）

- **定位**：面向 **卖家或店铺** 提供的 **订单级或账单级** 赊购/分期支付能力，与 **电商交易链路** 紧耦合（下单、发货、确认收货、结算）。
- **与 BCL/SCL**：SPL 更贴近 **交易订单**；现金贷更贴近 **纯借贷余额**。
- **关键对象**：用户/店铺、**订单**、**支付单**、**SPL 账单计划**、还款/退款流水。

---

## Regional Coverage（地区覆盖）

| 地区（示例） | 说明 |
|--------------|------|
| **ID / PH / TH / VN / MY** | 产品名与监管不同；Mart 用 **`region`** 区分 |

---

## Entry & Activation（入口与激活）

- **入口**：结账页支付方式、店铺设置、营销活动。
- **开通条件**：店铺资质、历史交易、风控评分；部分市场需 **单独签约**。
- **激活状态**：可在 **`credit_uc`** 或 SPL 专用用户/店铺维表查询；字段以字典为准。

---

## Payment & Disbursement（支付与资金）

- **支付**：用户选择 SPL → 创建 **支付授权** → 订单状态推进。
- **资金方向**：可能是 **平台垫付、资金方代付、后结算** 等模式（依市场）。
- **对账**：支付网关流水 ↔ 核心 SPL 账务 ↔ 结算单。

---

## Refund（退款）

- **全额/部分退款**：影响 **账单冲减、已还部分退回、息费回退规则**。
- **未结清订单关闭**：可能触发 **提前结清或撤销分期**。
- 数据：**退款事件表 + 账单变更流水**；注意 **负向金额** 与 **冲正单号**。

---

## Repayment（还款）

- **账单制**：按账单日生成应还；支持 **主动还、自动扣**。
- **最低还 vs 全额还**：产品规则决定 **利息资本化** 与否。
- **Mart**：常见 `dws_spl_<region>_...` 类还款/账单汇总（以元数据为准）。

---

## Extension（展期）

- **展期**：延长当前账单截止日或重组剩余期数（若产品支持）。
- 分析：展期前后 **DPD、MOB、费率** 变化；注意 **监管披露** 要求。

---

## System Architecture（系统架构）

```text
交易 / 订单服务
    → SPL 核心（额度、账单、还款计划）
    → 支付与清结算
    → 风控（反欺诈、额度、交易级策略）
    → 通知与催收（贷后）
    → ODS → DWD → DWS/ADS → Credit Mart
```

---

## Order Lifecycle（订单生命周期）

| 阶段 | 说明 |
|------|------|
| **Created** | 下单选择 SPL |
| **Authorized / Held** | 额度占用 |
| **Shipped / Completed** | 履约节点影响结算与账单生成 |
| **Billed** | 出账，应还日确定 |
| **Repaid** | 正常结清 |
| **Overdue** | 入逾，可能催收 |
| **Closed / Charged-off** | 关闭或核销（口径依表） |

---

## Business Scenarios（业务场景）

| 场景 | 要点 |
|------|------|
| 大促 | 额度、风控阈值、支付成功率 |
| 拒付 / 争议 | 订单纠纷与账单暂停 |
| 店铺切换主体 | 额度与历史账单继承规则 |
| 跨境（若有） | 币种、结算、合规 |

---

## Product Variants（产品变体）

- **期数**：3/6/12 期等。
- **免息营销**：息费补贴与会计分摊。
- **联合营销**：与品牌或类目的专属额度。

---

## Data Mart Core Tables（数据集市核心表）

> 命名示例；请以 **数据地图** 为准。

| 主题 | 示例模式 |
|------|----------|
| 用户/店铺宽表 | `credit_uc.ads_<region>_...` 或 SPL 专用宽表 |
| 订单与支付 | `dwd_spl_<region>_order_di`、`dwd_*_payment_di` |
| 账单与分期计划 | `dwd_spl_<region>_bill_df`、`installment` 类表 |
| 还款 | `dws_spl_<region>_repayment_df` |
| 退款 | `dwd_*_refund_di` |

**查询约定**：**`grass_date` / `pt` + `region`**；理解 **T-1**；订单粒度与账单粒度 **先分后总**。
