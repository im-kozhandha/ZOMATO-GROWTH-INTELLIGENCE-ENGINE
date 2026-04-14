--For each city, compare this week's orders vs last week's orders and calculate % change. Use a CTE.
WITH weekly AS (
    SELECT
        city,
        city_tier,
        strftime('%Y-%W', order_time)   AS year_week,
        COUNT(*)                         AS orders
    FROM orders
    GROUP BY city, city_tier, year_week
),
with_lag AS (
    SELECT
        city,
        city_tier,
        year_week,
        orders,
        LAG(orders, 1) OVER (
            PARTITION BY city
            ORDER BY year_week
        )                                AS prev_week_orders
    FROM weekly
)
SELECT
    city,
    city_tier,
    year_week,
    orders                                                  AS this_week,
    prev_week_orders                                        AS last_week,
    ROUND((orders - prev_week_orders) * 100.0
          / prev_week_orders, 1)                            AS pct_change
FROM with_lag
WHERE prev_week_orders IS NOT NULL
ORDER BY city, year_week;