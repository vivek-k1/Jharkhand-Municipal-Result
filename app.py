"""
Jharkhand Municipal Election Results 2026 – Live Dashboard
===========================================================
A production-ready Streamlit dashboard for visualizing Jharkhand
Urban Local Body (Nikay) election results in real time.

To replace sample data with real data:
  1. Update data/sample_data.json with live JSON from the Jharkhand
     State Election Commission API or CSV export.
  2. Or set the env var ELECTION_DATA_URL to a remote JSON endpoint;
     the app will fetch from that URL instead of the local file.

Run locally:
  streamlit run app.py
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page config – must be the first Streamlit command
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Jharkhand Nikay Chunav Results 2026 – Live",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Jharkhand Municipal Election Results 2026 Dashboard"
    }
)

# ---------------------------------------------------------------------------
# Google AdSense verification - inject into head using components
# ---------------------------------------------------------------------------
def inject_adsense_meta():
    """Inject AdSense meta tag into page head"""
    components.html("""
    <script>
        // Try to inject meta tag into document head
        if (typeof window !== 'undefined' && window.parent && window.parent.document) {
            var meta = window.parent.document.createElement('meta');
            meta.name = 'google-adsense-account';
            meta.content = 'ca-pub-9674118663923293';
            
            // Check if meta tag already exists
            var existing = window.parent.document.querySelector('meta[name="google-adsense-account"]');
            if (!existing) {
                window.parent.document.head.appendChild(meta);
            }
        }
    </script>
    """, height=0)

# Call the function to inject meta tag
inject_adsense_meta()

# ---------------------------------------------------------------------------
# Theme colours (Jharkhand: saffron, green, blue)
# ---------------------------------------------------------------------------
SAFFRON = "#FF9933"
GREEN = "#138808"
NAVY = "#000080"
WHITE = "#FFFFFF"
LIGHT_BG = "#F8F9FA"
DARK_BG = "#0E1117"

PARTY_COLORS = {
    "JMM": "#2E7D32",
    "BJP": "#FF9933",
    "INC": "#19AAED",
    "AJSU": "#8B0000",
    "JVM": "#9C27B0",
    "IND": "#757575",
}

# ---------------------------------------------------------------------------
# Inject CSS for government-style look, responsiveness & accessibility
# ---------------------------------------------------------------------------
def inject_css(dark_mode: bool):
    bg = DARK_BG if dark_mode else WHITE
    card_bg = "#1E1E1E" if dark_mode else WHITE
    text_color = "#E0E0E0" if dark_mode else "#1a1a2e"
    border_color = "#333" if dark_mode else "#dee2e6"
    header_gradient = f"linear-gradient(135deg, {SAFFRON}, {GREEN}, {NAVY})"

    st.markdown(f"""
    <style>
        /* ---------- Global ---------- */
        .stApp {{
            background-color: {bg};
            color: {text_color};
        }}
        /* ---------- Top banner ---------- */
        .main-header {{
            background: {header_gradient};
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,.25);
        }}
        .main-header h1 {{
            color: white;
            font-size: 1.85rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 1px 1px 3px rgba(0,0,0,.4);
        }}
        .main-header p {{
            color: rgba(255,255,255,.9);
            font-size: .95rem;
            margin: .4rem 0 0;
        }}
        /* ---------- Metric cards ---------- */
        .metric-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 1.2rem 1rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
            transition: transform .2s;
        }}
        .metric-card:hover {{ transform: translateY(-3px); }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: {SAFFRON};
        }}
        .metric-label {{
            font-size: .85rem;
            color: {text_color};
            opacity: .8;
            margin-top: .3rem;
        }}
        /* ---------- Status badges ---------- */
        .badge-declared {{
            background: {GREEN}; color: white;
            padding: 2px 10px; border-radius: 12px;
            font-size: .78rem; font-weight: 600;
        }}
        .badge-counting {{
            background: {SAFFRON}; color: white;
            padding: 2px 10px; border-radius: 12px;
            font-size: .78rem; font-weight: 600;
        }}
        /* ---------- Winner card ---------- */
        .winner-card {{
            background: {card_bg};
            border-left: 5px solid {GREEN};
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
        }}
        .winner-card h3 {{ margin: 0 0 .3rem; color: {GREEN}; }}
        .winner-card p {{ margin: 0; color: {text_color}; }}
        /* ---------- Footer ---------- */
        .footer {{
            text-align: center;
            padding: 1.5rem 1rem;
            margin-top: 2rem;
            border-top: 2px solid {SAFFRON};
            font-size: .82rem;
            color: {text_color};
            opacity: .75;
        }}
        /* ---------- Auto-refresh indicator ---------- */
        .refresh-dot {{
            display: inline-block;
            width: 10px; height: 10px;
            border-radius: 50%;
            background: {GREEN};
            animation: pulse 1.5s infinite;
            margin-right: 6px;
            vertical-align: middle;
        }}
        @keyframes pulse {{
            0%,100% {{ opacity: 1; }}
            50% {{ opacity: .3; }}
        }}
        /* ---------- Responsive ---------- */
        @media (max-width: 768px) {{
            .main-header h1 {{ font-size: 1.2rem; }}
            .metric-value {{ font-size: 1.4rem; }}
        }}
        /* ---------- Accessibility: focus outline ---------- */
        *:focus-visible {{
            outline: 3px solid {SAFFRON};
            outline-offset: 2px;
        }}
        /* ---------- Enhanced button styling ---------- */
        .stButton > button {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 0.75rem;
            transition: all 0.2s ease;
            color: {text_color};
            font-weight: 500;
        }}
        .stButton > button:hover {{
            background: {SAFFRON};
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,153,51,0.3);
            border-color: {SAFFRON};
        }}
        /* ---------- Municipality card buttons ---------- */
        div[data-testid="column"] .stButton > button {{
            height: auto;
            white-space: pre-wrap;
            text-align: left;
            min-height: 80px;
        }}
        /* Ward table tweaks */
        .ward-table {{ width: 100%; border-collapse: collapse; }}
        .ward-table th {{
            background: {NAVY}; color: white;
            padding: 8px 10px; text-align: left; font-size: .82rem;
        }}
        .ward-table td {{
            padding: 7px 10px; border-bottom: 1px solid {border_color};
            font-size: .82rem; color: {text_color};
        }}
        .ward-table tr:hover {{ background: rgba(255,153,51,.08); }}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=10)
def load_data() -> dict:
    """
    Load election data from local JSON or a remote URL.
    Set env var ELECTION_DATA_URL to point to a live endpoint.
    """
    url = os.getenv("ELECTION_DATA_URL")
    if url:
        import urllib.request
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode())

    data_path = Path(__file__).parent / "data" / "sample_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_wards(data: dict) -> pd.DataFrame:
    """Flatten all ward records across municipalities into a single DataFrame."""
    rows = []
    for muni in data["municipalities"]:
        for w in muni.get("wards", []):
            row = {
                "Municipality": muni["name"],
                "Type": muni.get("type", ""),
                "Ward No.": w["ward_no"],
                "Ward Name": w.get("ward_name", f"Ward {w['ward_no']}"),
                "Status": w["status"],
                "Winner/Leading": w.get("winner") or (
                    w["candidates"][0]["name"] if w.get("candidates") else "—"
                ),
                "Party": w.get("winner_party") or (
                    w["candidates"][0]["party"] if w.get("candidates") else "—"
                ),
                "Votes": w.get("winner_votes", 0) or (
                    w["candidates"][0]["votes"] if w.get("candidates") else 0
                ),
                "Vote %": w.get("vote_pct", 0),
                "Margin": w.get("margin", 0),
                "Turnout %": w.get("turnout", 0),
                "EVM %": w.get("evm_processed", 0),
                "Counted %": w.get("votes_counted_pct", 0),
                "Category": w.get("category", "—"),
                "Gender": w.get("gender", "—"),
                "candidates": w.get("candidates", []),
            }
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------
def metric_card(label: str, value, color: str = SAFFRON) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{color}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>"""


def status_badge(status: str) -> str:
    cls = "badge-declared" if status == "Declared" else "badge-counting"
    return f'<span class="{cls}">{status}</span>'


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------

def page_home(data: dict, df: pd.DataFrame):
    """Dashboard Home – state-level overview."""
    summary = data["summary"]

    st.markdown("""
    <div class="main-header">
        <h1>🗳️ Jharkhand Nikay Chunav Results 2026 – LIVE</h1>
        <p>Jharkhand Urban Local Body (Municipal) Election Results</p>
    </div>""", unsafe_allow_html=True)

    # Summary cards
    cols = st.columns(4)
    cards = [
        ("Total ULBs", summary["total_ulbs"], SAFFRON),
        ("Total Wards", summary["total_wards"], NAVY),
        ("Results Declared", f"{len(df[df['Status']=='Declared'])}/{len(df)}", GREEN),
        ("Avg. Turnout", f"{df['Turnout %'].mean():.1f}%", "#19AAED"),
    ]
    for col, (label, val, clr) in zip(cols, cards):
        col.markdown(metric_card(label, val, clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Refresh indicator with data timestamp
    auto_on = st.session_state.get("auto_refresh", True)
    dot = '<span class="refresh-dot"></span>' if auto_on else ""
    
    # Parse the data timestamp and format it properly
    try:
        data_time = datetime.fromisoformat(data["last_updated"].replace("T", " "))
        ts = data_time.strftime("%d %b %Y, %H:%M")
    except:
        ts = datetime.now().strftime("%d %b %Y, %H:%M")
    
    st.markdown(
        f"{dot}**Last updated:** {ts} &nbsp;|&nbsp; Auto-refresh: "
        f"{'🟢 ON' if auto_on else '🔴 OFF'}",
        unsafe_allow_html=True,
    )

    st.divider()

    # Party-wise seat share
    st.subheader("Party-wise Seat Share (Declared Wards)")
    declared = df[df["Status"] == "Declared"]
    party_seats = declared["Party"].value_counts().reset_index()
    party_seats.columns = ["Party", "Seats"]
    party_seats["Color"] = party_seats["Party"].map(PARTY_COLORS).fillna("#999")

    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            party_seats, names="Party", values="Seats",
            color="Party",
            color_discrete_map=PARTY_COLORS,
            hole=0.45,
        )
        fig_pie.update_layout(
            margin=dict(t=30, b=10, l=10, r=10),
            legend=dict(orientation="h", y=-0.15),
            font=dict(size=13),
        )
        fig_pie.update_traces(textinfo="label+value+percent", textfont_size=12)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bar = px.bar(
            party_seats.sort_values("Seats", ascending=True),
            x="Seats", y="Party", orientation="h",
            color="Party",
            color_discrete_map=PARTY_COLORS,
            text="Seats",
        )
        fig_bar.update_layout(
            margin=dict(t=30, b=10, l=10, r=10),
            showlegend=False,
            yaxis_title="", xaxis_title="Seats Won",
            font=dict(size=13),
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Leading party projection
    if not party_seats.empty:
        leader = party_seats.iloc[0]
        st.success(
            f"**Leading Party:** {leader['Party']} with "
            f"**{leader['Seats']}** seats declared so far"
        )

    st.divider()

    # Municipality summary with clickable cards
    st.subheader("Municipality-wise Summary")
    st.markdown("*Click on any municipality below to view detailed ward results*")
    
    muni_summary = []
    for m in data["municipalities"]:
        wards = m.get("wards", [])
        dec = sum(1 for w in wards if w["status"] == "Declared")
        muni_summary.append({
            "name": m["name"],
            "type": m.get("type", ""),
            "total_wards": m["total_wards"],
            "declared": dec,
            "progress": f"{dec}/{m['total_wards']}",
            "pct_complete": round(dec / m["total_wards"] * 100, 1) if m["total_wards"] else 0,
        })
    
    # Create clickable municipality cards in a grid
    cols_per_row = 3
    for i in range(0, len(muni_summary), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(muni_summary):
                m = muni_summary[i + j]
                with col:
                    # Create clickable card using button
                    status_color = "🟢" if m["pct_complete"] == 100 else "🟡" if m["pct_complete"] > 50 else "🔴"
                    card_text = f"""
                    **{m['name']}**  
                    {m['type']}  
                    {status_color} {m['progress']} wards ({m['pct_complete']}%)
                    """
                    
                    if st.button(
                        card_text,
                        key=f"muni_btn_{i+j}",
                        use_container_width=True,
                        help=f"Click to view {m['name']} ward details"
                    ):
                        # Set session state to switch to municipality page
                        st.session_state.nav = "🏛️ Municipality-wise"
                        st.session_state.selected_municipality = m['name']
                        st.rerun()
    
    # Also show traditional table for reference
    st.markdown("---")
    mdf = pd.DataFrame([{
        "Municipality": m["name"],
        "Type": m["type"],
        "Total Wards": m["total_wards"],
        "Declared": m["declared"],
        "Progress": m["progress"],
        "% Complete": m["pct_complete"],
    } for m in muni_summary])
    
    st.dataframe(
        mdf.style.background_gradient(subset=["% Complete"], cmap="YlGn"),
        use_container_width=True,
        hide_index=True,
    )


def page_municipality(data: dict, df: pd.DataFrame):
    """Municipality-wise ward results with search, sort, and detail."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Municipality-wise Results</h1>
        <p>Select a municipality to view ward-level details</p>
    </div>""", unsafe_allow_html=True)

    muni_names = [m["name"] for m in data["municipalities"]]
    
    # Check if municipality was selected from home page
    default_idx = 0
    if "selected_municipality" in st.session_state:
        try:
            default_idx = muni_names.index(st.session_state.selected_municipality)
        except ValueError:
            pass
    
    selected = st.selectbox(
        "Select Municipality", 
        muni_names, 
        index=default_idx,
        key="muni_select"
    )

    muni_data = next(m for m in data["municipalities"] if m["name"] == selected)
    mdf = df[df["Municipality"] == selected].copy()

    # Mayor race info if available
    if "mayor_race" in muni_data and muni_data["mayor_race"]:
        mr = muni_data["mayor_race"]
        st.info(
            f"**Mayor Race ({mr['status']}):** "
            f"{mr['leading']} ({mr['leading_party']}) leading by "
            f"{mr['margin']} votes over {mr['trailing']} ({mr['trailing_party']})"
        )

    # Quick stats
    c1, c2, c3, c4 = st.columns(4)
    total_w = muni_data["total_wards"]
    dec = len(mdf[mdf["Status"] == "Declared"])
    c1.metric("Total Wards", total_w)
    c2.metric("Declared", dec)
    c3.metric("Counting", total_w - dec)
    c4.metric("Avg Turnout", f"{mdf['Turnout %'].mean():.1f}%")

    st.divider()

    # Search / filter
    search = st.text_input("🔍 Search by ward name or candidate", "", key="ward_search")
    if search:
        mask = (
            mdf["Ward Name"].str.contains(search, case=False, na=False) |
            mdf["Winner/Leading"].str.contains(search, case=False, na=False)
        )
        mdf = mdf[mask]

    # Build HTML table for full control
    table_html = '<table class="ward-table" role="table" aria-label="Ward results"><thead><tr>'
    headers = ["Ward No.", "Ward Name", "Status", "Winner/Leading", "Party",
               "Votes", "Vote %", "Margin", "Turnout %"]
    for h in headers:
        table_html += f"<th>{h}</th>"
    table_html += "</tr></thead><tbody>"

    for _, row in mdf.sort_values("Ward No.").iterrows():
        table_html += "<tr>"
        table_html += f"<td>{row['Ward No.']}</td>"
        table_html += f"<td>{row['Ward Name']}</td>"
        table_html += f"<td>{status_badge(row['Status'])}</td>"
        table_html += f"<td><strong>{row['Winner/Leading']}</strong></td>"
        party = row["Party"]
        pc = PARTY_COLORS.get(party, "#999")
        table_html += f'<td><span style="color:{pc};font-weight:700">{party}</span></td>'
        table_html += f"<td>{row['Votes']:,}</td>"
        table_html += f"<td>{row['Vote %']:.1f}%</td>"
        table_html += f"<td>{row['Margin']:,}</td>"
        table_html += f"<td>{row['Turnout %']:.1f}%</td>"
        table_html += "</tr>"
    table_html += "</tbody></table>"

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Ward detail expander
    st.subheader("Ward Detail View")
    ward_options = mdf.sort_values("Ward No.").apply(
        lambda r: f"Ward {r['Ward No.']} – {r['Ward Name']}", axis=1
    ).tolist()
    if ward_options:
        chosen = st.selectbox("Select Ward for Details", ward_options, key="ward_detail")
        ward_no = int(chosen.split("–")[0].replace("Ward", "").strip())
        show_ward_detail(mdf, ward_no)


def show_ward_detail(mdf: pd.DataFrame, ward_no: int):
    """Render detailed candidate-level results for a ward."""
    row = mdf[mdf["Ward No."] == ward_no].iloc[0]
    candidates = row["candidates"]

    # Winner card
    st.markdown(f"""
    <div class="winner-card">
        <h3>{"🏆 Winner" if row["Status"] == "Declared" else "📊 Leading"}: {row["Winner/Leading"]}</h3>
        <p><strong>Party:</strong> {row["Party"]} &nbsp;|&nbsp;
           <strong>Votes:</strong> {row["Votes"]:,} &nbsp;|&nbsp;
           <strong>Margin:</strong> {row["Margin"]:,}</p>
    </div>""", unsafe_allow_html=True)

    # Progress bars
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Votes Counted**")
        st.progress(min(row["Counted %"] / 100, 1.0))
        st.caption(f"{row['Counted %']:.0f}% counted")
    with c2:
        st.markdown("**EVMs Processed**")
        st.progress(min(row["EVM %"] / 100, 1.0))
        st.caption(f"{row['EVM %']:.0f}% processed")

    # Candidate table
    if candidates:
        cdf = pd.DataFrame(candidates)
        cdf["Change"] = cdf.apply(
            lambda r: r["votes"] - r.get("prev_votes", r["votes"]), axis=1
        )
        cdf.columns = [c.title() for c in cdf.columns]
        cdf = cdf.rename(columns={"Pct": "Vote %", "Prev_Votes": "Prev Votes"})

        st.markdown("**All Candidates**")
        st.dataframe(
            cdf[["Name", "Party", "Votes", "Vote %", "Change"]].style.applymap(
                lambda v: "color: green; font-weight:700" if isinstance(v, (int, float)) and v > 0
                else ("color: red; font-weight:700" if isinstance(v, (int, float)) and v < 0 else ""),
                subset=["Change"],
            ),
            use_container_width=True,
            hide_index=True,
        )

        # Vote trend chart
        fig = go.Figure()
        for _, c in cdf.iterrows():
            clr = PARTY_COLORS.get(c["Party"], "#999")
            fig.add_trace(go.Bar(
                x=[c["Name"]],
                y=[c["Votes"]],
                name=c["Name"],
                marker_color=clr,
                text=[f"{c['Votes']:,}"],
                textposition="outside",
            ))
        fig.update_layout(
            title="Candidate Vote Comparison",
            yaxis_title="Votes",
            showlegend=False,
            margin=dict(t=40, b=10, l=10, r=10),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)


def page_analytics(data: dict, df: pd.DataFrame):
    """State Summary Analytics with charts and download."""
    st.markdown("""
    <div class="main-header">
        <h1>📈 State Summary Analytics</h1>
        <p>Comprehensive analysis across all municipalities</p>
    </div>""", unsafe_allow_html=True)

    declared = df[df["Status"] == "Declared"]

    # Party-wise total seats across all municipalities
    st.subheader("Party-wise Seats Won – All Municipalities")
    party_seats = declared["Party"].value_counts().reset_index()
    party_seats.columns = ["Party", "Seats"]
    fig = px.bar(
        party_seats, x="Party", y="Seats",
        color="Party", color_discrete_map=PARTY_COLORS,
        text="Seats",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=30, b=10),
        yaxis_title="Seats Won",
        xaxis_title="",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Municipality-wise party breakdown
    st.subheader("Municipality-wise Party Breakdown")
    cross = declared.groupby(["Municipality", "Party"]).size().reset_index(name="Seats")
    fig2 = px.bar(
        cross, x="Municipality", y="Seats", color="Party",
        color_discrete_map=PARTY_COLORS,
        barmode="stack",
    )
    fig2.update_layout(
        xaxis_tickangle=-35,
        margin=dict(t=30, b=80),
        legend=dict(orientation="h", y=-0.35),
        height=450,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Top 10 highest turnout wards
    st.subheader("Top 10 Highest Turnout Wards")
    top10 = df.nlargest(10, "Turnout %")[
        ["Municipality", "Ward Name", "Winner/Leading", "Party", "Turnout %"]
    ]
    fig3 = px.bar(
        top10, x="Turnout %", y="Ward Name", orientation="h",
        color="Municipality",
        text="Turnout %",
        hover_data=["Winner/Leading", "Party"],
    )
    fig3.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=30, b=10, l=10, r=10),
        height=400,
        legend=dict(orientation="h", y=-0.25),
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # Gender-wise summary
    st.subheader("Gender-wise Winners")
    c1, c2 = st.columns(2)
    gender_data = declared["Gender"].value_counts().reset_index()
    gender_data.columns = ["Gender", "Count"]
    with c1:
        fig_g = px.pie(gender_data, names="Gender", values="Count", hole=0.4,
                       color_discrete_sequence=[SAFFRON, GREEN, NAVY])
        fig_g.update_layout(margin=dict(t=30, b=10))
        st.plotly_chart(fig_g, use_container_width=True)

    # Category-wise summary (SC/ST/OBC/General)
    cat_data = declared["Category"].value_counts().reset_index()
    cat_data.columns = ["Category", "Count"]
    with c2:
        fig_c = px.pie(cat_data, names="Category", values="Count", hole=0.4,
                       color_discrete_sequence=["#FF9933", "#138808", "#19AAED", "#9C27B0", "#757575"])
        fig_c.update_layout(margin=dict(t=30, b=10))
        st.plotly_chart(fig_c, use_container_width=True)

    st.divider()

    # Margin analysis
    st.subheader("Victory Margin Distribution")
    fig_m = px.histogram(
        declared, x="Margin", nbins=20,
        color_discrete_sequence=[SAFFRON],
        labels={"Margin": "Victory Margin (votes)"},
    )
    fig_m.update_layout(
        margin=dict(t=30, b=10),
        yaxis_title="Number of Wards",
    )
    st.plotly_chart(fig_m, use_container_width=True)

    st.divider()

    # Download section
    st.subheader("📥 Download Data")
    c1, c2 = st.columns(2)
    export_df = df.drop(columns=["candidates"])
    with c1:
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="jharkhand_election_results_2026.csv",
            mime="text/csv",
        )
    with c2:
        try:
            from io import BytesIO
            buf = BytesIO()
            export_df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                "Download Excel",
                data=buf.getvalue(),
                file_name="jharkhand_election_results_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except ImportError:
            st.info("Install openpyxl for Excel export: pip install openpyxl")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        # Header with logo and title
        col1, col2 = st.columns([1, 2])
        with col1:
            logo_path = Path(__file__).parent / "jharkhand_map.png"
            if logo_path.exists():
                st.image(str(logo_path), width=60)
            else:
                st.image(
                    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/"
                    "Emblem_of_India.svg/200px-Emblem_of_India.svg.png",
                    width=60,
                )
        with col2:
            st.markdown("""
            <div style='padding-top: 8px;'>
                <h4 style='margin: 0; color: #FF9933;'>JSEC</h4>
                <p style='margin: 0; font-size: 0.8rem; color: #666;'>Nikay Chunav 2026</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()

        # Navigation with enhanced styling
        st.markdown("###")
        page = st.radio(
            "",
            ["🏠 Dashboard Home", "🏛️ Municipality-wise", "📈 State Analytics"],
            key="nav",
        )

        st.divider()

        # Settings
        st.markdown("### ⚙️ Settings")
        dark_mode = st.toggle("🌙 Dark Mode", value=False, key="dark_mode")
        auto = st.toggle("🔄 Auto-refresh (15s)", value=True, key="auto_refresh")

        # Live status indicator
        if auto:
            st.markdown("""
            <div style='text-align: center; padding: 10px; background: #d4edda; border-radius: 5px; margin: 10px 0;'>
                <span style='color: #155724; font-size: 0.8rem;'>
                    🟢 LIVE - Auto-updating every 15s
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # Footer
        st.markdown("""
        <div style='font-size: 0.7rem; color: #666; text-align: center;'>
            <p>Data refreshes automatically when enabled.</p>
            <p><strong>Source:</strong> Jharkhand State Election Commission</p>
            <p style='color: #FF9933;'><em>Sample data for demonstration</em></p>
        </div>
        """, unsafe_allow_html=True)

    return page, dark_mode, auto


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def render_footer():
    st.markdown("""
    <div class="footer">
        <strong>Disclaimer:</strong> Data is for demonstration purposes only.
        Official results are published by the
        <a href="https://jsec.jharkhand.gov.in" target="_blank" rel="noopener">
        Jharkhand State Election Commission</a>.<br>
        © 2026 Jharkhand Nikay Chunav Results Dashboard
    </div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    page, dark_mode, auto_refresh = render_sidebar()
    inject_css(dark_mode)

    with st.spinner("Loading election data…"):
        data = load_data()
    df = flatten_wards(data)

    if page == "🏠 Dashboard Home":
        page_home(data, df)
    elif page == "🏛️ Municipality-wise":
        page_municipality(data, df)
    elif page == "📈 State Analytics":
        page_analytics(data, df)

    render_footer()

    # Auto-refresh via st.rerun
    if auto_refresh:
        time.sleep(15)
        st.rerun()


if __name__ == "__main__":
    main()
