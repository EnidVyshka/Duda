from collections import defaultdict

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import psycopg2

c1, c2, c3 = st.columns(3)

with c1:
    btn1 = st.button("Home", use_container_width=True, key="H2")
with c2:
    btn2 = st.button("Inventory Tracker", use_container_width=True, key="I2")
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


# Function to connect to the Supabase PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=st.secrets.db_credentials["host"],
            port=st.secrets.db_credentials["port"],
            dbname=st.secrets.db_credentials["db_name"],
            user=st.secrets.db_credentials["db_user"],
            password=st.secrets.db_credentials["db_password"],
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None


# Streamlit app layout
st.title("Supabase PostgreSQL Database Connection")

# Try connecting to the database
conn = connect_to_db()

if conn:
    st.success("Successfully connected to the database!")
    # You can execute SQL queries here if connected
    try:
        cur = conn.cursor()
        cur.execute("SELECT version();")  # Example query
        version = cur.fetchone()
        st.write(f"PostgreSQL version: {version[0]}")
        cur.close()
    except Exception as e:
        st.error(f"Failed to run query: {e}")
    finally:
        conn.close()
else:
    st.error("Connection failed.")


def initialize_data(conn):
    """Initializes the inventory table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            Produkti TEXT,
            Cmim_shitje TEXT,
            Cmim_blerje TEXT,
            Cmim_pound TEXT,
            Description TEXT,
            magazinim TEXT,
            status_porosie TEXT,
            Porositesi TEXT,
            link TEXT,
            date_created DATE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            Produkti TEXT
        )
        """
    )

    conn.commit()


def load_data(conn):
    """Loads the inventory data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "Produkti",
            "Cmim_shitje",
            "Cmim_pound",
            "Cmim_blerje",
            "Description",
            "magazinim",
            "status_porosie",
            "Porositesi",
            "link",
            "date_created",
        ],
    )

    return df


def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update({"date_created": row_dict["date_created"].date()})
            row_dict.update(delta)
            rows.append(row_dict)
        cursor.executemany(
            """
            UPDATE inventory
            SET
                Produkti = :Produkti,
                Cmim_shitje = :Cmim_shitje,
                Cmim_pound = :Cmim_pound,
                Cmim_blerje = :Cmim_blerje,
                Description = :Description,
                magazinim = :magazinim,
                status_porosie = :status_porosie,
                Porositesi = :Porositesi,
                link = :link,
                date_created = :date_created
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        data = [
            (
                # row.get('id', None),
                row.get('Produkti', None),
                row.get('Porositesi', None),
                row.get('Cmim_shitje', None),
                row.get('Cmim_pound', None),
                row.get('Cmim_blerje', None),
                row.get('Description', None),
                row.get('magazinim', None),
                row.get('status_porosie', None),
                row.get('link', None),
                row.get('date_created', None)
            )
            for row in changes["added_rows"]
        ]

        cursor.executemany(
            """
                INSERT INTO inventory
                    (Produkti, Porositesi, Cmim_shitje, Cmim_pound, Cmim_blerje, Description, magazinim, status_porosie, link, date_created)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
            data,
        )

    if changes["deleted_rows"]:

        data = [(int(df.loc[i, "id"]),) for i in changes["deleted_rows"]]
        cursor.executemany(
            "DELETE FROM inventory WHERE id = %s",
            data,
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
"""
# :shopping_bags: Duda Shop Inventari
"""

st.info(
    """
    Perdorni tabelen e meposhtme per te shtuar, hequr apo edituar vlerat. \n
    """
)

# Connect to database and create table if needed
conn = connect_to_db()
initialize_data(conn)

# Initialize data.
# if db_was_just_created:
# initialize_data(conn)
# st.toast("Database initialized.")

# Load data from database
df = load_data(conn)
df["date_created"] = pd.to_datetime(df["date_created"])
# Display data with editable table
edited_df = st.data_editor(
    df.drop(columns=["id"]),
    column_order=[
        "date_created",
        "Porositesi",
        "Produkti",
        "Description",
        "magazinim",
        "status_porosie",
        "Cmim_shitje",
        "Cmim_pound",
        "Cmim_blerje",
    ],
    # disabled=['id'],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        "date_created": st.column_config.DateColumn("Data", required=True),
        "Porositesi": st.column_config.TextColumn("Klienti"),
        "Produkti": st.column_config.SelectboxColumn(
            "Artikulli", options=[t[1:][0] for t in fetch_data("products")]
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
            options=["Pending", "Likujduar", "Dorezuar", "Anulluar", "Kthyer"],
            required=True,
        ),
        # "link": st.column_config.LinkColumn("Foto"),
        "Cmim_shitje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_blerje": st.column_config.NumberColumn(format="ALL %.2f"),
        "Cmim_pound": st.column_config.NumberColumn(format="£ %.2f"),
    },
    key="inventory_table",
)

st.warning(
    """
!!! Mos harroni te klikoni butonin SAVE per te ruajtur te dhenat ne databaze !!!
"""
)
has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "SAVE",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)

data_from_db = fetch_data("inventory")
data_to_df = pd.DataFrame(data_from_db)

df_renamed = data_to_df.rename(
    columns={
        1: "Produkti",
        2: "Cmim_shitje",
        4: "Cmim_blerje",
        7: "Statusi",
        10: "Data",
    }
)

st.subheader(" ⚙️ Filtrimi i te dhenave ")
with st.expander("Klikoni KETU per te filtruar tabelen"):
    q1, q2 = st.columns(2)
    with q1:
        st.title("")
        data1 = st.date_input("Zgjidhni daten e fillimit: ", key="q1")
    with q2:
        st.title("")
        data2 = st.date_input("Zgjidhni daten e mbarimit: ", key="q2")
    if data1 > data2:
        st.warning(
            "Data e fillimit duhet te jete me perpara ne kohe se data e mbarimit"
        )
    else:
        try:
            df_renamed["Data"] = pd.to_datetime(df_renamed["Data"])
            filtered_dff = df_renamed[
                (df_renamed["Data"].dt.date >= data1)
                & (df_renamed["Data"].dt.date <= data2)
                ]
            filtered_dff["date_only"] = filtered_dff["Data"].dt.date
            st.dataframe(
                filtered_dff,
                column_order=[
                    "date_only",
                    "8",
                    "Produkti",
                    "5",
                    "6",
                    "Statusi",
                    "Cmim_shitje",
                    "3",
                    "Cmim_blerje",
                ],
                column_config={
                    "date_only": st.column_config.DateColumn("Date"),
                    "8": st.column_config.TextColumn("Klienti"),
                    "5": st.column_config.TextColumn("Description"),
                    "6": st.column_config.TextColumn("Magazinim"),
                    "7": st.column_config.TextColumn("Order Status"),
                    "Produkti": st.column_config.TextColumn("Artikulli"),
                    "Porositesi": st.column_config.TextColumn("Klienti"),
                    "Cmim_shitje": st.column_config.NumberColumn(
                        "Cmim Shitje", format="ALL %.2f"
                    ),
                    "Cmim_blerje": st.column_config.NumberColumn(
                        "Cmim Blerje", format="ALL %.2f"
                    ),
                    "3": st.column_config.NumberColumn("Cmim Pound", format="£ %.2f"),
                },
                use_container_width=True,
            )  # Display the DataFrame inside the expander
        except:
            st.error("Databaze eshte bosh. Ju lutem shtoni artikuj")

if not df.empty:
    st.markdown("## 📈 Statistika dhe Raporte")

    # Define options
    options = ["Raport Mujor Profit", "Raport Ditor Profit", "Raport Sipas Produktit"]

    # Add a placeholder option
    options_with_placeholder = ["Zgjidhni nje raport..."] + options

    report_type = st.selectbox("Zgjidhni llojin e raportit: ", options_with_placeholder)
    df_likujduar = df_renamed[df_renamed["Statusi"] == "Likujduar"]

    # filtered_df = df[df['City'] == 'Chicago']

    # Group by 'Category' and calculate sum of 'Value'
    grouped_df = (
        df_likujduar.groupby("Data")
        .agg({"Cmim_shitje": "sum", "Cmim_blerje": "sum"})
        .reset_index()
    )

    grouped_df.columns = ["Dita", "Xhiro (ALL)", "Blerje (ALL)"]
    grouped_df["Difference"] = grouped_df["Xhiro (ALL)"] - grouped_df["Blerje (ALL)"]

    if report_type == "Raport Ditor Profit":
        st.subheader("\nRaport Ditor Profit")
        st.data_editor(
            grouped_df, use_container_width=True, hide_index=True, disabled=True
        )
        st.subheader("\nGrafiku Ditor Profit")
        fig = go.Figure()
        grouped_df["Dita"] = grouped_df["Dita"].astype(str)

        for column in grouped_df.columns[
                      1:
                      ]:  # Skip the first column (Month) for x-values
            fig.add_trace(
                go.Scatter(
                    x=grouped_df["Dita"],  # x-values (months)
                    y=grouped_df[column],  # y-values
                    mode="lines+markers",
                    name=column,
                )
            )

        # Update layout for the chart
        fig.update_layout(
            xaxis_title="Dita",
            yaxis_title="Vlerat",
            xaxis=dict(
                tickformat="%d %b %Y ",  # Format: 'Jan 2024'
                tickvals=grouped_df["Dita"],  # Ensure all months are displayed
            ),
            template="plotly_white",
        )

        # Display the plotly chart in Streamlit
        st.plotly_chart(fig)

        # print(grouped_df.shape)
        df_dropped = grouped_df.drop("Blerje (ALL)", axis=1)
        df_dropped.set_index("Dita", inplace=True)

        # st.line_chart(df_dropped)

    elif report_type == "Raport Sipas Produktit":
        a1, a2 = st.columns(2)
        with a1:
            st.title("")
            data_e_pare = st.date_input("Zgjidhni daten e fillimit: ", key="d1")
        with a2:
            st.title("")
            data_e_dyte = st.date_input("Zgjidhni daten e mbarimit: ", key="d2")

        if data_e_pare > data_e_dyte:
            st.warning(
                "Data e fillimit duhet te jete me perpara ne kohe se data e mbarimit"
            )
        else:

            raport_ditor_produkt = (
                df_renamed.groupby(["Data", "Produkti"])
                .size()
                .reset_index(name="Count")
            )
            # st.dataframe(raport_ditor_produkt,
            #              use_container_width=True,
            #              hide_index=True)

            raport_ditor_produkt["Data"] = pd.to_datetime(raport_ditor_produkt["Data"])
            # raport_ditor_produkt

            filtered_df_by_timerange = raport_ditor_produkt[
                (raport_ditor_produkt["Data"].dt.date >= data_e_pare)
                & (raport_ditor_produkt["Data"].dt.date <= data_e_dyte)
                ]

            filtered_df_by_timerange = filtered_df_by_timerange.groupby("Produkti")[
                "Count"
            ].sum()

            filtered_df_by_timerange = filtered_df_by_timerange.reset_index()
            with a1:

                st.subheader("Tabela Permbledhese sipas Produktit")
                st.subheader("")
                st.dataframe(
                    filtered_df_by_timerange, use_container_width=True, hide_index=True
                )

            if not filtered_df_by_timerange.empty:
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=filtered_df_by_timerange["Produkti"],
                            values=filtered_df_by_timerange["Count"],
                            hole=0.3,  # Creates a donut chart; set to 0 for a regular pie chart
                            textinfo="label+value",  # Display label and percentage on the pie chart
                            insidetextorientation="radial",  # Ensures text is displayed radially inside the pie
                        )
                    ]
                )

                # Update layout
                fig.update_layout(
                    annotations=[
                        dict(text="Chart", x=0.5, y=0.5, font_size=25, showarrow=False)
                    ]
                )

                # Display the pie chart in Streamlit
                with a2:
                    st.subheader("Grafiku Permbledhes sipas Produktit")
                    st.plotly_chart(fig)
            else:
                st.warning(
                    "Nuk ka te dhena shitje per daten e zgjedhur. Provoni nje date tjeter!"
                )

    elif report_type == "Raport Mujor Profit":
        grouped_df["Dita"] = pd.to_datetime(grouped_df["Dita"])
        grouped_df["YearMonth"] = grouped_df["Dita"].dt.to_period("M")

        # Group by 'YearMonth' and aggregate
        grouped_df = (
            grouped_df.groupby("YearMonth")
            .agg(
                {
                    "Xhiro (ALL)": "sum",
                    "Blerje (ALL)": "sum",
                }
            )
            .reset_index()
        )

        grouped_df["Difference"] = (
                grouped_df["Xhiro (ALL)"] - grouped_df["Blerje (ALL)"]
        )
        grouped_df.rename(
            columns={
                "YearMonth": "Muaji",
            },
            inplace=True,
        )

        st.subheader("\nRaport Mujor Profit")
        st.data_editor(
            grouped_df, use_container_width=True, hide_index=True, disabled=True
        )
        st.subheader("Grafiku Permbledhes Mujor Profit")
        # df_dropped = grouped_df.drop('Blerje (ALL)', axis=1)
        # df_dropped.set_index('Muaji', inplace=True)
        # st.line_chart(df_dropped)

        fig = go.Figure()
        grouped_df["Muaji"] = grouped_df["Muaji"].astype(str)

        for column in grouped_df.columns[
                      1:
                      ]:  # Skip the first column (Month) for x-values
            fig.add_trace(
                go.Scatter(
                    x=grouped_df["Muaji"],  # x-values (months)
                    y=grouped_df[column],  # y-values
                    mode="lines+markers",
                    name=column,
                )
            )

        # Update layout for the chart
        fig.update_layout(
            xaxis_title="Muaji",
            yaxis_title="Vlerat",
            xaxis=dict(
                tickformat="%b %Y",  # Format: 'Jan 2024'
                tickvals=grouped_df["Muaji"],  # Ensure all months are displayed
            ),
            template="plotly_dark",
        )

        st.plotly_chart(fig)

#
# nr_lik_prod = get_number_of_tickets_with_status(status="Likujduar")
# nr_pending_prods = get_number_of_tickets_with_status(status="Pending")
#
# st.error(f"Numri i produkteve me status PENDING eshte: {nr_pending_prods}")
# st.success(f"Numri i produkteve me status  LIKUJDUAR eshte: {nr_lik_prod}")
