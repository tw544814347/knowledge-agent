---
topic: domain-knowledge
relevance: partial
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# Credit Product Classification

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462823

信贷产品线 **分类总表**：缩写、全称、**biz_type**、**product_id** 与简述。具体枚举值 **以线上维表与核心配置为准**；下表为 **结构与典型取值示例**，便于 Bot 与分析师对齐过滤条件。

---

## Core Products Table（核心产品表）

> **说明**：`biz_type` 与 `product_id` 为逻辑占位示例；落表时可能为 **INT / VARCHAR**；请以 **`dim_product`** 或 **`credit_*_dim_*`** 最新版本为准。

| 缩写 | 全称（英文） | 中文描述 | biz_type（示例） | product_id（示例） |
|------|--------------|----------|------------------|---------------------|
| **BCL** | Buyer Cashloan | 买家现金贷：循环/单笔额度、现金放款 | `BCL` / `10` | `1001` |
| **SCL** | Seller Cashloan | 卖家现金贷：与店铺经营相关授信 | `SCL` / `20` | `2001` |
| **SPL** | Seller PayLater / Shop PL | 卖家侧先买后付/赊购（名称依市场） | `SPL` / `30` | `3001` |
| **BNPL** | Buy Now Pay Later | 订单级先买后付 | `BNPL` / `40` | `4001` |
| **FES** | Financed invoice / Supply chain | 发票融资/保理等对公产品 | `FES` / `50` | `5001` |
| **CL (generic)** | Cashloan umbrella | 现金贷中台或多产品汇总口径 | `CL` / `0` | `0`（汇总行，若有） |

---

## How to Use in SQL（SQL 中使用方式）

```sql
-- 示例：按 biz_type / product_id 过滤（字段名以实际表为准）
SELECT ...
FROM credit_mart.dws_bcl_id_loan_df
WHERE grass_date = DATE '${bizdate}'
  AND biz_type = 'BCL'
  AND product_id IN (1001, 1002);  -- 子产品变体
```

- **多产品合并**：先 **分表或分 biz_type 聚合**，再 `UNION ALL`，避免 **JOIN 键不唯一** 导致翻倍。
- **历史变更**：`product_id` 拆分合并时需 **维表生效区间**（`start_date` / `end_date`）。

---

## Product Variants（产品变体，概念层）

| 变体维度 | 示例 |
|----------|------|
| 地区 | ID / PH / TH … |
| 资金模式 | 自营 / channeling / 联合贷 |
| 额度类型 | 循环 vs 单笔 |
| 客群 | 新客 / 老客 / 白名单 |

维表中常以 **组合键** 区分；报表需声明 **是否含已下线产品**。

---

## Cross-reference

- 缩写中文见 **Common Abbreviations.md**。
- 各产品线业务见 **CL / SPL / FES Biz Knowledge** 系列文档。
