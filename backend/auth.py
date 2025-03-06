import sqlite3
import hashlib
import streamlit as st


def get_user_id_from_users_table(email):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    query = '''
                SELECT uid
                FROM users
                WHERE email = ?
            '''
    
    
    try:
        c.execute(query

            , (email,))
        uid_data = c.fetchone()
        

        conn.close()
        return uid_data[0]
    except:
        return None

# take normal password and return hashed password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



# returns true if user successfully register , if user is already registered return false
def register_user(email, password):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    query = '''
        SELECT uid 
        FROM users
        WHERE email = ?
        '''
    
    # check if user exist
    c.execute(
        query
        ,
        (email,)
    )
    
    existing_data = c.fetchone()
    
    if existing_data:
        conn.close()
        return False
    
    else:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hash_password(password)))
        conn.commit()
        conn.close()
        return True




# Authenticate a user
# return true if user exist and password is correct
def authenticate_user(email, password):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    
    conn.close()
    
    # if user exist and password matches
    if user and user[0] == hash_password(password):
        return True
    return False







# =============== Login Page ===================

# Login page
def login():
    st.subheader("🔑 Login to Your Account")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        if not email or not password:  # Prevent empty inputs
            st.error("Please enter both email and password.")
            return None

        uid = get_user_id_from_users_table(email)
        if uid and authenticate_user(email, password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.uid = uid
            st.rerun()
        else:
            st.error("Invalid Credentials. Try Again!")


# register page
def register():
    st.subheader("📝 Register New Account")
    email = st.text_input("Choose a Email", placeholder="abc@example.com")
    password = st.text_input("Create a Password", type="password",placeholder="Enter password")
    if st.button("Register"):
        if not email or not password:  # Prevent empty inputs
            st.error("Please enter both email and password.")
            return None
        
        if register_user(email, password):
            st.success("Registration Successful! Please login.")
        else:
            st.error("Username already exists. Try another.")