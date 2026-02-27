"""
Vercel Serverless Entry Point
==============================
Vercel does not natively run Streamlit's WebSocket server. This entry point
provides a lightweight HTTP redirect / info page that guides users to the
preferred hosted version of the dashboard.

For full Streamlit functionality, deploy to:
  - Streamlit Community Cloud (share.streamlit.io)
  - Hugging Face Spaces (huggingface.co/spaces)
  - Any VM / container (e.g., Railway, Render, AWS EC2)

If you still want to serve the Streamlit app via Vercel, consider using
stlite (Streamlit on Pyodide/WASM) which runs entirely in the browser.
See: https://github.com/whitphx/stlite
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path


def load_results():
    data_path = Path(__file__).parent.parent / "data" / "sample_data.json"
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Data file not found"}


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jharkhand Nikay Chunav Results 2026</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0E1117 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }
        .header {
            background: linear-gradient(135deg, #FF9933, #138808, #000080);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            width: 100%;
            max-width: 900px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .header h1 { color: white; font-size: 1.8rem; }
        .header p { color: rgba(255,255,255,0.85); margin-top: 0.5rem; }
        .card {
            background: #1E1E1E;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            width: 100%;
            max-width: 900px;
        }
        .card h2 { color: #FF9933; margin-bottom: 1rem; font-size: 1.2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; }
        .stat { text-align: center; }
        .stat .val { font-size: 2rem; font-weight: 800; color: #FF9933; }
        .stat .lbl { font-size: 0.85rem; opacity: 0.7; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th { background: #000080; color: white; padding: 8px 12px; text-align: left; font-size: 0.85rem; }
        td { padding: 7px 12px; border-bottom: 1px solid #333; font-size: 0.85rem; }
        tr:hover { background: rgba(255,153,51,0.08); }
        .badge {
            display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 0.75rem; font-weight: 600; color: white;
        }
        .badge-declared { background: #138808; }
        .badge-counting { background: #FF9933; }
        .footer {
            margin-top: 2rem; text-align: center; font-size: 0.8rem;
            opacity: 0.6; max-width: 900px;
        }
        a { color: #19AAED; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗳️ Jharkhand Nikay Chunav Results 2026 – LIVE</h1>
        <p>Jharkhand Urban Local Body (Municipal) Election Results</p>
    </div>

    <div class="card">
        <h2>Overall Summary</h2>
        <div class="stats">
            <div class="stat"><div class="val">{total_ulbs}</div><div class="lbl">Total ULBs</div></div>
            <div class="stat"><div class="val">{total_wards}</div><div class="lbl">Total Wards</div></div>
            <div class="stat"><div class="val">{declared}</div><div class="lbl">Results Declared</div></div>
            <div class="stat"><div class="val">{turnout}%</div><div class="lbl">Avg. Turnout</div></div>
        </div>
    </div>

    <div class="card">
        <h2>Municipality Results</h2>
        <table>
            <thead><tr><th>Municipality</th><th>Type</th><th>Wards</th><th>Declared</th><th>Status</th></tr></thead>
            <tbody>{muni_rows}</tbody>
        </table>
    </div>

    <div class="card">
        <h2>Full Interactive Dashboard</h2>
        <p>For the complete interactive experience with charts, search, and analytics,
        deploy this app on <a href="https://share.streamlit.io" target="_blank">Streamlit Community Cloud</a>
        or <a href="https://huggingface.co/spaces" target="_blank">Hugging Face Spaces</a>.</p>
        <p style="margin-top:0.5rem">Vercel serves this static summary. Streamlit requires a persistent
        WebSocket server for full interactivity.</p>
    </div>

    <div class="card">
        <h2>API Endpoint</h2>
        <p>Access raw JSON data at: <a href="/api/data">/api/data</a></p>
    </div>

    <div class="footer">
        <strong>Disclaimer:</strong> Data is for demonstration purposes only.
        Official results are published by the Jharkhand State Election Commission.<br>
        © 2026 Jharkhand Nikay Chunav Results Dashboard
    </div>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/data" or self.path == "/api/data/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = load_results()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        data = load_results()
        summary = data.get("summary", {})
        munis = data.get("municipalities", [])

        muni_rows = ""
        for m in munis:
            wards = m.get("wards", [])
            dec = sum(1 for w in wards if w["status"] == "Declared")
            total = m["total_wards"]
            badge_cls = "badge-declared" if dec == total else "badge-counting"
            badge_txt = "Complete" if dec == total else "Counting"
            muni_rows += (
                f"<tr><td>{m['name']}</td><td>{m.get('type','')}</td>"
                f"<td>{total}</td><td>{dec}</td>"
                f'<td><span class="badge {badge_cls}">{badge_txt}</span></td></tr>'
            )

        html = HTML_TEMPLATE.format(
            total_ulbs=summary.get("total_ulbs", "—"),
            total_wards=summary.get("total_wards", "—"),
            declared=summary.get("declared", "—"),
            turnout=summary.get("turnout", "—"),
            muni_rows=muni_rows,
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
