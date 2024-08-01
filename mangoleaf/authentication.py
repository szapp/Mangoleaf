"""
Authenticate user access
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader


def reset():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["name"] = None


def authenticate(username, password):
    with open("data/config.yaml", encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)

    if username in config["credentials"]["usernames"]:
        user_info = config["credentials"]["usernames"][username]
        if user_info["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["name"] = user_info["name"]
            return True

    return False


def is_authenticated():
    return st.session_state.get("authenticated", False)


def get_user_info():
    return dict(
        username=st.session_state["username"],
        name=st.session_state["name"],
    )
