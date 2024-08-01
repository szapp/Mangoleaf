"""
Book recommendation page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_logo()

st.image("images/book_logo_transparent_background.png", width=530)
user_id = frontend.add_user_input(114368)
frontend.add_recommendations("books", user_id, n=8)

# Example user-IDs: 114368, 95359, 104636
