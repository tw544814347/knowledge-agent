---
topic: domain-knowledge
relevance: partial
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# CL (Cashloan) Business Knowledge

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462816

本文档概述 **现金贷（CL）** 业务域的产品范围、地区、用户旅程、系统架构与 **数据集市核心表**，供 Credit Bot 与数据侧对齐业务语言。

---

## Product Overview（产品概览）

- **CL（Cashloan）** 在内部常作为 **买家现金贷（BCL）** 与 **卖家现金贷（SCL）** 等现金贷产品的统称或中台能力域。
- 核心价值：为 **买家 / 卖家** 提供 **循环或单笔额度、快速授信、线上放款与还款**；与电商交易、店铺经营数据结合做风控与运营。
- 与 **SPL（先买后付）**、**BNPL** 区分：CL 多为 **纯现金借贷**；SPL 更贴近订单与账单。

---

## Regional Coverage（地区覆盖）

下表为说明性模板，**具体上线国家/地区与产品名以当地合规与 PRD 为准**。

| 地区代码（示例） | 产品形态说明 | 备注 |
|------------------|--------------|------|
| **ID** | 印尼现金贷 | 常见 `region` 占位符 |
| **PH** | 菲律宾现金贷 | 监管与利率规则独立 |
| **TH** | 泰国现金贷 | |
| **VN** | 越南现金贷 | |
| **MY** | 马来西亚现金贷 | |
| **SG** | 新加坡 | 若适用，额度与客群不同 |

Mart 表名中常含 **`_${region}_`**，查询时 **必须** 限定地区以避免误混。

---

## Entry & Activation（入口与激活）

1. **入口**：App / Web 金融 tab、营销位、还款提醒内链等。
2. **授信**：提交资料 → 风控决策 → 额度 / 利率展示。
3. **激活**：签署合同、KYC、绑卡等 **激活成功** 后方可动支（具体步骤因地区与产品版本而异）。
4. **数据**：激活漏斗常落在 **`credit_uc.ads_<region>_uc_user_list_wide_df`** 类宽表；字段以白名单、激活标志为准。

---

## Loan Application（借款申请）

- **申请**：输入金额、期数 → 二次风控 → 结果（通过/拒绝/人工）。
- **放款**：核心状态 **`disburse_status = SUCCESS`** 等；关联 **`loan_id`**、渠道、利率档位。
- **关键实体**：用户、借据、账单计划、支付单。

---

## Repayment（还款）

- **主动还款**：用户发起还款、扣款顺序（本金/息费）。
- **自动代扣**：绑卡代扣、失败重试。
- **提前结清**：可能涉及违约金或息费规则（产品配置）。
- **Mart**：常用 **`credit_mart.dws_bcl_<region>_loan_repayment_df`**、**`dws_scl_<region>_...`** 等还款汇总表（表名以字典为准）。

---

## System Architecture（系统架构，逻辑视图）

```text
客户端 / 网关
    → 信贷核心（授信、合同、借据、还款计划）
    → 支付 / 清结算
    → 风控引擎（策略、模型、名单）
    → 消息与任务（通知、代扣）
    → 数据管道（ODS → DWD → DWS/ADS）
    → Credit Mart / UC 宽表（分析）
```

- **读模型**：报表与 Bot 主要读 **Mart / ADS**，不写核心库。

---

## Loan Types（贷款类型）

| 类型 | 说明 |
|------|------|
| **循环额度** | 在额度内多次借款、随借随还 |
| **单笔单批** | 单次申请单次放款 |
| **分期** | 固定期数、等额本息/本金等 |

卖家侧（SCL）可能与 **店铺、订单、回款** 绑定不同风控与额度逻辑。

---

## Data Mart Core Tables（数据集市核心表）

以下为 **典型命名模式**（实际以元数据与 Confluence 指标页为准）：

| 主题 | 示例表模式 |
|------|------------|
| 用户名单 / 白名单 / 激活 | `credit_uc.ads_<region>_uc_user_list_wide_df` |
| 放款 | `credit_mart.dws_bcl_<region>_loan_disburse_df`、`dws_scl_<region>_loan_disburse_df` |
| 还款 | `credit_mart.dws_bcl_<region>_loan_repayment_df` |
| 借据 / 余额 / 逾期 | `dws_*_loan_*_df` 类借据日快照表 |
| 申请漏斗 | `dwd_*_loan_apply_di` 等申请明细 |

查询约定：**`grass_date` / `pt` + `region`**；理解 **T-1**；BCL 与 SCL **分表查询** 再合并。
