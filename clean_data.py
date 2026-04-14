import pandas as pd
import numpy as np
import sqlite3

# ── Load from SQLite ──────────────────────────────────────
conn   = sqlite3.connect('data/zgie.db')
orders = pd.read_sql('SELECT * FROM orders',       conn)
deliv  = pd.read_sql('SELECT * FROM delivery',     conn)
users  = pd.read_sql('SELECT * FROM users',        conn)
rests  = pd.read_sql('SELECT * FROM restaurants',  conn)
conn.close()

print("=== RAW DATA SHAPES ===")
for name, df in [('orders',orders),('delivery',deliv),('users',users),('restaurants',rests)]:
    print(f"  {name}: {df.shape[0]} rows × {df.shape[1]} cols")

# ── NULL audit ────────────────────────────────────────────
print("\n=== NULL AUDIT ===")
for name, df in [('orders',orders),('delivery',deliv),('users',users),('restaurants',rests)]:
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if len(nulls):
        print(f"\n{name}:")
        for col, n in nulls.items():
            print(f"  {col}: {n} nulls ({n/len(df)*100:.1f}%)")
    else:
        print(f"\n{name}: no nulls ✓")

# ── Outlier detection: delivery_time_min ─────────────────
print("\n=== OUTLIER DETECTION: delivery_time_min ===")
Q1  = deliv['delivery_time_min'].quantile(0.25)
Q3  = deliv['delivery_time_min'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = deliv[(deliv['delivery_time_min'] < lower) |
                 (deliv['delivery_time_min'] > upper)]

print(f"  Q1={Q1:.1f}  Q3={Q3:.1f}  IQR={IQR:.1f}")
print(f"  Lower fence: {lower:.1f}   Upper fence: {upper:.1f}")
print(f"  Outliers detected: {len(outliers)} rows ({len(outliers)/len(deliv)*100:.1f}%)")
print(f"  Max value: {deliv['delivery_time_min'].max()}")
print(f"  Decision: cap at upper fence (plausible but extreme, not errors)")

# Cap outliers — winsorize
deliv['delivery_time_min_clean'] = deliv['delivery_time_min'].clip(lower, upper)
deliv['is_outlier_delivery']     = ((deliv['delivery_time_min'] < lower) |
                                    (deliv['delivery_time_min'] > upper)).astype(int)

# ── Outlier detection: order_value ───────────────────────
print("\n=== OUTLIER DETECTION: order_value ===")
Q1o  = orders['order_value'].quantile(0.25)
Q3o  = orders['order_value'].quantile(0.75)
IQRo = Q3o - Q1o
uppero = Q3o + 1.5 * IQRo

out_orders = orders[orders['order_value'] > uppero]
print(f"  Upper fence: ₹{uppero:.2f}")
print(f"  High-value orders: {len(out_orders)} ({len(out_orders)/len(orders)*100:.1f}%)")
print(f"  Decision: flag only — large orders are plausible, not errors")
orders['is_high_value'] = (orders['order_value'] > uppero).astype(int)

# ── Structural NULL documentation ────────────────────────
cancelled_with_delivery = orders[orders['status']=='cancelled']['order_id'].isin(
    deliv['order_id']).sum()
print(f"\n=== STRUCTURAL NULL CHECK ===")
print(f"  Cancelled orders with delivery record: {cancelled_with_delivery}")
print(f"  (Expected: 0 — cancelled orders correctly have no delivery row)")

# ── Data quality summary ──────────────────────────────────
print("\n=== DATA QUALITY REPORT ===")
print(f"  Total orders:          {len(orders):,}")
print(f"  Delivered orders:      {(orders['status']=='delivered').sum():,}")
print(f"  Cancelled orders:      {(orders['status']=='cancelled').sum():,}")
print(f"  Delivery time outliers:{len(outliers):,} ({len(outliers)/len(deliv)*100:.1f}%) — capped")
print(f"  High-value orders:     {orders['is_high_value'].sum():,} — flagged, kept")
print(f"  Structural NULLs:      delivery_time_min NULL for all cancelled orders — correct by design")

# ── Export clean versions ─────────────────────────────────
orders.to_csv('data/orders_clean.csv', index=False)
deliv.to_csv('data/delivery_clean.csv', index=False)
print("\nCleaned files saved: orders_clean.csv, delivery_clean.csv")