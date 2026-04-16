import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random


# Page Configuration

st.set_page_config(page_title="Expense Insights", layout="wide")
st.title("💰 Personal Expense Insights Dashboard")


# Load or Generate Data

@st.cache_data
def load_data():
    """Load or generate sample expense data."""
    # Generate sample data for the last 90 days
    categories = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Health"]
    dates = [datetime.now() - timedelta(days=i) for i in range(90)]
    
    data = []
    for date in dates:
        # Generate 1-3 expenses per day
        for _ in range(random.randint(1, 3)):
            category = random.choice(categories)
            # Realistic spending amounts per category
            amount_ranges = {
                "Food": (8, 35),
                "Transport": (5, 25),
                "Entertainment": (10, 50),
                "Utilities": (20, 80),
                "Shopping": (15, 100),
                "Health": (10, 60),
            }
            amount = random.uniform(*amount_ranges[category])
            data.append({
                "Date": date.date(),
                "Category": category,
                "Amount": round(amount, 2),
            })
    
    return pd.DataFrame(data)

df = load_data()


# Sidebar Filters

st.sidebar.header("🎛️ Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select date range:",
    value=(df["Date"].min(), df["Date"].max()),
    min_value=df["Date"].min(),
    max_value=df["Date"].max(),
)

# Category filter
all_categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Select categories:",
    options=all_categories,
    default=all_categories,
)

# Apply filters
filtered_df = df[
    (df["Date"] >= date_range[0]) &
    (df["Date"] <= date_range[1]) &
    (df["Category"].isin(selected_categories))
]


# Key Metrics (Top Section)

st.subheader("📊 Summary")
col1, col2, col3 = st.columns(3)

total_spending = filtered_df["Amount"].sum()
num_transactions = len(filtered_df)
avg_transaction = filtered_df["Amount"].mean() if num_transactions > 0 else 0

col1.metric("Total Spending", f"${total_spending:.2f}")
col2.metric("Transactions", f"{num_transactions}")
col3.metric("Average per Transaction", f"${avg_transaction:.2f}")


# Charts Section

col_chart1, col_chart2 = st.columns(2)

# Spending by Category (Bar Chart)
with col_chart1:
    st.subheader("Spending by Category")
    spending_by_cat = filtered_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    
    if not spending_by_cat.empty:
        fig1 = px.bar(
            spending_by_cat.reset_index(),
            x="Category",
            y="Amount",
            color="Amount",
            color_continuous_scale="Blues",
            labels={"Amount": "Total Spending ($)"},
        )
        fig1.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No data for selected filters.")

# Spending over Time (Line Chart)
with col_chart2:
    st.subheader("Daily Spending Trend")
    daily_spending = filtered_df.groupby("Date")["Amount"].sum().reset_index()
    
    if not daily_spending.empty:
        fig2 = px.line(
            daily_spending,
            x="Date",
            y="Amount",
            markers=True,
            labels={"Amount": "Daily Spending ($)"},
        )
        fig2.update_layout(height=400, hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data for selected filters.")


# Insights Section

st.subheader("💡 Quick Insights")

if not filtered_df.empty:
    # Insight 1: Top category
    top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()
    top_amount = filtered_df.groupby("Category")["Amount"].sum().max()
    
    st.info(
        f"🏆 **Your biggest spending category is {top_category}** "
        f"(${top_amount:.2f}) during this period."
    )
    
    # Insight 2: Highest single transaction
    highest_transaction = filtered_df.loc[filtered_df["Amount"].idxmax()]
    st.info(
        f"📌 **Your highest single expense**: ${highest_transaction['Amount']:.2f} "
        f"on {highest_transaction['Category']} ({highest_transaction['Date']})"
    )
else:
    st.warning("No data to display. Adjust your filters.")


# Data Table (Optional, collapsible)

with st.expander("📋 View Raw Data"):
    st.dataframe(
        filtered_df.sort_values("Date", ascending=False),
        use_container_width=True,
        height=300,
    )

st.markdown("---")
st.caption("✨ Built with Streamlit | Data refreshes on filter change")