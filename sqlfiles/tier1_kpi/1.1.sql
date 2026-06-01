--for each city, show total orders, total revenue, avg order value, sorted by total orders descending.
SELECT city, count(*) AS total_orders,round(sum(order_value),2) AS total_revenue, round(avg(order_value),2) AS avg_order_value FROM orders GROUP By city ORDER by total_orders DESC;


