import streamlit as st
import os
from datetime import date
import sqlite3



# ============================= Backend ===================================
def get_details_from_profiles_table(uid):
    # Connecting to database
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # Fetch profile details from profiles table
    c.execute("""
        SELECT name, phone, about, dob, profile_photo 
        FROM profiles WHERE uid = ? 
        """, (uid,))  # ✅ Corrected

    profile_data = c.fetchone()

    # Fetch email from users table
    c.execute("SELECT email FROM users WHERE uid = ?", (uid,))  # ✅ Corrected
    email_data = c.fetchone()

    if email_data:
        email = email_data[0]
    else:
        email = "email not available"

    conn.close()

    # If user profile exists
    if profile_data:
        profile_photo = profile_data[4] if profile_data[4] else "assets/profile_photo/default.jpg"

        return {
            "name": profile_data[0],
            "phone": profile_data[1],
            "about": profile_data[2],
            "dob": profile_data[3],
            "profile_photo": profile_photo,
            "email": email
        }
        

    # If no record exists, return default values
    return {
        "name": "",
        "phone": "",
        "about": "",
        "dob": "",
        "profile_photo": "assets/profile_photo/default.jpg",
        "email": email
    }


#================= For manipulating data in profiles table =================
def add_profile_in_profile_table(uid, name, phone, about, dob, profile_photo):

    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
 

    # Check if profile exists
    c.execute("SELECT uid FROM profiles WHERE uid = ?", (uid,))
    existing_profile = c.fetchone()

    if existing_profile:
        # Update existing profile
        c.execute(
            """
            UPDATE profiles 
            SET name = ?, phone = ?, about = ?, dob = ?, profile_photo = ? 
            WHERE uid = ?
            """,
            (name, phone, about, dob, profile_photo, uid)
        )
    else:
        # Insert new profile
        c.execute(
            """
            INSERT INTO profiles (uid, name, phone, about, dob, profile_photo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uid, name, phone, about, dob, profile_photo)
        )

    conn.commit()
    conn.close()



# delete record from profile and users
def delete_records_from_profile_and_user(uid):
    conn = sqlite3.connect("finance.db")
    
    c = conn.cursor()
    c.execute("DELETE FROM profiles WHERE uid = ?", (uid,))
    c.execute("DELETE FROM users WHERE uid = ?", (uid,))
    c.execute("DELETE FROM transactions WHERE uid = ?", (uid,))
    
    conn.commit()
    conn.close()
    
    
def email_updater_in_users_table(email, uid):

    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    c.execute(
        """
        UPDATE users 
        SET email = ?
        WHERE uid = ?
        """,
        (email, uid)
    )
    
    
    conn.commit()
    conn.close()





# ============================= Frontend ===================================
def settings_page(uid):
    """Profile settings page that fetches user data from the database."""

    # Fetch user data from the database
    user_data = get_details_from_profiles_table(uid)

    
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # # Function to toggle edit mode
    def enter_edit_mode():
        st.session_state.edit_mode = True

    def exit_edit_mode():
        st.session_state.edit_mode = False
    
    
    
    if not st.session_state.edit_mode:
        # Stop execution if no data is found
        if not user_data:
            st.error("⚠️ User profile not found!")
            return  None 

        # Display profile details
        st.header("⚙️ Profile Settings", divider="gray")

        with st.container(border=True):
            st.subheader("👤 User Profile", divider="gray")

            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(user_data["profile_photo"], width=150, caption="Profile Photo")
            with col2:
                st.markdown(f"### **{user_data['name']}**")
                st.write(f"📧 Email: **{user_data['email']}**")
                st.write(f"📞 Phone: **{user_data['phone']}**")
                st.write(f"📅 DOB: **{user_data['dob']}**")
                st.markdown("**📃 About:**")  
                st.write(f"{user_data['about']}")  


            st.button("✏️ Edit Profile", on_click=enter_edit_mode)  

        st.markdown("---")
        
        
        
        
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        with st.container(border=True):
            st.subheader("⚠️ Danger Zone", divider="red")
            if st.button("🗑️ Delete Your Profile", type='primary'):
                st.session_state.confirm_delete = True
                st.rerun()
            if st.session_state.confirm_delete:    
                st.warning("Are your sure you want to delete your account,All your data will be deleted, and this action can be reverted!")
                
                if st.button("I agree, Delete Everything"):
                    delete_records_from_profile_and_user(uid)
                    st.session_state.logged_in = False
                    st.rerun()

    else:
        with st.container(border=True):
            st.header("✏️ Edit Profile", divider="gray")

            # Profile Edit Section
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(user_data["profile_photo"], width=150, caption="Profile Photo")

                with col2:
                    name = st.text_input("👤 Full Name", value=user_data['name'], placeholder="Enter your name")
                    email = st.text_input("📧 Email",value = user_data['email'], placeholder="Enter your email")
                    phone = st.text_input("📞 Phone",value = user_data['phone'], max_chars=10, placeholder="Enter phone number")
                    dob = st.date_input("📅 Date of Birth", min_value=date(1900, 1, 1), max_value=date(3000, 1, 1))
                    about = st.text_area("About", placeholder="About me")
                    

                # File Uploader (Outside Columns - No Layout Change)
                uploaded_file = st.file_uploader("Change Profile Photo", type=["png", "jpg", "jpeg"])

                # Handle File Upload
                if uploaded_file is not None:
                    
                    file_extension = uploaded_file.name.split('.')[-1]  # Get file extension
                    file_name = f"user{uid}.{file_extension}"  # Rename file
                    file_path = os.path.join("assets", "profile_photo", file_name)
                    
                    
                    # file_path = os.path.join("assets", "profile_photo", uploaded_file.name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    user_data["profile_photo"] = file_path
                    st.image(file_path, width=150, caption="New Profile Photo")  # Preview new image
                else:
                    file_path = user_data["profile_photo"]  # Keep existing photo if no new file uploaded

                # Save & Cancel Buttons
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.button("⬅️ Back", on_click=exit_edit_mode)  

                with col2:
                    if st.button("💾 Save Changes"):
                        add_profile_in_profile_table(uid, name, phone, about, dob, file_path)
                        email_updater_in_users_table(email, uid)
                        st.success("✅ Profile updated successfully!")
                        exit_edit_mode()

                        
                        # Reload updated data
                        user_data = get_details_from_profiles_table(uid)
                        exit_edit_mode()
                        st.rerun()
            


