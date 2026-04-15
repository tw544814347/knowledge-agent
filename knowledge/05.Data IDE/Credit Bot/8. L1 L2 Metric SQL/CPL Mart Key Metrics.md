# CPL Mart Key Metrics -- SQL Logic

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=2723828697

This page indexes **42** Corporate Loan (CPL) mart metrics from Confluence: disbursement counts and amounts (cumulative and periodic), repayment flows, outstanding / delinquency views, order and **GMV** constructs (financed GMV, basket GMV, order-linked amounts), and related funnel KPIs. Each section below states the business meaning and a **minimal** `credit_mart` / order-domain SQL sketch; replace table names, join keys, and filters with the authoritative definitions in Confluence.

### 1. Cumulative CPL disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND status = 'SUCCESS';
```

### 2. Cumulative CPL disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_cpl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND status = 'SUCCESS';
```

### 3. Period CPL disbursement count (e.g. daily / monthly)

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 4. Period CPL disbursement amount

```sql
SELECT SUM(disburse_amt) FROM credit_mart.dws_cpl_${region}_loan_disburse_df
WHERE pt = '${bizdate}' AND disburse_date BETWEEN '${start}' AND '${end}';
```

### 5. Cumulative repayment count (installments / events)

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND repayment_status = 'POSTED';
```

### 6. Cumulative repayment amount (total cash in)

```sql
SELECT SUM(repayment_amt) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND repayment_status = 'POSTED';
```

### 7. Cumulative principal repaid

```sql
SELECT SUM(principal_repaid) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 8. Cumulative interest / fee repaid

```sql
SELECT SUM(interest_repaid + fee_repaid) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}';
```

### 9. Early repayment count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND early_repay_flag = 1;
```

### 10. Early repayment amount

```sql
SELECT SUM(repayment_amt) FROM credit_mart.dws_cpl_${region}_loan_repayment_df
WHERE pt = '${bizdate}' AND early_repay_flag = 1;
```

### 11. End-of-period outstanding principal

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}';
```

### 12. End-of-period outstanding total (principal + interest + fee)

```sql
SELECT SUM(outstanding_total) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}';
```

### 13. Outstanding financed GMV linked exposure

```sql
SELECT SUM(financed_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}' AND loan_status = 'ACTIVE';
```

### 14. Count of active CPL loans

```sql
SELECT COUNT(DISTINCT loan_id) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND loan_status = 'ACTIVE';
```

### 15. Count of active CPL borrowers

```sql
SELECT COUNT(DISTINCT user_id) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND loan_status = 'ACTIVE';
```

### 16. PAR30 outstanding amount (example bucket)

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND dpd BETWEEN 1 AND 30;
```

### 17. PAR60 outstanding amount

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND dpd BETWEEN 31 AND 60;
```

### 18. PAR90+ outstanding amount

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND dpd >= 90;
```

### 19. New borrower disbursement count (first-ever CPL loan)

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_disburse_df d
WHERE pt = '${bizdate}' AND is_first_cpl_loan = 1;
```

### 20. Repeat borrower disbursement count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_disburse_df d
WHERE pt = '${bizdate}' AND is_first_cpl_loan = 0;
```

### 21. Credit limit granted (EOP aggregate)

```sql
SELECT SUM(credit_limit) FROM credit_mart.dws_cpl_${region}_user_limit_df
WHERE pt = '${bizdate}';
```

### 22. Limit utilization rate (disbursed / limit)

```sql
SELECT SUM(d.disburse_amt) / NULLIF(SUM(l.credit_limit),0)
FROM credit_mart.dws_cpl_${region}_loan_disburse_df d
JOIN credit_mart.dws_cpl_${region}_user_limit_df l USING (user_id)
WHERE d.pt = '${bizdate}' AND l.pt = '${bizdate}';
```

### 23. Application submitted count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_application_df
WHERE pt = '${bizdate}' AND app_status >= 'SUBMITTED';
```

### 24. Application approval count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_application_df
WHERE pt = '${bizdate}' AND app_status = 'APPROVED';
```

### 25. Application rejection count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_application_df
WHERE pt = '${bizdate}' AND app_status = 'REJECTED';
```

### 26. Approval rate (approved / submitted)

Ratio metric; exact denominator from Confluence (dedupe rules).

```sql
SELECT SUM(CASE WHEN app_status='APPROVED' THEN 1 END) * 1.0
     / NULLIF(SUM(CASE WHEN app_status>='SUBMITTED' THEN 1 END),0)
FROM credit_mart.dws_cpl_${region}_application_df WHERE pt='${bizdate}';
```

### 27. Placed orders count (CPL-tagged)

```sql
SELECT COUNT(DISTINCT order_id) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}' AND order_status = 'PLACED';
```

### 28. Placed order GMV (gross merchandise value)

```sql
SELECT SUM(order_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}' AND order_status = 'PLACED';
```

### 29. Financed GMV on disbursed loans

```sql
SELECT SUM(financed_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}' AND finance_status = 'DISBURSED';
```

### 30. Basket GMV including non-financed lines (if defined)

```sql
SELECT SUM(basket_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}';
```

### 31. Average order GMV (AOV)

```sql
SELECT AVG(order_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt = '${bizdate}' AND order_status = 'PLACED';
```

### 32. Financed share of GMV (financed / basket)

```sql
SELECT SUM(financed_gmv)/NULLIF(SUM(basket_gmv),0)
FROM credit_mart.dws_cpl_${region}_order_finance_df WHERE pt='${bizdate}';
```

### 33. Interest accrual (period)

```sql
SELECT SUM(interest_accrued) FROM credit_mart.dws_cpl_${region}_loan_accrual_df
WHERE pt = '${bizdate}' AND accrual_date BETWEEN '${start}' AND '${end}';
```

### 34. Fee income (period)

```sql
SELECT SUM(fee_amt) FROM credit_mart.dws_cpl_${region}_fee_df
WHERE pt = '${bizdate}' AND fee_date BETWEEN '${start}' AND '${end}';
```

### 35. Roll rate — current to 30 DPD (cohort style)

Cohort logic per Confluence vintage tables; placeholder snapshot join.

```sql
-- Use dws_cpl_${region}_dpd_roll_df or equivalent from Confluence
SELECT * FROM credit_mart.dws_cpl_${region}_dpd_roll_df WHERE pt='${bizdate}';
```

### 36. Cure rate from 30 DPD

```sql
SELECT * FROM credit_mart.dws_cpl_${region}_dpd_cure_df WHERE pt='${bizdate}';
```

### 37. Restructured loan count

```sql
SELECT COUNT(*) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND restructure_flag = 1;
```

### 38. Restructured outstanding amount

```sql
SELECT SUM(outstanding_principal) FROM credit_mart.dws_cpl_${region}_loan_snapshot_df
WHERE pt = '${bizdate}' AND restructure_flag = 1;
```

### 39. Vintage disbursement amount by origination month

```sql
SELECT DATE_TRUNC('month', disburse_date) m, SUM(disburse_amt)
FROM credit_mart.dws_cpl_${region}_loan_disburse_df
WHERE pt='${bizdate}' GROUP BY 1;
```

### 40. Vintage cumulative loss rate proxy

```sql
SELECT origination_month, SUM(writeoff_amt)/NULLIF(SUM(disburse_amt),0)
FROM credit_mart.dws_cpl_${region}_vintage_loss_df WHERE pt='${bizdate}' GROUP BY 1;
```

### 41. Merchant / corporate account order GMV (entity grain)

```sql
SELECT corporate_id, SUM(order_gmv) FROM credit_mart.dws_cpl_${region}_order_finance_df
WHERE pt='${bizdate}' GROUP BY 1;
```

### 42. Multi-order users in period (engagement)

```sql
SELECT COUNT(*) FROM (
  SELECT user_id FROM credit_mart.dws_cpl_${region}_order_finance_df
  WHERE pt='${bizdate}' GROUP BY 1 HAVING COUNT(DISTINCT order_id) > 1
) t;
```
