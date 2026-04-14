--join orders and delivery, show avg delivery time per city for delivered orders only.
SELECT
    o.city,
    o.city_tier,
    ROUND(AVG(d.delivery_time_min), 1)    AS avg_delivery_min,
    COUNT(*)                               AS delivered_orders
FROM orders o
INNER JOIN delivery d ON o.order_id = d.order_id
WHERE o.status = 'delivered'
GROUP BY o.city, o.city_tier
ORDER BY avg_delivery_min DESC;
