---
topic: metric-sql
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# TL Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703436544

This page lists **17** Term Loan (TL) mart metrics: whitelist / invitation, application and offer acceptance, disbursement amount and count, borrower counts, tenor mix, repayment and outstanding, **DPD** buckets, prepayment, restructure, and write-off. SQL sketches reference `credit_mart.dws_tl_${region}_*` style tables per Confluence.

### 1. Cumulative TL-whitelisted / invited users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <tl_whitelist_condition>;
```

### 2. Cumulative TL-activated or onboarded users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <tl_onboarded_flag>;
```

### 3. Applications submitted count

```sql
SELECT COUNT(*) FROM credit_mart.dws_tl_${region}_application_df
WHERE pt='${bizdate}' AND app_status>='SUBMITTED';
```

### 4. Applications approved count

```sql
SELECT COUNT(*) FROM credit_mart.dws_tl_${region}_application_df
WHERE pt='${bizdate}' AND app_status='APPROVED';
```

### 5. Offers accepted leading to disbursement (count)

```sql
SELECT COUNT(*) FROM credit_mart.dws_tl_${region}_offer_df
WHERE pt='${bizdate}' AND offer_status='ACCEPTED';
```

### 6. Cumulative disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_tl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 7. Cumulative disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_tl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 8. Distinct TL borrowers

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_tl_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_status='SUCCESS';
```

### 9. Disbursement amount by tenor bucket

```sql
SELECT tenor_months, SUM(disburse_amt) FROM credit_mart.dws_tl_${region}_loan_disburse_df
WHERE pt='${bizdate}' GROUP BY 1;
```

### 10. Cumulative principal repaid

```sql
SELECT SUM(principal_repaid) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 11. Cumulative interest repaid

```sql
SELECT SUM(interest_repaid) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 12. Repayable principal EOP

```sql
SELECT SUM(repayable_principal) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 13. Outstanding principal EOP (amortizing schedule)

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_tl_${region}_loan_snapshot_df
WHERE pt='${bizdate}';
```

### 14. Overdue amount DPD 1–30

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_1_30';
```

### 15. Overdue amount DPD 31–90

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket IN ('DPD_31_60','DPD_61_90');
```

### 16. Overdue amount DPD 90+

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_tl_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_90P';
```

### 17. Cumulative write-off amount

```sql
SELECT SUM(writeoff_amt) FROM credit_mart.dws_tl_${region}_loan_writeoff_df
WHERE pt='${bizdate}';
```
