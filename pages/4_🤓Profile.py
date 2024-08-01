"""
User profile
"""

import streamlit as st

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

# Check if the user is authenticated
if not authentication.is_authenticated():
    st.warning("Please log in from the home page to access this page.")
    st.stop()  # Stop further execution if not authenticated

user_data = authentication.get_user_info()

# Display user profile information
st.title("User Profile", anchor=False)
st.markdown(f"**Name:** {user_data['name']}")
st.markdown(f"**Email:** {user_data['email']}")

# Add additional profile information as needed
st.subheader("Additional Information", anchor=False)
st.write("You can add more user-specific details here.")

if st.button("Logout"):
    authentication.reset()
    st.success("You have logged out.")
    st.rerun()
