"""Generate a portable Power BI Desktop project from the validated order export."""
import base64
import json
from pathlib import Path


def build_report(root):
    folder = root / "powerbi"
    report = folder / "IndiaShipping.Report"
    model = folder / "IndiaShipping.SemanticModel"
    schema = "https://developer.microsoft.com/json-schemas/fabric/item/report/"

    def save(file, data):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    save(folder / "IndiaShipping.pbip", {
        "version": "1.0", "artifacts": [{"report": {"path": report.name}}],
        "settings": {"enableAutoRecovery": True}})
    save(report / "definition.pbir", {"version": "4.0",
         "datasetReference": {"byPath": {"path": "../"+model.name}}})
    save(model / "definition.pbism", {"version": "1.0", "settings": {}})
    fields = ["order_id", "state", "mode", "actual", "scheduled", "days_late"]
    csv_data = base64.b64encode((root/"build/orders.csv").read_bytes()).decode()
    # Chunk literals to stay below individual Power Query text-literal limits.
    payload = " & ".join('"'+csv_data[i:i+8000]+'"' for i in range(0,len(csv_data),8000))
    transforms = ", ".join('{"'+f+'", '+("type text" if i<3 else "Int64.Type")+'}'
                           for i,f in enumerate(fields))
    query = ["let", f"    Raw = Binary.FromText({payload}, BinaryEncoding.Base64),",
             '    Data = Csv.Document(Raw, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
             "    Headers = Table.PromoteHeaders(Data),",
             "    Typed = Table.TransformColumnTypes(Headers, {"+transforms+"})", "in Typed"]
    measures = []
    formats = ["#,0", "#,0", "0.0%", "0.0"]
    for line in (folder/"measures.dax").read_text().splitlines():
        if line and not line.startswith("//"):
            name, expression = line.split(" = ", 1)
            measures.append({"name": name, "expression": expression, "formatString": formats[len(measures)]})
    save(model/"model.bim", {"name":"IndiaShipping","compatibilityLevel":1567,
         "model":{"culture":"en-US","defaultPowerBIDataSourceVersion":"powerBI_V3","tables":[{
             "name":"orders","columns":[{"name":f,"sourceColumn":f,"dataType":"string" if i<3 else "int64",
                 "summarizeBy":"none"} for i,f in enumerate(fields)],"measures":measures,
             "partitions":[{"name":"orders","mode":"import","source":{"type":"m","expression":query}}]}]}})
    definition = report/"definition"
    page_id = "a94fe0eb260b457ab000"
    page = definition/"pages"/page_id
    save(definition/"version.json", {"$schema":schema+"definition/versionMetadata/1.0.0/schema.json","version":"2.0.0"})
    save(definition/"report.json", {"$schema":schema+"definition/report/2.0.0/schema.json","themeCollection":{}})
    save(definition/"pages/pages.json", {"$schema":schema+"definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder":[page_id],"activePageName":page_id})
    save(page/"page.json", {"$schema":schema+"definition/page/2.0.0/schema.json","name":page_id,
        "displayName":"India shipping performance","displayOption":"FitToPage","width":1280,"height":720})
    names = [m["name"] for m in measures]

    def visual(index, kind, position, roles):
        ident = f"{index:020x}"
        query_state = {}
        for role, columns in roles.items():
            projections = []
            for col in columns:
                field = {"Expression":{"SourceRef":{"Entity":"orders"}},"Property":col}
                projections.append({"field":{"Measure" if col in names else "Column":field},
                                    "queryRef":"orders."+col,"nativeQueryRef":col})
            query_state[role] = {"projections":projections}
        x,y,w,h = position
        save(page/"visuals"/ident/"visual.json", {"$schema":schema+"definition/visualContainer/2.1.0/schema.json",
             "name":ident,"position":{"x":x,"y":y,"width":w,"height":h,"z":index,"tabOrder":index},
             "visual":{"visualType":kind,"query":{"queryState":query_state}}})
    for i,name in enumerate(names):
        visual(i+1,"card",(20+i*312,16,304,110),{"Values":[name]})
    visual(5,"slicer",(20,144,220,285),{"Values":["state"]})
    visual(6,"slicer",(20,438,220,255),{"Values":["mode"]})
    visual(7,"barChart",(253,145,495,548),{"Category":["state"],"Y":["Late Orders"]})
    visual(8,"tableEx",(757,145,505,548),{"Values":["state"]+names})
