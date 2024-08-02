import sqlite3
from pathlib import Path
import streamlit as st

c1, c2, c3 = st.columns(3)

with c1:
    btn1 = st.button("Home", use_container_width=True, key="H3")
with c2:
    btn2 = st.button("Inventary Tracker", use_container_width=True, key="I3")
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

    DB_FILENAME = Path(__file__).parent / 'product.db'
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    '''Initializes the inventory table with some data.'''
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Produkti TEXT
        )
        '''
    )

    conn.commit()


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


conn, db_was_just_created = connect_db()
initialize_data(conn=conn)

prod = st.text_input("Produkti i ri")
if st.button("Shto ne liste"):
    insert_non_existing_values_to_table("products", f"{prod}")
# insert_non_existing_values_to_table("products", "sd")

del_prod = st.text_input("Produkti i vjeter")
if st.button("Hiq nga liste"):
    delete_value_from_table("products", f"{del_prod}")

st.subheader("Tabela permbledhese e listes se produkteve")
st.dataframe(fetch_data("products"),
             hide_index=True,
             column_order=["1"],
             column_config={
                 "1": st.column_config.TextColumn(
                     "Lista e produkteve"
                 )
             }
             )


product_list = [t[1:] for t in fetch_data("products")]
