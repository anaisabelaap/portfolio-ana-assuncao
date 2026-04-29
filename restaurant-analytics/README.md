# Restaurant Analytics

> **⚠️ Status: Work in Progress (WIP)** > This project is currently under development. The data structure and SQL analyses are complete, and the interactive dashboard is in the final stages of development.

A SQL-based portfolio project simulating six months of operational data from a Brazilian restaurant (July–December 2024). The goal was to move beyond simple revenue reporting and explore what the data actually reveals about menu profitability, product performance, and food waste cost.

The dataset was generated synthetically using realistic Brazilian restaurant patterns — pricing margins, day-of-week demand multipliers, typical meal periods, and ingredient cost structures.

---

## What this project covers

- Total and monthly revenue trends
- Product performance: sales volume vs. revenue vs. profit (they don't always tell the same story)
- Menu Engineering Matrix: classifying items as Stars, Plowhorses, Puzzles, and Dogs based on popularity and margin
- Food waste analysis by ingredient, reason, and financial impact
- Window functions and CTE patterns applied to a real business context

---

## Project structure

```
restaurant_analytics/
│
├── setup_restaurant_db.py     # Creates and populates the PostgreSQL database
├── 01_restaurant_analysis.sql # Full analysis: revenue, profitability, menu engineering, waste
├── insights.md                # Key findings and recommendations from the analysis
├── .env.example               # Environment variable template (copy to .env and fill in)
└── README.md
```

---

## Database schema

**`menu_items`** — item catalog with sale price and food cost per item  
**`orders`** — one row per order, with date, time, meal period, and table info  
**`order_items`** — line items linking orders to menu items, with quantity and unit price at time of sale  
**`waste_log`** — daily waste records by ingredient, with quantity (kg), cost per kg, and reason  

---

## How to run locally

**Requirements**
- Python 3.8+
- PostgreSQL running locally
- pip packages: `psycopg2-binary`, `pandas`, `numpy`, `python-dotenv`

```bash
pip install psycopg2-binary pandas numpy python-dotenv
```

**Setup**

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your PostgreSQL credentials:
```bash
cp .env.example .env
```
3. Run the setup script:
```bash
python setup_restaurant_db.py
```
4. Open `01_restaurant_analysis.sql` in your SQL client (DBeaver, pgAdmin, etc.) and run the queries

---

## Notes

- Data is entirely synthetic but built to reflect realistic Brazilian restaurant operations
- Item names and some field values are in Portuguese, consistent with the restaurant context
- `random.seed(42)` ensures the generated dataset is fully reproducible
