import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="VC Dashboard", layout="wide")

df = pd.read_csv("investments_VC.csv", encoding="latin1")
df.columns = df.columns.str.strip()

df["funding_total_usd"] = pd.to_numeric(df["funding_total_usd"], errors="coerce")

st.title("🌍 Global Venture Capital Dashboard")

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["country_code"].dropna().unique().tolist())
)

if country != "All":
    df = df[df["country_code"] == country]

col1, col2, col3 = st.columns(3)

col1.metric("Startups", df["name"].nunique())
col2.metric("Countries", df["country_code"].nunique())
col3.metric("Funding", f"${df['funding_total_usd'].sum():,.0f}")

st.subheader("Top Industries")

industry = (
    df.groupby("market")["funding_total_usd"]
      .sum()
      .nlargest(10)
      .reset_index()
)

fig = px.bar(
    industry,
    x="market",
    y="funding_total_usd",
    color="funding_total_usd"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top Countries")

country_df = (
    df.groupby("country_code")["funding_total_usd"]
      .sum()
      .nlargest(10)
      .reset_index()
)

fig2 = px.bar(
    country_df,
    x="country_code",
    y="funding_total_usd",
    color="funding_total_usd"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Funding Map")

fig3 = px.choropleth(
    country_df,
    locations="country_code",
    locationmode="ISO-3",
    color="funding_total_usd"
)

st.plotly_chart(fig3, use_container_width=True)
