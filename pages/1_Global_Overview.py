import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Global Overview")
df = pd.read_csv("data_processed/final_dataset.csv")


#Removed impossible values 
df = df.copy()

df = df[
    (df["slum_pct"] >= 0) &
    (df["slum_pct"] <= 100)]

df = df[df["urban_pop"] > 0]
df = df[df["slum_population"] >= 0]

#Removed years with weak reporting coverage to avoid distorted global averages. This is important for the global overview page, which shows global trends and comparisons. I set a threshold of 70% of the maximum number of countries reporting in any year, but this can be adjusted as needed. The goal is to ensure that the global trends are based on a representative sample of countries, rather than being skewed by years with very few reports.

coverage = (
    df.groupby("year")["country"]
    .nunique()
    .reset_index(name="countries_reporting"))

max_coverage = coverage["countries_reporting"].max()

# keep years with at least 70% of max coverage
min_required = max_coverage * 0.70

valid_years = coverage.loc[
    coverage["countries_reporting"] >= min_required,
    "year"]

df_clean = df[
    df["year"].isin(valid_years)
].copy()


global_trend = (
    df_clean.groupby("year")
    .agg(
        avg_slum_pct=("slum_pct","mean"),
        total_slum_population=("slum_population","sum"),
        countries_reporting=("country","nunique")
    )
    .reset_index())

latest_year = int(global_trend["year"].max())

latest = global_trend[
    global_trend["year"] == latest_year
].iloc[0]

first = global_trend.iloc[0]

change_pp = latest["avg_slum_pct"] - first["avg_slum_pct"]


st.markdown("""
## Global Reality Check

This page compares the **average share of urban residents living in slum conditions**
with the **total estimated number of people living in slums**.

The objective is to show an important development paradox:

**slum rates may fall, while the number of people living in slums can still rise due to rapid urban growth.** """)


#KPI CARDS

c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.metric(
        "Latest year",
        latest_year )

with c2:
    st.metric(
        "Average slum share",
        f"{latest['avg_slum_pct']:.1f}%")

with c3:
    st.metric(
        "People living in slums",
        f"{latest['total_slum_population']:,.0f}")

with c4:
    st.metric(
        "Countries reported",
        int(latest["countries_reporting"]))

with c5:
    st.metric(
        "Change in slum share",
        f"{change_pp:.1f} pp" )

st.markdown("---")


#2 TREND CHARTS

col1,col2 = st.columns(2)

with col1:

    fig1 = px.line(
        global_trend,
        x="year",
        y="avg_slum_pct",
        markers=True,
        title="Average Slum Share Over Time")

    fig1.update_layout(
        template="plotly_white",
        xaxis_title="Year",
        yaxis_title="Average Slum Share (%)")

    fig1.update_xaxes(
        tickmode="linear",
        dtick=2)

    st.plotly_chart(
        fig1,
        use_container_width=True)


with col2:

    fig2 = px.line(
        global_trend,
        x="year",
        y="total_slum_population",
        markers=True,
        title="Total Estimated Slum Population Over Time"  )

    fig2.update_layout(
        template="plotly_white",
        xaxis_title="Year",
        yaxis_title="Estimated Slum Population" )

    fig2.update_xaxes(
        tickmode="linear",
        dtick=2 )

    st.plotly_chart(
        fig2,
        use_container_width=True )



#WORLD MAP
# Final-year snapshot (2022) showing latest global pattern

st.markdown("### Global Slum Conditions in 2022")

# Use latest available year automatically
latest_year = int(df["year"].max())

map_df = df[
    df["year"] == latest_year
].copy()

fig_map = px.choropleth(
    map_df,
    locations="country_code",
    color="slum_pct",
    hover_name="country",
    hover_data={
        "slum_pct":":.1f",
        "slum_population":":,.0f",
        "urban_pop":":,.0f",
        "country_code":False
    },
    color_continuous_scale="Reds",
    range_color=[0,100],
    title=f"Slum Share by Country ({latest_year})",
    labels={
        "slum_pct":"Slum Share (%)",
        "slum_population":"Estimated Slum Population",
        "urban_pop":"Urban Population"
    })

fig_map.update_layout(
    template="plotly_white",

    margin=dict(
        l=0,
        r=0,
        t=50,
        b=0 ),

    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="lightgrey",
        showland=True,
        landcolor="whitesmoke",
        showocean=True,
        oceancolor="aliceblue"),

    coloraxis_colorbar=dict(
        title="Slum Share (%)",
        thickness=15,
        len=0.60 ),

    height=550)

st.plotly_chart(
    fig_map,
    use_container_width=True)




#KEY INSIGHT


st.success(
f"""
**Key takeaway:** From {int(first['year'])} to {latest_year},
the average slum share changed from **{first['avg_slum_pct']:.1f}%**
to **{latest['avg_slum_pct']:.1f}%**.

However, the estimated number of people living in slums changed from
**{first['total_slum_population']:,.0f}**
to
**{latest['total_slum_population']:,.0f}**.

This shows why both **percentage indicators** and **absolute population estimates**
are needed to understand urban housing pressure.
"""
)