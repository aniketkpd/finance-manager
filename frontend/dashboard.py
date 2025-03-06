import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta

# ================ Backend =======================

def get_summary(uid):
    
    df = get_transactions(uid)
    
    # Checking if table is empty
    if df.empty:
        return {"total_income": 0, "total_expense": 0, "balance": 0}

    else:
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expense = df[df['type'] == 'Expense']['amount'].sum()
        balance = total_income - total_expense

        return {"total_income": total_income, "total_expense": total_expense, "balance": balance}

def get_transactions_with_category(uid):
    # Connect to the database
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    query = """
    SELECT transactions.*, categories.name AS category_name
    FROM transactions
    JOIN categories ON transactions.cid = categories.cid
    WHERE transactions.uid = ?
    ORDER BY created_at DESC
    LIMIT 5;
    """

    df = pd.read_sql(query, conn, params=(uid,))
    conn.close()
    
    
    selected_df = df[['tid', 'date', 'type', 'amount', 'description', 'payment_method', 'created_at', 'category_name']]

    return selected_df

def get_transactions(uid):
    with sqlite3.connect("finance.db") as conn:
        df = pd.read_sql("SELECT * FROM transactions WHERE uid = ?", conn, params=(uid,))
    return df

def filter_transactions(df, time_range):
    """Filter transactions based on the selected time range."""
    today = datetime.today()

    if time_range == "last_week":
        start_date = today - timedelta(days=7)
    elif time_range == "last_month":
        start_date = today - timedelta(days=30)
    elif time_range == "last_year":
        start_date = today - timedelta(days=365)
    else:
        return df  # No filter applied

    df["date"] = pd.to_datetime(df["date"])  # Ensure date is in datetime format
    return df[df["date"] >= start_date]  # Filter the dataframe







# ===================== Frontend ====================
def visualize_transactions(uid):
    df = get_transactions(uid)

    if df.empty:
        st.warning("No transactions found for this user.")
        return

    # **💡 Segmented Control for Time Range**
    page_map = {
        "all_time": "📅 All Time",
        "last_week": "🗓️ Last Week",
        "last_month": "📆 Last Month",
        "last_year": "📅 Last Year",
    }

    # Ensure a default selection is set
    time_range = st.segmented_control(
        "Select Time Range",
        options=list(page_map.keys()),
        format_func=lambda option: page_map[option]
    ) or "all_time"  # Default to "All Time" if None



    # **Filter the transactions**
    df = filter_transactions(df, time_range)

    if df.empty:
        st.warning(f"No transactions found for {page_map[time_range]}.")
        return
    
    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    st.subheader(f"Filter by ({page_map[time_range]})")
    
    st.markdown('###')

    # 1️⃣ Transactions Over Time (Line Chart)
    st.subheader("📈 Transactions Over Time")
    fig = px.line(df, x="date", y="amount", title="Total Transactions Over Time", markers=True)
    fig.update_layout(xaxis_title="Date", yaxis_title="Total Amount")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('###')

    col1, col2 = st.columns(2)
    
    with col1:
        # 2️⃣ Payment Method Share (Pie Chart)
        st.subheader("💳 Payment Method Share")
        fig = px.pie(df, names="payment_method", title="Proportion of Transactions by Payment Method")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 3️⃣ Income vs Expense Breakdown (Pie Chart)
        st.subheader("💰 Income vs Expense Breakdown")
        fig = px.pie(df, names="type", title="Transaction Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown('###')

    # 4️⃣ Payment Method Usage (Bar Chart)
    st.subheader("💳 Payment Method Usage (Total Amount)")
    fig = px.bar(df, x="payment_method", y="amount", title="Total Amount by Payment Method", color="payment_method")
    fig.update_layout(xaxis_title="Payment Method", yaxis_title="Total Amount")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('###')

    # 5️⃣ Monthly Income vs Expense (Bar Chart)
    st.subheader("📅 Monthly Income vs Expense")
    df["month"] = df["date"].dt.strftime("%Y-%m")  # Extract year-month
    monthly_summary = df.groupby(["month", "type"])["amount"].sum().reset_index()
    fig = px.bar(monthly_summary, x="month", y="amount", color="type", barmode="group", title="Monthly Income vs Expense")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('###')

    # 6️⃣ Top Spending Categories (Bar Chart)
    if "description" in df.columns:
        st.subheader("🛒 Top Spending Categories")
        top_categories = df.groupby("description")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        fig = px.bar(top_categories.head(10), x="description", y="amount", title="Top 10 Spending Categories", color="amount")
        fig.update_layout(xaxis_title="Category", yaxis_title="Total Spent")
        st.plotly_chart(fig, use_container_width=True)

def dashboard(uid):
    # Part1 - Financial Summary
    with st.container(border=True):
        st.subheader("🏠 Finance Dashboard")
        col1, col2, col3 = st.columns(3)

        summary = get_summary(uid)
        df = get_transactions(uid)

        if not df.empty:      
            last_transaction = df.iloc[-1]
            last_amount = last_transaction["amount"]
            last_type = last_transaction["type"]

            delta_income = None
            delta_expense = None
            delta_balance = None

            if last_type == "Income":
                delta_income = f"+₹{last_amount:.2f}"
                delta_balance = f"+₹{last_amount:.2f}"
            elif last_type == "Expense":
                delta_expense = f"+₹{last_amount:.2f}"
                delta_balance = f"-₹{last_amount:.2f}"

        else:
            delta_income = delta_expense = delta_balance = None

        col1.metric("Total Income", f"₹{summary['total_income']:.2f}", delta=delta_income)
        col2.metric("Total Expense", f"₹{summary['total_expense']:.2f}", delta=delta_expense)
        col3.metric("Current Balance", f"₹{summary['balance']:.2f}", delta=delta_balance)

    st.markdown("---")

    # Part 2 - Recent Transactions
    st.subheader("📝 Recent Transactions")
    df = get_transactions_with_category(uid)

    if df.empty:
        st.info("No recent transactions found.")
    else:
        df.index = ["->"] * len(df)
        st.table(df)

    st.divider()

        # ==== Visualizations ====
    visualize_transactions(uid)
