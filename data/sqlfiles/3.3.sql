--The full diagnostic: city × period × restaurant quality combined
SELECT
    o.city,
    o.city_tier,
    o.is_crisis_period,
    COUNT(*)                                                    AS orders,
    ROUND(AVG(r.rating), 2)                                    AS avg_restaurant_rating,
    ROUND(AVG(r.avg_prep_time), 1)                             AS avg_prep_min,
    ROUND(AVG(d.delivery_time_min), 1)                         AS avg_delivery_min,
    ROUND(AVG(CASE WHEN o.status='cancelled'
               THEN 1.0 ELSE 0 END) * 100, 1)                 AS cancel_rate_pct,
    ROUND(AVG(d.delay_flag) * 100, 1)                          AS delay_rate_pct
FROM orders o
JOIN restaurants r  ON o.restaurant_id = r.restaurant_id
LEFT JOIN delivery d ON o.order_id = d.order_id
GROUP BY o.city, o.city_tier, o.is_crisis_period
ORDER BY o.city_tier DESC, o.city, o.is_crisis_period;