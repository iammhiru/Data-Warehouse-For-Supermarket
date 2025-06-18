DROP TABLE IF EXISTS warehouse.sales_overview_table;

CREATE TABLE warehouse.sales_overview_table AS
SELECT 
  fs.sale_key,
  d.date,
  d.year,
  d.month,
  d.day,
  i.item_name,
  i.category_name,
  tt.tran_type,
  df.discount_flag,
  fs.quantity_kilo,
  fs.unit_price,
  fs.total_amount
FROM warehouse.fact_sales fs
JOIN warehouse.dim_date d ON fs.date_key = d.date_key
JOIN warehouse.dim_item i ON fs.item_key = i.item_key
JOIN warehouse.dim_transaction_type tt ON fs.tran_type_key = tt.tran_type_key
JOIN warehouse.dim_discount_flag df ON fs.discount_flag_key = df.discount_flag_key;
