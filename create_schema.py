"""
This script creates and fills the schema for the database with data.
If the schema already exists, it will be overwritten (dropped and
recreated). Any data in the tables will be lost.

The schema is described in the file schema.sql. The data is loaded
from the cleaned CSV files in the data folder.
"""

import os

import bcrypt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.sql import text

from mangoleaf import Connection


def main():
    # Establish a connection to the database
    db_engine = Connection().get()

    # Create schema from SQL file
    with open("schema.sql") as f:
        sql_commands = f.read()

    print("Create schema")
    with db_engine.connect() as connection:
        for command in sql_commands.split(";"):
            if command.strip():
                connection.execute(text(command))
        connection.commit()

    # Load cleaned data locally
    print("Load data from disk")
    books = pd.read_csv("data/books/clean/books.csv", dtype="object")
    mangas = pd.read_csv("data/mangas/clean/mangas.csv", dtype="object")
    books_ratings = pd.read_csv("data/books/clean/ratings.csv", dtype="object")
    mangas_ratings = pd.read_csv("data/mangas/clean/ratings.csv", dtype="object")

    # Fill the static data: Books
    print("Fill static data")
    df = books[["ISBN", "Book-Title", "Book-Author", "Year-Of-Publication", "Image-URL-M"]]
    df = df.rename(
        columns={
            "ISBN": "item_id",
            "Book-Title": "title",
            "Book-Author": "author",
            "Year-Of-Publication": "year",
            "Image-URL-M": "image",
        }
    )
    df.to_sql("books", db_engine, if_exists="append", index=False)

    # Fill the static data: Mangas
    df = mangas[["anime_id", "English name", "Other name", "Genres", "Image URL"]]
    df = df.rename(
        columns={
            "anime_id": "item_id",
            "English name": "title",
            "Other name": "other_title",
            "Genres": "genres",
            "Image URL": "image",
        }
    )
    df["genres"] = df["genres"].str.lower().str.split(", ").apply(lambda x: "|".join(x))
    df.to_sql("mangas", db_engine, if_exists="append", index=False)

    # Create users
    print("Create static users from ratings")
    user_id = set(books_ratings["User-ID"].unique()) | set(mangas_ratings["user_id"].unique())
    user_id = list(user_id)
    usernames = [f"user_{i}" for i in user_id]
    full_names = [f"User {i}" for i in user_id]
    salt = bcrypt.gensalt()
    general_password = os.getenv("DUMMY_PASSWORD")
    dummy_password = bcrypt.hashpw(general_password.encode("utf-8"), salt).decode("utf-8")
    passwords = [dummy_password] * len(user_id)
    df = pd.DataFrame(
        dict(
            user_id=user_id,
            username=usernames,
            password=passwords,
            full_name=full_names,
            registered="2024-07-23",
        )
    )
    df.to_sql("users", db_engine, if_exists="append", index=False)

    # Fill the ratings: Books
    print("Add ratings")
    df = books_ratings.rename(
        columns={"User-ID": "user_id", "ISBN": "item_id", "Book-Rating": "rating"}
    )
    df.to_sql("books_ratings", db_engine, if_exists="append", index=False)

    # Fill the ratings: Mangas
    df = mangas_ratings.rename(columns={"anime_id": "item_id"})
    df.to_sql("mangas_ratings", db_engine, if_exists="append", index=False)

    # Create backup tables for easy resetting
    print("Create backup tables")
    query = """
    CREATE TABLE users_original AS TABLE users;
    CREATE TABLE books_ratings_original AS TABLE books_ratings;
    CREATE TABLE mangas_ratings_original AS TABLE mangas_ratings;
    """
    with db_engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

    # Close the connection
    db_engine.dispose()
    print("Done")


if __name__ == "__main__":
    load_dotenv(".streamlit/secrets.toml")
    main()
