import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3, os

np.random.seed(42)

TODAY  = datetime(2024, 3, 31)
CUTOFF = TODAY - timedelta(days=14)

tier1_cities = ['Mumbai', 'Delhi', 'Bangalore']
tier2_cities = ['Coimbatore', 'Indore', 'Bhopal', 'Surat', 'Vadodara']
all_cities   = tier1_cities + tier2_cities

city_tier = {c: 'Tier-1' for c in tier1_cities}
city_tier.update({c: 'Tier-2' for c in tier2_cities})

cancel_normal = 0.08
cancel_crisis = 0.25


def generate_users(n=500):
    ids    = [f'U{str(i).zfill(4)}' for i in range(1, n+1)]
    wts    = [0.15, 0.15, 0.10, 0.16, 0.14, 0.12, 0.10, 0.08]
    cities = np.random.choice(all_cities, size=n, p=wts)

    s_off  = np.random.randint(1, 180, size=n)
    sdates = [TODAY - timedelta(days=int(d)) for d in s_off]

    lo = []
    for i, c in enumerate(cities):
        da = max(1, (TODAY - sdates[i]).days)

        # BUG 2 FIX: only allow churn flag if user has been active > 14 days
        is_tier2         = city_tier[c] == 'Tier-2'
        been_long_enough = da > 14
        churned          = is_tier2 and been_long_enough and np.random.random() < 0.40

        mn = 14 if churned else 1

        # Safety guard: ensure valid randint range
        upper = min(da, 60)
        if mn >= upper:
            mn = 1

        days_ago = np.random.randint(mn, upper + 1)
        lo.append(TODAY - timedelta(days=int(days_ago)))

    return pd.DataFrame({
        'user_id':         ids,
        'city':            cities,
        'city_tier':       [city_tier[c] for c in cities],
        'signup_date':     sdates,
        'last_order_date': lo
    })


def generate_restaurants(n=100):
    ids     = [f'R{str(i).zfill(3)}' for i in range(1, n+1)]
    wts     = [0.18, 0.17, 0.15, 0.13, 0.12, 0.10, 0.09, 0.06]
    cities  = np.random.choice(all_cities, size=n, p=wts)
    ratings = np.clip(np.random.normal(3.8, 0.6, size=n), 1.0, 5.0).round(1)
    prep    = np.clip(35 - (5 * ratings) + np.random.normal(0, 2, size=n), 8, 35).round(1)
    cuisine = np.random.choice(
        ['North Indian','South Indian','Chinese','Fast Food','Biryani','Pizza'],
        size=n, p=[0.25, 0.20, 0.18, 0.17, 0.12, 0.08]
    )
    return pd.DataFrame({
        'restaurant_id': ids, 'city': cities,
        'city_tier':     [city_tier[c] for c in cities],
        'rating':        ratings, 'avg_prep_time': prep,
        'cuisine_type':  cuisine
    })


def generate_orders(df_u, df_r, n=10000):
    rbc  = df_r.groupby('city')['restaurant_id'].apply(list).to_dict()
    uc   = df_u.set_index('user_id')['city'].to_dict()
    pool = df_u['user_id'].tolist()

    # BUG 1 FIX: normalize weights so floating point can't cause sum != 1
    hw_raw = [0.005,0.003,0.002,0.002,0.002,0.003,0.010,0.020,
              0.030,0.040,0.050,0.055,0.090,0.085,0.070,0.050,
              0.040,0.045,0.060,0.090,0.095,0.080,0.055,0.020]
    hw = [x / sum(hw_raw) for x in hw_raw]

    rows = []
    for i in range(n):
        uid   = np.random.choice(pool)
        city  = uc[uid]
        tier  = city_tier[city]

        d_off = np.random.randint(0, 90)
        odate = TODAY - timedelta(days=int(d_off))
        hr    = np.random.choice(range(24), p=hw)
        otime = odate.replace(hour=hr, minute=np.random.randint(0, 60))

        crisis = (tier == 'Tier-2') and (odate >= CUTOFF)
        cp     = cancel_crisis if crisis else cancel_normal
        status = 'cancelled' if np.random.random() < cp else 'delivered'

        val  = round(max(80, min(2000, np.random.lognormal(5.3, 0.45))), 2)
        disc = round(val * np.random.uniform(0.1, 0.3), 2) \
               if np.random.random() < 0.30 else 0.0

        rows.append({
            'order_id':           f'ORD{str(i+1).zfill(5)}',
            'user_id':            uid,
            'restaurant_id':      np.random.choice(rbc[city]),
            'city':               city,
            'city_tier':          tier,
            'order_time':         otime,
            'order_value':        val,
            'discount_applied':   disc,
            'status':             status,
            'is_crisis_period':   crisis
        })

    return pd.DataFrame(rows)


def generate_delivery(df_o):
    dlvd = df_o[df_o['status'] == 'delivered'].copy()
    rows = []
    for _, row in dlvd.iterrows():
        c  = row['is_crisis_period']
        dt = round(np.clip(np.random.normal(44 if c else 28, 10 if c else 7), 8, 90), 1)
        rows.append({
            'order_id':            row['order_id'],
            'delivery_partner_id': f'DP{np.random.randint(1, 51):03d}',
            'delivery_time_min':   dt,
            'delay_flag':          1 if dt > 35 else 0,
            'city':                row['city'],
            'is_crisis_period':    c
        })
    return pd.DataFrame(rows)


def export_all(dfu, dfr, dfo, dfd):
    os.makedirs('data', exist_ok=True)
    tables = [(dfu,'users'), (dfr,'restaurants'), (dfo,'orders'), (dfd,'delivery')]
    for df, name in tables:
        df.to_csv(f'data/{name}.csv', index=False)
    conn = sqlite3.connect('data/zgie.db')
    for df, name in tables:
        df.to_sql(name, conn, if_exists='replace', index=False)
        n = pd.read_sql(f'SELECT COUNT(*) n FROM {name}', conn)['n'][0]
        print(f'  {name}: {n} rows')
    conn.close()
    print('Done → data/zgie.db + 4 CSVs in /data')


# ── Run ───────────────────────────────────────────────────
df_users       = generate_users()
df_restaurants = generate_restaurants()
df_orders      = generate_orders(df_users, df_restaurants)
df_delivery    = generate_delivery(df_orders)
export_all(df_users, df_restaurants, df_orders, df_delivery)

# ── Verify ────────────────────────────────────────────────
print("\n=== STORY CHECK ===")
print(df_orders.groupby(['city_tier', 'is_crisis_period'])['status']
      .apply(lambda x: (x == 'cancelled').mean()).round(3))
print("\nDelay rates:")
print(df_delivery.groupby('is_crisis_period')['delay_flag'].mean().round(3))