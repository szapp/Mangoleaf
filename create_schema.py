"""
This script creates and fills the schema for the database with data.
If the schema already exists, it will be overwritten (dropped and
recreated). Any data in the tables will be lost.

The schema is described in the file schema.sql. The data is loaded
from the cleaned CSV files in the data folder.
"""

import pandas as pd
from sqlalchemy.sql import text

from mangoleaf.connection import Connection


def main():
    # Establish a connection to the database

    db_engine = Connection().get()

    # Create schema from SQL file
    with open("schema.sql") as f:
        sql_commands = f.read()

    with db_engine.connect() as connection:
        for command in sql_commands.split(";"):
            if command.strip():
                connection.execute(text(command))
        connection.commit()

    # Load cleaned data locally
    books = pd.read_csv("data/books/clean/books.csv", dtype="object")
    mangas = pd.read_csv("data/mangas/clean/mangas.csv", dtype="object")
    books_ratings = pd.read_csv("data/books/clean/ratings.csv", dtype="object")
    mangas_ratings = pd.read_csv("data/mangas/clean/ratings.csv", dtype="object")

    # Fill the static data: Books
    df = books[["ISBN", "Book-Title", "Book-Author", "Image-URL-M"]]
    df = df.rename(
        columns={
            "ISBN": "item_id",
            "Book-Title": "title",
            "Book-Author": "author",
            "Image-URL-M": "image",
        }
    )
    df.to_sql("books", db_engine, if_exists="append", index=False)

    # Fill the static data: Mangas
    df = mangas[["anime_id", "English name", "Other name", "Image URL"]]
    df = df.rename(
        columns={
            "anime_id": "item_id",
            "English name": "title",
            "Other name": "other_title",
            "Image URL": "image",
        }
    )
    df.to_sql("mangas", db_engine, if_exists="append", index=False)

    # Create users
    user_id = set(books_ratings["User-ID"].unique())
    user_id |= set(mangas_ratings["user_id"].unique())
    user_id = list(user_id)
    usernames = [f"User {i}" for i in user_id]
    passwords = [f"password{i}" for i in user_id]
    df = pd.DataFrame(dict(user_id=user_id, username=usernames, password=passwords))
    df.to_sql("users", db_engine, if_exists="append", index=False)

    # Fill the ratings: Books
    df = books_ratings.rename(
        columns={"User-ID": "user_id", "ISBN": "item_id", "Book-Rating": "rating"}
    )
    df.to_sql("books_ratings", db_engine, if_exists="append", index=False)

    # Fill the ratings: Mangas
    df = mangas_ratings.rename(columns={"anime_id": "item_id"})
    df.to_sql("mangas_ratings", db_engine, if_exists="append", index=False)

    # Close the connection
    db_engine.dispose()


if __name__ == "__main__":
    main()
