import streamlit as st

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout="wide",
    page_title='Duda Shop',
    page_icon=':shopping_bags:',  # This is an emoji shortcode. Could be a URL too.
)

c1, c2, c3 = st.columns(3)

with c1:
    btn1 = st.button("Home", use_container_width=True, key="H1")
with c2:
    btn2 = st.button("Inventary Tracker", use_container_width=True, key="I1")
with c3:
    btn3 = st.button("Produktet", use_container_width=True, key="P1")
    st.write("")
    st.image("vector-logo.png", width=300)
    st.write("")

# Define a function to show different pages based on the selection
def main():

    # Define custom CSS for background image
    # background_image_url = "/Users/enidvyshka/PycharmProjects/Inventory_App/logo.jpg"
    background_image_url = "https://images.pexels.com/photos/1648374/pexels-photo-1648374.jpeg?auto=compress&cs=tinysrgb&w=1200"  # Replace with your image file or URL
    background_css = f"""
        <style>
            .stApp {{
                background-image: url("{background_image_url}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                min-height: 100vh; /* Ensures background covers the whole viewport height */
            }}
            .container {{
                background-color: rgba(255, 255, 255, 0.8); /* Slightly transparent white background for content */
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
        </style>
    """

    # Render the CSS to set the background image
    st.markdown(background_css, unsafe_allow_html=True)


    # Content of the landing page
    st.markdown("""
        <div class="container">
            <h1>Welcome to Duda Shop</h1>
            <p>We are thrilled to have you here. Explore our offerings and get to know more about us.</p>
        </div>
    """, unsafe_allow_html=True)


    if btn2:
        st.switch_page("pages/Inventory_Page.py")
    if btn3:
        st.switch_page("pages/Products.py")
    if btn1:
        st.switch_page("main.py")


if __name__ == "__main__":
    main()
