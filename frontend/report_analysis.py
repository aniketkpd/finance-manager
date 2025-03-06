import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

# ------------------ Data Fetching Functions ------------------
def get_income_data(uid):
    with sqlite3.connect("finance.db") as conn:
        query = """
        SELECT t.date, t.amount, c.name AS category
        FROM transactions t
        JOIN categories c ON t.cid = c.cid
        WHERE t.type = 'Income' AND t.uid = ?;
        """
        df = pd.read_sql_query(query, conn, params=(uid,))
    # Convert date to datetime and normalize (set time to 00:00:00)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    return df

def get_expense_data(uid):
    with sqlite3.connect("finance.db") as conn:
        query = """
        SELECT t.date, t.amount, c.name AS category
        FROM transactions t
        JOIN categories c ON t.cid = c.cid
        WHERE t.type = 'Expense' AND t.uid = ?;
        """
        df = pd.read_sql_query(query, conn, params=(uid,))
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    return df

def get_financial_data(uid):
    with sqlite3.connect("finance.db") as conn:
        query = """
        SELECT t.date, t.amount, t.type, c.name AS category
        FROM transactions t
        JOIN categories c ON t.cid = c.cid
        WHERE t.uid = ?;
        """
        df = pd.read_sql_query(query, conn, params=(uid,))
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    return df

# ------------------ Report Page Functions ------------------
def income_report_page(uid):
    st.title("📈 Income Report")
    
    df = get_income_data(uid)
    if df.empty:
        st.warning("No income records found.")
        return

    # Define reference dates (normalized to midnight)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Calculate totals
    total_income = df['amount'].sum()
    weekly_income = df[df['date'] >= start_of_week]['amount'].sum()
    monthly_income = df[df['date'] >= start_of_month]['amount'].sum()
    yearly_income = df[df['date'] >= start_of_year]['amount'].sum()
    
    st.metric(label="💰 Total Income", value=f"₹{total_income:,.2f}")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="📆 Income This Week", value=f"₹{weekly_income:,.2f}")
    col2.metric(label="📅 Income This Month", value=f"₹{monthly_income:,.2f}")
    col3.metric(label="📆 Income This Year", value=f"₹{yearly_income:,.2f}")

    # Pie Chart for Income Distribution by Category
    category_chart = px.pie(df, values='amount', names='category', title="Income Distribution by Category")
    st.plotly_chart(category_chart, use_container_width=True)

    # Line Chart for Monthly Income Trends
    df['month'] = df['date'].dt.to_period('M').astype(str)
    monthly_trend = df.groupby('month')['amount'].sum().reset_index()
    line_chart = px.line(monthly_trend, x='month', y='amount', title="Monthly Income Trends", markers=True)
    st.plotly_chart(line_chart, use_container_width=True)

    # Bar Chart for Yearly Income Comparison
    df['year'] = df['date'].dt.year
    yearly_trend = df.groupby('year')['amount'].sum().reset_index()
    bar_chart = px.bar(yearly_trend, x='year', y='amount', title="Yearly Income Comparison", text_auto=True)
    st.plotly_chart(bar_chart, use_container_width=True)

    # Download Income Report as CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Income Report (CSV)", data=csv_data, file_name="income_report.csv", mime="text/csv")

def expense_report_page(uid):
    st.title("📉 Expense Report")
    
    df = get_expense_data(uid)
    if df.empty:
        st.warning("No expense records found.")
        return

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    
    total_expense = df['amount'].sum()
    weekly_expense = df[df['date'] >= start_of_week]['amount'].sum()
    monthly_expense = df[df['date'] >= start_of_month]['amount'].sum()
    yearly_expense = df[df['date'] >= start_of_year]['amount'].sum()
    
    st.metric(label="💸 Total Expense", value=f"₹{total_expense:,.2f}")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="📆 Expense This Week", value=f"₹{weekly_expense:,.2f}")
    col2.metric(label="📅 Expense This Month", value=f"₹{monthly_expense:,.2f}")
    col3.metric(label="📆 Expense This Year", value=f"₹{yearly_expense:,.2f}")

    # Pie Chart for Expense Distribution by Category
    category_chart = px.pie(df, values='amount', names='category', title="Expense Distribution by Category")
    st.plotly_chart(category_chart, use_container_width=True)

    # Line Chart for Monthly Expense Trends
    df['month'] = df['date'].dt.to_period('M').astype(str)
    monthly_trend = df.groupby('month')['amount'].sum().reset_index()
    line_chart = px.line(monthly_trend, x='month', y='amount', title="Monthly Expense Trends", markers=True)
    st.plotly_chart(line_chart, use_container_width=True)

    # Bar Chart for Yearly Expense Comparison
    df['year'] = df['date'].dt.year
    yearly_trend = df.groupby('year')['amount'].sum().reset_index()
    bar_chart = px.bar(yearly_trend, x='year', y='amount', title="Yearly Expense Comparison", text_auto=True)
    st.plotly_chart(bar_chart, use_container_width=True)

    # Download Expense Report as CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Expense Report (CSV)", data=csv_data, file_name="expense_report.csv", mime="text/csv")

def savings_trends_page(uid):
    st.title("💰 Savings Trends")
    
    df = get_financial_data(uid)
    if df.empty:
        st.warning("No financial records found.")
        return

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Calculate income, expense, and savings
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expense = df[df['type'] == 'Expense']['amount'].sum()
    total_savings = total_income - total_expense

    weekly_income = df[(df['date'] >= start_of_week) & (df['type'] == 'Income')]['amount'].sum()
    weekly_expense = df[(df['date'] >= start_of_week) & (df['type'] == 'Expense')]['amount'].sum()
    weekly_savings = weekly_income - weekly_expense

    monthly_income = df[(df['date'] >= start_of_month) & (df['type'] == 'Income')]['amount'].sum()
    monthly_expense = df[(df['date'] >= start_of_month) & (df['type'] == 'Expense')]['amount'].sum()
    monthly_savings = monthly_income - monthly_expense

    yearly_income = df[(df['date'] >= start_of_year) & (df['type'] == 'Income')]['amount'].sum()
    yearly_expense = df[(df['date'] >= start_of_year) & (df['type'] == 'Expense')]['amount'].sum()
    yearly_savings = yearly_income - yearly_expense

    st.metric(label="💰 Total Savings", value=f"₹{total_savings:,.2f}")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="📆 Savings This Week", value=f"₹{weekly_savings:,.2f}")
    col2.metric(label="📅 Savings This Month", value=f"₹{monthly_savings:,.2f}")
    col3.metric(label="📆 Savings This Year", value=f"₹{yearly_savings:,.2f}")

    # Prepare data for monthly savings trends
    df['month'] = df['date'].dt.to_period('M').astype(str)
    monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
    monthly_data['savings'] = monthly_data.get('Income', 0) - monthly_data.get('Expense', 0)
    monthly_savings_trend = monthly_data.reset_index()

    # Line Chart for Monthly Savings Trends
    line_chart = px.line(monthly_savings_trend, x='month', y='savings', title="Monthly Savings Trends", markers=True)
    st.plotly_chart(line_chart, use_container_width=True)

    # Prepare data for yearly savings comparison
    df['year'] = df['date'].dt.year
    yearly_data = df.groupby(['year', 'type'])['amount'].sum().unstack().fillna(0)
    yearly_data['savings'] = yearly_data.get('Income', 0) - yearly_data.get('Expense', 0)
    yearly_savings_trend = yearly_data.reset_index()

    # Bar Chart for Yearly Savings Comparison
    bar_chart = px.bar(yearly_savings_trend, x='year', y='savings', title="Yearly Savings Comparison", text_auto=True)
    st.plotly_chart(bar_chart, use_container_width=True)

    # Download Savings Report as CSV
    csv_data = monthly_savings_trend.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Savings Report (CSV)", data=csv_data, file_name="savings_report.csv", mime="text/csv")

# ------------------ Main Navigation ------------------
def report_analysis_page(uid):
    tab1, tab2, tab3 = st.tabs(["Income Report", "Expense Report", "Savings Trends"])
    with tab1:
        income_report_page(uid)
    with tab2:
        expense_report_page(uid)
    with tab3:
        savings_trends_page(uid)

