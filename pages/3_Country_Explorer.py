import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Country Explorer")

df = pd.read_csv("data_processed/final_dataset.csv")


# Country + Year Selection

countries = sorted(df["country"].unique())
selected_country = st.selectbox("Select a country", countries)

country_df = df[df["country"] == selected_country].sort_values("year").copy()

year_min = int(country_df["year"].min())
year_max = int(country_df["year"].max())

years = st.slider(
    "Select year range",
    year_min,
    year_max,
    (year_min, year_max)
)

country_df = country_df[
    (country_df["year"] >= years[0]) &
    (country_df["year"] <= years[1])
].copy()

# Global comparison

global_trend = df.groupby("year").agg({
    "slum_pct": "mean",
    "urban_pop": "sum"
}).reset_index()

country_df = country_df.merge(
    global_trend,
    on="year",
    suffixes=("", "_global")
)

latest = country_df.iloc[-1]
first = country_df.iloc[0]

slum_change_total = latest["slum_pct"] - first["slum_pct"]
urban_growth_total = ((latest["urban_pop"] - first["urban_pop"]) / first["urban_pop"]) * 100
slum_population_change_total = latest["slum_population"] - first["slum_population"]


# Header

st.markdown(f"""
### Country profile: {selected_country}

This page analyses how **urban population growth** and **slum conditions** have evolved over time.
""")


# Metrics

c1, c2, c3 = st.columns(3)

delta_slum = latest["slum_pct"] - first["slum_pct"]

with c1:
    st.metric(
        "Latest slum share",
        f"{latest['slum_pct']:.1f}%",
        delta=f"{delta_slum:.1f} pp"
    )

with c2:
    st.metric(
        "Urban population growth",
        f"{urban_growth_total:.1f}%"
    )

with c3:
    st.metric(
        "Change in slum population",
        f"{slum_population_change_total:,.0f}"
    )


# Explanation

st.info("""
**How to read this page:**
- Slum share indicates housing conditions
- Urban population shows growth pressure
- Slum population reflects real human impact
""")


# Trends

st.markdown("### Trends over time")

fig1 = px.line(
    country_df,
    x="year",
    y="slum_pct",
    markers=True,
    title=f"Slum Share vs Global Average – {selected_country}"
)

fig1.add_scatter(
    x=country_df["year"],
    y=country_df["slum_pct_global"],
    mode="lines",
    name="Global average",
    line=dict(dash="dash")
)

fig1.update_layout(template="plotly_white", hovermode="x unified")

fig2 = px.line(
    country_df,
    x="year",
    y="urban_pop",
    markers=True,
    title=f"Urban Population Over Time – {selected_country}"
)

fig2.update_layout(template="plotly_white", hovermode="x unified")

fig3 = px.line(
    country_df,
    x="year",
    y="slum_population",
    markers=True,
    title=f"Estimated Slum Population Over Time – {selected_country}"
)

fig3.update_layout(template="plotly_white", hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

# Classification

if urban_growth_total > 0 and slum_change_total < 0:
    category = "Improving urbanisation"
    st.success(f"{selected_country} → Improving urbanisation")
elif urban_growth_total > 0 and slum_change_total > 0:
    category = "Growth with pressure"
    st.warning(f"{selected_country} → Growth with pressure")
else:
    category = "Weak development pattern"
    st.error(f"{selected_country} → Weak development pattern")

# Key Insight 

st.markdown("### Key Insight")

st.success(
    f"""
**{selected_country} is classified as: {category}**

Between **{int(first['year'])} and {int(latest['year'])}**:
- Slum share changed from **{first['slum_pct']:.1f}% → {latest['slum_pct']:.1f}%**
- Urban population increased from **{first['urban_pop']:,.0f} → {latest['urban_pop']:,.0f}**
- Estimated slum population changed by **{slum_population_change_total:,.0f} people**

This indicates that urban growth in **{selected_country}** is **{"not translating into improved housing conditions" if slum_change_total > 0 else "being managed relatively effectively"}**.
"""
)

# Rankings

summary = df[[
    "country",
    "urban_growth_total",
    "slum_change_total"
]].drop_duplicates()

rank_df = summary.copy()
rank_df["rank_growth"] = rank_df["urban_growth_total"].rank(ascending=False)
rank_df["rank_slum"] = rank_df["slum_change_total"].rank()

country_rank = rank_df[rank_df["country"] == selected_country]

st.markdown("### How this country compares globally")

st.info(
    f"""
- **Urban growth rank:** {int(country_rank['rank_growth'].values[0])} / {len(rank_df)}
- **Slum improvement rank:** {int(country_rank['rank_slum'].values[0])} / {len(rank_df)}

Lower slum rank = better improvement performance.
"""
)

# Data Table

with st.expander("View country data table"):
    st.dataframe(
        country_df[["year", "slum_pct", "urban_pop", "slum_population"]].style.format({
            "slum_pct": "{:.1f}%",
            "urban_pop": "{:,.0f}",
            "slum_population": "{:,.0f}"
        }),
        use_container_width=True
    )