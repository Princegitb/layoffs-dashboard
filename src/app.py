"""
app.py — Dash dashboard for exploring tech layoffs data.

Layout:
  - Year multi-select dropdown that controls every chart
  - 3 KPI cards (Total Layoffs, Companies Affected, Avg % Laid Off)
  - Monthly time-series line chart
  - Top 10 industries bar chart
  - Top 10 countries bar chart
  - Layoffs by funding stage pie chart

Run:  python src/app.py
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_clean.csv")
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

# Build the list of years for the dropdown (sorted ascending)
all_years = sorted(df["year"].dropna().unique().astype(int).tolist())

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY TEMPLATE — consistent dark styling for all charts
# ─────────────────────────────────────────────────────────────────────────────
CHART_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"          # transparent so CSS card background shows
CHART_FONT = dict(family="Inter, sans-serif", color="#e8eaf6")
CHART_MARGINS = dict(l=30, r=30, t=50, b=30)
GRIDCOLOR = "rgba(255,255,255,0.06)"

# Colour palette for charts
PALETTE = [
    "#6c63ff", "#00d2ff", "#ff6b9d", "#00e676", "#ff8a65",
    "#ab47bc", "#42a5f5", "#ffd54f", "#26c6da", "#ec407a",
]


def style_figure(fig):
    """Apply consistent styling to any Plotly figure."""
    fig.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=CHART_FONT,
        margin=CHART_MARGINS,
        xaxis=dict(gridcolor=GRIDCOLOR),
        yaxis=dict(gridcolor=GRIDCOLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# DASH APP INIT
# ─────────────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    title="Tech Layoffs Dashboard",
    assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
)
server = app.server


# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
app.layout = html.Div(className="app-container", children=[

    # ── Header ───────────────────────────────────────────────────────────
    html.Div(className="header", children=[
        html.H1("Tech Layoffs Dashboard"),
        html.P("Tracking workforce reductions across the global tech industry"),
    ]),

    # ── Year Filter ──────────────────────────────────────────────────────
    html.Div(className="filter-bar", children=[
        html.Label("Filter by Year"),
        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": str(y), "value": y} for y in all_years],
            value=all_years,          # default: all years selected
            multi=True,
            placeholder="Select year(s)...",
            className="year-dropdown",
        ),
    ]),

    # ── KPI Cards ────────────────────────────────────────────────────────
    html.Div(className="kpi-row", children=[
        html.Div(className="kpi-card", children=[
            html.Div("Total Layoffs", className="kpi-label"),
            html.Div(id="kpi-total-layoffs", className="kpi-value"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div("Companies Affected", className="kpi-label"),
            html.Div(id="kpi-companies", className="kpi-value"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div("Avg % Laid Off", className="kpi-label"),
            html.Div(id="kpi-avg-pct", className="kpi-value"),
        ]),
    ]),

    # ── Time-Series Chart (full width) ───────────────────────────────────
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-timeseries"),
        ]),
    ]),

    # ── Two-column row: Industries + Countries ───────────────────────────
    html.Div(className="charts-grid-2col", style={"marginTop": "22px"}, children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-industries"),
        ]),
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-countries"),
        ]),
    ]),

    # ── Pie chart (full width, constrained height) ───────────────────────
    html.Div(className="charts-grid", style={"marginTop": "22px"}, children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-stage"),
        ]),
    ]),
])

# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS — one callback updates all KPIs and charts from the year filter
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    # Outputs: 3 KPIs + 4 chart figures
    Output("kpi-total-layoffs", "children"),
    Output("kpi-companies",     "children"),
    Output("kpi-avg-pct",       "children"),
    Output("chart-timeseries",  "figure"),
    Output("chart-industries",  "figure"),
    Output("chart-countries",   "figure"),
    Output("chart-stage",       "figure"),
    # Input: selected years from the dropdown
    Input("year-dropdown", "value"),
)
def update_dashboard(selected_years):
    """
    Master callback: filters the dataset by the selected year(s)
    and returns updated KPI text + chart figures.
    """
    # If nothing is selected, show all data
    if not selected_years:
        filtered = df.copy()
    else:
        filtered = df[df["year"].isin(selected_years)]

    # ── KPI calculations ─────────────────────────────────────────────────
    # Sum of total_laid_off, excluding NaN
    total_layoffs = filtered["total_laid_off"].sum()
    kpi_total = f"{int(total_layoffs):,}" if pd.notna(total_layoffs) else "0"

    # Count of unique company names in the filtered data
    companies_affected = filtered["company"].nunique()
    kpi_companies = f"{companies_affected:,}"

    # Mean of percentage_laid_off, excluding NaN
    avg_pct = filtered["percentage_laid_off"].mean()
    kpi_avg_pct = f"{avg_pct:.1%}" if pd.notna(avg_pct) else "N/A"

    # ── Chart 1: Monthly time-series of total layoffs ────────────────────
    # Group by month, sum total_laid_off (NaN rows excluded automatically)
    ts = (
        filtered
        .dropna(subset=["date"])
        .set_index("date")
        .resample("MS")["total_laid_off"]   # MS = month-start frequency
        .sum()
        .reset_index()
    )
    ts.columns = ["date", "total_laid_off"]

    fig_ts = px.area(
        ts, x="date", y="total_laid_off",
        title="Monthly Layoffs Over Time",
        labels={"date": "", "total_laid_off": "Layoffs"},
        color_discrete_sequence=["#6c63ff"],
    )
    fig_ts.update_traces(
        line=dict(width=2.5),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.15)",
    )
    style_figure(fig_ts)

    # ── Chart 2: Top 10 industries by total layoffs ──────────────────────
    top_industries = (
        filtered
        .groupby("industry", dropna=True)["total_laid_off"]
        .sum()
        .nlargest(10)
        .sort_values()   # ascending for horizontal bar
        .reset_index()
    )

    fig_ind = px.bar(
        top_industries, x="total_laid_off", y="industry",
        orientation="h",
        title="Top 10 Industries by Layoffs",
        labels={"total_laid_off": "Total Layoffs", "industry": ""},
        color="total_laid_off",
        color_continuous_scale=["#6c63ff", "#00d2ff"],
    )
    fig_ind.update_layout(coloraxis_showscale=False)
    style_figure(fig_ind)

    # ── Chart 3: Top 10 countries by total layoffs ───────────────────────
    top_countries = (
        filtered
        .groupby("country", dropna=True)["total_laid_off"]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )

    fig_ctry = px.bar(
        top_countries, x="total_laid_off", y="country",
        orientation="h",
        title="Top 10 Countries by Layoffs",
        labels={"total_laid_off": "Total Layoffs", "country": ""},
        color="total_laid_off",
        color_continuous_scale=["#ff6b9d", "#ff8a65"],
    )
    fig_ctry.update_layout(coloraxis_showscale=False)
    style_figure(fig_ctry)

    # ── Chart 4: Layoffs by funding stage (pie) ──────────────────────────
    stage_data = (
        filtered
        .groupby("stage", dropna=True)["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("total_laid_off", ascending=False)
    )

    fig_stage = px.pie(
        stage_data, values="total_laid_off", names="stage",
        title="Layoffs by Funding Stage",
        color_discrete_sequence=PALETTE,
        hole=0.42,   # donut style
    )
    fig_stage.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="%{label}<br>%{value:,} layoffs<br>%{percent}<extra></extra>",
    )
    style_figure(fig_stage)
    fig_stage.update_layout(height=480)

    return kpi_total, kpi_companies, kpi_avg_pct, fig_ts, fig_ind, fig_ctry, fig_stage


# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
