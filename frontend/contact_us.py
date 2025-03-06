import streamlit as st

def contact_us_page():
    tab1, tab2 = st.tabs(["Customer Support", "FAQs"])

    with tab1:



        # Customer Support Page
        st.title("📞 Customer Support")

        # Contact Details
        st.subheader("Contact Details")
        st.write("For assistance, please reach out to us:")
        st.write("📧 **Email:** aniketsingh7855@gmail.com")
        st.write("📞 **Phone:** +91 930450XXXX")
        st.write("🏢 **Address:** Bhubaneswaar")



        
        
        
        
        
        
        
        
        
        

    with tab2:

        st.title("❓ Frequently Asked Questions (FAQs)")

        st.subheader("General FAQs")
        st.write("**What is this application about?**")
        st.write("This application helps you manage your finances, track income and expenses, and gain insights into your savings and budgeting.")

        st.write("**How does this platform work?**")
        st.write("You can log in, add your transactions, view visualizations, and generate financial reports.")

        st.subheader("Account-Related FAQs")
        st.write("**How do I create an account?**")
        st.write("Click on the 'Sign Up' button, fill out the registration form, and verify your email to create an account.")

        st.write("**How can I reset my password?**")
        st.write("Click on 'Forgot Password' on the login page and follow the instructions to reset your password.")

        st.subheader("Usage-Related FAQs")
        st.write("**How can I add a transaction?**")
        st.write("Navigate to the 'Manage Transactions' section and fill out the transaction details.")

        st.write("**How do I generate reports?**")
        st.write("Go to the 'Reports & Analytics' section, choose the desired report type, and export it as CSV or PDF.")

        st.subheader("Security FAQs")
        st.write("**Is my financial data secure?**")
        st.write("Yes, your data is encrypted and stored securely using industry-standard practices.")

        st.write("**How does the platform handle my information?**")
        st.write("We follow strict privacy policies and do not share your data with third parties.")

        st.subheader("Technical FAQs")
        st.write("**Why is my account not loading?**")
        st.write("Check your internet connection and try refreshing the page. If the issue persists, contact support.")

        st.write("**What should I do if I encounter an error?**")
        st.write("Take a screenshot of the error and contact our support team for assistance.")
