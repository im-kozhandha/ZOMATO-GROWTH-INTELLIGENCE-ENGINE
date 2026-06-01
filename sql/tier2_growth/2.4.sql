WITH user_cohorts AS (
    SELECT
        u.user_id,
        u.city_tier,
        strftime('%Y-%W', u.signup_date)    AS cohort_week,
        strftime('%Y-%W', o.order_time)     AS order_week,
        CAST(strftime('%W', o.order_time) AS INT) -
        CAST(strftime('%W', u.signup_date) AS INT)  AS weeks_since_signup
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
),
cohort_sizes AS (
    SELECT
        cohort_week,
        city_tier,
        COUNT(DISTINCT user_id)     AS cohort_size
    FROM user_cohorts
    GROUP BY cohort_week, city_tier
)
SELECT
    uc.cohort_week,
    uc.city_tier,
    cs.cohort_size,
    ROUND(COUNT(DISTINCT CASE WHEN uc.weeks_since_signup = 1
          THEN uc.user_id END) * 100.0 / cs.cohort_size, 1)   AS week1_retention,
    ROUND(COUNT(DISTINCT CASE WHEN uc.weeks_since_signup = 2
          THEN uc.user_id END) * 100.0 / cs.cohort_size, 1)   AS week2_retention,
    ROUND(COUNT(DISTINCT CASE WHEN uc.weeks_since_signup = 4
          THEN uc.user_id END) * 100.0 / cs.cohort_size, 1)   AS week4_retention
FROM user_cohorts uc
JOIN cohort_sizes cs
    ON uc.cohort_week = cs.cohort_week
    AND uc.city_tier  = cs.city_tier
GROUP BY uc.cohort_week, uc.city_tier, cs.cohort_size
ORDER BY uc.cohort_week, uc.city_tier;