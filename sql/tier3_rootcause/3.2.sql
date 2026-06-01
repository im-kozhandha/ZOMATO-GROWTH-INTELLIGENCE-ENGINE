--Delivery partner load: orders per partner by city
SELECT
    d.city,
    o.city_tier,
    COUNT(DISTINCT d.delivery_partner_id)               AS active_partners,
    COUNT(*)                                             AS total_deliveries,
    ROUND(COUNT(*) * 1.0 /
          COUNT(DISTINCT d.delivery_partner_id), 1)     AS deliveries_per_partner,
    ROUND(AVG(d.delivery_time_min), 1)                  AS avg_delivery_min
FROM delivery d
JOIN orders o ON d.order_id = o.order_id
GROUP BY d.city, o.city_tier
ORDER BY deliveries_per_partner DESC;