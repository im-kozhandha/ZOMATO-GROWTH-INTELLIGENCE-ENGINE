--for each date in the last 30 days, show order count and total revenue.
select date(order_time) as order_date, count(*) as daily_orders, round(sum(order_value),2) as daily_revenue from orders where Date(order_time) >= Date('2024-03-31', '-30 days') group by date(order_time) order by order_date;
