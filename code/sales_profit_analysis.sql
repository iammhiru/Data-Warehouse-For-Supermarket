DROP TABLE IF EXISTS warehouse.sale_profit_analysis;

CREATE TABLE warehouse.sale_profit_analysis AS
SELECT
  fs.sale_key,
  d.date,
  d.year,
  d.month,
  i.item_name,
  i.category_name,
  fs.quantity_kilo,
  fs.unit_price,
  fs.total_amount,
  ws.wholesale_price,
  ls.loss_rate,
  (ws.wholesale_price * (1 + ls.loss_rate / 100)) AS real_cost_per_kg,
  (fs.quantity_kilo * ws.wholesale_price * (1 + ls.loss_rate / 100)) AS estimated_cost,
  (fs.total_amount - (fs.quantity_kilo * ws.wholesale_price * (1 + ls.loss_rate / 100))) AS gross_profit
FROM warehouse.fact_sales fs
JOIN warehouse.dim_transaction_type tt ON fs.tran_type_key = tt.tran_type_key
JOIN warehouse.dim_item i ON fs.item_key = i.item_key
JOIN warehouse.dim_date d ON fs.date_key = d.date_key
JOIN warehouse.fact_wholesale ws ON fs.item_key = ws.item_key AND fs.date_key = ws.date_key
JOIN warehouse.fact_loss ls ON fs.item_key = ls.item_key
WHERE tt.tran_type = 'sale';
