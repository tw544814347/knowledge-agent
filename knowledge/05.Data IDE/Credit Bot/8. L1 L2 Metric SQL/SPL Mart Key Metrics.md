# SPL Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2703434836

This page summarizes **19** Shopee Pay Later (SPL) mart metrics: user funnel (eligible, activated, transacting), credit lines and utilization, order-level financed GMV, billing cycle performance, repayment and outstanding, **DPD** delinquency, charge-off, and engagement ratios. Illustrative SQL uses `credit_mart.dws_spl_${region}_*`; verify joins to checkout / BNPL order facts in Confluence.

### 1. Cumulative SPL-eligible users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <spl_eligible_flag>;
```

### 2. Cumulative SPL-activated users

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_uc.ads_${region}_uc_user_list_wide_df
WHERE pt='${bizdate}' AND <spl_activated_flag>;
```

### 3. Users with active SPL limit

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_spl_${region}_user_limit_df
WHERE pt='${bizdate}' AND limit_status='ACTIVE';
```

### 4. Aggregate SPL limit (EOP)

```sql
SELECT SUM(credit_limit) FROM credit_mart.dws_spl_${region}_user_limit_df
WHERE pt='${bizdate}' AND limit_status='ACTIVE';
```

### 5. Utilized limit (outstanding-based)

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_spl_${region}_loan_snapshot_df
WHERE pt='${bizdate}' AND loan_status='ACTIVE';
```

### 6. Limit utilization ratio

```sql
SELECT SUM(s.outstanding_principal)/NULLIF(SUM(l.credit_limit),0)
FROM credit_mart.dws_spl_${region}_loan_snapshot_df s
JOIN credit_mart.dws_spl_${region}_user_limit_df l USING(user_id)
WHERE s.pt='${bizdate}' AND l.pt='${bizdate}';
```

### 7. Period transacting users (SPL checkout)

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_spl_${region}_order_df
WHERE pt='${bizdate}' AND order_date BETWEEN '${start}' AND '${end}' AND spl_used=1;
```

### 8. Period order count (SPL-financed)

```sql
SELECT COUNT(DISTINCT order_id) FROM credit_mart.dws_spl_${region}_order_df
WHERE pt='${bizdate}' AND order_date BETWEEN '${start}' AND '${end}' AND spl_used=1;
```

### 9. Period financed GMV / billed amount

```sql
SELECT SUM(financed_amt) FROM credit_mart.dws_spl_${region}_order_df
WHERE pt='${bizdate}' AND order_date BETWEEN '${start}' AND '${end}' AND spl_used=1;
```

### 10. Statement generated count

```sql
SELECT COUNT(*) FROM credit_mart.dws_spl_${region}_billing_statement_df
WHERE pt='${bizdate}' AND stmt_date BETWEEN '${start}' AND '${end}';
```

### 11. Statement billed principal + interest

```sql
SELECT SUM(billed_amt) FROM credit_mart.dws_spl_${region}_billing_statement_df
WHERE pt='${bizdate}' AND stmt_date BETWEEN '${start}' AND '${end}';
```

### 12. Repayment success count

```sql
SELECT COUNT(*) FROM credit_mart.dws_spl_${region}_repayment_df
WHERE pt='${bizdate}' AND repay_status='SUCCESS';
```

### 13. Repayment success amount

```sql
SELECT SUM(repay_amt) FROM credit_mart.dws_spl_${region}_repayment_df
WHERE pt='${bizdate}' AND repay_status='SUCCESS';
```

### 14. Past-due amount at statement level (bucket 1–30)

```sql
SELECT SUM(past_due_amt) FROM credit_mart.dws_spl_${region}_billing_statement_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_1_30';
```

### 15. Past-due amount — DPD 31–60

```sql
SELECT SUM(past_due_amt) FROM credit_mart.dws_spl_${region}_billing_statement_df
WHERE pt='${bizdate}' AND dpd_bucket='DPD_31_60';
```

### 16. Past-due amount — DPD 61+

```sql
SELECT SUM(past_due_amt) FROM credit_mart.dws_spl_${region}_billing_statement_df
WHERE pt='${bizdate}' AND dpd_bucket IN ('DPD_61_90','DPD_90P');
```

### 17. Outstanding receivable EOP

```sql
SELECT SUM(outstanding_total) FROM credit_mart.dws_spl_${region}_loan_snapshot_df
WHERE pt='${bizdate}';
```

### 18. Charge-off / write-off amount (cumulative)

```sql
SELECT SUM(writeoff_amt) FROM credit_mart.dws_spl_${region}_writeoff_df
WHERE pt='${bizdate}';
```

### 19. Net flow rate — new disburse vs repayment (period)

```sql
SELECT SUM(new_financed)-SUM(repay_amt) AS net_flow
FROM credit_mart.dws_spl_${region}_cashflow_df WHERE pt='${bizdate}';
```
