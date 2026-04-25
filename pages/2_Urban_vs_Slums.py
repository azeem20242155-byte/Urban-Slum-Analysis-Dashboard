import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Urbanisation vs Slums")

# Load cleaned dataset
df = pd.read_csv("data_processed/final_dataset.csv")

# Keep one row per country for the scatter plot
summary = df[[
    "country",
    "country_code",
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
]].drop_duplicates()

# Remove missing values to avoid plotting errors
summary = summary.dropna(subset=[
    "urban_growth_total",
    "slum_change_total",
    "slum_population_change_total"
])

st.markdown("""
### What this page shows

This page compares **urban population growth** with the **change in slum share**.

The purpose is to identify whether countries are:
- urbanising while improving housing conditions, or
- urbanising while slum conditions are worsening
""")

st.info("""
**How to read this chart:**

- Right side = stronger urban population growth
- Above zero = slum share increased
- Below zero = slum share decreased
- Larger bubbles = larger change in estimated slum population

The bottom-right area represents countries that grew urban populations while reducing slum share.
The top-right area represents countries where urban growth was linked with worsening slum conditions.
""")

# Cap extreme urban growth values so the chart is easier to read
summary["urban_growth_capped"] = summary["urban_growth_total"].clip(upper=300)

# Bubble size must always be positive
summary["bubble_size"] = summary["slum_population_change_total"].abs()

# Create a simple category for clearer colour interpretation
def classify_pattern(row):
    if row["urban_growth_total"] > 0 and row["slum_change_total"] < 0:
        return "Improving with growth"
    elif row["urban_growth_total"] > 0 and row["slum_change_total"] > 0:
        return "Growth with pressure"
    elif row["urban_growth_total"] <= 0 and row["slum_change_total"] > 0:
        return "Low growth + worsening"
    else:
        return "Low growth + improving"

summary["pattern"] = summary.apply(classify_pattern, axis=1)

# Main scatter chart
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
        "bubble_size": False,
        "pattern": True
    },
    size="bubble_size",
    color="pattern",
    color_discrete_map={
        "Improving with growth": "#2E8B57",
        "Growth with pressure": "#FF4B4B",
        "Low growth + worsening": "#8B0000",
        "Low growth + improving": "#87CEEB"
    },
    labels={
        "urban_growth_capped": "Urban Population Growth (%)",
        "slum_change_total": "Change in Slum Share (percentage points)",
        "slum_population_change_total": "Change in Estimated Slum Population",
        "pattern": "Urbanisation Pattern"
    },
    title="Urban Growth vs Change in Slum Share"
)

# Add reference lines to create four clear quadrants
fig.add_hline(y=0, line_dash="dash")
fig.add_vline(x=0, line_dash="dash")

# Add quadrant labels
fig.add_annotation(x=220, y=50, text="High growth + worsening", showarrow=False)
fig.add_annotation(x=220, y=-50, text="High growth + improving", showarrow=False)
fig.add_annotation(x=20, y=50, text="Low growth + worsening", showarrow=False)
fig.add_annotation(x=20, y=-50, text="Low growth + improving", showarrow=False)

# Improved the chart formatting for better readability
fig.update_layout(
    template="plotly_white",
    hovermode="closest",
    legend_title_text="Urbanisation Pattern"
)

fig.update_xaxes(range=[0, 300], title="Urban Population Growth (%)")
fig.update_yaxes(range=[-80, 80], title="Change in Slum Share (percentage points)")

st.plotly_chart(fig, use_container_width=True)

# Key insight calculation
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