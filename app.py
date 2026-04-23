import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Urban Slum Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Urban Slum Analysis Dashboard")

st.markdown("""
This dashboard analyses urban housing pressure using slum population data and urban population data.

It is designed to help users explore:
- global slum trends
- the relationship between urbanisation and slum conditions
- country-level patterns
- which countries may be improving or falling behind
""")

# Load dataset just to show a quick summary on the home page
df = pd.read_csv("data_processed/final_dataset.csv")

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries", df["country"].nunique())

with col2:
    st.metric("Years Available", df["year"].nunique())

with col3:
    st.metric("Rows", len(df))

st.info("Use the sidebar to open each analysis page.")