"""
Landing page
"""

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

# Social links
social_max = frontend.add_social_links("max", True, True)
social_soren = frontend.add_social_links("soren", True, True)

st.image("images/white_logo_transparent_background.png")

st.markdown(
    """
**Welcome to MANGOLEAF**, your ultimate guide to discovering the best books and manga tailored
to your tastes. Whether you're a seasoned reader or just starting, MANGOLEAF provides personalized
recommendations to help you find your next favorite read.
"""
)

hydrate_recommendation = frontend.add_mixed_recommendations(n=8)


st.subheader("About Us", anchor=False)
st.markdown(
    f"""
MANGOLEAF is brought to you by Max {social_max} and Sören {social_soren}, passionate developers and
data scientists dedicated to enhancing your reading experience.
""",
    unsafe_allow_html=True,
)

st.subheader("How To Use MANGOLEAF", anchor=False)
st.markdown(
    """
Choose on the left if you are interested in Books or Manga and explore the recommendations!

If you want to save your ratings and get personalized recommendations based on your ratings,
create an account in the side bar.
Personalized recommendations based on ratings are updated every 24 hours.

<div class="explorer_info"><div align="center">
  To prevent spam and abuse, user profiles are reset and deleted every 5 days.<br />
  But you can export and download your ratings at any time.
</div></div>
""",
    unsafe_allow_html=True,
)

hydrate_recommendation()
