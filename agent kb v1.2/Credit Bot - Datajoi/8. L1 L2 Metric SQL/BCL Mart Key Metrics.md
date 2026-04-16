---
topic: metric-sql
relevance: partial
language: en
source: confluence
last_reviewed: 2026-04-16
---

# BCL Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703430917

This page summarizes **20** Buyer Cashloan (BCL) mart metrics: whitelist and activation funnels, disbursement volume and counts, borrower universes, disbursement-request lifecycle (submitted / approved / disbursed outcomes), repayment and repayable exposure, **DPD** overdue buckets, and write-offs. Full production SQL lives in Confluence; below each metric is a short description and a minimal SQL sketch showing typical tables and `${region}` placeholders (`credit_uc.ads_${region}_uc_user_list_wide_df`, `credit_mart.dws_bcl_${region}_loan_repayment_df`, etc.).

### 1. The cumulative number of users who are whitelisted for BCL

Counts distinct users on the UC user list wide table with BCL whitelist / eligible flags as of the reporting date.

```sql
-- credit_uc.ads_${region}_uc_user_list_wide_df
SELECT COUNT(DISTINCT user_id) AS whitelist_users
FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt = '${bizdate}' AND <bcl_whitelist_condition>;
```

### 2. The cumulative number of BCL-activated users

Users who completed activation (e.g. KYC / contract) on or before the snapshot date.

```sql
SELECT COUNT(DISTINCT user_id) AS activated_users
FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt = '${bizdate}' AND <bcl_activated_flag>;
```

### 3. Cumulative BCL disbursement amount

Sum of disbursed principal (or contract amount, per mart definition) for successful disbursements.

```sql
SELECT SUM(disburse_amount) AS cum_disburse_amt
FROM credit_mart.dws_bcl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 4. Cumulative BCL disbursement count

Count of successful disbursement events / loans.

```sql
SELECT COUNT(*) AS cum_disburse_cnt
FROM credit_mart.dws_bcl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 5. Cumulative number of distinct BCL borrowers

Distinct users with at least one successful disbursement.

```sql
SELECT COUNT(DISTINCT user_id) AS borrowers
FROM credit_mart.dws_bcl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 6. Disbursement requests submitted (count)

DR records entering “submitted” state in the window / cumulatively (per Confluence grain).

```sql
SELECT COUNT(*) FROM credit_mart.dws_bcl_${region}_disburse_request_df
WHERE pt = '${bizdate}' AND request_stage = 'SUBMITTED';
```

### 7. Disbursement requests approved (count)

DR approved by risk / policy before payout.

```sql
SELECT COUNT(*) FROM credit_mart.dws_bcl_${region}_disburse_request_df
WHERE pt = '${bizdate}' AND request_stage = 'APPROVED';
```

### 8. Disbursement requests with disburse success (count)

DR that reached successful disbursement linkage.

```sql
SELECT COUNT(*) FROM credit_mart.dws_bcl_${region}_disburse_request_df
WHERE pt = '${bizdate}' AND disburse_result = 'SUCCESS';
```

### 9. Disbursement requests with disburse failure (count)

Failed payout or reversed disburse outcomes (if defined separately).

```sql
SELECT COUNT(*) FROM credit_mart.dws_bcl_${region}_disburse_request_df
WHERE pt = '${bizdate}' AND disburse_result = 'FAILED';
```

### 10. Cumulative repaid amount (cash / principal component)

Actual repayments posted, aligned with mart amortization rules.

```sql
SELECT SUM(repaid_amount) AS cum_repaid_amt
FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 11. Outstanding repayable principal (EOP)

End-of-period repayable principal before write-off adjustments.

```sql
SELECT SUM(repayable_principal) AS repayable_principal_eop
FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 12. Repayable amount including interest/fees (if split in mart)

Total repayable exposure per loan snapshot fields.

```sql
SELECT SUM(repayable_total) AS repayable_total_eop
FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 13. Overdue amount — DPD 1–30 bucket

Overdue principal (or total overdue) in 1–30 days past due.

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_1_30';
```

### 14. Overdue amount — DPD 31–60 bucket

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_31_60';
```

### 15. Overdue amount — DPD 61–90 bucket

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_61_90';
```

### 16. Overdue amount — DPD 90+ bucket

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_90P';
```

### 17. Borrower-weighted overdue exposure (optional mart view)

Distinct borrowers with any overdue balance in bucket.

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_bcl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND overdue_amt > 0;
```

### 18. Cumulative write-off amount

Charged-off principal / balance per accounting policy.

```sql
SELECT SUM(writeoff_amount) AS cum_writeoff_amt
FROM credit_mart.dws_bcl_${region}_loan_writeoff_df
WHERE pt = '${bizdate}';
```

### 19. Cumulative write-off count (loans / accounts)

```sql
SELECT COUNT(*) FROM credit_mart.dws_bcl_${region}_loan_writeoff_df
WHERE pt = '${bizdate}' AND writeoff_status = 'WRITTEN_OFF';
```

### 20. Net book after write-off reconciliation (if provided as separate metric)

Post-write-off outstanding or recovery-adjusted balance—see Confluence for exact join keys between repayment and write-off snapshots.

```sql
-- Illustrative join between repayment snapshot and writeoff event table
SELECT SUM(r.repayable_principal) - COALESCE(SUM(w.writeoff_amount),0)
FROM credit_mart.dws_bcl_${region}_loan_repayment_df r
LEFT JOIN credit_mart.dws_bcl_${region}_loan_writeoff_df w
  ON r.loan_id = w.loan_id AND r.pt = w.pt
WHERE r.pt = '${bizdate}';
```
