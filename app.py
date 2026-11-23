
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="Netflix Engagement Analytics",
    page_icon="🎬",
    layout="wide"
)

# -------------------------------
# LOAD DATA
# -------------------------------

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE = os.path.join(
    BASE_DIR,
    "What_We_Watched_A_Netflix_Engagement_Report_2023Jan-Jun.xlsx"
)

@st.cache_data
def load_data():
    df = pd.read_excel(
        FILE,
        skiprows=5,
        usecols="B:E",
        names=[
            "Title",
            "Available Globally",
            "Release Date",
            "Hours Viewed"
        ]
    )

    df["Release Date"] = pd.to_datetime(
        df["Release Date"], errors="coerce"
    )

    df["Release Year"] = (
        df["Release Date"].dt.year.astype("Int64")
    )

    return df

df = load_data()

# -------------------------------
# DASHBOARD TITLE
# -------------------------------

st.title("🎬 Netflix Engagement Analytics")
st.markdown(
    "### Viewing Performance Report | January – June 2023"
)

st.markdown(
    "Explore viewing performance, title rankings "
    "and global availability."
)

st.divider()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------

st.sidebar.header("Dashboard Filters")

availability = st.sidebar.selectbox(
    "Global Availability",
    ["All", "Yes", "No"]
)

years = sorted(
    df["Release Year"].dropna().unique().tolist()
)

year_options = ["All", "Unknown"] + years

selected_year = st.sidebar.selectbox(
    "Release Year",
    year_options
)

# Apply filters
filtered = df.copy()

if availability != "All":
    filtered = filtered[
        filtered["Available Globally"] == availability
    ]

if selected_year == "Unknown":
    filtered = filtered[
        filtered["Release Year"].isna()
    ]
elif selected_year != "All":
    filtered = filtered[
        filtered["Release Year"] == selected_year
    ]

# -------------------------------
# KPI SECTION
# -------------------------------

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Viewing Hours",
    f"{filtered['Hours Viewed'].sum()/1e9:.2f}B"
)

col2.metric(
    "Total Titles",
    f"{len(filtered):,}"
)

col3.metric(
    "Average Hours Viewed",
    f"{filtered['Hours Viewed'].mean()/1e6:.2f}M"
)

global_count = (
    filtered["Available Globally"] == "Yes"
).sum()

col4.metric(
    "Globally Available Titles",
    f"{global_count:,}"
)

st.divider()

# -------------------------------
# TOP 10 TITLES
# -------------------------------

st.subheader("Top 10 Most Watched Titles")

top10 = (
    filtered.nlargest(10, "Hours Viewed")
    .sort_values("Hours Viewed")
)

fig1 = px.bar(
    top10,
    x="Hours Viewed",
    y="Title",
    orientation="h",
    title="Top 10 Titles by Hours Viewed",
    color="Hours Viewed",
    color_continuous_scale="reds",
    labels={"Hours Viewed": "Viewing Hours"}
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------
# GLOBAL AVAILABILITY
# -------------------------------

st.subheader("Global Availability Analysis")

availability_data = (
    filtered.groupby("Available Globally")["Hours Viewed"]
    .sum()
    .reset_index()
)

fig2 = px.pie(
    availability_data,
    names="Available Globally",
    values="Hours Viewed",
    hole=0.45,
    title="Viewing Hours by Global Availability"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# RELEASE YEAR ANALYSIS
# -------------------------------

st.subheader("Viewing Hours by Release Year")

year_data = (
    filtered.dropna(subset=["Release Year"])
    .groupby("Release Year")["Hours Viewed"]
    .sum()
    .reset_index()
)

year_data["Release Year"] = (
    year_data["Release Year"].astype(str)
)

fig3 = px.bar(
    year_data,
    x="Release Year",
    y="Hours Viewed",
    title="Viewing Hours by Original Release Year",
    color="Hours Viewed",
    color_continuous_scale="reds"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# VIEWING DISTRIBUTION
# -------------------------------

st.subheader("Viewing Hours Distribution")

fig4 = px.histogram(
    filtered,
    x="Hours Viewed",
    nbins=40,
    log_x=True,
    title="Distribution of Viewing Hours (Logarithmic Scale)"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# BUSINESS INSIGHTS
# -------------------------------

st.divider()

st.header("Business Insights")

if not filtered.empty:

    top_title = filtered.loc[
        filtered["Hours Viewed"].idxmax()
    ]

    st.success(
        f"Highest-performing title: {top_title['Title']} "
        f"with {top_title['Hours Viewed']:,} viewing hours."
    )

    global_hours = filtered.loc[
        filtered["Available Globally"] == "Yes",
        "Hours Viewed"
    ].sum()

    total_hours = filtered["Hours Viewed"].sum()

    if total_hours > 0:
        st.write(
            f"Globally available titles contribute "
            f"{global_hours / total_hours:.1%} "
            f"of the viewing hours in the selected data."
        )

    st.write(
        f"The dataset contains "
        f"{filtered['Release Date'].isna().sum():,} "
        f"titles with unknown release dates in the selection."
    )

else:
    st.warning("No records match the selected filters.")

# -------------------------------
# DATA TABLE
# -------------------------------

st.divider()

st.subheader("Netflix Dataset")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Source: Netflix What We Watched Engagement Report, "
    "January–June 2023."
)

