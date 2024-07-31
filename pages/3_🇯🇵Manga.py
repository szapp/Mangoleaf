"""
Manga recommendation page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()

st.header("Manga Recommendations", anchor=False)
user_id = frontend.add_user_input(1002)
frontend.add_recommendations("mangas", user_id, n=8)

# Example user-IDs: 1002, 357, 2507
