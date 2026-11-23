# India shipping performance

An offline Python, SQL and Power BI portfolio project about shipments destined for India. Which states contribute the most late orders, and how does performance vary by shipping mode?

Of 2,070 eligible orders, 1,207 shipped beyond schedule (58.3%). Maharashtra accounted for 222 late orders out of 382. The Python and SQL dashboard runs offline, and the report data reconciles to SQL across all 91 observed state and shipping-mode combinations. Native Power BI Desktop rendering and refresh are pending verification.

## Run in VS Code

Open this folder in VS Code. Choose **Terminal → Run Build Task** (on macOS, **Cmd+Shift+B**) or run `python3 build.py` in the integrated terminal. Python 3 is the only dependency. The included India extract lets the build run offline.

Open `build/dashboard.html` in a browser. Choose Gujarat to see 74 of 121 orders above schedule. Clear filters to see 1,207 of 2,070 (58.3%). These figures describe the historical sample.

## Follow the analysis

- `india_lines.csv` contains six fields from item rows where the order destination country equals India.
- `analysis.sql` excludes canceled shipments, collapses repeated items to one shipping record per order and translates five state names into English. A unique index catches inconsistent records. An order is late when actual shipping days exceed scheduled shipping days.
- `build.py` runs the SQL, checks totals and produces a queryable SQLite database, Power BI CSV and standalone dashboard.
- `dashboard.template.html` contains the dashboard layout and filter logic.

## Power BI report

`powerbi/IndiaShipping.pbip` contains a report definition and linked semantic model. The page has four KPI cards, destination and shipping-mode slicers, a state chart and a detail table. The build embeds the order snapshot into the model's Power Query import, so the project travels without an absolute source path. Refreshing the model in Power BI Desktop loads the embedded rows. The browser dashboard provides an offline preview of the same metrics.

## Source and scope

Fabian Constante, Fernando Silva and António Pereira (2019), [DataCo SMART SUPPLY CHAIN FOR BIG DATA ANALYSIS, version 5](https://data.mendeley.com/datasets/8gx2fvg2k6/5), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project filters a global dataset to India destinations, selects shipping fields and derives order-level measures. Locations follow the source period. No review scores are available.

To regenerate the included extract, download DataCoSupplyChainDataset.csv from the source, run `python3 extract.py "/path/to/DataCoSupplyChainDataset.csv"`, then rebuild. Keep the full source CSV outside the project.

## GitHub handoff

When the analysis and report are finished, open this folder’s Source Control panel, initialize a repository if needed, review the files, and commit. The ignore file excludes generated builds. Include the report or screenshots you intend to share. Confirm the target GitHub account is Hrushi56 before publishing.
