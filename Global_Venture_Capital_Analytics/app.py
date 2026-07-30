import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Venture Capital Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ----------------------------
# LOAD DATA
# ----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("investments_VC.csv", encoding="latin1")

    df.columns = df.columns.str.strip()

    df["funding_total_usd"] = (
        df["funding_total_usd"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df["funding_total_usd"] = pd.to_numeric(
        df["funding_total_usd"],
        errors="coerce"
    )

    df["first_funding_at"] = pd.to_datetime(
        df["first_funding_at"],
        errors="coerce"
    )

    return df


df = load_data()

# ----------------------------
# TITLE
# ----------------------------

st.title("🌍 Global Venture Capital Dashboard")

st.markdown(
"""
Interactive analysis of startup funding across countries and industries.
"""
)

# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.header("Filters")

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["country_code"].dropna().unique().tolist())
)

industry = st.sidebar.selectbox(
    "Industry",
    ["All"] + sorted(df["market"].dropna().unique().tolist())
)

status = st.sidebar.selectbox(
    "Startup Status",
    ["All"] + sorted(df["status"].dropna().unique().tolist())
)

filtered = df.copy()

if country != "All":
    filtered = filtered[
        filtered["country_code"] == country
    ]

if industry != "All":
    filtered = filtered[
        filtered["market"] == industry
    ]

if status != "All":
    filtered = filtered[
        filtered["status"] == status
    ]

# ----------------------------
# KPI CARDS
# ----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🚀 Startups",
    f"{filtered['name'].nunique():,}"
)

c2.metric(
    "💰 Funding",
    f"${filtered['funding_total_usd'].sum():,.0f}"
)

c3.metric(
    "🌍 Countries",
    filtered["country_code"].nunique()
)

c4.metric(
    "🏭 Industries",
    filtered["market"].nunique()
)

st.divider()

tab1, tab2, tab3 = st.tabs(
[
"📈 Overview",
"🏭 Industry",
"🌍 Geography"
]
)
# =====================================================
# OVERVIEW TAB
# =====================================================

with tab1:

    st.header("📈 Startup Funding Overview")

    # -------------------------------
    # Funding Trend
    # -------------------------------

    trend = (
        filtered
        .dropna(subset=["first_funding_at", "funding_total_usd"])
        .copy()
    )

    if not trend.empty:

        trend["Year"] = trend["first_funding_at"].dt.year

        yearly = (
            trend
            .groupby("Year")["funding_total_usd"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            yearly,
            x="Year",
            y="funding_total_usd",
            markers=True,
            title="Funding Trend Over Time"
        )

        fig.update_layout(
            template="plotly_white",
            height=450,
            xaxis_title="Year",
            yaxis_title="Funding (USD)"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No funding trend available for the selected filters.")

    st.divider()

    # -------------------------------
    # Bubble Chart
    # -------------------------------

    st.subheader("🌍 Top Startup Ecosystems")

    bubble = (
        filtered
        .groupby("country_code")
        .agg(
            Funding=("funding_total_usd", "sum"),
            Startups=("name", "nunique")
        )
        .reset_index()
    )

    bubble = bubble.sort_values(
        "Funding",
        ascending=False
    ).head(20)

    if not bubble.empty:

        fig2 = px.scatter(
            bubble,
            x="Startups",
            y="Funding",
            size="Funding",
            color="Funding",
            hover_name="country_code",
            text="country_code",
            size_max=60,
            title="Top Startup Ecosystems"
        )

        fig2.update_traces(
            textposition="top center"
        )

        fig2.update_layout(
            template="plotly_white",
            height=550
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:
        st.info("No country data available.")

    st.divider()

    # -------------------------------
    # Top Funded Startups
    # -------------------------------

    st.subheader("🏆 Top 10 Most Funded Startups")

    top10 = (
        filtered[
            ["name",
             "country_code",
             "market",
             "funding_total_usd"]
        ]
        .sort_values(
            "funding_total_usd",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top10,
        use_container_width=True
    )

# =====================================================
# INDUSTRY TAB
# =====================================================

with tab2:

    st.header("🏭 Industry Analysis")

    # -----------------------------------
    # Top Industries
    # -----------------------------------

    st.subheader("Top Industries by Funding")

    industry = (
        filtered
        .groupby("market")
        .agg(
            Funding=("funding_total_usd", "sum"),
            Startups=("name", "nunique")
        )
        .reset_index()
        .sort_values("Funding", ascending=False)
        .head(15)
    )

    fig = px.bar(
        industry,
        x="Funding",
        y="market",
        orientation="h",
        color="Funding",
        title="Top 15 Industries Receiving Venture Capital"
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        yaxis_title="Industry",
        xaxis_title="Funding (USD)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -----------------------------------
    # Treemap
    # -----------------------------------

    st.subheader("Industry Funding Distribution")

    tree = (
        filtered
        .groupby("market")["funding_total_usd"]
        .sum()
        .reset_index()
        .sort_values("funding_total_usd", ascending=False)
        .head(20)
    )

    fig2 = px.treemap(
        tree,
        path=["market"],
        values="funding_total_usd",
        color="funding_total_usd",
        title="Funding Share by Industry"
    )

    fig2.update_layout(
        template="plotly_white",
        height=650
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # -----------------------------------
    # Startup Status
    # -----------------------------------

    st.subheader("Funding by Startup Status")

    status_df = (
        filtered
        .groupby("status")["funding_total_usd"]
        .sum()
        .reset_index()
    )

    fig3 = px.pie(
        status_df,
        names="status",
        values="funding_total_usd",
        hole=0.45,
        title="Funding Distribution by Startup Status"
    )

    fig3.update_layout(
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # -----------------------------------
    # Industry Summary
    # -----------------------------------

    st.subheader("Industry Summary")

    summary = (
        filtered
        .groupby("market")
        .agg(
            Total_Startups=("name", "nunique"),
            Total_Funding=("funding_total_usd", "sum"),
            Average_Funding=("funding_total_usd", "mean")
        )
        .sort_values(
            "Total_Funding",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(summary, use_container_width=True)

# =====================================================
# GEOGRAPHY TAB
# =====================================================

with tab3:

    st.header("🌍 Geographic Analysis")

    # ------------------------------------
    # Top Countries
    # ------------------------------------

    st.subheader("Top Countries by Funding")

    country = (
        filtered
        .groupby("country_code")
        .agg(
            Funding=("funding_total_usd","sum"),
            Startups=("name","nunique")
        )
        .reset_index()
        .sort_values("Funding",ascending=False)
        .head(15)
    )

    fig = px.bar(
        country,
        x="country_code",
        y="Funding",
        color="Funding",
        text="Funding",
        title="Top Countries Receiving Venture Capital"
    )

    fig.update_traces(texttemplate="%{text:.2s}")

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis_title="Country",
        yaxis_title="Funding (USD)"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    # ------------------------------------
    # World Map
    # ------------------------------------

    st.subheader("Global Funding Map")

    world = (
        filtered
        .groupby("country_code")["funding_total_usd"]
        .sum()
        .reset_index()
    )

    fig2 = px.choropleth(
        world,
        locations="country_code",
        locationmode="ISO-3",
        color="funding_total_usd",
        hover_name="country_code",
        color_continuous_scale="Viridis",
        title="Worldwide Venture Capital Funding"
    )

    fig2.update_layout(
        template="plotly_white",
        height=650
    )

    st.plotly_chart(fig2,use_container_width=True)

    st.divider()

    # ------------------------------------
    # Heatmap
    # ------------------------------------

    st.subheader("Country vs Industry")

    heat = (
        filtered
        .groupby(["country_code","market"])
        .size()
        .reset_index(name="Count")
    )

    top_country = (
        heat.groupby("country_code")["Count"]
        .sum()
        .nlargest(10)
        .index
    )

    top_market = (
        heat.groupby("market")["Count"]
        .sum()
        .nlargest(10)
        .index
    )

    heat = heat[
        heat["country_code"].isin(top_country)
        &
        heat["market"].isin(top_market)
    ]

    pivot = heat.pivot(
        index="market",
        columns="country_code",
        values="Count"
    ).fillna(0)

    fig3 = px.imshow(
        pivot,
        text_auto=True,
        color_continuous_scale="Blues",
        aspect="auto",
        title="Startup Density by Country & Industry"
    )

    fig3.update_layout(
        height=650,
        template="plotly_white"
    )

    st.plotly_chart(fig3,use_container_width=True)

    st.divider()

    # ------------------------------------
    # Country Summary
    # ------------------------------------

    st.subheader("Country Summary")

    summary = (
        filtered
        .groupby("country_code")
        .agg(
            Total_Startups=("name","nunique"),
            Total_Funding=("funding_total_usd","sum"),
            Average_Funding=("funding_total_usd","mean")
        )
        .sort_values("Total_Funding",ascending=False)
    )

    st.dataframe(summary,use_container_width=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
"""
<div style='text-align:center;'>

### 🌍 Global Venture Capital Dashboard

Built using **Streamlit**, **Pandas**, and **Plotly**

**University of Europe for Applied Sciences**

</div>
""",
unsafe_allow_html=True
)
