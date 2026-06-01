--show what percentage of delivered orders had delay_flag = 1, per city.
SELECT
    o.city,
    o.city_tier,
    COUNT(*)                                           AS delivered,
    SUM(d.delay_flag)                                  AS delayed_count,
    ROUND(SUM(d.delay_flag) * 100.0 / COUNT(*), 2)    AS delay_rate_pct
FROM orders o
INNER JOIN delivery d ON o.order_id = d.order_id
WHERE o.status = 'delivered'
GROUP BY o.city, o.city_tier
ORDER BY delay_rate_pct DESC;