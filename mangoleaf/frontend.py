"""
Functionality for the frontend of repeated tasks
"""

import streamlit as st

from mangoleaf import authentication, query


def add_config():
    st.set_page_config(
        page_title="Mangoleaf - Book & Manga Recommendations",
        page_icon=":mango:",
        layout="wide",
    )


def add_style():
    with open("style/style.css") as f:
        st.html(f"<style>{f.read()}</style>")


def add_sidebar_logo():
    st.sidebar.image("images/mango_logo.png", use_column_width=True)


def add_user_input(default_user_id):
    user_id = st.text_input(
        "User ID",
        value=str(default_user_id),
        placeholder="Enter your user ID",
    )

    # Convert to integer
    try:
        user_id = int(user_id.strip())
    except ValueError:
        user_id = -1

    return user_id


def make_row(heading, df, n):
    if "author" in df.columns:
        url = "https://isbnsearch.org/isbn/"
    else:
        url = "https://myanimelist.net/anime/"

    st.html(f"<h2 class='row_header'>{heading}</h2>")  # Allow coloring

    html_element = """<div class="rec_element">
        <a href="{url}{item_id}"
           rel="noopener noreferrer" target="_blank">
            <img src="{img_src}" alt="{title}" class="rec_image">
            <div class="rec_text">
                <p></p>
                <p>{title}</p>
                <p>{secondary}</p>
            </div>
        </a>
    </div>"""

    columns = st.columns(n)
    for col, (_, row) in zip(columns, df.iterrows()):
        with col:
            st.markdown(
                html_element.format(
                    url=url,
                    item_id=row.iloc[0],
                    title=row.iloc[1],
                    secondary=row.iloc[2],
                    img_src=row.iloc[3],
                ),
                unsafe_allow_html=True,
            )


def add_recommendations(dataset, user_id, n):
    # First row
    with st.spinner("Loading recommendations..."):
        df = query.popularity(n, dataset, exclude_rated_by=user_id)
    make_row(f"Popular {dataset}", df, n)

    # Check if user exists
    if not query.user_exists(user_id, dataset):
        st.error("Invalid User ID", icon="🚨")
        st.stop()

    # Second row (retry different items that the user has not yet rated)
    with st.spinner("Loading recommendations..."):
        df = []
        attempt = 0
        while len(df) == 0 and attempt < 5:
            ref_item = query.get_random_high_rated(user_id, dataset=dataset)
            df = query.item_based(ref_item.item_id, n, dataset=dataset, exclude_rated_by=user_id)
            attempt += 1

    title = ref_item.title
    title = title[0] + title[1:].split("(")[0]
    title = title[0] + title[1:].split(":")[0]
    title = title[0] + title[1:].split("-")[0]
    title = title.strip()
    if len(title) > 20:
        title = title[:20] + "…"
    make_row(
        f"Because you read <span class='highlight'>{title}</span> you might also like...", df, n
    )

    # Third row
    with st.spinner("Loading recommendations..."):
        df = query.user_based(user_id, n, dataset=dataset)
    make_row("Specifically for you", df, n)


def add_mixed_recommendations(n):
    n = 2 * n // 2  # Make sure n is even
    df_books = query.popularity(n // 2, "books")
    df_mangas = query.popularity(n // 2, "mangas")
    rows = list(df_books.iterrows()) + [(None, None)] + list(df_mangas.iterrows())

    st.html(
        """<h2 class='row_header' style='display: flex; flex-direction: row;'>
            <div style='flex-grow: 0;'><a href="Books">Popular books</a></div>
            <div style='flex-grow: 1;'></div>
            <div style='flex-grow: 0;'><a href="Manga">Popular mangas</a></div>
    </h2>"""
    )

    html_element = """<div class="rec_element">
        <img src="{img_src}" alt="{title}" class="rec_image">
        <div class="rec_text">
            <p></p>
            <p>{title}</p>
            <p>{secondary}</p>
        </div>
    </div><br>"""

    col_width = [1] * (n // 2) + [0.5] + [1] * (n // 2)
    columns = st.columns(col_width)
    for col, (_, row) in zip(columns, rows):
        with col:
            if row is None:
                continue
            st.markdown(
                html_element.format(
                    item_id=row.iloc[0],
                    title=row.iloc[1],
                    secondary=row.iloc[2],
                    img_src=row.iloc[3],
                ),
                unsafe_allow_html=True,
            )


def add_sidebar_login():
    if authentication.is_authenticated():
        st.sidebar.success(f"Logged in as {st.session_state['name']}")
        if st.sidebar.button("Logout", key="sidebar_logout"):
            authentication.reset()
            st.sidebar.info("You have logged out")
            st.rerun()
        else:
            st.sidebar.success("Choose between books and mangas")
            st.sidebar.markdown("**Now you have access to other pages.**")
    else:
        st.sidebar.title("Login")

        # Sidebar inputs for username and password
        with st.sidebar.form("login_mask", border=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

        # Sidebar button for login
        if submit:
            if authentication.authenticate(username, password):
                user = authentication.get_user_info()
                st.sidebar.success(f"Welcome {user['name']}")
                st.rerun()
            else:
                st.sidebar.error("Username/password is incorrect")

        st.sidebar.info("Please log in to access the content")
