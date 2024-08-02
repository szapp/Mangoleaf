"""
Manga explorer page
"""

import pandas as pd
import streamlit as st

from mangoleaf import Connection, authentication, frontend, query

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("Magna Explorer")

st.markdown(
    """
Have a look through our manga database and use filters to find what you are looking for!
"""
)


def filter_builder(filter_options, display_names=None):
    """
    Adds filter options for the user to query the database

    Parameters
    ----------
    filter_options : dict
        Mapping of column names to select for filtering and their filter
        type, either "text", "rating", or a tuple/list of categories for
        a multiselect

    display_names : list, optional
        List of display names for the columns in the filter. Defaults to
        the table column names

    Returns
    -------
    where_query : str
        Partial SQL query to filter the database (WHERE clause)

    query_params : dict
        Mapping of query parameters to pass to the SQL query
    """
    clauses = []
    query_params = {}
    if display_names is None:
        display_names = list(filter_options.keys())
    with st.container(border=True):
        for (column, filter_type), disp_name in zip(filter_options.items(), display_names):

            assert column.find(" ") == -1, "Column names cannot contain spaces"

            if isinstance(filter_type, str) and filter_type == "text":
                # Text search
                user_text_input = st.text_input(f"Search {disp_name}", key=f"{column}_text_input")
                if user_text_input:
                    query_params[column] = f"%{user_text_input}%"
                    clauses.append(column + f" LIKE %({column})s")
            elif isinstance(filter_type, str) and filter_type == "rating":
                # Numeric range slider
                col1, col2 = st.columns(2, gap="large", vertical_alignment="center")
                user_num_input = col1.slider(
                    "Range of your rating",
                    min_value=1,
                    max_value=5,
                    value=(1, 5),
                    step=1,
                    key=f"{column}_num_slider",
                )
                user_bool_input = col2.checkbox(
                    "Include unrated",
                    value=True,
                    key=f"{column}_bool_checkbox",
                )
                query_params[f"{column}_min"] = int(user_num_input[0])
                query_params[f"{column}_max"] = int(user_num_input[1])
                if user_bool_input:
                    clauses.append(
                        "(" + column + f" BETWEEN %({column}_min)s AND %({column}_max)s"
                        " OR " + column + " IS NULL)"
                    )
                else:
                    clauses.append(column + f" BETWEEN %({column}_min)s AND %({column}_max)s")
            else:
                # Categorical values
                filter_type = list(map(str, filter_type))
                user_cat_input = st.multiselect(
                    f"Categories of {disp_name}",
                    filter_type,
                    default=filter_type,
                    key=f"{column}_cat_multiselect",
                )
                query_params[column] = tuple(user_cat_input)
                clauses.append(column + f" IN %({column})s")

    where_query = " AND ".join(clauses)
    if where_query:
        where_query = "WHERE " + where_query
    return where_query, query_params


user_id = authentication.get_user_info()["user_id"]


def update_rating(item_id, rating_before, key):
    rating = st.session_state.get(key, pd.NA)
    if not pd.isna(rating):
        rating += 1
        if rating != rating_before:
            print(f"User {user_id} updated rating for {item_id} from {rating_before} to {rating}")
            query.update_rating("mangas", user_id, item_id, rating)
            st.toast("Rating updated", icon="⭐")


# Filter the DataFrame using the filter function
filter_options = dict(
    title="text",
    other_title="text",
)
if user_id is not None:
    filter_options["rating"] = "rating"
where_query, query_params = filter_builder(
    filter_options, ["english title", "original title", "your rating"]
)

# Load the database table into a DataFrame
max_items = 21
if user_id is None:
    query_str = f"""
    SELECT * FROM mangas
    {where_query}
    ORDER BY title
    LIMIT {max_items};
    """
else:
    query_str = f"""
    SELECT * FROM mangas
    LEFT JOIN (
        SELECT * FROM mangas_ratings
        WHERE user_id = {user_id}
    ) r USING (item_id)
    {where_query}
    ORDER BY title
    LIMIT {max_items};
    """

df = pd.read_sql(query_str, Connection().get(), params=query_params)

# Fill the ratings
for _, row in df.iterrows():
    if not pd.isna(row.get("rating", pd.NA)):
        key = f"rate_{row['item_id']}"
        st.session_state[key] = row["rating"] - 1

st.html("<br>")
outer_columns = st.columns(3)
for idx, (_, row) in enumerate(df.iterrows()):
    col1, col2 = outer_columns[idx % 3].columns([1, 3])
    item = f"""
        <div class="rec_element">
            <a href="https://myanimelist.net/anime/{row['item_id']}" rel="noopener noreferrer"
               target="_blank">
                <img src="{row['image']}" alt="" class="rec_image">
                <div class="rec_text">
                    <p></p>
                    <p>{row['title']}</p>
                    <p>{row['other_title']}</p>
                </div>
            </a>
        </div>
    </div>
    """
    col1.html(item)
    col2.markdown(f"**{row['title']}**  \n{row['other_title']}")
    key = f"rate_{row['item_id']}"
    col2.feedback(
        "stars",
        key=key,
        on_change=update_rating,
        args=(row["item_id"], row.get("rating", pd.NA), key),
        disabled=user_id is None,
    )
    if user_id is None:
        col2.markdown("Log in to rate")

if len(df) >= max_items:
    st.html(
        f"""
    <div style="width: 100%; display: flex; justify-content: center; margin-top: 20px;">
        <div style="background-color: #202020; border: 1px solid #303030; border-radius:
                    8px; padding: 4px 12px;">
            Showing the first {max_items} results. Refine your search to see more.
        </div>
    </div>
    """
    )
