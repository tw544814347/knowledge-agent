---
topic: domain-knowledge
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# Project Table Name Schema

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462875

## ODS Layer Naming

| Pattern | Meaning |
|---------|---------|
| `ods__<dbname>_db__<tablename>_tab__df` | Full daily snapshot style ODS object for table `<tablename>` in database `<dbname>` |
| `ods__<dbname>_db__<tablename>_tab` | ODS object for the same logical table without the `__df` daily-snapshot suffix (usage depends on pipeline convention) |

Components are separated by double underscores (`__`) between logical segments; `<dbname>` and `<tablename>` follow internal DB and table naming.

## DW Layer Naming

Credit DW objects are typically qualified by **product** and **region** in the broader naming scheme.

**Product range (examples)**

`bcl`, `chp`, `cpl`, `fes`, `mcl`, `scf`, `scl`, `spl`, `svl`, `tl`, `vcl`, `cl`

**Region range (examples)**

`id`, `ph`, `my`, `th`, `tw`, `vn`, `sg`, `br`, `mx`

Exact combinations depend on the mart product matrix; not every product exists in every region.

## credit_mart Schema

General pattern:

```text
<dwd|dws|ads|wide|dim>_<product>_<region>_<suffix>_<di|df>
```

- **Layer prefix**: `dwd`, `dws`, `ads`, `wide`, or `dim`
- **`<product>`**: One of the product codes from the product range
- **`<region>`**: One of the region codes from the region range
- **`<suffix>`**: Business or pipeline-specific table stem (e.g. gateway, workflow, strategy)
- **`<di|df>`**: Incremental daily partition vs full daily / snapshot semantics per pipeline definition

Example shape (illustrative only):

```text
dwd_spl_id_gateway_req_rsp_final_result_di
```

## credit_uc Schema Patterns

- UC (underwriting / user-credit) tables often mirror the same **layer_product_region_suffix_di/df** discipline with a `credit_uc` database/schema prefix in fully qualified names.
- Prefer official UC naming from metadata or Confluence over inferring `_uc_` in every table name; some objects may use abbreviated stems shared with `credit_mart`.

## credit_fund Schema Pattern

- Fund-related pipelines typically use **`credit_fund`** as the schema/database boundary with layer and periodicity suffixes aligned to fund reporting cycles.
- Table stems often encode **fund product**, **counterparty**, or **ledger** concepts; confirm with the fund data dictionary for exact `<suffix>` vocabulary.

## credit_promotion Schema Pattern

- Promotion and campaign attribution tables live under **`credit_promotion`** with names that combine **campaign**, **channel**, or **offer** stems plus `_di` / `_df` where applicable.
- Join keys frequently include **user**, **order**, or **request** identifiers depending on the promotion type—check column lists per table.

## credit_collect Schema Pattern

- Collections and delinquency facts use **`credit_collect`** with suffixes reflecting **bucket**, **dunning**, **repayment**, or **contact** events.
- Time-based partitions (`process_date`, `biz_date`) are critical for replaying collection state; align with the collect pipeline’s documented grain (DI vs DF).

---

When in doubt, resolve the canonical name from Hive/Glue (or internal catalog) metadata rather than constructing names from this document alone.
