# Tech Layoffs Dashboard 

A modern, interactive dashboard built with **Dash** and **Plotly** to visualize and analyze global tech layoff trends.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Dash](https://img.shields.io/badge/Dash-Plotly-informational)

##  Features

- **Interactive Filtering:** Filter data dynamically by year using a multi-select dropdown.
- **KPI Metrics:** Quick insights into Total Layoffs, Companies Affected, and Average Percentage Laid Off.
- **Time-Series Analysis:** A sleek area chart showing monthly layoffs over time.
- **Industry & Country Insights:** Horizontal bar charts highlighting the top 10 most affected industries and countries.
- **Funding Stage Breakdown:** A donut chart showing the distribution of layoffs across different company funding stages.
- **Modern UI/UX:** Clean, minimalist monochrome styling featuring stark black backgrounds, sharp border cards, and custom-styled grayscale interactive charts.

##  Project Structure

```
layoffs-dashboard/
├── data/
│   ├── layoffs_raw.csv        # Original, uncleaned dataset
│   └── layoffs_clean.csv      # Standardized data used by the app
├── src/
│   ├── clean_data.py          # Data cleaning and preprocessing script
│   ├── app.py                 # Main Dash application
│   └── assets/
│       └── style.css          # Custom CSS for UI styling
├── notebooks/                 # Directory for Jupyter exploration
├── .gitignore                 # Git ignore file
└── README.md                  # Project documentation
```

##  Getting Started

### Prerequisites

Ensure you have Python installed. Then, install the required dependencies:

```bash
pip install pandas plotly dash
```

### 1. Clean the Data

Before running the app, process the raw data by running the cleaning script. This script formats dates, standardizes text casing, and handles missing values.

```bash
python src/clean_data.py
```

### 2. Run the Dashboard

Start the Dash server:

```bash
python src/app.py
```

Open your browser and navigate to `http://127.0.0.1:8050/` to interact with the dashboard.

##  Built With

- [Dash](https://dash.plotly.com/) - The web framework used.
- [Plotly Express](https://plotly.com/python/plotly-express/) - Used for creating the interactive charts.
- [Pandas](https://pandas.pydata.org/) - For data manipulation and analysis.

##  License

This project is open-source and available under the MIT License.
