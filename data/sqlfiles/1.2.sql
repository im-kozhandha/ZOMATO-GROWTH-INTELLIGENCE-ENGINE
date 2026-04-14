--for each city, show total orders, cancelled count, and cancellation rate as a percentage.
Select city,count(*) AS total_orders, sum(Case when status='cancelled' then 1 else 0 end) as cancelled, round(sum(case when status='cancelled' then 1 else 0 end)*100/ Count(*),2) as cancel_rate_pct From orders GROUP by city order by cancel_rate_pct DESC;
