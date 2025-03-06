# Categories Page
import sqlite3
import streamlit as st
import pandas as pd
import time



# ======================== Backend =====================================
def view_categories(uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    query = "SELECT * FROM categories WHERE uid = ? or uid = 0"
    df = pd.read_sql(query,conn,params=(uid,))
    conn.close()
    
    selected_df = df[['cid','name','description','type']]
    
    return selected_df





def create_a_category(uid, name, description, type_):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()

    query = "SELECT * FROM categories WHERE uid = ? and name = ?"
    df = pd.read_sql(query,conn,params=(uid,name))

    if df.empty:
        query = "INSERT INTO categories (uid, name, description, type) VALUES (?, ?, ?, ?)"
        c.execute(query, (uid,name,description,type_))
        conn.commit()
        conn.close()
    
        return True
    else:
        conn.close()
        return False
    
    


def delete_a_category(cid, uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    
    query = "SELECT * FROM categories WHERE cid = ? and uid = ?"
    df = pd.read_sql(query,conn,params=(cid,uid))

    if df.empty:
        conn.close()
        return False
    
    query = "DELETE FROM categories WHERE cid = ? AND uid = ?"
    
    c.execute(query, (cid, uid))
    
    conn.commit()
    conn.close()
    return True    
    
    
def delete_all_user_category(uid):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    query = "SELECT * FROM categories WHERE uid = ?"
    df = pd.read_sql(query,conn,params=(uid,))

    if df.empty:
        conn.close()
        return False
    
    
    query = "DELETE FROM categories WHERE uid = ?"
    
    c.execute(query, (uid,))
    
    conn.commit()
    conn.close()
    return True








def update_category(cid, uid, name, description, type_):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    
    
    query = "SELECT * FROM categories WHERE uid = ? and cid = ?"
    df = pd.read_sql(query,conn,params=(uid,cid,))

    if df.empty:
        conn.close()
        return False
    
    
    
    c.execute("UPDATE categories SET name = ?, description = ?, type = ? WHERE cid = ? AND uid = ?",
              (name, description, type_, cid, uid))
    
    
    
    
    conn.commit()
    conn.close()
    return True
    
# ======================== Frontend =====================================



def categories_page(uid):
    tab1, tab2, tab3, tab4 = st.tabs(["View Categories", "Add Category", "Delete Category", "Update Category"])
    with tab1:
        st.header("📂 View Categories")
        df = view_categories(uid)
        
        toggle_state = st.toggle("Change Mode")
        
        
        if toggle_state:
            st.subheader("Search Mode")
            df.index = ["->"] * len(df)
            st.dataframe(df, use_container_width=True)
        
        else:
            st.subheader("Classic Mode")
            df.index = ["->"] * len(df)
            st.table(df)
        st.divider()
        


    with tab2:
        pass
        st.header("➕ Add Category")


        categories_name = st.text_input("Enter category name")
        category_description = st.text_area("Enter description")
        type_ = st.radio("Category Type", ["Income", "Expense"], key='add_cat_type')
        
        if st.button("Add Category", key="add_btn"):
            if create_a_category(uid, categories_name, category_description, type_):
                st.success(f"Category {categories_name} created successfully.")
                time.sleep(2)
                st.rerun()
            else:
                st.info("Category Already Exist!")


    with tab3:
        # Delete specific record
        st.header("Delete a Category")
        cid = st.number_input("Enter tid number to delete", step=1)

        if st.button("Delete a Category",key="del_button2"):
            
            if cid in [1,2,3,4,5,6]:
                st.warning("Default categories can't be deleted")
            
            elif delete_a_category(cid,uid):
                st.success("Category Deleted Successfully!")
                time.sleep(2)  
                st.rerun()
            else:
                st.warning("Invalid cid!!!")
        
        
        
        
        
        st.divider()
        st.header("Delete All Manually Created Categories")
        
        # if st.button("Delete All Category", key="del_button", type='primary'):
        #     if delete_all_user_category(uid):
        #         st.success("Categories deleted successfully.")
        #         time.sleep(2)
        #         st.rerun()
        #     else:
        #         st.info("You have not created any special category.")
                
                
                
                
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False

        if st.button("Delete All Category", key="del_button", type='primary'):
            st.session_state.confirm_delete = True
            st.rerun()

        if st.session_state.confirm_delete:    
            st.warning("Are you sure? All your special categories will be deleted.")

            col1, col2 = st.columns(2)  # Create two buttons side by side

            with col1:
                if st.button("Yes, Delete it."):
                    if delete_all_user_category(uid):
                        st.success("Categories deleted successfully.")
                        time.sleep(2)
                        st.session_state.confirm_delete = False
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = False
                        st.info("You have not created any special category.")
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete = False
                    st.rerun()

        
        
        
        

    with tab4:
        pass
        st.header("Update a Category")

        cid = st.number_input("Enter cid",step=1, placeholder="Enter cid")
        category_name = st.text_input("Enter category name",key="category_name_input")
        type_ = st.radio("Transaction Type", ["Income", "Expense"], key='update_type')
        description = st.text_area("Description", key='update_description')


        if st.button("Update Category", key="update_btn"):
            if cid is None:
                st.error(f"❌ The selected category '{category_name}' does not exist")
            else:
                update_category(cid, uid, category_name, description, type_)
                st.success("✅ Category Updated Successfully!")
                time.sleep(2)
                st.rerun()



