"""
Functionality for the frontend of repeated tasks
"""

import streamlit as st

from mangoleaf import query


def add_config():
    st.set_page_config(
        page_title="Mangoleaf - Book & Manga Recommendations",
        page_icon=":mango:",
        layout="wide",
    )


def add_style():
    with open("style/style.css") as f:
        st.html(f"<style>{f.read()}</style>")


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
    if "anime_id" in df.columns:
        url = "https://myanimelist.net/anime/"
    else:
        url = "https://www.goodreads.com/book/show/"

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
            st.html(
                html_element.format(
                    url=url,
                    item_id=row.iloc[0],
                    title=row.iloc[1],
                    secondary=row.iloc[2],
                    img_src=row.iloc[3],
                )
            )


def add_recommendations(dataset, user_id, n):
    # First row
    df = query.popularity(n, dataset, exclude_rated_by=user_id)
    make_row(f"Popular {dataset}", df, n)

    # Check if user exists
    if not query.user_exists(user_id, dataset):
        st.error("Invalid User ID", icon="🚨")
        st.stop()

    # Second row (retry different items that the user has not yet rated)
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
    df = query.user_based(user_id, n, dataset=dataset)
    make_row("Specifically for you", df, n)
