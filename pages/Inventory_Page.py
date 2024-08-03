from collections import defaultdict
from pathlib import Path
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px

# st.set_page_config(
#     initial_sidebar_state="collapsed",
#     layout="wide",
#     page_title='Duda Shop',
#     page_icon=':shopping_bags:',  # This is an emoji shortcode. Could be a URL too.
# )

c1, c2, c3 = st.columns(3)

with c1:
    btn1 = st.button("Home", use_container_width=True, key="H2")
with c2:
    btn2 = st.button("Inventary Tracker", use_container_width=True, key="I2")
with c3:
    btn3 = st.button("Produktet", use_container_width=True, key="P2")

if btn2:
    st.switch_page("pages/Inventory_Page.py")
if btn3:
    st.switch_page("pages/Products.py")
if btn1:
    st.switch_page("main.py")


# -----------------------------------------------------------------------------
# Declare some useful functions.

def connect_db():
    '''Connects to the sqlite database.'''

    DB_FILENAME = Path(__file__).parent / 'inventory.db'
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
            link TEXT,
            date_created DATE
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Produkti TEXT
        )
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
                          'link',
                          'date_created'
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
            row_dict.update({"date_created": row_dict['date_created'].date()})
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
                link = :link,
                date_created = :date_created
            WHERE id = :id
            ''',
            rows,
        )

    if changes['added_rows']:
        cursor.executemany(
            '''
            INSERT INTO inventory
                (id, Produkti, Porositesi, Cmim_shitje, Cmim_blerje, Cmim_pound, Description, magazinim, status_porosie, link, date_created)
            VALUES
                (:id, :Produkti, :Porositesi, :Cmim_shitje, :Cmim_blerje, :Cmim_pound, :Description, :magazinim, :status_porosie, :link, :date_created)
            ''',
            (defaultdict(lambda: None, row) for row in changes['added_rows']),
        )

    if changes['deleted_rows']:
        cursor.executemany(
            'DELETE FROM inventory WHERE id = :id',
            ({'id': int(df.loc[i, 'id'])} for i in changes['deleted_rows'])
        )

    conn.commit()


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


def get_number_of_tickets_with_status(status):
    cursor = conn.cursor()
    cursor.execute(
        f"""
            SELECT 
               COUNT(status_porosie) 
            FROM 
               "inventory"
            WHERE
               status_porosie = '{status}';
        """
    )
    result = cursor.fetchall()
    conn.commit()
    return result[0][0]


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
df['date_created'] = pd.to_datetime(df['date_created'])

# Display data with editable table
edited_df = st.data_editor(
    df.drop(columns=['id']),
    column_order=["date_created", "Porositesi", "Produkti", "Description", "magazinim", "status_porosie", "Cmim_blerje",
                  "Cmim_pound", "Cmim_shitje", "link"],
    disabled=['id'],  # Don't allow editing the 'id' column.
    num_rows='dynamic',  # Allow appending/deleting rows.
    column_config={
        "Produkti": st.column_config.SelectboxColumn(
            "Produktet",
            options=[t[1:][0] for t in fetch_data("products")]
        ),
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
                "Pending",
                "Likujduar",
                "Dorezuar",
                "Anulluar",
                "Kthyer"
            ],
            required=True,
        ),

        "link": st.column_config.LinkColumn("Foto"),
        # Show dollar sign before price columns.
        "Cmim_shitje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_blerje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_pound": st.column_config.NumberColumn(format="£ %.2f"),
        "date_created": st.column_config.DateColumn(required=True, ),
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


st.markdown("## 📈 Statistika dhe Raporte")

a = fetch_data('inventory')
b = pd.DataFrame(a)

df_renamed = b.rename(columns={
    1: 'Produkti',
    2: 'Cmim_shitje',
    3: 'Cmim_blerje',
    7: 'Statusi',
    10: 'Data'
})
print(df_renamed)

b1, b2, b3, b4, b5= st.columns(5)
with b1:
    rd = st.button("Raport Ditor Profit", key='raport_ditor')
with b2:
    rm = st.button("Raport Mujor Profit", key='raport_mujor')
with b3:
    rd_prod = st.button("Raport Ditor Produkt", key='raport_ditor_prod')
with b4:
    rm_prod = st.button("Raport Mujor Produkt", key='raport_mujor_prod')
with b5:
    bs = st.button("Best Seller Chart", key='best_seller')


# Group by 'Category' and calculate sum of 'Value'
grouped_df = df_renamed.groupby('Data').agg({
    'Cmim_shitje': 'sum',
    'Cmim_blerje': 'sum'
}).reset_index()

grouped_df.columns = ['Dita', 'Xhiro (ALL)', 'Blerje (ALL)']
grouped_df['Difference'] = grouped_df['Xhiro (ALL)'] - grouped_df['Blerje (ALL)']

if rd:
    st.subheader("\nRaport Ditor")
    st.data_editor(grouped_df,
                   use_container_width=True,
                   hide_index=True,
                   disabled=True)

if rd_prod:
    raport_ditor_produkt = df_renamed.groupby(['Data', 'Produkti']).size().reset_index(name='Count')
    st.dataframe(raport_ditor_produkt,
                 use_container_width=True,
                 hide_index=True)

if rm_prod:
    df_renamed['Data'] = pd.to_datetime(df_renamed['Data'])
    df_renamed['YearMonth'] = df_renamed['Data'].dt.to_period('M')
    raport_mujor_produkt = df_renamed.groupby(['YearMonth','Produkti']).size().reset_index(name='Count')
    st.dataframe(raport_mujor_produkt,
                 use_container_width=True,
                 hide_index=True)


grouped_df['Dita'] = pd.to_datetime(grouped_df['Dita'])
grouped_df['YearMonth'] = grouped_df['Dita'].dt.to_period('M')

# Group by 'YearMonth' and aggregate
grouped_df = grouped_df.groupby('YearMonth').agg({
    'Xhiro (ALL)': 'sum',
    'Blerje (ALL)': 'sum',
}).reset_index()

grouped_df['Difference'] = grouped_df['Xhiro (ALL)'] - grouped_df['Blerje (ALL)']
grouped_df.rename(columns={
    'YearMonth': 'Muaji',
}, inplace=True)
if rm:
    st.subheader("\nRaport Mujor")
    st.data_editor(grouped_df,
                   use_container_width=True,
                   hide_index=True,
                   disabled=True
                   )

# Display the chart in Streamlit
if bs:
    count_df = df_renamed.groupby('Produkti').size().reset_index(name='Count')
    df_sorted = count_df.sort_values(by='Count', ascending=True)
    st.subheader("\nAll time Best Seller Chart")
    # Create a horizontal bar chart using plotly
    fig = px.bar(df_sorted, y='Produkti', x='Count', orientation='h')
    st.plotly_chart(fig)








nr_lik_prod = get_number_of_tickets_with_status(status="Likujduar")
nr_pending_prods = get_number_of_tickets_with_status(status="Pending")

st.error(f"Numri i produkteve me status PENDING eshte: {nr_pending_prods}")
st.success(f"Numri i produkteve me status  LIKUJDUAR eshte: {nr_lik_prod}")
