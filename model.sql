-- SQL views and data model are implemented in alexion_rare_disease.sqlite.
-- Run this query in SQLite to reproduce the executive scorecard:
SELECT product, revenue_9m_2026_usdm, growth_cer_pct, portfolio_share_pct
FROM vw_product_performance ORDER BY revenue_9m_2026_usdm DESC;

-- Validate published group revenue and geographical allocation:
SELECT * FROM vw_reconciliation;

-- SWOT factor counts and evidence by quadrant:
SELECT quadrant, COUNT(*) AS factor_count FROM swot_factors GROUP BY quadrant;

-- Pipeline stage scorecard (selected examples, not the complete pipeline):
SELECT stage, COUNT(*) AS showcased_assets FROM pipeline_assets GROUP BY stage;
