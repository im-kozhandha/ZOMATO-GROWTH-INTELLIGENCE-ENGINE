# Zomato Growth Intelligence Engine (ZGIE)

> Diagnosing an order drop in Tier-2 cities using SQL, Python, and Power BI

---

## The Problem

Orders dropped in Tier-2 cities. The business question:  
**Is this caused by restaurant quality, user churn, or delivery failure?**

This project builds a complete analytical system — synthetic dataset, 
SQL root cause analysis, data cleaning, and an executive dashboard — 
to answer that question with evidence.

---

## The Answer

**Delivery infrastructure failure.** Not restaurants. Not users.

| Metric | Prior Period | Crisis Period | Change |
|--------|-------------|---------------|--------|
| Avg delivery time (Tier-2) | 28.0 min | 44.1 min | **+57%** |
| Delay rate (Tier-2) | 16% | 82% | **+5×** |
| Cancellation rate (Tier-2) | 8% | 25% | **+3×** |
| Avg restaurant rating | 4.01 | 3.99 | unchanged |
| Avg prep time | 13.7 min | 13.8 min | unchanged |
| Tier-1 delivery time | 28.1 min | 27.9 min | unchanged |

Restaurant ratings and prep times were statistically flat across both 
periods. Tier-1 cities showed zero degradation. The failure is 
geographically isolated to Tier-2 delivery operations.

---
## Features

- Interactive Power BI dashboard with 5 analytical pages
- KPI monitoring and operational analytics
- Root-cause diagnosis framework
- Cohort retention analysis
- SQL-based business investigation
- Revenue impact estimation
- Executive recommendation engine
---
## Architecture Diagram
<img width="728" height="1836" alt="deepseek_mermaid_20260601_b56a24" src="https://github.com/user-attachments/assets/3d73e0f7-0c77-49ff-a0ea-a11fe8da48c3" />

----

## Dashboard Preview
### Executive Overview
<img width="957" height="545" alt="PAGE 1" src="https://github.com/user-attachments/assets/7d54dfc9-0b3f-44dc-a349-d218a921c640" />
### Geographic Diagnosis
<img width="965" height="544" alt="PAGE 2" src="https://github.com/user-attachments/assets/4b43e624-3578-40a8-82c9-2ad4603e2b9e" />
### Root Cause Analysis
<img width="1267" height="712" alt="image" src="https://github.com/user-attachments/assets/02380e5b-5632-4bd2-b1ce-286a23957946" />

### Operational Recommendations
<img width="963" height="542" alt="PAGE 4" src="https://github.com/user-attachments/assets/3903839a-6ef2-4e82-87e9-09339ad79445" />

-----

## Dataset Design

10,000 orders across 8 cities (3 Tier-1, 5 Tier-2), generated with 
realistic probability distributions and embedded story rules:

| Table | Rows | Key design decision |
|-------|------|---------------------|
| orders | 10,000 | Tier-2 cancellation rate: 8% → 25% after March 17 |
| delivery | 9,031 | Tier-2 delivery time: N(28,7) → N(44,10) in crisis |
| users | 500 | Tier-2 users: 40% churn probability embedded |
| restaurants | 100 | Rating and prep time: negatively correlated |

**Why synthetic data?**  
Designing the dataset requires understanding what realistic food 
delivery data looks like — distributions, correlations, time patterns, 
and edge cases. The design decisions are documented and defensible.

---

## SQL Analysis — 12 Queries, 3 Tiers

### Analytics Workflow
<img width="1571" height="2680" alt="deepseek_mermaid_20260601_795f00" src="https://github.com/user-attachments/assets/cb0efec7-95fc-4355-bb84-d5efb322dc58" />

### Tier 1: KPI Layer
| Query | What it answers |
|-------|----------------|
| Q1 — City KPI | Orders, revenue, avg value per city |
| Q2 — Cancel rate | Cancellation % per city, sorted |
| Q3 — Daily trend | Day-by-day orders and revenue |
| Q4 — Delivery avg | Avg delivery time per city (INNER JOIN) |
| Q5 — Delay rate | % delayed orders per city |

### Tier 2: Growth Analysis
| Query | What it answers |
|-------|----------------|
| Q6 — Week-over-week | LAG() window function, % change by city |
| Q7 — Period comparison | Last 14d vs prior 14d, all metrics |
| Q8 — Delivery spike | Avg delay time split by period and city |
| Q9 — Cohort retention | User signup week → reorder behaviour |

### Tier 3: Root Cause
| Query | What it answers |
|-------|----------------|
| Q10 — Restaurant diagnosis | Rating bucket vs cancellation rate |
| Q11 — Partner load | Deliveries per partner vs delivery time |
| Q12 — Master diagnostic | All metrics, all cities, before vs after |

**Key SQL techniques used:**  
CTEs • Window Functions (LAG) • PARTITION BY • CASE WHEN Aggregations • NULLIF Guards • Multi-table JOINs • Cohort Retention Analysis • Time-Series Analytics • Date Arithmetic

### Advanced Analytics Techniques

- Week-over-week growth tracking using LAG() window functions
- Cohort retention analysis (Week 1, Week 2, Week 4)
- Comparative period analysis (Recent vs Prior 14 Days)
- Root-cause diagnostics across operations, restaurants, and users
---

## Data Cleaning
Delivery time outliers:  230 rows (2.5%) — capped at 49.7 min (IQR upper fence)
High-value orders:       301 rows (3.0%) — flagged, kept (plausible bulk orders)
Structural NULLs:        Cancelled orders have no delivery record — correct by design
Missing values:          0 across all 4 tables
**Decision log:**
- Capped rather than dropped delivery outliers ; a 55-min delivery is 
  plausible during a crisis, not a data entry error
- Flagged high-value orders without removing ; dropping them would 
  understate revenue in dashboard metrics
- Documented structural NULLs explicitly ; prevents Power BI from 
  misinterpreting missing delivery data as data quality issues

---

## Dashboard — 5 Pages

Built in Power BI with Zomato dark theme (`#1A1A2E` background, 
`#E23744` accent).

| Page | Question answered | Key visual |
|------|------------------|------------|
| Overview | What happened? | Tier-1 vs Tier-2 daily trend line |
| Where | Which cities? | Crisis vs prior cancellation by city |
| Root Cause | Why? | Before/after delivery time + delay rate |
| Actions | What to do? | 3 recommendations with evidence |
| Deep Dive | Full picture | Weekly trends + master diagnostic table |

---

## Recommendations

### Immediate (0–7 days)
**Surge delivery allocation** in Coimbatore, Indore, Bhopal, Vadodara 
during 7–10 PM peak hours. All cities have identical partner counts to 
Tier-1 but run 57% slower — route density is the gap, not headcount.

### Short term (1–4 weeks)
**Dynamic ETA display** — show realistic 40–45 min estimates instead 
of the standard 28 min. Order attempts increased 18–21% during the 
crisis while completions collapsed, showing users are willing to order 
but cancel when ETA is missed.

### Medium term (1–3 months)
**Tier-2 density program** — local logistics partnerships for 
last-mile coverage in Indore, Bhopal, Surat. Partner count is not 
the issue; route efficiency requires structural investment.

### Estimated impact
Restoring Tier-2 delay rate to baseline (16%):  
→ ~969 cancelled orders recovered per 14-day period  
→ × ₹220 avg order value = **₹2.13L per fortnight**  
→ Annualised: **₹55L+ GMV recovery** across 5 Tier-2 cities

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python (pandas, numpy) | Dataset generation, cleaning, pivot export |
| SQLite + DB Browser | Database storage and SQL analysis |
| SQL | 12 queries across KPI, growth, root cause layers |
| Power BI | 5-page executive dashboard |

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas numpy

# 2. Generate dataset
python generate_dataset.py

# 3. Run data cleaning
python clean_data.py

# 4. Generate Power BI pivots
python make_pivots.py

# 5. Open dashboard
# Launch Power BI Desktop → open ZGIE_Dashboard.pbix
# Or view screenshots in /screenshots folder
```

---

## Key Insight

The most important finding is what the data *did not* show.  
Restaurant ratings held flat at 4.01 → 3.99.  
Prep times barely moved at 13.7 → 13.8 min.  
The obvious hypothesis ; bad restaurants cause cancellations — 
was disproved by the data.  

Delivery time increased 57% in 14 days with zero restaurant or 
user behaviour change. That's the kind of finding that separates 
analysis from storytelling.

---

*Analysis period: January 1 – March 31, 2024*  
*Dataset: synthetic, modelled on realistic food delivery operations*  
*Crisis period defined: March 17–31, 2024 (14 days)*
