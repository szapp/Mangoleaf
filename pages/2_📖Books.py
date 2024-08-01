"""
Book recommendation page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_logo()

st.image("images/book_logo_transparent_background.png", width=530)

# Check if the user is authenticated
if not st.session_state.get('authenticated', False):
    st.warning('Please log in from the home page to access this page.')
    st.stop()  # Stop further execution if not authenticated

user_id = frontend.add_user_input(114368)
frontend.add_recommendations("books", user_id, n=8)

# Example user-IDs: 114368, 95359, 104636
