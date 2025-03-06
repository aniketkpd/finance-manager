import sqlite3
import streamlit as st
import pandas as pd
import time


# ======================== Backend =====================================
def add_transaction(uid, cid, date, type_, amount, description, payment_method):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (uid, cid, date, type, amount, description, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (uid, cid, date, type_, amount, description, payment_method))
    conn.commit()
    conn.close()





def update_transaction(tid, new_date, new_type, new_amount, new_description, new_payment_method, new_cid):
    """Update an existing transaction using tid only (without uid)."""
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # Check if the transaction exists
    df = pd.read_sql("SELECT * FROM transactions WHERE tid = ?", conn, params=(tid,))
    
    if df.empty:
        conn.close()
        return False  # Transaction does not exist

    # Perform the update
    c.execute("""
        UPDATE transactions 
        SET date = ?, type = ?, amount = ?, description = ?, payment_method = ?, cid = ? 
        WHERE tid = ?
    """, (new_date, new_type, new_amount, new_description, new_payment_method, new_cid, tid))
    
    conn.commit()
    conn.close()
    return True  # Successfully updated





def delete_all_transaction(uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()    
    c.execute("DELETE FROM transactions WHERE uid = ?", (uid,))
    conn.commit()
    conn.close()
    
    
    
def delete_transaction(tid, uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    df = pd.read_sql('SELECT * FROM transactions WHERE tid = ? AND uid=?', conn,params=(tid,uid,))
    
    if df.empty:
        conn.close()
        return False
    
    else:
        c.execute("DELETE FROM transactions WHERE tid = ? AND uid = ?", (tid, uid))
    conn.commit()
    conn.close()
    return True
    
    




def get_transactions_with_category(uid):
    # Connect to the database
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # ✅ Corrected SQL query
    query = """
    SELECT transactions.*, categories.name AS category_name
    FROM transactions
    JOIN categories ON transactions.cid = categories.cid
    WHERE transactions.uid = ?;
    """

    df = pd.read_sql(query, conn, params=(uid,))
    conn.close()
    
    
    selected_df = df[['tid', 'date', 'type', 'amount', 'description', 'payment_method', 'created_at', 'category_name']]

    return selected_df





def get_category_names(uid):
    """Fetch category names dynamically for the user based on type (Income/Expense)."""
    
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    query = "SELECT name FROM categories WHERE uid = ? or uid = 0;"
    df = pd.read_sql(query, conn,params=(uid,))  # Fetch data directly into a DataFrame
    
    conn.close()
    
    return df["name"].values.tolist()
 

# ========================================================================================
def get_categories():
    """Fetch all category details (uid, cid, name, type) from the database as a DataFrame."""
    conn = sqlite3.connect("finance.db")
    
    query = "SELECT uid, cid, name, type FROM categories"
    df = pd.read_sql(query, conn) 
    conn.close()
    return df

def get_category_id(uid, category_name, type_):
    df = get_categories()  # Get full category details

    df["uid"] = df["uid"].astype(int)  

    # Filter DataFrame for matching category (user-specific or default category)
    filtered_df = df[((df["uid"] == uid) | (df["uid"] == 0)) & 
                     (df["name"] == category_name) & 
                     (df["type"] == type_)]

    if not filtered_df.empty:
        return int(filtered_df.iloc[0]["cid"])  # Ensure integer output
    return None  # No matching category found




# ======================== Frontend =====================================
def transactions_page(uid):
    tab1, tab2, tab3, tab4 = st.tabs(["View all Transactions", "Add Transaction", "Delete Transaction", "Update Transaction"])


    with tab1:
        st.header("📃 Your Transactions")
        df = get_transactions_with_category(uid)
        
        toggle_state = st.toggle("Change Mode")
        
        if toggle_state:
            st.write("Search Mode")
            df.index = ["->"] * len(df)
            st.dataframe(df,use_container_width=True)
        else:
            st.write("Classic Mode")
            df.index = ["->"] * len(df)
            
            st.table(df)
        
        st.divider()


    with tab2:
        st.header("➕ Add New Transaction")

        # inputs
        type_ = st.radio("Transaction Type", ["Income", "Expense"], key='add_type')
        categories = get_category_names(uid)
        category = st.selectbox("Category:",categories, key='add_category')
        cid = get_category_id(uid, category, type_)
        date = st.date_input("Transaction Date", key='add_date')
        amount = st.number_input("Amount", min_value=0, step=1, key='add_amount')
        description = st.text_area("Description", key='add_description')
        payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "UPI", "Other"], key='add_payment_method')

        if st.button("Add Transaction", key="add_transaction_btn"):
            if cid is None:
                st.error(f"❌ The selected category '{category}' does not match the transaction type '{type_}'. Please choose the correct category.")
            else:
                add_transaction(uid, cid, date, type_, amount, description, payment_method)
                st.success("✅ Transaction Added Successfully!")
                time.sleep(2)
                st.rerun()

        st.divider()




    with tab3:

        # Delete specific record

        st.header("🚮 Delete a Specific Transaction")
        tid = st.number_input("Enter tid number to delete", step=1)

        if st.button("Delete a transaction",key="del_button2"):
            if delete_transaction(tid,uid):
                st.success("Transaction Deleted Successfully!")
                time.sleep(2)  # Small delay to allow the message to be seen
                st.rerun()
            else:
                st.warning("Invalid tid!!!")
        












        # Delete all records
        st.divider()
        st.header("🗑️ Delete All Transaction")        
        
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        
        if st.button("Delete All transactions", key="del_button", type='primary'):
            st.session_state.confirm_delete = True
            st.rerun()
        
            
        if st.session_state.confirm_delete:    
            st.warning("Are your sure , all your transactions will be deleted")
            
            if st.button("Yes, Delete it."):
                delete_all_transaction(uid)
                st.session_state.confirm_delete = False
                st.rerun()
        
        
        st.divider()

    with tab4:
        st.header("📝 Update transactions")

        # inputs
        tid = st.number_input("Enter tid",step=1, placeholder="Enter tid")
        type_ = st.radio("Transaction Type", ["Income", "Expense"], key='update_type')
        categories = get_category_names(uid)
        category = st.selectbox("Category:",categories, key='update_category')
        cid = get_category_id(uid, category, type_)
        date = st.date_input("Transaction Date", key='update_date')
        amount = st.number_input("Amount", min_value=0, step=1, key='update_amount')
        description = st.text_area("Description", key='update_description')
        payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "UPI", "Other"], key='update_payment_method')


        if st.button("Update Transaction", key="update_btn"):
            if cid is None:
                st.error(f"❌ The selected category '{category}' does not match the transaction type '{type_}'. Please choose the correct category.")
            else:
                update_transaction(tid, date, type_, amount, description, payment_method, cid)
                st.success("✅ Transaction Updated Successfully!")
                time.sleep(2)
                st.rerun()


