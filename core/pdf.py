from django.template.loader import render_to_string
from weasyprint import HTML

def render_anomalies_pdf(anomalies_qs):
    html = render_to_string("core/anomalies_pdf.html", {"anomalies": anomalies_qs})
    return HTML(string=html).write_pdf()
