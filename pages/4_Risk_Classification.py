import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Risk Classification")

df = pd.read_csv("data_processed/final_dataset.csv")

# ----------------------------
# Build summary
# ----------------------------
summary = df[[
    "country",
    "country_code",
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
]].drop_duplicates().dropna()

summary["bubble_size"] = summary["slum_population_change_total"].abs()

# ----------------------------
# Classification
# ----------------------------
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

# ----------------------------
# Risk score
# ----------------------------
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

summary["urban_growth_capped"] = summary["urban_growth_total"].clip(upper=300)

# ----------------------------
# Intro
# ----------------------------
st.markdown("""
### What this page shows

This page groups countries into **urban development risk categories** using:

- Urban population growth  
- Change in slum share  
- Change in estimated slum population  

The objective is to identify where urban growth is **effectively managed**
versus where **housing pressure is intensifying**.
""")

st.info("""
**How to interpret the chart:**

- Top-right → High growth + worsening conditions (**High Risk**)  
- Bottom-right → High growth + improving conditions (**Best Managed**)  
- Top-left → Low growth + worsening  
- Bubble size → magnitude of slum population change  
""")

# ----------------------------
# KPIs
# ----------------------------
counts = summary["risk_category"].value_counts()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Countries analysed", len(summary))
c2.metric("Improving", counts.get("Improving urbanisation", 0))
c3.metric("Under pressure", counts.get("Growth with pressure", 0))
c4.metric("Deteriorating", counts.get("Housing deterioration", 0))

st.markdown("---")

# ----------------------------
# FILTERS
# ----------------------------
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

# ----------------------------
# SCATTER
# ----------------------------
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
        "slum_population_change_total": ":,.0f"
    },
    color_discrete_map={
        "Improving urbanisation": "#2E8B57",
        "Growth with pressure": "#FF4B4B",
        "Housing deterioration": "#8B0000",
        "Low growth / mixed outcome": "#87CEEB"
    },
    labels={
        "urban_growth_capped": "Urban growth (%)",
        "slum_change_total": "Change in slum share (pp)"
    }
)

fig.add_hline(y=0, line_dash="dash")
fig.add_vline(x=0, line_dash="dash")

fig.update_yaxes(range=[-80, 80])
fig.update_xaxes(range=[0, 300])

fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# DISTRIBUTION
# ----------------------------
st.subheader("Distribution of risk categories")

dist = summary["risk_category"].value_counts().reset_index()
dist.columns = ["category", "count"]

fig2 = px.bar(
    dist,
    x="category",
    y="count",
    color="category",
    text="count",
    color_discrete_map={
        "Improving urbanisation": "#2E8B57",
        "Growth with pressure": "#FF4B4B",
        "Housing deterioration": "#8B0000",
        "Low growth / mixed outcome": "#87CEEB"
    }
)

fig2.update_layout(showlegend=False, template="plotly_white")

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------
st.subheader("Country classification table")

sort_option = st.selectbox(
    "Sort countries by",
    [
        "Highest risk score",
        "Highest urban growth",
        "Largest increase in slum share",
        "Largest decrease in slum share"
    ]
)

table = summary.copy()

if sort_option == "Highest risk score":
    table = table.sort_values(["risk_score", "slum_change_total"], ascending=[False, False])
elif sort_option == "Highest urban growth":
    table = table.sort_values("urban_growth_total", ascending=False)
elif sort_option == "Largest increase in slum share":
    table = table.sort_values("slum_change_total", ascending=False)
else:
    table = table.sort_values("slum_change_total")

st.dataframe(
    table[[
        "country",
        "risk_category",
        "risk_score",
        "urban_growth_total",
        "slum_change_total"
    ]].style.format({
        "urban_growth_total": "{:.1f}%",
        "slum_change_total": "{:.1f} pp"
    }),
    use_container_width=True
)

# ----------------------------
# WORST / BEST
# ----------------------------
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Highest risk countries")
    worst = summary.sort_values(
        ["risk_score", "slum_change_total"],
        ascending=[False, False]
    ).head(10)
    st.dataframe(worst[["country", "risk_category", "risk_score"]], use_container_width=True)

with col2:
    st.subheader("Best performing countries")
    best = summary[
        (summary["urban_growth_total"] > 0) &
        (summary["slum_change_total"] < 0)
    ].sort_values("slum_change_total").head(10)
    st.dataframe(best[["country", "urban_growth_total", "slum_change_total"]], use_container_width=True)

# ----------------------------
# INSIGHT 
# ----------------------------
st.subheader("Key takeaway")

st.success(f"""
Out of **{len(summary)} countries**,  

- **{counts.get("Improving urbanisation", 0)}** show improving urbanisation  
- **{counts.get("Growth with pressure", 0)}** face increasing housing pressure  
- **{counts.get("Housing deterioration", 0)}** exhibit worsening conditions  

### Key insight:

Urban population growth alone does not guarantee improved living conditions.

While some countries successfully absorb urban expansion,
others experience rising slum populations and increasing housing stress.

This suggests that outcomes depend heavily on **urban planning, infrastructure investment,
and housing policy effectiveness**, rather than growth alone.
""")

# ----------------------------
# METHOD
# ----------------------------
with st.expander("Method note"):
    st.write("""
This is a simplified classification designed for analytical comparison.

It is not a causal model. Countries are grouped using:
- Urban population growth
- Change in slum share
- Change in slum population
""")

# ----------------------------
# DOWNLOAD
# ----------------------------
st.download_button(
    "Download classification data",
    summary.to_csv(index=False),
    "risk_classification.csv",
    "text/csv"
)