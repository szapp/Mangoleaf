"""
Book recommendation page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()

st.header("Manga Recommendations", anchor=False)
user_id = frontend.add_user_input(114368)
frontend.add_recommendations("books", user_id, n=8)

# Example user-IDs: 114368, 95359, 104636
