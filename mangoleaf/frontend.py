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


def add_row_header(heading):
    st.html(f"<h2 class='row_header'>{heading}</h2>")  # Allow coloring


def make_row(df, n):
    if "author" in df.columns:
        url = "https://isbnsearch.org/isbn/"
    else:
        url = "https://myanimelist.net/anime/"

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
    # Check if user_id has rated items in that dataset
    user_id_valid = user_id if query.user_exists(user_id, dataset) else None

    # First row
    add_row_header(f"Popular {dataset}")
    with st.spinner("Loading recommendations..."):
        df = query.popularity(n, dataset, exclude_rated_by=user_id_valid)
        make_row(df, n)

    # Second row (retry different items that the user has not yet rated)
    if "second_row_title" not in st.session_state:
        st.session_state.second_row_title = dataset
    if user_id_valid is None:
        header = "If you like"
    else:
        header = "Because you read"
    header += f"""
        <span class='highlight'>{st.session_state.second_row_title}</span> you might also like...
    """
    add_row_header(header)
    with st.spinner("Loading recommendations..."):
        df = []
        attempt = 0
        while len(df) == 0 and attempt < 5:
            ref_item = query.get_random_high_rated(user_id_valid, dataset=dataset)
            title = ref_item.title
            title = title[0] + title[1:].split("(")[0]
            title = title[0] + title[1:].split(":")[0]
            title = title[0] + title[1:].split("-")[0]
            title = title.strip()
            if len(title) > 20:
                title = title[:20] + "…"
            st.session_state.second_row_title = title
            df = query.item_based(
                ref_item.item_id, n, dataset=dataset, exclude_rated_by=user_id_valid
            )
            attempt += 1
            make_row(df, n)

    # Third row
    add_row_header("Specifically for you")
    if user_id is None:
        st.warning("Please log in to unlock personal recommendations")
    elif not user_id_valid:
        st.warning(f"Start rating {dataset} to unlock personal recommendations")
    else:
        print(user_id)
        with st.spinner("Loading recommendations..."):
            df = query.user_based(user_id, n, dataset=dataset)
        make_row(df, n)


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
        user = authentication.get_user_info()
        st.sidebar.markdown(f"Logged in as {user['username']}")
        if st.sidebar.button("Logout", key="sidebar_logout"):
            authentication.reset()
            st.sidebar.info("You have logged out")
            st.rerun()
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
                st.sidebar.success(f"Welcome {user['username']}")
                st.rerun()
            else:
                st.sidebar.error("Username/password is incorrect")

        st.sidebar.info("Please log in to access the content")
