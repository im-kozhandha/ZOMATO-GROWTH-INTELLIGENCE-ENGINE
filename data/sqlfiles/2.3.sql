--Delivery spike: avg delivery time by city × period
SELECT
    o.city,
    o.city_tier,

    ROUND(AVG(CASE WHEN DATE(o.order_time) >= DATE('2024-03-31','-14 days')
              THEN d.delivery_time_min END), 1)   AS avg_delay_recent,

    ROUND(AVG(CASE WHEN DATE(o.order_time) <  DATE('2024-03-31','-14 days')
               AND  DATE(o.order_time) >= DATE('2024-03-31','-28 days')
              THEN d.delivery_time_min END), 1)   AS avg_delay_prior,

    ROUND(AVG(CASE WHEN DATE(o.order_time) >= DATE('2024-03-31','-14 days')
              THEN d.delay_flag END) * 100, 1)    AS delay_rate_recent_pct,

    ROUND(AVG(CASE WHEN DATE(o.order_time) <  DATE('2024-03-31','-14 days')
               AND  DATE(o.order_time) >= DATE('2024-03-31','-28 days')
              THEN d.delay_flag END) * 100, 1)    AS delay_rate_prior_pct

FROM orders o
JOIN delivery d ON o.order_id = d.order_id
GROUP BY o.city, o.city_tier
ORDER BY o.city_tier, delay_rate_recent_pct DESC;