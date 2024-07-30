from collections import defaultdict
from pathlib import Path
import sqlite3
import streamlit as st
import pandas as pd

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout="wide",
    page_title='Duda Shop',
    page_icon=':shopping_bags:',  # This is an emoji shortcode. Could be a URL too.
)

btn1 = st.button("Home")
if btn1:
    st.switch_page("main.py")


# -----------------------------------------------------------------------------
# Declare some useful functions.

def connect_db():
    '''Connects to the sqlite database.'''

    DB_FILENAME = Path(__file__).parent/'inventory.db'
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    '''Initializes the inventory table with some data.'''
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Produkti TEXT,
            Cmim_shitje REAL,
            Cmim_pound REAL,
            Cmim_blerje REAL,
            Description TEXT,
            magazinim REAL,
            status_porosie TEXT,
            Porositesi TEXT,
            Order_date TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        INSERT INTO inventory
            (Produkti, Cmim_shitje, Cmim_pound, Cmim_blerje, Description, magazinim, status_porosie, Porositesi, Order_date)
        VALUES
            ('Tutina 6-pack', 1500.00, 10.00, 1240.00,  'Mosha 12-18', 'Inventar', 'Likujduar', 'Enid Vyshka', '2021-09-01'),
            ('Body 3-pack', 800.00, 3.00, 500.00,  'Mosha 9-12', 'Porosi e re', 'Kthyer', 'John Doe', '2021-09-02'),
            ('Grykore', 250.00, 1.00, 120.00,  'Me dinosaur per djem', 'Inventar', 'Anulluar', 'Dua Veizaj', '2021-09-03')
        '''
    )
    conn.commit()


def load_data(conn):
    '''Loads the inventory data from the database.'''
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM inventory')
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(data,
        columns=[
            'id',
            'Produkti',
            'Cmim_shitje',
            'Cmim_blerje',
            'Cmim_pound',
            'Description',
            'magazinim',
            'status_porosie',
            'Porositesi',
            'Order_date'
        ])

    return df


def update_data(conn, df, changes):
    '''Updates the inventory data in the database.'''
    cursor = conn.cursor()

    if changes['edited_rows']:
        deltas = st.session_state.inventory_table['edited_rows']
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            '''
            UPDATE inventory
            SET
                Produkti = :Produkti,
                Cmim_shitje = :Cmim_shitje,
                Cmim_blerje = :Cmim_blerje,
                Cmim_pound = :Cmim_pound,
                Description = :Description,
                magazinim = :magazinim,
                status_porosie = :status_porosie,
                Porositesi = :Porositesi,
                Order_date = :Order_date
            WHERE id = :id
            ''',
            rows,
        )

    if changes['added_rows']:
        cursor.executemany(
            '''
            INSERT INTO inventory
                (id, Produkti, Porositesi, Cmim_shitje, Cmim_blerje, Cmim_pound, Description, magazinim, status_porosie, Order_date)
            VALUES
                (:id, :Produkti, :Porositesi, :Cmim_shitje, :Cmim_blerje, :Cmim_pound, :Description, :magazinim, :status_porosie, :Order_date)
            ''',
            (defaultdict(lambda: None, row) for row in changes['added_rows']),
        )

    if changes['deleted_rows']:
        cursor.executemany(
            'DELETE FROM inventory WHERE id = :id',
            ({'id': int(df.loc[i, 'id'])} for i in changes['deleted_rows'])
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.


# Set the title that appears at the top of the page.
'''
# :shopping_bags: Duda Shop Inventari
'''

st.info('''
    Perdorni tabelen e meposhtme per te shtuar, hequr apo edituar vlerat. \n
    ''')


# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast('Database initialized.')

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df.drop(columns=['id']),
    column_order=["Order_date", "Porositesi", "Produkti", "Description", "magazinim", "status_porosie", "Cmim_blerje", "Cmim_pound", "Cmim_shitje"],
    disabled=['id'], # Don't allow editing the 'id' column.
    num_rows='dynamic', # Allow appending/deleting rows.
    column_config={
        "magazinim": st.column_config.SelectboxColumn(
            "Magazinim",
            # help="The category of the app",
            width="medium",
            options=[
                "Porosi e re",
                "Inventar",
            ],
            required=True,
        ),


        "status_porosie": st.column_config.SelectboxColumn(
            "Order Status",
            # help="The category of the app",
            width="medium",
            options=[
                "Likujduar",
                "Dorezuar",
                "Anulluar",
                "Kthyer"
            ],
            required=True,
        ),
        # Show dollar sign before price columns.
        "Cmim_shitje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_blerje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_pound": st.column_config.NumberColumn(format="£ %.2f"),

    },
    key='inventory_table')

st.warning('''
!!! Mos harroni te klikoni butonin SAVE per te ruajtur te dhenat ne databaze !!!
''')
has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    'SAVE',
    type='primary',
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table))