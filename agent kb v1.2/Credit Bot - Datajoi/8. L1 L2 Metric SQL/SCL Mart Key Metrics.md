---
topic: metric-sql
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# SCL Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703434803

This page lists **17** Cashloan Seller (SCL) mart metrics from Confluence: user eligibility and activation, credit limits, application and disbursement funnels, repayment and outstanding, delinquency buckets, and loss / write-off views. Below are concise descriptions with minimal SQL sketches on `credit_mart.dws_scl_${region}_*` and UC wide tables; use Confluence for authoritative column names.

### 1. Cumulative SCL-whitelisted sellers

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <scl_whitelist_condition>;
```

### 2. Cumulative SCL-activated sellers

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <scl_activated_flag>;
```

### 3. Active seller count with SCL limit

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_scl_${region}_user_limit_df
WHERE pt='${bizdate}' AND limit_status='ACTIVE';
```

### 4. Aggregate SCL credit limit (EOP)

```sql
SELECT SUM(credit_limit) FROM credit_mart.dws_scl_${region}_user_limit_df
WHERE pt='${bizdate}';
```

### 5. Application submitted count

```sql
SELECT COUNT(*) FROM credit_mart.dws_scl_${region}_application_df
WHERE pt='${bizdate}' AND app_status>='SUBMITTED';
```

### 6. Application approved count

```sql
SELECT COUNT(*) FROM credit_mart.dws_scl_${region}_application_df
WHERE pt='${bizdate}' AND app_status='APPROVED';
```

### 7. Cumulative disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_scl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 8. Cumulative disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_scl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 9. Distinct borrower count

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_scl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 10. Period disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_scl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 11. Cumulative repaid amount

```sql
SELECT SUM(repaid_amt) FROM credit_mart.dws_scl_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 12. Repayable principal EOP

```sql
SELECT SUM(repayable_principal) FROM credit_mart.dws_scl_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 13. Outstanding principal EOP (snapshot)

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_scl_${region}_loan_snapshot_df
WHERE pt='${bizdate}';
```

### 14. Overdue amount DPD 1–30

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_scl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_1_30';
```

### 15. Overdue amount DPD 31–90

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_scl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket IN ('DPD_31_60','DPD_61_90');
```

### 16. Overdue amount DPD 90+

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_scl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_90P';
```

### 17. Cumulative write-off amount

```sql
SELECT SUM(writeoff_amt) FROM credit_mart.dws_scl_${region}_loan_writeoff_df
WHERE pt='${bizdate}';
```
