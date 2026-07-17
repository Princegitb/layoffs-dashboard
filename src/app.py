

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_clean.csv")
df = pd.read_csv(DATA_PATH, parse_dates=["date"])


all_years = sorted(df["year"].dropna().unique().astype(int).tolist())


CHART_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"         
CHART_FONT = dict(family="Inter, sans-serif", color="#e8eaf6")
CHART_MARGINS = dict(l=30, r=30, t=50, b=30)
GRIDCOLOR = "rgba(255,255,255,0.06)"

PALETTE = [
    "#ffffff", "#f5f5f5", "#e5e5e5", "#d4d4d4", "#a3a3a3",
    "#737373", "#525252", "#404040", "#262626", "#171717"
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
───────────────────────────────────────────────
app = Dash(
    __name__,
    title="Tech Layoffs Dashboard",
    assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
)
server = app.server



app.layout = html.Div(className="app-container", children=[

    html.Div(className="header", children=[
        html.H1("Tech Layoffs Dashboard"),
        html.P("Tracking workforce reductions across the global tech industry"),
    ]),

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


    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-timeseries"),
        ]),
    ]),

    
    html.Div(className="charts-grid-2col", style={"marginTop": "22px"}, children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-industries"),
        ]),
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-countries"),
        ]),
    ]),

   
    html.Div(className="charts-grid", style={"marginTop": "22px"}, children=[
        html.Div(className="chart-card", children=[
            dcc.Graph(id="chart-stage"),
        ]),
    ]),
])


@app.callback(
    
    Output("kpi-total-layoffs", "children"),
    Output("kpi-companies",     "children"),
    Output("kpi-avg-pct",       "children"),
    Output("chart-timeseries",  "figure"),
    Output("chart-industries",  "figure"),
    Output("chart-countries",   "figure"),
    Output("chart-stage",       "figure"),
   
    Input("year-dropdown", "value"),
)
def update_dashboard(selected_years):
    """
    Master callback: filters the dataset by the selected year(s)
    and returns updated KPI text + chart figures.
    """
    
    if not selected_years:
        filtered = df.copy()
    else:
        filtered = df[df["year"].isin(selected_years)]

  
    total_layoffs = filtered["total_laid_off"].sum()
    kpi_total = f"{int(total_layoffs):,}" if pd.notna(total_layoffs) else "0"

   
    companies_affected = filtered["company"].nunique()
    kpi_companies = f"{companies_affected:,}"

    avg_pct = filtered["percentage_laid_off"].mean()
    kpi_avg_pct = f"{avg_pct:.1%}" if pd.notna(avg_pct) else "N/A"

    
    ts = (
        filtered
        .dropna(subset=["date"])
        .set_index("date")
        .resample("MS")["total_laid_off"]   
        .sum()
        .reset_index()
    )
    ts.columns = ["date", "total_laid_off"]

    fig_ts = px.area(
        ts, x="date", y="total_laid_off",
        title="Monthly Layoffs Over Time",
        labels={"date": "", "total_laid_off": "Layoffs"},
        color_discrete_sequence=["#ffffff"],
    )
    fig_ts.update_traces(
        line=dict(width=2.5),
        fill="tozeroy",
        fillcolor="rgba(255, 255, 255, 0.07)",
    )
    style_figure(fig_ts)

    
    top_industries = (
        filtered
        .groupby("industry", dropna=True)["total_laid_off"]
        .sum()
        .nlargest(10)
        .sort_values()  
        .reset_index()
    )

    fig_ind = px.bar(
        top_industries, x="total_laid_off", y="industry",
        orientation="h",
        title="Top 10 Industries by Layoffs",
        labels={"total_laid_off": "Total Layoffs", "industry": ""},
        color="total_laid_off",
        color_continuous_scale=["#262626", "#ffffff"],
    )
    fig_ind.update_layout(coloraxis_showscale=False)
    style_figure(fig_ind)

 
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
        color_continuous_scale=["#404040", "#e5e5e5"],
    )
    fig_ctry.update_layout(coloraxis_showscale=False)
    style_figure(fig_ctry)

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

if __name__ == "__main__":
    app.run(debug=True)
