---
topic: domain-knowledge
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# Risk Mart Current Scope

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462863

## Scope Boundary

- **Domain**: Schema risk
- **Scale**: ~3159 column definitions across **109** tables
- **Layers covered**: **DWD**, **DWS**, **ADS**, **DIM**

## Layer Semantics

| Layer | Role |
|--------|------|
| **DWD** | Event- and process-level detail (granular facts suitable for joins and lineage) |
| **DWS** | Summarized / aggregated views built on DWD for analysis and reporting |
| **ADS** | Business-facing datasets optimized for product and operations consumption |
| **DIM** | Reference / dimension data (codes, mappings, stable attributes) |

## High-Value Table Families

| Family | Typical suffix / pattern | Use |
|--------|---------------------------|-----|
| Gateway request/response final result | `*_gateway_req_rsp_final_result_di` | End-to-end gateway outcome per request |
| Anti-fraud workflow detail | `*_af_kafka_workflow_di`, `*_af_kafka_workflow_step_di` | AF workflow runs and step-level detail |
| Underwriting process detail | `*_uw_process_di` | UW pipeline state and transitions |
| Strategy result merge | `*_strategy_final_result_merge_di`, `*_strategy_node_result_merge_di` | Consolidated strategy outcomes and per-node results |

## Stable Join and Trace Keys

Prefer these keys when linking facts across layers and domains:

- `flow_no`
- `request_id`
- `task_id`
- `platform_user_id`
- `region`
- `process_date`

Always confirm column availability and grain (DI vs DF) on the specific table before joining.

## Recommended Answering Heuristics

1. **Start from the question’s grain**: gateway event, workflow step, UW process, or strategy node—pick the narrowest table family that still answers the question.
2. **Anchor on stable keys**: join using `flow_no` / `request_id` / `task_id` when present; add `region` and `process_date` for partition-safe filters.
3. **Respect layer order**: use **DWD** for traceability and raw-ish facts; **DWS**/**ADS** when the question is already aggregated or business-metric oriented; **DIM** for labels and reference only.
4. **Name patterns over guesses**: rely on documented suffixes (`*_gateway_req_rsp_final_result_di`, `*_af_kafka_workflow*_di`, `*_uw_process_di`, `*_strategy_*_merge_di`) rather than inventing table names.
5. **State uncertainty**: if a column or join path is not in scope or not verified in mart metadata, say so instead of fabricating semantics.

## What Not To Assume

- Do **not** assume every table exists in all products or regions; scope is mart-defined, not universal warehouse coverage.
- Do **not** treat DI and DF as interchangeable without checking update frequency and late-arrival behavior.
- Do **not** infer business rules (pass/fail, thresholds, policy) solely from table or column names—confirm with product/strategy docs or labeled fields.
- Do **not** assume one `request_id` always maps to a single strategy run across all engines; validate with workflow and merge tables where available.
- Do **not** extend scope beyond the **109** tables / **~3159** columns documented for this mart unless explicitly cited from another source.
