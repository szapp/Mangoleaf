"""
Query the current recommendations from the database.

This file does not compute any recommendations, it only loads the
precomputed recommendations from the SQL database. The recommendations
are then displayed in the streamlit app.
"""

import pandas as pd

from mangoleaf import Connection


def popularity(n, dataset, exclude_rated_by=None):
    """
    Popular books or mangas recommender.

    Parameters
    ----------
    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "mangas"

    exclude_rated_by : int, optional
        Exclude books or mangas that have been rated by this user

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n most popular books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_popular
    INNER JOIN {dataset} USING(item_id)
    WHERE item_id NOT IN (
        SELECT item_id FROM {dataset}_ratings WHERE user_id = {exclude_rated_by or -1}
    )
    ORDER BY id
    LIMIT {n};
    """
    df = pd.read_sql(query, Connection().get(), index_col="id")
    return df


def item_based(item_id, n, dataset, exclude_rated_by=None):
    """
    Item-based collaborative filtering recommender.

    Parameters
    ----------
    item_id : str
        ISBN or anime_id of the book or manga to base recommendations on

    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "manga"

    exclude_rated_by : int, optional
        Exclude books or mangas that have been rated by this user

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n recommended books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_item_based
    WHERE item_id = '{item_id}'
    LIMIT 1;
    """
    item_ids = pd.read_sql(query, Connection().get(), index_col="item_id").squeeze().to_list()

    query = f"""
    SELECT * FROM {dataset}
    WHERE item_id IN ({", ".join([f"'{i}'" for i in item_ids])})
    AND item_id NOT IN (
        SELECT item_id FROM {dataset}_ratings
        WHERE user_id = {exclude_rated_by or -1}
    );
    """
    df = pd.read_sql(query, Connection().get(), index_col="item_id")
    item_ids = [i for i in item_ids if i in df.index]
    df = df.loc[item_ids].reset_index().head(n)
    return df


def user_based(user_id, n, dataset="books"):
    """
    User-based collaborative filtering recommender.

    Parameters
    ----------
    user_id : int
        ID of the user to base recommendations on

    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n recommended books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_user_based
    WHERE user_id = '{user_id}'
    LIMIT 1;
    """
    item_ids = pd.read_sql(query, Connection().get(), index_col="user_id").squeeze()
    if item_ids.empty:
        return pd.DataFrame()
    item_ids = item_ids.to_list()

    query = f"""
    SELECT * FROM {dataset}
    WHERE item_id IN ({", ".join([f"'{i}'" for i in item_ids])});
    """
    df = pd.read_sql(query, Connection().get(), index_col="item_id")
    item_ids = [i for i in item_ids if i in df.index]
    df = df.loc[item_ids].reset_index().head(n)
    return df


def get_random_high_rated(user_id, dataset):
    """
    Get a random high rated book or manga from the user's history

    Parameters
    ----------
    user_id : int
        ID of the user to get the book or manga from

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    pd.Series
        Item information of the random high rated book or manga
    """
    query = f"""
    SELECT * FROM {dataset}_ratings
    INNER JOIN {dataset} USING (item_id)
    WHERE user_id = {user_id}
    ORDER BY rating DESC, RANDOM()
    LIMIT 10;
    """
    ratings = pd.read_sql(query, Connection().get())
    df = ratings.sample(1).drop(columns=["user_id", "rating"]).iloc[0]
    return df


def user_exists(user_id, dataset):
    """
    Check if a user exists in the dataset

    Parameters
    ----------
    user_id : int
        ID of the user to check

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    bool
        True if the user exists, False otherwise
    """
    query = f"""
    SELECT * FROM {dataset}_ratings
    WHERE user_id = {user_id}
    """
    df = pd.read_sql(query, Connection().get())
    return len(df) > 0
