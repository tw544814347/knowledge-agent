# FES Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703437079

This page summarizes **14** Fast Escrow (FES) mart metrics aligned with Confluence: whitelist and activation populations, disbursement amounts and counts, borrower counts, repayable / repaid balances, **DPD** overdue buckets, and write-off amounts. Table names follow the `credit_uc.ads_${region}_uc_user_list_wide_df` and `credit_mart.dws_fes_${region}_*` pattern; confirm exact mart suffixes in Confluence.

### 1. The cumulative number of users who are whitelisted for FES

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt = '${bizdate}' AND <fes_whitelist_condition>;
```

### 2. The cumulative number of FES-activated users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt = '${bizdate}' AND <fes_activated_flag>;
```

### 3. Cumulative FES disbursement amount

```sql
SELECT SUM(disburse_amount) FROM credit_mart.dws_fes_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 4. Cumulative FES disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_fes_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 5. Cumulative number of distinct FES borrowers

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_fes_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_status = 'SUCCESS';
```

### 6. Period FES disbursement amount

```sql
SELECT SUM(disburse_amount) FROM credit_mart.dws_fes_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 7. Period FES disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_fes_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 8. Cumulative repaid amount

```sql
SELECT SUM(repaid_amount) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 9. End-of-period repayable principal

```sql
SELECT SUM(repayable_principal) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 10. End-of-period repayable total (if split)

```sql
SELECT SUM(repayable_total) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 11. Overdue amount — DPD 1–30

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_1_30';
```

### 12. Overdue amount — DPD 31–60

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket = 'DPD_31_60';
```

### 13. Overdue amount — DPD 61+ (or 90+ per mart)

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_fes_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND dpd_bucket IN ('DPD_61_90','DPD_90P');
```

### 14. Cumulative write-off amount

```sql
SELECT SUM(writeoff_amount) FROM credit_mart.dws_fes_${region}_loan_writeoff_df
WHERE pt = '${bizdate}';
```
