"""
Authenticate user access
"""

import streamlit as st

from mangoleaf import query


def reset():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["full_name"] = None
    st.session_state["user_id"] = None
    st.session_state["registered"] = None
    for key in st.session_state.keys():
        if key.startswith("rate_"):
            del st.session_state[key]


def authenticate(username, password):
    user_info = query.match_user_credentials(username, password)
    if user_info is None:
        return False

    st.session_state["authenticated"] = True
    st.session_state["username"] = user_info["username"]
    st.session_state["full_name"] = user_info["full_name"]
    st.session_state["user_id"] = user_info["user_id"]
    st.session_state["registered"] = user_info["registered"]
    return True


def is_authenticated():
    return st.session_state.get("authenticated", False)


def register(username, password, min_length=8):
    if query.user_exists(username):
        return "user_exists"
    if len(username) < 5:
        return "username_short"
    if len(password) < min_length:
        return "password_short"
    success = query.register_user(username, password)
    return success


def get_user_info():
    return dict(
        username=st.session_state.get("username", None),
        full_name=st.session_state.get("full_name", None),
        user_id=st.session_state.get("user_id", None),
        registered=st.session_state.get("registered", None),
    )


def get_extended_user_info():
    return query.get_extended_user_info(st.session_state.get("user_id", None))
