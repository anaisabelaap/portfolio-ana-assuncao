"""
setup_restaurant_db.py
----------------------
Creates and populates the restaurant_analytics PostgreSQL database
with 6 months of realistic Brazilian restaurant data.


Requirements:
    pip install psycopg2-binary pandas numpy

Usage:
    python setup_restaurant_db.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "restaurant_analytics")
}

random.seed(42)
np.random.seed(42)


# ── Step 1: Create the database ────────────────────────────────────────────────
def create_database():
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'restaurant_analytics'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE restaurant_analytics")
        print("✅ Database 'restaurant_analytics' created.")
    else:
        print("ℹ️  Database 'restaurant_analytics' already exists.")

    cur.close()
    conn.close()


# ── Step 2: Create tables ──────────────────────────────────────────────────────
def create_tables(cur):
    cur.execute("""
        DROP TABLE IF EXISTS waste_log CASCADE;
        DROP TABLE IF EXISTS order_items CASCADE;
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS menu_items CASCADE;
    """)

    cur.execute("""
        CREATE TABLE menu_items (
            item_id       SERIAL PRIMARY KEY,
            name          VARCHAR(100) NOT NULL,
            category      VARCHAR(50)  NOT NULL,
            sale_price    NUMERIC(8,2) NOT NULL,
            food_cost     NUMERIC(8,2) NOT NULL,
            is_active     BOOLEAN DEFAULT TRUE
        );
    """)

    cur.execute("""
        CREATE TABLE orders (
            order_id      SERIAL PRIMARY KEY,
            order_date    DATE        NOT NULL,
            order_time    TIME        NOT NULL,
            day_of_week   VARCHAR(20) NOT NULL,
            meal_period   VARCHAR(20) NOT NULL,
            table_number  INTEGER     NOT NULL,
            covers        INTEGER     NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id      INTEGER REFERENCES orders(order_id),
            item_id       INTEGER REFERENCES menu_items(item_id),
            quantity      INTEGER     NOT NULL,
            unit_price    NUMERIC(8,2) NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE waste_log (
            waste_id      SERIAL PRIMARY KEY,
            waste_date    DATE        NOT NULL,
            ingredient    VARCHAR(100) NOT NULL,
            category      VARCHAR(50)  NOT NULL,
            quantity_kg   NUMERIC(6,3) NOT NULL,
            cost_per_kg   NUMERIC(8,2) NOT NULL,
            reason        VARCHAR(100) NOT NULL
        );
    """)

    print("✅ Tables created.")


# ── Step 3: Insert menu items ──────────────────────────────────────────────────
# Food costs based on realistic Brazilian restaurant margins (25-40% cost ratio)
MENU_ITEMS = [
    # Pratos Principais
    ("Filé Mignon ao Molho Madeira",  "Prato Principal", 89.90, 28.50),
    ("Frango Grelhado com Legumes",   "Prato Principal", 52.90, 14.00),
    ("Salmão Grelhado",               "Prato Principal", 79.90, 30.00),
    ("Picanha na Brasa",              "Prato Principal", 94.90, 35.00),
    ("Risoto de Camarão",             "Prato Principal", 72.90, 24.00),
    ("Frango à Parmegiana",           "Prato Principal", 54.90, 15.50),
    ("Tilápia Grelhada",              "Prato Principal", 48.90, 13.00),
    ("Feijoada Completa",             "Prato Principal", 59.90, 16.00),
    # Massas
    ("Carbonara",                     "Massa",           44.90, 11.00),
    ("Lasanha Bolonhesa",             "Massa",           42.90, 10.50),
    ("Penne ao Molho de Tomate",      "Massa",           36.90,  8.00),
    ("Nhoque ao Pesto",               "Massa",           39.90,  9.50),
    # Saladas
    ("Salada Caesar",                 "Salada",          32.90,  7.00),
    ("Salada Caprese",                "Salada",          28.90,  8.50),
    ("Salada Tropical",               "Salada",          26.90,  6.00),
    # Entradas
    ("Carpaccio de Carne",            "Entrada",         38.90, 12.00),
    ("Bruschetta Tradicional",        "Entrada",         24.90,  5.50),
    ("Caldo de Costela",              "Entrada",         22.90,  6.00),
    ("Bolinho de Bacalhau (6un)",     "Entrada",         34.90,  9.00),
    # Sobremesas
    ("Petit Gâteau",                  "Sobremesa",       24.90,  5.00),
    ("Pudim de Leite",                "Sobremesa",       16.90,  3.50),
    ("Mousse de Maracujá",            "Sobremesa",       18.90,  4.00),
    ("Tiramisù",                      "Sobremesa",       22.90,  6.50),
    # Bebidas
    ("Suco Natural (400ml)",          "Bebida",          12.90,  3.00),
    ("Refrigerante",                  "Bebida",           8.90,  1.50),
    ("Água Mineral",                  "Bebida",           5.90,  0.80),
    ("Cerveja Artesanal",             "Bebida",          18.90,  4.50),
    ("Caipirinha",                    "Bebida",          22.90,  4.00),
]

def insert_menu_items(cur):
    cur.executemany("""
        INSERT INTO menu_items (name, category, sale_price, food_cost)
        VALUES (%s, %s, %s, %s)
    """, MENU_ITEMS)
    print(f"✅ {len(MENU_ITEMS)} menu items inserted.")


# ── Step 4: Generate realistic orders ─────────────────────────────────────────
# Demand patterns based on real restaurant operations knowledge:
# - Friday and Saturday are busiest (1.8x multiplier)
# - Lunch (12-15h) and dinner (19-22h) are peak periods
# - Mains and drinks sell most; desserts ~30% attachment rate

DAYS_PT = {
    0: "Segunda", 1: "Terça", 2: "Quarta",
    3: "Quinta",  4: "Sexta", 5: "Sábado", 6: "Domingo"
}

DAY_MULTIPLIERS = {
    "Segunda": 0.6, "Terça": 0.7, "Quarta": 0.8,
    "Quinta":  0.9, "Sexta": 1.8, "Sábado": 2.0, "Domingo": 1.2
}

MEAL_PERIODS = {
    "Almoço":  (11, 15),
    "Jantar":  (18, 23),
}

CATEGORY_WEIGHTS = {
    "Prato Principal": 0.35,
    "Massa":           0.15,
    "Salada":          0.10,
    "Entrada":         0.12,
    "Sobremesa":       0.08,
    "Bebida":          0.20,
}

def get_meal_period(hour):
    if 11 <= hour < 16:
        return "Almoço"
    elif 18 <= hour < 23:
        return "Jantar"
    return "Outros"

def generate_orders(cur):
    start_date = datetime(2024, 7, 1)
    end_date   = datetime(2024, 12, 31)
    base_daily_orders = 35

    all_orders = []
    all_order_items = []
    order_id = 1

    # Fetch menu items
    cur.execute("SELECT item_id, category, sale_price FROM menu_items")
    items = cur.fetchall()
    items_by_category = {}
    for item_id, category, price in items:
        items_by_category.setdefault(category, []).append((item_id, price))

    current_date = start_date
    while current_date <= end_date:
        day_name = DAYS_PT[current_date.weekday()]
        multiplier = DAY_MULTIPLIERS[day_name]
        n_orders = max(5, int(np.random.normal(
            base_daily_orders * multiplier,
            base_daily_orders * multiplier * 0.15
        )))

        for _ in range(n_orders):
            # Determine meal period and time
            period = random.choice(["Almoço", "Jantar"])
            h_start, h_end = MEAL_PERIODS[period]
            hour = random.randint(h_start, h_end - 1)
            minute = random.randint(0, 59)
            order_time = f"{hour:02d}:{minute:02d}:00"

            covers = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 35, 20, 20, 10, 5])[0]
            table_number = random.randint(1, 20)

            all_orders.append((
                current_date.date(),
                order_time,
                day_name,
                period,
                table_number,
                covers
            ))

            # Generate items for this order
            n_items = random.randint(covers, covers * 2)
            categories_chosen = random.choices(
                list(CATEGORY_WEIGHTS.keys()),
                weights=list(CATEGORY_WEIGHTS.values()),
                k=n_items
            )

            for cat in categories_chosen:
                if cat in items_by_category:
                    item_id, price = random.choice(items_by_category[cat])
                    quantity = 1 if cat != "Bebida" else random.randint(1, covers)
                    all_order_items.append((order_id, item_id, quantity, float(price)))

            order_id += 1

        current_date += timedelta(days=1)

    # Batch insert orders
    cur.executemany("""
        INSERT INTO orders (order_date, order_time, day_of_week, meal_period, table_number, covers)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, all_orders)

    # Batch insert order items
    cur.executemany("""
        INSERT INTO order_items (order_id, item_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
    """, all_order_items)

    print(f"✅ {len(all_orders):,} orders inserted.")
    print(f"✅ {len(all_order_items):,} order items inserted.")


# ── Step 5: Generate waste log ─────────────────────────────────────────────────
WASTE_INGREDIENTS = [
    ("Alface",        "Hortaliça",   8.90,  ["Vencimento", "Excesso de compra"]),
    ("Tomate",        "Hortaliça",   6.50,  ["Vencimento", "Dano físico"]),
    ("Rúcula",        "Hortaliça",   12.00, ["Vencimento"]),
    ("Banana",        "Fruta",       4.50,  ["Amadurecimento", "Vencimento"]),
    ("Maçã",          "Fruta",       7.20,  ["Amadurecimento", "Dano físico"]),
    ("Frango",        "Proteína",    18.90, ["Vencimento", "Excesso de compra"]),
    ("Carne Bovina",  "Proteína",    45.00, ["Vencimento", "Preparo excessivo"]),
    ("Pão Francês",   "Panificado",  12.00, ["Preparo excessivo", "Vencimento"]),
    ("Arroz Cozido",  "Cereal",      3.50,  ["Preparo excessivo"]),
    ("Camarão",       "Fruto do Mar",89.00, ["Vencimento"]),
]

def generate_waste_log(cur):
    start_date = datetime(2024, 7, 1)
    end_date   = datetime(2024, 12, 31)
    waste_records = []

    current_date = start_date
    while current_date <= end_date:
        n_waste_items = random.randint(1, 4)
        ingredients_today = random.sample(WASTE_INGREDIENTS, n_waste_items)

        for ingredient, category, cost_per_kg, reasons in ingredients_today:
            quantity = round(random.uniform(0.1, 2.5), 3)
            reason = random.choice(reasons)
            waste_records.append((
                current_date.date(),
                ingredient,
                category,
                quantity,
                cost_per_kg,
                reason
            ))

        current_date += timedelta(days=1)

    cur.executemany("""
        INSERT INTO waste_log (waste_date, ingredient, category, quantity_kg, cost_per_kg, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, waste_records)

    print(f"✅ {len(waste_records):,} waste records inserted.")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("\n🍽️  Restaurant Analytics — Database Setup")
    print("=" * 45)

    create_database()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        create_tables(cur)
        insert_menu_items(cur)
        generate_orders(cur)
        generate_waste_log(cur)
        conn.commit()
        print("\n✅ All done! Database is ready.")
        print("   Connect Power BI or run the analysis notebook.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
