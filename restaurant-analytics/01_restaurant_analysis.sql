-- ============================================================
-- Restaurant Analytics — Performance & Waste Analysis
-- Period: July 1 – December 31, 2024
-- Database: restaurant_analytics (PostgreSQL)
-- Author: Ana Isabel Assunção| Portfolio Project
-- ============================================================


-- ============================================================
-- SECTION 1: DATA EXPLORATION
-- Purpose: Inspect raw table structure and sample rows before
-- any transformation.
-- ============================================================

SELECT * FROM menu_items   LIMIT 5;
SELECT * FROM orders       LIMIT 5;
SELECT * FROM order_items  LIMIT 5;
SELECT * FROM waste_log    LIMIT 5;


-- ============================================================
-- SECTION 2: REVENUE ANALYSIS
-- Purpose: Understand total and monthly revenue trends.
-- Revenue = quantity sold × unit price at time of sale.
-- Note: unit_price in order_items captures the price at the
-- moment of the transaction, decoupled from menu_items.sale_price,
-- which is important for historical accuracy.
-- ============================================================

-- 2.1 Total revenue across the full period
SELECT
    SUM(quantity * unit_price) AS total_revenue
FROM order_items;


-- 2.2 Monthly revenue trend
-- DATE_TRUNC truncates the order date to the first day of each
-- month, enabling clean monthly aggregation without needing
-- a separate calendar table.
SELECT
    DATE_TRUNC('month', o.order_date) AS month,
    SUM(oi.quantity * oi.unit_price)  AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- SECTION 3: PRODUCT PERFORMANCE
-- Purpose: -- Looking at volume vs revenue separately 
-- because they don’t always tell the same story
-- ============================================================

-- 3.1 Most popular items by total units sold
-- Popularity is the first axis of menu performance analysis.
SELECT
    mi.name,
    mi.category,
    SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN menu_items mi
    ON oi.item_id = mi.item_id
GROUP BY mi.name, mi.category
ORDER BY total_sold DESC;


-- 3.2 Revenue contribution per item
-- Revenue = quantity × unit_price to reflect actual charged prices.
SELECT
    mi.name,
    mi.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN menu_items mi
    ON oi.item_id = mi.item_id
GROUP BY mi.name, mi.category
ORDER BY revenue DESC;


-- 3.3 Profitability per item: unit margin and total profit
-- Unit margin = sale_price − food_cost (contribution margin).
-- Total profit = units sold × unit margin.
-- This reveals the gap between revenue and actual profit contribution —
-- a key insight that volume-only analysis misses entirely.
SELECT
    mi.name,
    mi.category,
    SUM(oi.quantity)                                    AS total_sold,
    (mi.sale_price - mi.food_cost)                      AS unit_margin,
    SUM(oi.quantity * (mi.sale_price - mi.food_cost))   AS total_profit
FROM order_items oi
JOIN menu_items mi
    ON oi.item_id = mi.item_id
GROUP BY mi.name, mi.category, mi.sale_price, mi.food_cost
ORDER BY total_profit DESC;


-- ============================================================
-- SECTION 4: WINDOW FUNCTIONS
-- Purpose: Rank items within the full dataset without collapsing
-- results into groups. RANK() preserves ties and allows
-- direct comparison between items in a single result set.
-- ============================================================

-- 4.1 Items ranked by revenue (highest to lowest)
SELECT
    mi.name,
    mi.category,
    SUM(oi.quantity * oi.unit_price)                                        AS revenue,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC)            AS revenue_rank
FROM order_items oi
JOIN menu_items mi
    ON oi.item_id = mi.item_id
GROUP BY mi.name, mi.category
ORDER BY revenue_rank;


-- ============================================================
-- SECTION 5: MENU ENGINEERING MATRIX
-- Purpose: Classify every menu item into one of four strategic
-- categories based on two dimensions:
--   • Popularity: total units sold vs. menu average
--   • Profitability: unit margin vs. menu average
--
-- Classification:
--   Star      → high popularity + high margin  (protect & promote)
--   Plowhorse → high popularity + low margin   (review pricing/cost)
--   Puzzle    → low popularity  + high margin  (improve visibility)
--   Dog       → low popularity  + low margin   (evaluate removal)
--
-- This framework is a standard tool in restaurant management,
-- first formalized by Kasavana & Smith (1982).
-- ============================================================

-- 5.1 Item-level metrics: popularity and margin per item
WITH item_metrics AS (
    SELECT
        mi.item_id,
        mi.name,
        mi.category,
        SUM(oi.quantity)               AS qty_sold,
        (mi.sale_price - mi.food_cost) AS margin
    FROM menu_items mi
    JOIN order_items oi
        ON mi.item_id = oi.item_id
    GROUP BY mi.item_id, mi.name, mi.category, mi.sale_price, mi.food_cost
)
SELECT * FROM item_metrics;


-- 5.2 Benchmark averages: the thresholds that define each quadrant
-- Items above avg_qty are "popular"; above avg_margin are "profitable".
-- Using the mean as benchmark is the standard approach in menu engineering.
WITH item_metrics AS (
    SELECT
        mi.item_id,
        mi.name,
        mi.category,
        SUM(oi.quantity)               AS qty_sold,
        (mi.sale_price - mi.food_cost) AS margin
    FROM menu_items mi
    JOIN order_items oi
        ON mi.item_id = oi.item_id
    GROUP BY mi.item_id, mi.name, mi.category, mi.sale_price, mi.food_cost
),
benchmarks AS (
    SELECT
        AVG(qty_sold) AS avg_qty,
        AVG(margin)   AS avg_margin
    FROM item_metrics
)
SELECT * FROM benchmarks;


-- 5.3 Full Menu Engineering classification
-- CROSS JOIN brings the single-row benchmarks table into every item row,
-- enabling the CASE comparison without a subquery in each branch.
WITH item_metrics AS (
    SELECT
        mi.item_id,
        mi.name,
        mi.category,
        SUM(oi.quantity)               AS qty_sold,
        (mi.sale_price - mi.food_cost) AS margin
    FROM menu_items mi
    JOIN order_items oi
        ON mi.item_id = oi.item_id
    GROUP BY mi.item_id, mi.name, mi.category, mi.sale_price, mi.food_cost
),
benchmarks AS (
    SELECT
        AVG(qty_sold) AS avg_qty,
        AVG(margin)   AS avg_margin
    FROM item_metrics
)
SELECT
    im.name,
    im.category,
    im.qty_sold,
    ROUND(im.margin, 2)   AS unit_margin,
    CASE
        WHEN im.qty_sold >= b.avg_qty AND im.margin >= b.avg_margin THEN 'Star'
        WHEN im.qty_sold >= b.avg_qty AND im.margin <  b.avg_margin THEN 'Plowhorse'
        WHEN im.qty_sold <  b.avg_qty AND im.margin >= b.avg_margin THEN 'Puzzle'
        ELSE 'Dog'
    END                   AS menu_class
FROM item_metrics im
CROSS JOIN benchmarks b
ORDER BY menu_class, im.qty_sold DESC;


-- ============================================================
-- SECTION 6: WASTE ANALYSIS
-- Purpose: Quantify the financial cost of food waste by ingredient
-- and understand which waste reasons (expiration, overproduction,
-- physical damage) drive the most loss.
--
-- Key insight: waste cost = quantity_kg × cost_per_kg.
-- Two distinct patterns emerge: ingredients like lettuce have high
-- discarded volume but low unit cost, so their financial impact is
-- limited. Shrimp, by contrast, combines high unit cost with high
-- discarded volume — a compounding effect that makes it the
-- dominant waste driver by a significant margin.
-- ============================================================

-- 6.1 Total waste cost and quantity per ingredient
-- Ordered by financial impact to surface the highest-priority items.
SELECT
    ingredient,
    SUM(quantity_kg)                          AS total_qty_kg,
    SUM(quantity_kg * cost_per_kg)            AS total_waste_cost
FROM waste_log
GROUP BY ingredient
ORDER BY total_waste_cost DESC;


-- 6.2 Waste breakdown by reason for the two highest-cost ingredients
-- Camarão (shrimp) and Carne Bovina (beef) together account for the
-- majority of waste cost. Understanding WHY they are wasted
-- (expiration vs. overproduction) determines the correct intervention:
-- purchasing control vs. production planning.
SELECT
    ingredient,
    reason,
    SUM(quantity_kg * cost_per_kg) AS waste_cost
FROM waste_log
WHERE ingredient IN ('Camarão', 'Carne Bovina')
GROUP BY ingredient, reason
ORDER BY waste_cost DESC;


-- 6.3 Percentage contribution of each ingredient to total waste cost
-- CROSS JOIN with the single-row total CTE allows the percentage
-- calculation to stay in a clean SELECT without a correlated subquery.
-- This is the standard pattern for share-of-total calculations in SQL.
WITH waste_by_item AS (
    SELECT
        ingredient,
        SUM(quantity_kg * cost_per_kg) AS waste_cost
    FROM waste_log
    GROUP BY ingredient
),
total AS (
    SELECT SUM(waste_cost) AS total_waste
    FROM waste_by_item
)
SELECT
    w.ingredient,
    ROUND(w.waste_cost, 2)                           AS waste_cost,
    ROUND(w.waste_cost / t.total_waste * 100, 2)     AS pct_of_total
FROM waste_by_item w
CROSS JOIN total t
ORDER BY pct_of_total DESC;


-- 6.4 Full waste breakdown: every ingredient × reason combination
-- Useful for identifying which reason-ingredient pairs generate
-- the most loss across the entire waste log.
SELECT
    ingredient,
    reason,
    SUM(quantity_kg * cost_per_kg) AS waste_cost
FROM waste_log
GROUP BY ingredient, reason
ORDER BY waste_cost DESC;