---
topic: domain-knowledge
relevance: partial
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# Credit Mart Terminology Primer

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462814

Credit 数据集市相关 **产品缩写、业务流程、关键指标、领域词与表字段术语** 速查，便于跨团队沟通与写 SQL / 配置指标时对齐口径。

---

## Product Terms（产品术语）

| 缩写 / 名称 | 英文 / 说明 |
|-------------|-------------|
| **SPL** | Seller / Shop PayLater 类赊购产品（卖家侧先买后付相关能力，具体以当地产品名为准） |
| **BCL** | Buyer Cashloan，买家现金贷 |
| **SCL** | Seller Cashloan，卖家现金贷 |
| **CL** | Cashloan 总称或现金贷产品域 |
| **BNPL** | Buy Now Pay Later，先买后付 |
| **CF** | Consumer Finance 相关产品线或内部通道统称（上下文依赖） |
| **FES** | 供应链金融 / 发票融资类对公产品域 |
| **LDN** | Loan / 借据编号或内部借据标识体系（以字段字典为准） |

---

## Business Process Terms（业务流程）

| 术语 | 含义 |
|------|------|
| **授信** | 额度评估与授信结果生效 |
| **激活** | 用户完成协议 / KYC 等可用额度的动作 |
| **动支 / 放款** | 额度使用、资金到账成功 |
| **账单日 / 还款日** | 出账与应还日期 |
| **逾期** | 超过应还日未足额还款 |
| **催收** | 逾期后的联系与回收流程 |
| **核销 /  write-off** | 会计口径损失确认（与运营“结清”区分） |
| **展期** | 延长还款期限或重组还款计划 |
| **退款** | 订单或放款撤销导致的资金回退 |

---

## Key Metrics（关键指标）

| 指标 | 说明 |
|------|------|
| **DPD** | Days Past Due，逾期天数 |
| **MOB** | Month on Book，在账月序 |
| **Vintage** | 按放款 cohort 观察后续表现 |
| **Disbursement** | 放款金额 / 笔数 |
| **OS / Outstanding** | 在贷余额、敞口 |
| **PAR** | Portfolio at Risk，风险敞口占比（定义依报表） |
| **Roll rate** | 逾期桶迁徙率 |
| **NIR / EIR** | 名义 / 有效利率（口径见财务说明） |
| **FPD / SPD** | 首逾 / 二逾等早期风险指标 |

---

## Domain-specific Terms（领域词）

| 术语 | 说明 |
|------|------|
| **grass_date** | 业务日分区键，Mart 查询核心过滤字段 |
| **T-1** | 离线数据通常滞后一日完整闭合 |
| **Channeling** | 导流 / 联合贷等合作模式相关 |
| **JFS** | 内部资金或金服相关主体 / 通道（上下文依赖） |
| **ABS** | 资产证券化，出表与资产池相关 |
| **Whitelist** | 白名单 / 可营销可授信人群 |
| **Bucket** | 逾期天数分桶（M1、S1 等，与催收策略一致） |

---

## Data Schema Terms（数据模式与字段）

| 类别 | 常见字段 / 概念 |
|------|-----------------|
| **用户** | `user_id`、`buyer_id`、`seller_id`（按产品线） |
| **订单** | `order_id`、`checkout_id`（电商侧） |
| **借据** | `loan_id`、`agreement_id`、LDN |
| **账单** | `bill_id`、`installment_no` |
| **状态** | `loan_status`、`bill_status`、`disburse_status` |
| **逾期** | `dpd`、`dpd_eod`、`dpd_finance` |
| **分区** | `grass_date`、`pt`、`region` |
| **金额** | `principal`、`interest`、`fee`、`outstanding` |
| **时间** | ODS UTC vs Mart 本地 VARCHAR / TIMESTAMP |

---

## Cross-reference

- 更全缩写表见 **Common Abbreviations.md**。
- 产品枚举与 `biz_type` / `product_id` 见 **Credit Product Classification.md**。
- 催收专有名词见 **Collection Terminology.md**。
