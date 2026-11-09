# Alexion Rare Disease | Commercial & Strategic Intelligence Portfolio

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
