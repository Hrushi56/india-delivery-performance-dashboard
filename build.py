"""Build the local SQLite database, Power BI export and offline dashboard."""
import csv
import json
import sqlite3
from pathlib import Path
from report_project import build_report

root = Path(__file__).resolve().parent
output = root / "build"
output.mkdir(exist_ok=True)
db = sqlite3.connect(":memory:")
db.execute("""CREATE TABLE lines(order_id TEXT NOT NULL, state TEXT NOT NULL, mode TEXT NOT NULL,
           status TEXT NOT NULL, actual INTEGER NOT NULL, scheduled INTEGER NOT NULL)""")
with (root / "india_lines.csv").open(encoding="utf-8", newline="") as src:
    for r in csv.DictReader(src):
        db.execute("INSERT INTO lines VALUES(?,?,?,?,?,?)",
                   (r["order_id"], r["state"], r["mode"], r["status"],
                    int(r["actual"]), int(r["scheduled"])))
db.executescript((root / "analysis.sql").read_text())
db.row_factory = sqlite3.Row
orders = db.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
rows = [dict(r) for r in db.execute("SELECT * FROM performance ORDER BY state,mode")]
assert orders and sum(r["orders"] for r in rows) == len(orders)
assert all(r["actual"] >= 0 and r["scheduled"] >= 0 for r in orders)
with (output / "orders.csv").open("w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(orders[0].keys())
    writer.writerows(orders)
with sqlite3.connect(output / "delivery.sqlite") as saved:
    db.backup(saved)
template = (root / "dashboard.template.html").read_text()
(output / "dashboard.html").write_text(template.replace("__DATA__", json.dumps(rows)))
build_report(root)
print(f"{len(orders):,} eligible India orders; {sum(r['late'] for r in rows):,} above schedule.")
