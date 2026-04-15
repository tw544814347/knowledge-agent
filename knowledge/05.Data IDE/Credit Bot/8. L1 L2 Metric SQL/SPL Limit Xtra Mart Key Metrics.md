# SPL Limit Xtra Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703435734

This page covers **17** SPL Limit Xtra (CHP / handphone loan) mart metrics: eligibility and line assignment, checkout and financing attach rates, disbursement and repayment, outstanding and **DPD** buckets, device or SKU-level aggregates where applicable, and write-offs. SQL below uses illustrative `credit_mart.dws_spl_xtra_${region}_*` names—match Confluence naming exactly.

### 1. Users with Xtra line offered / visible

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_spl_xtra_${region}_user_line_df
WHERE pt='${bizdate}' AND line_status IN ('OFFERED','ACTIVE');
```

### 2. Users with active Xtra limit

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_spl_xtra_${region}_user_line_df
WHERE pt='${bizdate}' AND line_status='ACTIVE';
```

### 3. Aggregate Xtra credit limit

```sql
SELECT SUM(credit_limit) FROM credit_mart.dws_spl_xtra_${region}_user_line_df
WHERE pt='${bizdate}' AND line_status='ACTIVE';
```

### 4. Checkout orders eligible for Xtra (count)

```sql
SELECT COUNT(DISTINCT order_id) FROM credit_mart.dws_spl_xtra_${region}_checkout_df
WHERE pt='${bizdate}' AND xtra_eligible=1;
```

### 5. Orders financed with Xtra (count)

```sql
SELECT COUNT(DISTINCT order_id) FROM credit_mart.dws_spl_xtra_${region}_checkout_df
WHERE pt='${bizdate}' AND finance_channel='XTRA';
```

### 6. Financed GMV / principal for Xtra orders

```sql
SELECT SUM(financed_amt) FROM credit_mart.dws_spl_xtra_${region}_checkout_df
WHERE pt='${bizdate}' AND finance_channel='XTRA';
```

### 7. Cumulative disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_spl_xtra_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND status='SUCCESS';
```

### 8. Cumulative disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND status='SUCCESS';
```

### 9. Distinct financed users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_spl_xtra_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND status='SUCCESS';
```

### 10. Period disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_disburse_df
WHERE pt='${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 11. Cumulative repayment amount

```sql
SELECT SUM(repay_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 12. Repayable principal EOP

```sql
SELECT SUM(repayable_principal) FROM credit_mart.dws_spl_xtra_${region}_loan_repayment_df
WHERE pt='${bizdate}';
```

### 13. Outstanding principal EOP

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_spl_xtra_${region}_loan_snapshot_df
WHERE pt='${bizdate}';
```

### 14. Overdue amount DPD 1–30

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_1_30';
```

### 15. Overdue amount DPD 31–60

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_31_60';
```

### 16. Overdue amount DPD 61+

```sql
SELECT SUM(overdue_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_repayment_df
WHERE pt='${bizdate}' AND dpd_bucket IN ('DPD_61_90','DPD_90P');
```

### 17. Cumulative write-off amount

```sql
SELECT SUM(writeoff_amt) FROM credit_mart.dws_spl_xtra_${region}_loan_writeoff_df
WHERE pt='${bizdate}';
```
