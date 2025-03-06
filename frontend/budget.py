# Categories Page
import sqlite3
import streamlit as st
import pandas as pd
import time



# ======================== Backend =====================================

def get_budgets(uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    query = '''
        SELECT budget.*, categories.name AS category_name
        FROM budget
        JOIN categories ON budget.cid = categories.cid
        WHERE budget.uid = ?
    '''
    df  = pd.read_sql(query,conn, params=(uid,))
    
    conn.close()
    
    selected_df = df[['bid','amount','start_date','end_date','created_at','category_name']]
    
    return selected_df




def create_budget(uid, cid, amount, start_date, end_date):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    query = '''
        SELECT * FROM budget WHERE uid = ? AND cid = ?
    '''
    
    df = pd.read_sql(query, conn, params=(uid,cid))

    if df.empty:
        c.execute("INSERT INTO budget (uid, cid, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                (uid, cid, amount, start_date, end_date))
        conn.commit()
        conn.close()
        return True
    conn.commit()
    conn.close()
    return False



def update_budget(bid, uid, cid, amount, start_date, end_date):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    query = "SELECT * FROM budget WHERE bid = ? AND uid = ? AND cid=?;"
    
    
    df = pd.read_sql(query, conn,params=(bid, uid,cid))
    
    
    if df.empty:
        conn.commit()
        conn.close()
        return False
    
    c.execute("UPDATE budget SET cid = ?, amount = ?, start_date = ?, end_date = ? WHERE bid = ? AND uid = ?",
              (cid, amount, start_date, end_date, bid, uid))
    conn.commit()
    conn.close()
    return True


# not redundant
def get_category_names(uid):
    """Fetch category names dynamically for the user based on type (Income/Expense)."""
    
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    query = "SELECT name FROM categories WHERE (uid = ? or uid = 0) AND type = 'Expense' ;"
    df = pd.read_sql(query, conn,params=(uid,))
    
    conn.close()
    
    return df["name"].values.tolist()










# redundants
def get_categories():
    """Fetch all category details (uid, cid, name, type) from the database as a DataFrame."""
    conn = sqlite3.connect("finance.db")
    
    query = "SELECT uid, cid, name, type FROM categories"
    df = pd.read_sql(query, conn) 

    conn.close()
    
    return df  # Return full category details

def get_category_id(uid, category_name, type_):
    """Fetch category ID (cid) based on user-specific or default category (uid = 0)."""
    df = get_categories()  # Get full category details

    # Ensure correct data types for filtering
    df["uid"] = df["uid"].astype(int)  # Convert UID to int (prevents float issues)

    # Filter DataFrame for matching category (user-specific or default category)
    filtered_df = df[((df["uid"] == uid) | (df["uid"] == 0)) & 
                     (df["name"] == category_name) & 
                     (df["type"] == type_)]

    if not filtered_df.empty:
        return int(filtered_df.iloc[0]["cid"])  # Ensure integer output
    return None  # No matching category found










def delete_a_budget(bid, uid):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    query = "SELECT * FROM budget WHERE bid = ? or uid = ? ;"
    
    
    df = pd.read_sql(query, conn,params=(bid, uid,))
    
    
    if df.empty:
        conn.commit()  
        conn.close()
        return False
    
    c.execute("DELETE FROM budget WHERE bid = ? AND uid = ?", (bid, uid))
    conn.commit()
    conn.close()
    return True




def delete_all_budget(uid):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    query = "SELECT * FROM budget WHERE uid = ? ;"
    
    
    df = pd.read_sql(query, conn,params=(uid,))
    
    
    if df.empty:
        conn.commit()
        conn.close()
        return False
    
    c.execute("DELETE FROM budget WHERE uid = ?", (uid,))
    conn.commit()
    conn.close()
    return True












# ======================== Frontend =====================================



def budget_page(uid):
    tab1, tab2, tab3, tab4 = st.tabs(["View Budgets", "Add a new budget", "Delete budget", "Update a Budget"])
    
    
    
    
    with tab1:
        st.header("📉 View Budget")
        df = get_budgets(uid)
        
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
        st.header("➕ Add Budget")

        # inputs
        amount = st.number_input("Enter amount")
        # we need to show user the available categories so he can select one of them
        categories = get_category_names(uid)
        category = st.selectbox("Category:",categories, key='add_category')
        start_date = st.date_input("Enter start date", key="Start_date")
        end_date = st.date_input("Enter end date", key="End date")
        
        # then we need to get the cid for the chosen category
        type_ = 'Expense'
        cid = get_category_id(uid, category, type_)
        
        if st.button("Add Budget", key="add_btn"):
            if create_budget(uid, cid, amount, start_date, end_date):
                st.success("Budget added Successfully.")
                time.sleep(2)
                st.rerun()
            else:
                st.info("Budget already exist")






    with tab3:

        st.header("🚮 Delete Budget for a Category")
        bid = st.number_input("Enter bid number to delete", step=1)

        if st.button("Delete a transaction",key="del_button2"):
            if delete_a_budget(bid,uid):
                st.success("Budget deleted successfully")
                time.sleep(2)
                st.rerun()
            else:
                st.info("No budget exist for this bid.")



        st.divider()

        st.header("🗑️ Delete Budgets for All Categories")

        # Ensure session state for confirmation exists
        if "confirm_delete_budget" not in st.session_state:
            st.session_state.confirm_delete_budget = False

        # Delete Button - Initial Click
        if st.button("Delete All Budgets", key="del_budget_button", type='primary'):
            st.session_state.confirm_delete_budget = True
            st.rerun()

        # Confirmation Prompt
        if st.session_state.confirm_delete_budget:
            st.warning("Are you sure? This will delete **all budget data** across categories.")

            col1, col2 = st.columns(2)  # Two buttons side by side

            with col1:
                if st.button("Yes, Delete All Budgets"):
                    if delete_all_budget(uid):
                        st.success("Budgets for all categories **DELETED** successfully.")
                        time.sleep(1)
                        st.session_state.confirm_delete_budget = False
                        st.rerun()
                    else:
                        st.info("No budgets exist.")
                        time.sleep(2)
                        st.session_state.confirm_delete_budget = False
                        st.rerun()

            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete_budget = False
                    st.rerun()
            
            
        st.divider()


    with tab4:
        st.header("📝 Update Budget for a Category")

        bid = st.number_input("Enter bid",step=1, placeholder="Enter bid", key="update_bid")
        amount = st.number_input("Enter amount", key="update_amout")
        
        # we need to show user the available categories so he can select one of them
        categories = get_category_names(uid)
        category = st.selectbox("Category:",categories, key='update_category')
        start_date = st.date_input("Enter start date", key="new_Start_date")
        end_date = st.date_input("Enter end date", key="new_End date")
        
        # then we need to get the cid for the chosen category
        type_ = 'Expense'
        cid = get_category_id(uid, category, type_)
        
        if st.button("Add Budget", key="update_btn"):
            if update_budget(bid, uid, cid, amount, start_date, end_date):
                st.success("Budget Updated Successfully.")
                time.sleep(2)
                st.rerun()
            else:
                st.info("Invalid bid or Budget already exist for this category")
        
        




