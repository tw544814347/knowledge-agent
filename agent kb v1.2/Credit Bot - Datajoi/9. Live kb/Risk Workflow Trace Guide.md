---
topic: domain-knowledge
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# Risk Workflow Trace Guide

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3158462869

## Core Architecture Roles

End-to-end risk handling can be read as a pipeline of responsibilities:

```text
Risk Gateway → Workflow orchestration → Risk / UW Engine → Feature & Function execution
```

| Role | Responsibility (conceptual) |
|------|-------------------------------|
| **Risk Gateway** | Ingress for GRPC/HTTP risk calls; correlation IDs; routing to workflow/engine |
| **Workflow** | Orchestration of steps, branches, and callbacks across engines and data producers |
| **Engine** | Core decision logic (rules, models, underwriting steps) executed inside the workflow |
| **Feature / Function** | Data preparation, external lookups, and callable units invoked by rules or engine steps |

## Gateway Request Basics

- **Protocols**: GRPC and HTTP entry paths may both exist; identify the path used for the incident under investigation.
- **AppID**: Application / caller identity for quota, routing, and audit.
- **SceneID**: Business scene (product flow) used to select workflow template and parameters.
- **FlowNo**: Stable flow-level identifier for correlating gateway, workflow, and downstream artifacts when emitted consistently.
- **ReqNo**: Request-level identifier within a flow; use together with `FlowNo` when tracing duplicate or retried calls.

Document actual column names in mart tables (e.g. gateway final result tables) rather than assuming 1:1 naming with runtime field names.

## How To Trace One Risk Request

Recommended drill-down order:

1. **Gateway final result**  
   Start from `*_gateway_req_rsp_final_result_di` (or equivalent gateway outcome table) using `flow_no`, `request_id`, `region`, and `process_date` as filters.

2. **Workflow execution**  
   Follow into `*_af_kafka_workflow_di` for workflow instance state; use `*_af_kafka_workflow_step_di` for step-level timestamps, status, and payloads where available.

3. **Underwriting**  
   If UW is in scope, open `*_uw_process_di` keyed by the same correlation keys to see process phases and outcomes.

4. **Strategy-node detail**  
   Use `*_strategy_final_result_merge_di` for merged final strategy view and `*_strategy_node_result_merge_di` for per-node inputs/outputs and ordering.

If any hop is missing data, widen the time window on `process_date` and verify AppID/SceneID filters before concluding absence of execution.

## Workflow Vocabulary

| Term | Meaning |
|------|---------|
| **workflow** | Executable graph of steps (conditions, parallel branches, engine calls) for one risk scene |
| **RiskWorkflow** | Shopee risk-specific workflow implementation / metadata (naming may appear in logs and mart) |
| **Feature** | Computed or fetched attribute used as input to rules or models |
| **L1Rule / L2Rule / L3Rule** | Tiered rule layers (coarse → finer granularity); exact semantics depend on product configuration |
| **KYC** | Know-your-customer checks and identity-related steps |
| **LC** | Limit / line / credit-limit related controls (context-specific) |
| **FM** | Fraud-monitoring or fraud-model related components (context-specific) |
| **AS** | Anti-fraud / antifraud subsystem shorthand where used in internal naming |

Always map abbreviations to the concrete step codes or node types present in the trace tables for the region/product in question.

## Practical Mapping Between Process Concepts And Mart Tables

| Concept | Typical mart anchor |
|---------|---------------------|
| Gateway ingress / final HTTP-like outcome | `*_gateway_req_rsp_final_result_di` |
| AF workflow run | `*_af_kafka_workflow_di` |
| AF workflow step / sub-event | `*_af_kafka_workflow_step_di` |
| Underwriting process timeline | `*_uw_process_di` |
| Strategy outcome (merged) | `*_strategy_final_result_merge_di` |
| Strategy per-node detail | `*_strategy_node_result_merge_di` |

Join keys commonly include `flow_no`, `request_id`, `task_id`, `platform_user_id`, `region`, and `process_date`—verify per table before producing SQL or answers.
