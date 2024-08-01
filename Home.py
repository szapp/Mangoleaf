"""
Landing page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()

st.sidebar.success("Choose between books and mangas")
frontend.add_sidebar_logo()

st.image("images/white_logo_transparent_background.png")

st.markdown(
    """
**Welcome to MANGOLEAF**, your ultimate guide to discovering the best books and manga tailored
to your tastes. Whether you're a seasoned reader or just starting, MANGOLEAF provides personalized
recommendations to help you find your next favorite read.
"""
)

frontend.add_mixed_recommendations(n=8)

st.markdown(
    """

**About Us:**

Mangoleaf is brought to you by Max and Sören, passionate developers and data scientists dedicated
to enhancing your reading experience.

How To Use MANGOLEAF:

Choose on the left if you are interested in Books or Manga and explore the recommendations!
"""
)
