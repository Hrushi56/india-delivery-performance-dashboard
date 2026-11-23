"""Optional: refresh the India-only input from DataCo v5's original CSV."""
import csv
import sys
from pathlib import Path

fields = {
    "order_id": "Order Id", "state": "Order State", "mode": "Shipping Mode",
    "status": "Delivery Status", "actual": "Days for shipping (real)",
    "scheduled": "Days for shipment (scheduled)",
}
source = Path(sys.argv[1])
with source.open(encoding="latin-1", newline="") as src:
    rows = [tuple(r[name].strip() for name in fields.values())
            for r in csv.DictReader(src) if r["Order Country"].strip() == "India"]
if not rows:
    raise ValueError("No destination orders matched India")
target = Path(__file__).with_name("india_lines.csv")
with target.open("w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    writer.writerow(fields)
    writer.writerows(rows)
