import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

c1, c2, c3 = st.columns(3)

with c1:
    btn1 = st.button("Home", use_container_width=True, key="H3")
with c2:
    btn2 = st.button("Inventory Tracker", use_container_width=True, key="I3")
with c3:
    btn3 = st.button("Produktet", use_container_width=True, key="P3")

if btn2:
    st.switch_page("pages/Inventory_Page.py")
if btn3:
    st.switch_page("pages/Products.py")
if btn1:
    st.switch_page("main.py")


st.header("Manaxhimi i Produkteve")


def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


conn, db_was_just_created = connect_db()


def insert_non_existing_values_to_table(table_name, name):
    cursor = conn.cursor()
    cursor.execute(
        f"""
            INSERT INTO "{table_name}"(Produkti)
            SELECT '{name}'
            WHERE
            NOT EXISTS (
            SELECT Produkti FROM "{table_name}" WHERE Produkti = '{name}'
            );
        """
    )


def fetch_data(table):
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT * from "{table}";
        """
    )
    result = cursor.fetchall()
    conn.commit()
    # conn.close()
    return result


def delete_value_from_table(table_name, name):
    cursor = conn.cursor()
    cursor.execute(
        f"""
        DELETE FROM "{table_name}"
        WHERE Produkti = '{name}';
        """
    )
    conn.commit()


# product_list = [t[1:][0] for t in fetch_data("products")]

prod = st.text_input("Produkti i ri")
if st.button("Shto ne liste"):
    insert_non_existing_values_to_table("products", f"{prod}")
# insert_non_existing_values_to_table("products", "sd")

del_prod = st.selectbox(
    "Produkti i vjeter", options=[t[1:][0] for t in fetch_data("products")]
)

if st.button("Hiq nga lista"):
    delete_value_from_table("products", f"{del_prod}")

st.subheader("Tabela permbledhese e produkteve")
st.dataframe(
    fetch_data("products"),
    hide_index=True,
    column_order=["1"],
    column_config={"1": st.column_config.TextColumn("Lista e produkteve")},
)
