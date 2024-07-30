import streamlit as st

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout="wide",
    page_title='Duda Shop',
    page_icon=':shopping_bags:',  # This is an emoji shortcode. Could be a URL too.
)

btn1 = st.button("Inventory Tracker")


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
            <img src="logo.JPG" alt="Logo" style="max-width: 200px; height: auto;">
            <h1>Welcome to Duda Shop</h1>
            <p>We are thrilled to have you here. Explore our offerings and get to know more about us.</p>
        </div>
    """, unsafe_allow_html=True)

    if btn1:
        st.switch_page("pages/Inventory_Page.py")


if __name__ == "__main__":
    main()