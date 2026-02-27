# Jharkhand Municipal Election Results 2026 – Live Dashboard

A production-ready **Streamlit** dashboard for visualizing Jharkhand Urban Local Body (Nikay) election results in real time, built with Python, Pandas, and Plotly.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit 1.32+](https://img.shields.io/badge/Streamlit-1.32%2B-red)

---

## Features

- **Dashboard Home** – state-level summary cards, party-wise pie/bar charts, leading party projection
- **Municipality-wise View** – searchable ward tables, candidate detail view with vote comparison charts
- **State Analytics** – cross-municipality breakdowns, turnout ranking, gender/category analysis, margin histogram
- **Auto-refresh** every 15 seconds (toggleable)
- **Dark / Light mode** toggle
- **CSV & Excel download** for the full dataset
- **Mobile-responsive** and WCAG 2.1 AA accessible
- Official government-style design (saffron, green, blue palette)

## Municipalities Covered (sample data)

| Municipality | Type | Wards (data) |
|---|---|---|
| Ranchi Municipal Corporation | Municipal Corporation | 13 |
| Koderma Nagar Panchayat | Nagar Panchayat | 7 |
| Basukinath Nagar Panchayat | Nagar Panchayat | 12 |
| Pakur Nagar Panchayat | Nagar Panchayat | 21 |
| Madhupur Nagar Parishad | Nagar Parishad | 5 |
| Jugsalai Nagar Parishad | Nagar Parishad | 4 |
| Gumla Nagar Panchayat | Nagar Panchayat | 11 |
| Medininagar Nagar Nigam | Nagar Nigam | 7 |
| Latehar Nagar Panchayat | Nagar Panchayat | 9 |
| Chaibasa Nagar Parishad | Nagar Parishad | 4 |
| Hazaribagh Nagar Nigam | Nagar Nigam | 4 |

---

## Project Structure

```
JH Election/
├── app.py                  # Main Streamlit application
├── data/
│   └── sample_data.json    # Election data (replace with live data)
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── api/
│   └── index.py            # Vercel serverless entry point
└── README.md               # This file
```

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/jh-election-results.git
cd jh-election-results

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Replacing Sample Data with Real Data

### Option A: Replace the JSON file

Edit `data/sample_data.json` with live data from the Jharkhand State Election Commission. The schema must match:

```json
{
  "election_name": "...",
  "last_updated": "ISO-8601 timestamp",
  "summary": { "total_ulbs": 12, "total_wards": 1248, "declared": 987, "turnout": 64.8 },
  "municipalities": [
    {
      "name": "Ranchi Municipal Corporation",
      "type": "Municipal Corporation",
      "total_wards": 55,
      "declared": 52,
      "wards": [
        {
          "ward_no": 1,
          "ward_name": "Ward 1 - Doranda",
          "status": "Declared",
          "winner": "Candidate Name",
          "winner_party": "PARTY",
          "winner_votes": 1245,
          "vote_pct": 42.3,
          "margin": 187,
          "turnout": 68.2,
          "evm_processed": 100,
          "votes_counted_pct": 100,
          "category": "ST",
          "gender": "Female",
          "candidates": [
            {"name": "...", "party": "...", "votes": 1245, "pct": 42.3, "prev_votes": 1100}
          ]
        }
      ]
    }
  ]
}
```

### Option B: Point to a live API

Set the environment variable `ELECTION_DATA_URL` to a URL that returns JSON in the above format:

```bash
export ELECTION_DATA_URL="https://api.jsec.jharkhand.gov.in/results.json"
streamlit run app.py
```

---

## Deploy to Vercel via GitHub

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Jharkhand election dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/jh-election-results.git
git push -u origin main
```

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **"Add New… → Project"**.
3. Import your `jh-election-results` repository.
4. Vercel will detect the `vercel.json` configuration automatically.
5. Click **Deploy**.
6. Your dashboard will be live at `https://jh-election-results.vercel.app` (or your custom domain).

> **Note:** Streamlit apps on Vercel use the serverless Python runtime. The `vercel.json` and `api/index.py` files handle the routing. For the best experience with Streamlit's WebSocket features, consider Streamlit Community Cloud or Hugging Face Spaces as well.

---

## Deploy to Hugging Face Spaces (One-Click)

### Step 1: Create a new Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces).
2. Click **"Create new Space"**.
3. Choose **Streamlit** as the SDK.
4. Set runtime to **Python 3.11**.
5. Name it `jharkhand-election-results`.

### Step 2: Upload files

Upload these files to your Space:
- `app.py`
- `requirements.txt`
- `data/sample_data.json`

### Step 3: Make it public

1. Go to **Settings → Visibility** and set to **Public**.
2. Your dashboard will be live at:
   `https://huggingface.co/spaces/YOUR_USERNAME/jharkhand-election-results`

---

## Deploy to Streamlit Community Cloud

1. Push your code to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click **"New app"** → select your repo → set main file to `app.py`.
4. Click **Deploy**.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit 1.32+ |
| Data | Pandas, JSON |
| Charts | Plotly |
| Language | Python 3.11+ |
| Export | openpyxl (Excel), CSV |

---

## Disclaimer

> Data shown in this dashboard is for **demonstration purposes only**. Official election results are published by the [Jharkhand State Election Commission](https://jsec.jharkhand.gov.in).

---

## License

MIT License – free to use, modify, and distribute.
