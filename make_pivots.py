import pandas as pd
import sqlite3

conn   = sqlite3.connect('data/zgie.db')
orders = pd.read_sql('SELECT * FROM orders',      conn)
deliv  = pd.read_sql('SELECT * FROM delivery',    conn)
rests  = pd.read_sql('SELECT * FROM restaurants', conn)
conn.close()

orders['order_time'] = pd.to_datetime(orders['order_time'])
orders['order_date'] = orders['order_time'].dt.date
orders['order_week'] = orders['order_time'].dt.strftime('%Y-%W')

# SQLite stores booleans as 0/1 integers — confirm and normalise
# is_crisis_period comes back as 0 or 1, not True/False
orders['is_crisis_period'] = orders['is_crisis_period'].astype(int)
deliv['is_crisis_period']  = deliv['is_crisis_period'].astype(int)

print("Orders columns :", list(orders.columns))
print("Delivery columns:", list(deliv.columns))

# ── Pivot 1: Orders + cancel rate by city × week ─────────
pv1 = orders.groupby(['city', 'city_tier', 'order_week']).agg(
    total_orders  = ('order_id',    'count'),
    cancelled     = ('status',      lambda x: (x == 'cancelled').sum()),
    total_revenue = ('order_value', 'sum')
).reset_index()
pv1['cancel_rate_pct'] = (pv1['cancelled'] / pv1['total_orders'] * 100).round(2)
pv1['total_revenue']   = pv1['total_revenue'].round(2)
pv1.to_csv('data/pivot1_orders_by_city_week.csv', index=False)
print(f"Pivot 1 saved: {len(pv1)} rows")

# ── Pivot 2: KPI summary by city × period ────────────────
# FIX: map on integers 0/1, not booleans
orders['period'] = orders['is_crisis_period'].map(
    {1: 'Crisis (last 14d)', 0: 'Prior period'}
)
pv2 = orders.groupby(['city', 'city_tier', 'period']).agg(
    total_orders  = ('order_id',    'count'),
    delivered     = ('status',      lambda x: (x == 'delivered').sum()),
    cancelled     = ('status',      lambda x: (x == 'cancelled').sum()),
    total_revenue = ('order_value', 'sum'),
    avg_order_val = ('order_value', 'mean')
).reset_index()
pv2['cancel_rate_pct']    = (pv2['cancelled'] / pv2['total_orders']  * 100).round(2)
pv2['completion_rate_pct']= (pv2['delivered'] / pv2['total_orders']  * 100).round(2)
pv2['total_revenue']      = pv2['total_revenue'].round(2)
pv2['avg_order_val']      = pv2['avg_order_val'].round(2)
pv2.to_csv('data/pivot2_kpi_by_city_period.csv', index=False)
print(f"Pivot 2 saved: {len(pv2)} rows")

# ── Pivot 3: Delivery by city × period ───────────────────
# FIX: merge only the columns we need from orders
# deliv already has city and is_crisis_period from generate_delivery
# but city_tier is NOT in deliv — pull it from orders
order_lookup = orders[['order_id', 'city_tier']].drop_duplicates()
merged = deliv.merge(order_lookup, on='order_id', how='left')

# FIX: map on integers
merged['period'] = merged['is_crisis_period'].map(
    {1: 'Crisis (last 14d)', 0: 'Prior period'}
)

print("Merged columns:", list(merged.columns))  # confirm city, city_tier, period exist

pv3 = merged.groupby(['city', 'city_tier', 'period']).agg(
    deliveries       = ('order_id',           'count'),
    avg_delivery_min = ('delivery_time_min',   'mean'),
    median_delivery  = ('delivery_time_min',   'median'),
    pct90_delivery   = ('delivery_time_min',   lambda x: x.quantile(0.90)),
    delay_count      = ('delay_flag',          'sum'),
    delay_rate_pct   = ('delay_flag',          'mean')
).reset_index()
pv3['avg_delivery_min']  = pv3['avg_delivery_min'].round(1)
pv3['median_delivery']   = pv3['median_delivery'].round(1)
pv3['pct90_delivery']    = pv3['pct90_delivery'].round(1)
pv3['delay_rate_pct']    = (pv3['delay_rate_pct'] * 100).round(2)
pv3.to_csv('data/pivot3_delivery_by_city_period.csv', index=False)
print(f"Pivot 3 saved: {len(pv3)} rows")

# ── Pivot 4: Daily trend ──────────────────────────────────
daily = orders[orders['order_time'] >= pd.Timestamp('2024-01-31')].copy()
pv4 = daily.groupby(['order_date', 'city_tier']).agg(
    orders        = ('order_id',    'count'),
    revenue       = ('order_value', 'sum'),
    cancellations = ('status',      lambda x: (x == 'cancelled').sum())
).reset_index()
pv4['cancel_rate_pct'] = (pv4['cancellations'] / pv4['orders'] * 100).round(2)
pv4['revenue']         = pv4['revenue'].round(2)
pv4.to_csv('data/pivot4_daily_trend.csv', index=False)
print(f"Pivot 4 saved: {len(pv4)} rows")

# ── Pivot 5: Restaurant rating vs performance ─────────────
ord_rest = orders.merge(
    rests[['restaurant_id', 'rating', 'avg_prep_time', 'cuisine_type']],
    on='restaurant_id'
)
ord_rest['rating_bucket'] = pd.cut(
    ord_rest['rating'],
    bins=[0, 3.0, 3.5, 4.0, 5.0],
    labels=['<3.0', '3.0-3.5', '3.5-4.0', '>4.0']
)
pv5 = ord_rest.groupby(['city', 'city_tier', 'rating_bucket'],
                        observed=True).agg(
    orders        = ('order_id',      'count'),
    avg_prep_min  = ('avg_prep_time', 'mean'),
    cancel_rate   = ('status',        lambda x: (x == 'cancelled').mean() * 100),
    avg_order_val = ('order_value',   'mean')
).reset_index()
pv5['avg_prep_min']    = pv5['avg_prep_min'].round(1)
pv5['cancel_rate']     = pv5['cancel_rate'].round(2)
pv5['avg_order_val']   = pv5['avg_order_val'].round(2)
pv5.to_csv('data/pivot5_restaurant_rating_performance.csv', index=False)
print(f"Pivot 5 saved: {len(pv5)} rows")

print("\n=== ALL PIVOTS COMPLETE ===")
print("Files saved in /data — ready for Power BI import")