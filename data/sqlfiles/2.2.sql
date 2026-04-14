--last 14 days vs prior 14 days per city
SELECT
    city,
    city_tier,

    -- Order counts
    SUM(CASE WHEN DATE(order_time) >= DATE('2024-03-31','-14 days')
        THEN 1 ELSE 0 END)                                      AS orders_recent,

    SUM(CASE WHEN DATE(order_time) <  DATE('2024-03-31','-14 days')
         AND  DATE(order_time) >= DATE('2024-03-31','-28 days')
        THEN 1 ELSE 0 END)                                      AS orders_prior,

    -- % change in orders
    ROUND(
        (SUM(CASE WHEN DATE(order_time) >= DATE('2024-03-31','-14 days')
             THEN 1.0 ELSE 0 END) -
         SUM(CASE WHEN DATE(order_time) <  DATE('2024-03-31','-14 days')
              AND  DATE(order_time) >= DATE('2024-03-31','-28 days')
             THEN 1.0 ELSE 0 END))
        * 100.0 /
        NULLIF(SUM(CASE WHEN DATE(order_time) <  DATE('2024-03-31','-14 days')
                    AND  DATE(order_time) >= DATE('2024-03-31','-28 days')
                   THEN 1.0 ELSE 0 END), 0)
    , 1)                                                        AS order_pct_change,

    -- Cancellation rates
    ROUND(AVG(CASE WHEN DATE(order_time) >= DATE('2024-03-31','-14 days')
              AND status = 'cancelled' THEN 1.0 ELSE 0 END) * 100, 1)  AS cancel_recent_pct,

    ROUND(AVG(CASE WHEN DATE(order_time) <  DATE('2024-03-31','-14 days')
               AND DATE(order_time) >= DATE('2024-03-31','-28 days')
              AND status = 'cancelled' THEN 1.0 ELSE 0 END) * 100, 1)  AS cancel_prior_pct

FROM orders
GROUP BY city, city_tier
ORDER BY city_tier, order_pct_change;