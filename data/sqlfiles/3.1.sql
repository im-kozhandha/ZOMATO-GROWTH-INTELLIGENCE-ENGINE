--Restaurant rating vs cancellation rate
SELECT
    CASE
        WHEN r.rating < 3.0 THEN '1. Below 3.0'
        WHEN r.rating < 3.5 THEN '2. 3.0 – 3.5'
        WHEN r.rating < 4.0 THEN '3. 3.5 – 4.0'
        ELSE                     '4. Above 4.0'
    END                                                         AS rating_bucket,
    COUNT(*)                                                    AS total_orders,
    ROUND(AVG(r.avg_prep_time), 1)                             AS avg_prep_min,
    ROUND(AVG(CASE WHEN o.status='cancelled'
               THEN 1.0 ELSE 0 END) * 100, 2)                 AS cancel_rate_pct,
    ROUND(AVG(CASE WHEN o.is_crisis_period = 1
               AND o.status='cancelled'
               THEN 1.0 ELSE 0 END) * 100, 2)                 AS crisis_cancel_pct
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY rating_bucket
ORDER BY rating_bucket;