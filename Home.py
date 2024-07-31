"""
Landing page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()

st.title("MANGOLEAF", anchor=False)
st.sidebar.success("Choose between books and mangas")
