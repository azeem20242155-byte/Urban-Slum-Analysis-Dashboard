import streamlit as st
import pandas as pd

st.title("Global Overview")
st.markdown("""
## Global Reality Check

Even though the **percentage of people living in slums is decreasing**,  
the **total number of people living in slum conditions is still increasing**.

This highlights a key challenge:  
**urban growth is outpacing improvements in living conditions.**
""")

df = pd.read_csv("data_processed/final_dataset.csv")


# Clean obvious invalid values

df = df.copy()
df = df[(df["slum_pct"] >= 0) & (df["slum_pct"] <= 100)]
df = df[df["urban_pop"] > 0]
df = df[df["slum_population"] >= 0]


# Check country coverage by year
# Keep only years with reasonable coverage

coverage = (
    df.groupby("year")["country"]
    .nunique()
    .reset_index(name="countries_reporting")
)

max_coverage = coverage["countries_reporting"].max()
min_required = max_coverage * 0.7

valid_years = coverage.loc[
    coverage["countries_reporting"] >= min_required, "year"
]

df_clean = df[df["year"].isin(valid_years)]


# Global trend table

global_trend = (
    df_clean.groupby("year")
    .agg(
        avg_slum_pct=("slum_pct", "mean"),
        total_slum_population=("slum_population", "sum"),
        countries_reporting=("country", "nunique")
    )
    .reset_index()
)

latest_year = int(global_trend["year"].max())
latest_row = global_trend[global_trend["year"] == latest_year].iloc[0]

# Header text

st.markdown("""
### What this page shows
This page compares the **average share of urban residents living in slum conditions**
with the **total estimated number of people living in slums**.

The aim is to show that percentage improvement does not always mean the human burden is falling.
""")


# KPI cards

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Latest year",
        latest_year
    )

with c2:
    st.metric(
        "Change in slum share (pp)",
        f"{latest_row['avg_slum_pct']:.1f}%"
    )

with c3:
    st.metric(
        "People living in slums",
        f"{latest_row['total_slum_population']:,.0f}"
    )

c4, c5 = st.columns(2)

with c4:
    st.metric(
        "Countries reported",
        int(latest_row["countries_reporting"])
    )

with c5:
    first_row = global_trend.iloc[0]
    change_pp = latest_row["avg_slum_pct"] - first_row["avg_slum_pct"]
    st.metric(
        "Change in average slum %",
        f"{change_pp:.1f} pp"
    )


# Charts

col1, col2 = st.columns(2)

with col1:
    st.subheader("Decline in Slum Share Over Time")
    chart1 = global_trend.set_index("year")[["avg_slum_pct"]]
    st.line_chart(chart1)

with col2:
    st.subheader("Total People Living in Slums Over Time")
    chart2 = global_trend.set_index("year")[["total_slum_population"]]
    st.line_chart(chart2)


# Coverage chart

st.subheader("Country Coverage by Year")
coverage_chart = global_trend.set_index("year")[["countries_reporting"]]
st.bar_chart(coverage_chart)


# Insight box

first_year = int(global_trend["year"].min())
first_avg = global_trend.iloc[0]["avg_slum_pct"]
first_pop = global_trend.iloc[0]["total_slum_population"]

latest_avg = latest_row["avg_slum_pct"]
latest_pop = latest_row["total_slum_population"]

avg_direction = "decreased" if latest_avg < first_avg else "increased"
pop_direction = "decreased" if latest_pop < first_pop else "increased"

st.success(
    f"""
**Key takeaway:** Between {first_year} and {latest_year}, the share of urban residents living in slums fell from 
**{first_avg:.1f}% to {latest_avg:.1f}%**.

However, the **actual number of people living in slum conditions increased** from 
**{first_pop:,.0f} to {latest_pop:,.0f}**.

This means that improvements in percentages do not necessarily translate into improvements in real living conditions, 
as rapid urban population growth continues to put pressure on housing systems.
"""
)

# the aggregated table
with st.expander("View aggregated global data"):
    st.dataframe(global_trend, use_container_width=True)