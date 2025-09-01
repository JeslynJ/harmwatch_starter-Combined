from datetime import datetime

HTML_TMPL = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>HarmWatch Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1 {{ margin-bottom: 0; }}
    small {{ color:#666; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f4f4f4; }}
    .note {{ color:#444; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>HarmWatch — Summary Report</h1>
  <small>Generated {now}</small>
  <h2>Category Summary</h2>
  <table>
    <tr><th>Category</th><th>Count</th></tr>
    {rows}
  </table>
  <h2>Flagged Examples (Top 10)</h2>
  {examples}
  <p class="note">Note: Rule-based detections may include false positives. Use responsibly.</p>
</body>
</html>"""

def render_html(summary_counts, examples_table_html) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    rows = "\\n".join(f"<tr><td>{cat}</td><td>{cnt}</td></tr>" for cat, cnt in summary_counts.items())
    return HTML_TMPL.format(now=now, rows=rows, examples=examples_table_html)
