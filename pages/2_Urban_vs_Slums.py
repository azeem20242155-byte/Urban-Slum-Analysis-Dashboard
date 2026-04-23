import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Urbanisation vs Slums")

df = pd.read_csv("data_processed/final_dataset.csv")

# Keep one row per country for the scatter plot
summary = df[[
    "country",
    "country_code",
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
]].drop_duplicates()

# Remove missing values just in case
summary = summary.dropna(subset=[
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
])

st.markdown("""
### What this page shows
This view compares **urban population growth** with **change in slum share**.

It helps identify whether countries are:
- urbanising while improving housing conditions, or
- urbanising while slum conditions are worsening
""")

st.info("""
**How to read this chart:**
- **Right side** = strong urban population growth
- **Above zero** = slum share increased
- **Below zero** = slum share decreased

Countries in the **bottom-right area** may represent more successful urbanisation,
while countries in the **top-right area** may be facing growing housing pressure.
""")

# Cap extreme values so the chart is easier to read
summary["urban_growth_capped"] = summary["urban_growth_total"].clip(upper=300)

# Bubble size must always be positive
summary["bubble_size"] = summary["slum_population_change_total"].abs()

fig = px.scatter(
    summary,
    x="urban_growth_capped",
    y="slum_change_total",
    hover_name="country",
    hover_data={
        "urban_growth_total": ":.1f",
        "slum_change_total": ":.1f",
        "slum_population_change_total": ":,.0f",
        "urban_growth_capped": False,
        "bubble_size": False
    },
    size="bubble_size",
    color="slum_population_change_total",
    labels={
        "urban_growth_capped": "Urban population growth (%)",
        "slum_change_total": "Change in slum share (percentage points)",
        "bubble_size": "Absolute change in slum population",
        "slum_population_change_total": "Change in slum population"
    },
    title="Urbanisation vs Slum Conditions: Country-Level Patterns (2000–2022)"
)

fig.add_hline(y=0, line_dash="dash")
fig.add_vline(x=0, line_dash="dash")

# Add quadrant labels
fig.add_annotation(x=220, y=50, text="High growth + worsening slums", showarrow=False)
fig.add_annotation(x=220, y=-50, text="High growth + improving slums", showarrow=False)
fig.add_annotation(x=20, y=50, text="Low growth + worsening", showarrow=False)
fig.add_annotation(x=20, y=-50, text="Low growth + improving", showarrow=False)


st.plotly_chart(fig, use_container_width=True)

st.subheader("Country comparison table")

sort_option = st.selectbox(
    "Sort countries by",
    [
        "Urban growth (highest first)",
        "Slum change (highest first)",
        "Slum change (lowest first)"
    ]
)

if sort_option == "Urban growth (highest first)":
    table = summary.sort_values("urban_growth_total", ascending=False)
elif sort_option == "Slum change (highest first)":
    table = summary.sort_values("slum_change_total", ascending=False)
else:
    table = summary.sort_values("slum_change_total", ascending=True)

table_df = table[[
    "country",
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
]].copy()

st.dataframe(
    table_df.style.format({
        "urban_growth_total": "{:.1f}%",
        "slum_change_total": "{:.1f} pp",
        "slum_population_change_total": "{:,.0f}"
    }),
    use_container_width=True
)

best_zone = summary[
    (summary["urban_growth_total"] > 0) & (summary["slum_change_total"] < 0)
]
worst_zone = summary[
    (summary["urban_growth_total"] > 0) & (summary["slum_change_total"] > 0)
]

st.success(
    f"""
**Key insight:** {len(best_zone)} countries show urban growth together with a falling slum share,
while {len(worst_zone)} countries show urban growth together with a rising slum share.

This highlights that urbanisation alone does not guarantee better housing outcomes.
The quality of planning, housing policy and infrastructure development appears to matter just as much as growth itself.
"""
)