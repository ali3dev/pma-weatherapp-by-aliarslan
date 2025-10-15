import json, csv
from fpdf import FPDF

def export_data(data, format_type="json", filename="export"):
    if format_type == "json":
        with open(f"{filename}.json", "w") as f:
            json.dump(data, f, indent=2)
    elif format_type == "csv":
        keys = data[0].keys() if data else []
        with open(f"{filename}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    elif format_type == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for item in data:
            pdf.cell(200, 10, txt=str(item), ln=True)
        pdf.output(f"{filename}.pdf")
