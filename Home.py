"""
Landing page
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()

st.image("images/white_logo_transparent_background.png")

st.markdown(
    """
**Welcome to MANGOLEAF**, your ultimate guide to discovering the best books and manga tailored
to your tastes. Whether you're a seasoned reader or just starting, MANGOLEAF provides personalized
recommendations to help you find your next favorite read.
"""
)

frontend.add_mixed_recommendations(n=8)


st.subheader("About Us", anchor=False)
st.markdown(
    """
Mangoleaf is brought to you by Max and Sören, passionate developers and data scientists dedicated
to enhancing your reading experience.
"""
)

st.subheader("How To Use MANGOLEAF", anchor=False)
st.markdown(
    """
Choose on the left if you are interested in Books or Manga and explore the recommendations!
"""
)

with open("data/config.yaml", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)


# Authentication function
def authenticate(username, password):
    if username in config["credentials"]["usernames"]:
        user_info = config["credentials"]["usernames"][username]
        if user_info["password"] == password:
            return True, user_info["name"], user_info["email"]
    return False, None, None


# Sidebar for login
st.sidebar.title("Login")

# Sidebar inputs for username and password
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Sidebar button for login
if st.sidebar.button("Login"):
    authenticated, name, email = authenticate(username, password)
    if authenticated:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["name"] = name
        st.session_state["email"] = email
        st.sidebar.success(f"Welcome {name}")
    else:
        st.sidebar.error("Username/password is incorrect")

# Display content if authenticated
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    st.sidebar.success(f"Logged in as {st.session_state['name']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["name"] = None
        st.session_state["email"] = None
        st.sidebar.info("You have logged out")
else:
    st.sidebar.info("Please log in to access the content")

# Sidebar

if "authenticated" in st.session_state and st.session_state["authenticated"]:
    st.sidebar.success("Choose between books and mangas")
    st.markdown("**Now you have access to other pages.**")

frontend.add_sidebar_logo()
