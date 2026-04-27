import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Risk Classification")

# Load cleaned dataset
df = pd.read_csv("data_processed/final_dataset.csv")


# Build summary
# I keep one row per country because this page compares countries, not yearly trends

summary = df[[
    "country",
    "country_code",
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
]].drop_duplicates().dropna()

# Bubble size must be positive because Plotly does not allow negative marker sizes
summary["bubble_size"] = summary["slum_population_change_total"].abs()


# Classification
# Countries are grouped based on urban growth and direction of slum change

def classify_country(row):
    if row["urban_growth_total"] > 0 and row["slum_change_total"] < 0:
        return "Improving urbanisation"
    elif row["urban_growth_total"] > 0 and row["slum_change_total"] > 0:
        return "Growth with pressure"
    elif row["urban_growth_total"] <= 0 and row["slum_change_total"] > 0:
        return "Housing deterioration"
    else:
        return "Low growth / mixed outcome"


summary["risk_category"] = summary.apply(classify_country, axis=1)


# Risk score
# This simple score is used only for ranking countries in the dashboard

def risk_score(row):
    score = 0

    if row["urban_growth_total"] > 0:
        score += 1
    if row["slum_change_total"] > 0:
        score += 2
    if row["slum_population_change_total"] > 0:
        score += 1

    return score


summary["risk_score"] = summary.apply(risk_score, axis=1)

# Cap very high urban growth values so the scatter plot stays readable
summary["urban_growth_capped"] = summary["urban_growth_total"].clip(upper=300)


# Intro

st.markdown("""

This page groups countries into **urban development risk categories** using:

- Urban population growth  
- Change in slum share  
- Change in estimated slum population  

The objective is to identify where urban growth is being effectively managed
and where housing pressure may be increasing.
""")

st.info("""
**How to interpret the chart:**

- Top-right = high growth + worsening conditions  
- Bottom-right = high growth + improving conditions  
- Top-left = low growth + worsening conditions  
- Bubble size = magnitude of change in estimated slum population  
""")


# KPI cards

counts = summary["risk_category"].value_counts()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Countries analysed", len(summary))
c2.metric("Improving", counts.get("Improving urbanisation", 0))
c3.metric("Under pressure", counts.get("Growth with pressure", 0))
c4.metric("Deteriorating", counts.get("Housing deterioration", 0))

st.markdown("---")


# Filters
# These checkboxes allow the user to focus on specific risk groups

st.subheader("Filters")

f1, f2, f3, f4 = st.columns(4)

with f1:
    show_improving = st.checkbox("Improving", True)
with f2:
    show_pressure = st.checkbox("Pressure", True)
with f3:
    show_deterioration = st.checkbox("Deteriorating", True)
with f4:
    show_low = st.checkbox("Low growth", True)

filtered = summary[
    ((summary["risk_category"] == "Improving urbanisation") & show_improving) |
    ((summary["risk_category"] == "Growth with pressure") & show_pressure) |
    ((summary["risk_category"] == "Housing deterioration") & show_deterioration) |
    ((summary["risk_category"] == "Low growth / mixed outcome") & show_low)
]


# Scatter plot
# This is the main decision-support visual for the classification page

st.subheader("Country risk map")

fig = px.scatter(
    filtered,
    x="urban_growth_capped",
    y="slum_change_total",
    color="risk_category",
    size="bubble_size",
    hover_name="country",
    hover_data={
        "urban_growth_total": ":.1f",
        "slum_change_total": ":.1f",
        "slum_population_change_total": ":,.0f",
        "urban_growth_capped": False,
        "bubble_size": False
    },
    color_discrete_map={
        "Improving urbanisation": "#2E8B57",
        "Growth with pressure": "#FF4B4B",
        "Housing deterioration": "#8B0000",
        "Low growth / mixed outcome": "#87CEEB"
    },
    labels={
        "urban_growth_capped": "Urban Population Growth (%)",
        "slum_change_total": "Change in Slum Share (percentage points)",
        "risk_category": "Risk Category",
        "urban_growth_total": "Urban Population Growth (%)",
        "slum_population_change_total": "Change in Estimated Slum Population"
    },
    title="Country Risk Map Based on Urban Growth and Slum Change"
)

# Reference lines divide the chart into four interpretation zones
fig.add_hline(y=0, line_dash="dash")
fig.add_vline(x=0, line_dash="dash")

fig.update_xaxes(
    range=[0, 300],
    title="Urban Population Growth (%)"
)

fig.update_yaxes(
    range=[-80, 80],
    title="Change in Slum Share (percentage points)"
)

fig.update_layout(
    template="plotly_white",
    legend_title_text="Risk Category",
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)


# Category distribution
# This summarises how many countries fall into each risk category

st.subheader("Distribution of risk categories")

dist = summary["risk_category"].value_counts().reset_index()
dist.columns = ["Risk Category", "Number of Countries"]

fig2 = px.bar(
    dist,
    x="Risk Category",
    y="Number of Countries",
    color="Risk Category",
    text="Number of Countries",
    color_discrete_map={
        "Improving urbanisation": "#2E8B57",
        "Growth with pressure": "#FF4B4B",
        "Housing deterioration": "#8B0000",
        "Low growth / mixed outcome": "#87CEEB"
    },
    title="Number of Countries in Each Risk Category"
)

fig2.update_layout(
    showlegend=False,
    template="plotly_white",
    xaxis_title="Risk Category",
    yaxis_title="Number of Countries"
)

st.plotly_chart(fig2, use_container_width=True)


# Worst and best countries
# I removed the full raw table and kept only the two comparison tables because they are more useful for decision-makers

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Highest risk countries")

    worst = summary.sort_values(
        ["risk_score", "slum_change_total"],
        ascending=[False, False]
    ).head(10)

    st.dataframe(
        worst[[
            "country",
            "risk_category",
            "risk_score",
            "urban_growth_total",
            "slum_change_total"
        ]].style.format({
            "urban_growth_total": "{:.1f}%",
            "slum_change_total": "{:.1f} pp"
        }),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Best performing countries")

    best = summary[
        (summary["urban_growth_total"] > 0) &
        (summary["slum_change_total"] < 0)
    ].sort_values("slum_change_total").head(10)

    st.dataframe(
        best[[
            "country",
            "urban_growth_total",
            "slum_change_total"
        ]].style.format({
            "urban_growth_total": "{:.1f}%",
            "slum_change_total": "{:.1f} pp"
        }),
        use_container_width=True,
        hide_index=True
    )


# Key takeaway

st.subheader("Key takeaway")

st.success(f"""
Out of **{len(summary)} countries**:

- **{counts.get("Improving urbanisation", 0)}** show improving urbanisation  
- **{counts.get("Growth with pressure", 0)}** face increasing housing pressure  
- **{counts.get("Housing deterioration", 0)}** exhibit worsening conditions  

**Main insight:** Urban population growth alone does not guarantee improved living conditions.

Some countries are successfully absorbing urban expansion, while others experience rising slum populations and increasing housing stress.
This suggests that outcomes depend heavily on urban planning, infrastructure investment and housing policy effectiveness.
""")


