import google.generativeai as genai
import sqlite3
import pandas as pd
import streamlit as st
import time

def ai(uid):
    API_KEY = "AIzaSyDd5sBg1YPdcPpN_Ufx4Rkl0d6bgv1Da4k"

    # Initialize the Gemini API
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    # Connect to SQLite database
    conn = sqlite3.connect("finance.db")

    # Load data into Pandas DataFrames
    transactions = pd.read_sql("SELECT * FROM transactions WHERE uid = ?", conn, params=(uid,))
    budget = pd.read_sql("SELECT * FROM budget WHERE uid = ?", conn, params=(uid,))  # Filtered for user
    categories = pd.read_sql("SELECT * FROM categories", conn)  # Keeping all categories (base + user)

    conn.close()

    # **Check if any required table is empty**
    if transactions.empty and budget.empty:
        return False  # Data is missing, trigger the "else" block

    # Convert data to JSON format
    transactions_json = transactions.to_json()
    budget_json = budget.to_json()
    categories_json = categories.to_json()

    # Create a prompt for AI analysis
    insights_prompt = f"""
    Here is the user's financial data:
    - Transactions: {transactions_json}
    - Budget: {budget_json}
    - Categories: {categories_json}

    Analyze this data and provide insights on:
    1. Spending trends
    2. Budget utilization
    3. Potential savings
    4. Any concerning financial patterns
    """

    # Send request to Gemini
    response = model.generate_content(insights_prompt)

    # Print AI-generated insights
    st.divider()
    st.write(response.text)

    return True  # Indicates successful AI execution





