"""
Vercel Serverless Entry Point
==============================
Serves a static HTML summary dashboard and a JSON API endpoint
for the Jharkhand Municipal Election Results.

Routes:
  /           → HTML dashboard with summary + municipality table
  /api/data   → Raw JSON election data
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import traceback

DATA = None

def load_results():
    global DATA
    if DATA is not None:
        return DATA

    search_paths = [
        os.path.join(os.getcwd(), "data", "sample_data.json"),
        os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.json"),
        os.path.join(os.path.dirname(__file__), "data", "sample_data.json"),
        "/var/task/data/sample_data.json",
        "/var/task/api/data/sample_data.json",
    ]

    for p in search_paths:
        p = os.path.normpath(p)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                DATA = json.load(f)
            return DATA

    return {"error": "Data file not found", "searched": search_paths}


PARTY_COLORS = {
    "JMM": "#2E7D32", "BJP": "#FF9933", "INC": "#19AAED",
    "AJSU": "#8B0000", "JVM": "#9C27B0", "IND": "#757575",
}


def build_ward_rows(munis):
    """Build detailed ward-level HTML rows grouped by municipality."""
    sections = ""
    for m in munis:
        wards = m.get("wards", [])
        if not wards:
            continue
        sections += f'<div class="card"><h2>{m["name"]}</h2>'
        sections += '<table><thead><tr><th>Ward</th><th>Status</th><th>Winner / Leading</th><th>Party</th><th>Votes</th><th>Margin</th><th>Turnout</th></tr></thead><tbody>'
        for w in sorted(wards, key=lambda x: x["ward_no"]):
            status = w["status"]
            badge = "badge-declared" if status == "Declared" else "badge-counting"
            winner = w.get("winner") or (w["candidates"][0]["name"] if w.get("candidates") else "—")
            party = w.get("winner_party") or (w["candidates"][0]["party"] if w.get("candidates") else "—")
            votes = w.get("winner_votes", 0) or (w["candidates"][0]["votes"] if w.get("candidates") else 0)
            pc = PARTY_COLORS.get(party, "#999")
            sections += (
                f'<tr><td>Ward {w["ward_no"]}</td>'
                f'<td><span class="badge {badge}">{status}</span></td>'
                f'<td><strong>{winner}</strong></td>'
                f'<td style="color:{pc};font-weight:700">{party}</td>'
                f'<td>{votes:,}</td>'
                f'<td>{w.get("margin",0):,}</td>'
                f'<td>{w.get("turnout",0):.1f}%</td></tr>'
            )
        sections += '</tbody></table></div>'
    return sections


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jharkhand Nikay Chunav Results 2026 – Live</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0E1117 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1.5rem;
        }}
        .header {{
            background: linear-gradient(135deg, #FF9933, #138808, #000080);
            padding: 1.8rem 2rem;
            border-radius: 16px;
            text-align: center;
            width: 100%;
            max-width: 1000px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .header h1 {{ color: white; font-size: 1.7rem; font-weight: 800; }}
        .header p {{ color: rgba(255,255,255,0.85); margin-top: 0.4rem; font-size: 0.95rem; }}
        .card {{
            background: #1E1E1E;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
            width: 100%;
            max-width: 1000px;
        }}
        .card h2 {{ color: #FF9933; margin-bottom: 0.8rem; font-size: 1.15rem; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; }}
        .stat {{ text-align: center; padding: 0.8rem; background: #161622; border-radius: 10px; }}
        .stat .val {{ font-size: 2rem; font-weight: 800; color: #FF9933; }}
        .stat .lbl {{ font-size: 0.82rem; opacity: 0.7; margin-top: 0.2rem; }}
        .party-bar {{ display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.5rem; }}
        .party-chip {{
            padding: 6px 14px; border-radius: 20px; font-size: 0.82rem;
            font-weight: 700; color: white; display: inline-flex; align-items: center; gap: 6px;
        }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        th {{
            background: #000080; color: white;
            padding: 8px 10px; text-align: left; font-size: 0.8rem;
            position: sticky; top: 0;
        }}
        td {{ padding: 6px 10px; border-bottom: 1px solid #2a2a2a; font-size: 0.82rem; }}
        tr:hover {{ background: rgba(255,153,51,0.06); }}
        .badge {{
            display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 0.72rem; font-weight: 600; color: white;
        }}
        .badge-declared {{ background: #138808; }}
        .badge-counting {{ background: #FF9933; }}
        .footer {{
            margin-top: 1.5rem; text-align: center; font-size: 0.78rem;
            opacity: 0.5; max-width: 1000px; border-top: 1px solid #333; padding-top: 1rem;
        }}
        a {{ color: #19AAED; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        @media (max-width: 600px) {{
            .header h1 {{ font-size: 1.15rem; }}
            .stat .val {{ font-size: 1.5rem; }}
            td, th {{ padding: 5px 6px; font-size: 0.75rem; }}
        }}
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
            <div class="stat"><div class="val">{declared_count}</div><div class="lbl">Results Declared</div></div>
            <div class="stat"><div class="val">{turnout}%</div><div class="lbl">Avg. Turnout</div></div>
        </div>
    </div>

    <div class="card">
        <h2>Party-wise Seats Won</h2>
        <div class="party-bar">{party_chips}</div>
    </div>

    <div class="card">
        <h2>Municipality Progress</h2>
        <table>
            <thead><tr><th>Municipality</th><th>Type</th><th>Total Wards</th><th>Declared</th><th>Status</th></tr></thead>
            <tbody>{muni_rows}</tbody>
        </table>
    </div>

    {ward_sections}

    <div class="footer">
        <strong>Disclaimer:</strong> Data is for demonstration purposes only.
        Official results are published by the
        <a href="https://jsec.jharkhand.gov.in" target="_blank">Jharkhand State Election Commission</a>.<br>
        &copy; 2026 Jharkhand Nikay Chunav Results Dashboard &nbsp;|&nbsp;
        <a href="/api/data">JSON API</a>
    </div>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = load_results()

            if "error" in data:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode("utf-8"))
                return

            if self.path == "/api/data" or self.path == "/api/data/":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
                return

            summary = data.get("summary", {})
            munis = data.get("municipalities", [])

            # Municipality progress rows
            muni_rows = ""
            total_declared = 0
            for m in munis:
                wards = m.get("wards", [])
                dec = sum(1 for w in wards if w["status"] == "Declared")
                total_declared += dec
                total = m["total_wards"]
                badge_cls = "badge-declared" if dec == total else "badge-counting"
                badge_txt = "Complete" if dec == total else f"Counting ({dec}/{total})"
                muni_rows += (
                    f"<tr><td><strong>{m['name']}</strong></td><td>{m.get('type','')}</td>"
                    f"<td>{total}</td><td>{dec}</td>"
                    f'<td><span class="badge {badge_cls}">{badge_txt}</span></td></tr>'
                )

            # Party seats chips
            party_count = {}
            for m in munis:
                for w in m.get("wards", []):
                    if w["status"] == "Declared" and w.get("winner_party"):
                        p = w["winner_party"]
                        party_count[p] = party_count.get(p, 0) + 1
            party_chips = ""
            for p, count in sorted(party_count.items(), key=lambda x: -x[1]):
                clr = PARTY_COLORS.get(p, "#999")
                party_chips += f'<span class="party-chip" style="background:{clr}">{p}: {count}</span>'

            # Ward detail sections
            ward_sections = build_ward_rows(munis)

            html = HTML_TEMPLATE.format(
                total_ulbs=len(munis),
                total_wards=summary.get("total_wards", sum(m["total_wards"] for m in munis)),
                declared_count=total_declared,
                turnout=summary.get("turnout", "—"),
                muni_rows=muni_rows,
                party_chips=party_chips,
                ward_sections=ward_sections,
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err = f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>"
            self.wfile.write(err.encode("utf-8"))

    def log_message(self, format, *args):
        pass
