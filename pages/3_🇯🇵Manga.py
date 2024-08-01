"""
Manga recommendation page
"""

import streamlit as st

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

st.image("images/manga_logo_transparent_background.png", width=600)

# Check if the user is authenticated
if not authentication.is_authenticated():
    st.warning("Please log in from the home page to access this page.")
    st.stop()  # Stop further execution if not authenticated

user_id = frontend.add_user_input(1002)
frontend.add_recommendations("mangas", user_id, n=8)

# Example user-IDs: 1002, 357, 2507
