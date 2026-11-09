import sqlite3,csv,json,zipfile,os
from pathlib import Path
root=Path(__file__).parent
SOURCE='https://www.sec.gov/Archives/edgar/data/901832/000165495426009256/a0835b.htm'
SOURCES={
 'financial':SOURCE,
 'medicines':'https://alexion.com/our-medicines',
 'us_medicines':'https://alexion.us/our-medicines',
 'pipeline':'https://www.astrazeneca.com/our-therapy-areas/pipeline.html',
 'canada':'https://health-products.canada.ca/dpd-bdpp/search-fast-recherche-rapide?code=15662&lang=eng',
 'fda':'https://www.fda.gov/drugs/biosimilars/biosimilar-product-information',
 'az_earnings':'https://www.astrazeneca.com/media-centre/press-releases/2026/9m-and-q3-2026-results.html'}
# Separate reported line items, no fabricated per-brand breakouts
products=[
 ('Ultomiris + Voydeya','ravulizumab + danicopan (included)','Complement inhibition','PNH, aHUS, gMG, NMOSD',4016,16,16,'Ultomiris revenue includes Voydeya; never add Voydeya again', 'financial'),
 ('Strensiq','asfotase alfa','Enzyme replacement','Hypophosphatasia (HPP)',1641,38,37,'', 'financial'),
 ('Soliris','eculizumab','Complement inhibition','PNH, aHUS, gMG, NMOSD',1076,-25,-26,'Biosimilar competition and switching to Ultomiris', 'financial'),
 ('Koselugo','selumetinib','MEK inhibition','NF1 plexiform neurofibromas',585,17,15,'', 'financial'),
 ('Other Rare Disease','includes Kanuma and Beyonttra (JP only)','Other / aggregated','Multiple rare diseases',226,28,25,'Not separable into Kanuma and Beyonttra from this disclosure', 'financial')]
regions=[
 ('Ultomiris + Voydeya',2190,306,915,605),('Strensiq',1332,111,104,94),('Soliris',595,311,89,81),('Koselugo',149,225,149,62),('Other Rare Disease',89,51,60,26)]
# SWOT entries are analyst interpretations of publicly sourced evidence, not company self-assessments.
swot=[
 ('Strength','Strong flagship franchise','Ultomiris + Voydeya accounts for $4,016m of reported 9M 2026 Rare Disease revenue.','Protect leadership while monitoring concentration risk.','financial'),
 ('Strength','Growing diversified anchors','Strensiq grew 37% CER and Koselugo 15% CER in 9M 2026.','Maintain access and scientific education across franchises.','financial'),
 ('Weakness','Portfolio concentration','Ultomiris including Voydeya represents about 53% of Rare Disease revenue.','Diversify the growth mix and track concentration each quarter.','financial'),
 ('Weakness','Established-brand erosion','Soliris revenue declined 26% CER in 9M 2026.','Plan lifecycle transition and realistic legacy-brand forecasts.','financial'),
 ('Opportunity','Pipeline and label expansion','Rare Disease pipeline includes Phase III efzimfotase alfa, eneboparatide and additional projects.','Use milestone tracking to evaluate development opportunities.','pipeline'),
 ('Opportunity','Market access expansion','The 2026 results cite geographic launches and increasing demand for Ultomiris and Strensiq.','Track country-level reimbursement and launch progress.','financial'),
 ('Threat','Eculizumab biosimilars','FDA lists Bkemv and Epysqli as biosimilars referencing Soliris.','Monitor competitive entrants and erosion by geography.','fda'),
 ('Threat','Regulatory and development uncertainty','Rare-disease pipeline assets face clinical, approval and reimbursement uncertainty.','Build scenario analysis; do not treat pipeline assets as approved sales.','pipeline')]
pipeline=[('ALXN2080','Phase I','Healthy participants'),('ALXN2230','Phase I','Healthy participants'),('ALXN2350','Phase I','BAG3-associated dilated cardiomyopathy'),('AZD0120','Phase I','AL amyloidosis'),('AZD1390','Phase I','Glioblastoma'),('ALXN1920','Phase II','Primary membranous nephropathy'),('cevolisiran (ALXN2030)','Phase II','Antibody-mediated rejection'),('tarperprumig','Phase II','ANCA-associated vasculitis'),('Amlypave (anselamimab)','Phase III','AL amyloidosis – kappa light-chain'),('cliramitug','Phase III','ATTR cardiomyopathy'),('efzimfotase alfa','Phase III','Hypophosphatasia'),('eneboparatide','Phase III','Hypoparathyroidism'),('Klygefa (gefurulimab)','Phase III','Generalized myasthenia gravis')]
con=sqlite3.connect(root/'alexion_rare_disease.sqlite'); cur=con.cursor()
cur.executescript('''DROP VIEW IF EXISTS vw_product_performance; DROP VIEW IF EXISTS vw_reconciliation; DROP VIEW IF EXISTS vw_revenue_share; DROP TABLE IF EXISTS product_financials; DROP TABLE IF EXISTS regional_financials; DROP TABLE IF EXISTS swot_factors; DROP TABLE IF EXISTS pipeline_assets; DROP TABLE IF EXISTS sources;
CREATE TABLE sources (source_key TEXT PRIMARY KEY,url TEXT NOT NULL,accessed_on TEXT NOT NULL);
CREATE TABLE product_financials (product TEXT PRIMARY KEY, molecule TEXT, modality TEXT, indications TEXT, revenue_9m_2026_usdm INTEGER NOT NULL CHECK(revenue_9m_2026_usdm>=0), growth_actual_pct INTEGER, growth_cer_pct INTEGER, caveat TEXT,source_key TEXT NOT NULL REFERENCES sources(source_key));
CREATE TABLE regional_financials(product TEXT PRIMARY KEY REFERENCES product_financials(product),us_usdm INTEGER,emerging_usdm INTEGER,europe_usdm INTEGER,established_row_usdm INTEGER);
CREATE TABLE swot_factors(id INTEGER PRIMARY KEY,quadrant TEXT NOT NULL CHECK(quadrant IN ('Strength','Weakness','Opportunity','Threat')),title TEXT,evidence TEXT,implication TEXT,source_key TEXT REFERENCES sources(source_key));
CREATE TABLE pipeline_assets(asset TEXT PRIMARY KEY,stage TEXT,area TEXT,source_key TEXT REFERENCES sources(source_key));
CREATE VIEW vw_product_performance AS SELECT p.product,p.molecule,p.modality,p.indications,p.revenue_9m_2026_usdm,p.growth_actual_pct,p.growth_cer_pct,ROUND(100.0*p.revenue_9m_2026_usdm/(SELECT SUM(revenue_9m_2026_usdm) FROM product_financials),1) AS portfolio_share_pct,p.caveat FROM product_financials p;
CREATE VIEW vw_reconciliation AS SELECT 'Total product revenue vs reported rare disease' AS control,SUM(revenue_9m_2026_usdm) AS calculated,7544 AS expected,CASE WHEN SUM(revenue_9m_2026_usdm)=7544 THEN 'PASS' ELSE 'FAIL' END AS result FROM product_financials UNION ALL SELECT 'Product totals vs regional breakdown', (SELECT SUM(us_usdm+emerging_usdm+europe_usdm+established_row_usdm) FROM regional_financials), (SELECT SUM(revenue_9m_2026_usdm) FROM product_financials), CASE WHEN (SELECT SUM(us_usdm+emerging_usdm+europe_usdm+established_row_usdm) FROM regional_financials)=(SELECT SUM(revenue_9m_2026_usdm) FROM product_financials) THEN 'PASS' ELSE 'FAIL' END;
CREATE VIEW vw_revenue_share AS SELECT product,region,revenue_usdm FROM (SELECT product,us_usdm AS 'US',emerging_usdm AS 'Emerging Markets',europe_usdm AS 'Europe',established_row_usdm AS 'Established RoW' FROM regional_financials) LIMIT 0;''')
cur.executemany('INSERT INTO sources VALUES(?,?,?)',[(k,v,'2026-11-07') for k,v in SOURCES.items()])
cur.executemany('INSERT INTO product_financials VALUES(?,?,?,?,?,?,?,?,?)',products)
cur.executemany('INSERT INTO regional_financials VALUES(?,?,?,?,?)',regions)
cur.executemany('INSERT INTO swot_factors(quadrant,title,evidence,implication,source_key) VALUES(?,?,?,?,?)',swot)
cur.executemany('INSERT INTO pipeline_assets VALUES(?,?,?,?)',[(a,b,c,'pipeline') for a,b,c in pipeline])
con.commit()
checks=list(cur.execute('SELECT * FROM vw_reconciliation'));print('Quality controls:',checks)
assert all(x[-1]=='PASS' for x in checks)
for table,name in [('product_financials','products.csv'),('regional_financials','regions.csv'),('swot_factors','swot.csv'),('pipeline_assets','pipeline.csv')]:
 c=cur.execute('SELECT * FROM '+table);rows=c.fetchall()
 with open(root/name,'w',newline='') as f:
  w=csv.writer(f);w.writerow([x[0] for x in c.description]);w.writerows(rows)
con.close()
(root/'model.sql').write_text('''-- SQL views and data model are implemented in alexion_rare_disease.sqlite.
-- Run this query in SQLite to reproduce the executive scorecard:
SELECT product, revenue_9m_2026_usdm, growth_cer_pct, portfolio_share_pct
FROM vw_product_performance ORDER BY revenue_9m_2026_usdm DESC;

-- Validate published group revenue and geographical allocation:
SELECT * FROM vw_reconciliation;

-- SWOT factor counts and evidence by quadrant:
SELECT quadrant, COUNT(*) AS factor_count FROM swot_factors GROUP BY quadrant;

-- Pipeline stage scorecard (selected examples, not the complete pipeline):
SELECT stage, COUNT(*) AS showcased_assets FROM pipeline_assets GROUP BY stage;
''')
(root/'README.md').write_text('''# Alexion Rare Disease | Commercial & Strategic Intelligence Portfolio

**Purpose:** an interactive, recruiter-shareable BI portfolio demonstrating pharmaceutical product revenue analysis, risk assessment (SWOT), source traceability, SQL modeling, reconciliation and decision support.

## Open
Open `dashboard.html` in any modern browser. This is a self-contained HTML dashboard; filters, interactive charts, tabs, and CSV export work offline. The SQLite database and SQL file can be inspected in DB Browser for SQLite or with `sqlite3`.

## Data definitions
- As-of: 9M 2026 (January–September), published 30 October 2026; snapshot researched 7 November 2026.
- Currency: USD millions, AstraZeneca reported **Total Revenue** in Rare Disease. Not Alexion standalone accounts.
- Growth percentages: published year-on-year *actual* and *constant exchange rate (CER)* changes. Not a time series.
- `Ultomiris + Voydeya`: reported Ultomiris total includes Voydeya, **not** a separate additive Voydeya figure.
- `Other Rare Disease`: grouped total includes Kanuma and Beyonttra (Japan only); no unsupported product allocations.
- Pipeline cards: **selected** assets from AstraZeneca's 30 October 2026 pipeline; not a complete count of all company studies; phases may include lifecycle research on already-marketed brands.
- SWOT: portfolio author's qualitative assessment grounded in referenced sources; no proprietary data.
- The embedded UI is JavaScript-based, not a Power BI or Snowflake deployment.

## Data quality and governance
- `vw_reconciliation` tests that product revenue sums to **7,544 USDm** and regions sum to product totals.
- Product and region rows reconcile. Null or missing product-level facts are never estimated.
- Foreign keys link source metadata to records. No patient-level or identifiable health data used.
- Reconcile as of each future data refresh; public figures can be restated.

## Sources
- AstraZeneca Q3 / 9M results: https://www.sec.gov/Archives/edgar/data/901832/000165495426009256/a0835b.htm
- Investor overview: https://www.astrazeneca.com/media-centre/press-releases/2026/9m-and-q3-2026-results.html
- Global product list: https://alexion.com/our-medicines
- Pipeline: https://www.astrazeneca.com/our-therapy-areas/pipeline.html
- FDA biosimilars: https://www.fda.gov/drugs/biosimilars/biosimilar-product-information
- Health Canada registration check: https://health-products.canada.ca/dpd-bdpp/search-fast-recherche-rapide?code=15662&lang=eng

## Skills demonstrated
Business requirements → SQL semantic views → reproducible scorecards → interactive filtering and export → SWOT insights → data lineage and reconciliation. Suitable for publishing to a personal GitHub Pages portfolio (upload the HTML).

**No affiliation or endorsement by Alexion/AstraZeneca. Educational/portfolio analysis, not financial or medical advice.**
''')
(root/'data.json').write_text(json.dumps({'products':[dict(zip(['product','molecule','modality','indications','revenue','actual','cer','caveat','source'],r)) for r in products], 'regions':[dict(zip(['product','us','emerging','europe','row'],r)) for r in regions], 'swot':[dict(zip(['quadrant','title','evidence','implication','source'],r)) for r in swot], 'pipeline':[dict(zip(['asset','stage','area'],r)) for r in pipeline], 'sources':SOURCES},indent=2))
