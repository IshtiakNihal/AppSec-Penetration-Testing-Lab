from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_report(data: dict, pdf_path: str, html_path: str):
    findings = data.get("findings", [])

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, 760, "Project C - Penetration Test Report")
    c.setFont("Helvetica", 12)
    c.drawString(40, 740, f"Generated: {datetime.utcnow().isoformat()}Z")

    y = 700
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Findings")
    y -= 20

    c.setFont("Helvetica", 10)
    for finding in findings:
        c.drawString(40, y, f"- {finding.get('id')} ({finding.get('severity')})")
        y -= 14
        if y < 80:
            c.showPage()
            y = 760

    c.save()

    env = Environment(loader=FileSystemLoader("framework/reporting/templates"))
    template = env.get_template("report_template.html")
    html = template.render(findings=findings)

    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(html)
