import streamlit as st

st.set_page_config(layout='wide')


# Include SELECT commands
import sqlite3
import pandas as pd
uid = 1

# Fetch all columns from transaction table
def get_transactions():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    # Modified query to exclude the 'receipt' column
    df = pd.read_sql("SELECT * FROM transactions", conn)

    conn.close()
    return df


# Fetch all columns from profiles table
def get_profiles():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    df = pd.read_sql("SELECT * FROM profiles", conn)

    conn.close()
    return df


# Fetch all columns from categories table
def get_categories():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    df = pd.read_sql("SELECT * FROM categories", conn)

    conn.close()
    return df


# Fetch all columns from users table
def get_users():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    df = pd.read_sql("SELECT * FROM users", conn)

    conn.close()
    return df


# Fetch all columns from budget table
def get_budget():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    df = pd.read_sql("SELECT * FROM budget", conn)

    conn.close()
    return df



# Fetch all columns from notifications table
def get_notifications():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    df = pd.read_sql("SELECT * FROM notifications", conn)

    conn.close()
    return df




def db_data():
    st.title("Database tables with all data")


    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["users", "profile","transactions", "categories","budget"])
    
    
    with tab1:
        st.table(get_users())
    
    with tab2:
        st.table(get_profiles())


    with tab3:
        st.table(get_transactions())
        



    with tab4:
        st.table(get_categories())
        
    
    
    with tab5:
        st.table(get_budget())
        
    
db_data()

    