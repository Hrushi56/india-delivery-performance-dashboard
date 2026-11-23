-- Source rows represent items. Collapse repeated shipping attributes per order.
-- The unique index rejects conflicting records instead of counting an order twice.
CREATE TABLE orders AS
SELECT DISTINCT order_id, CASE state
    WHEN 'Guyarat' THEN 'Gujarat' WHEN 'Bengala Occidental' THEN 'West Bengal'
    WHEN 'Rajastán' THEN 'Rajasthan' WHEN 'Punyab' THEN 'Punjab'
    WHEN 'Jammu y Cachemira' THEN 'Jammu and Kashmir' ELSE state END AS state,
    mode, actual, scheduled,
       MAX(actual - scheduled, 0) AS days_late
FROM lines
WHERE status IN ('Late delivery', 'Advance shipping', 'Shipping on time');
CREATE UNIQUE INDEX orders_key ON orders(order_id);

CREATE VIEW performance AS
SELECT state, mode, COUNT(*) AS orders, SUM(days_late > 0) AS late,
       SUM(days_late) AS excess_days
FROM orders
GROUP BY state, mode;
