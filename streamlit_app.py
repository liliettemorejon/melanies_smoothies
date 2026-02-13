import streamlit as st
from snowflake.snowpark.functions import col
import requests 

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Title / Instructions

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie Order:")

# -----------------------------
# Load Fruit Table
# Must include SEARCH_ON column
# -----------------------------
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).to_pandas()

# -----------------------------
# Create Lookup Dictionary
# GUI name → API search value
# -----------------------------
fruit_lookup = dict(
    zip(
        my_dataframe["FRUIT_NAME"],
        my_dataframe["SEARCH_ON"]
    )
)

# -----------------------------
# Multiselect
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"],
    max_selections=5
)

# -----------------------------
# If Fruits Selected
# -----------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build order string
        ingredients_string += fruit_chosen + " "

        # Lookup API search value
        search_value = fruit_lookup[fruit_chosen]

        # Section header per fruit
        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        # API Call
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_value}"
        )

        # Display JSON → Dataframe
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # -----------------------------
    # Insert Order SQL
    # -----------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES
        ('{ingredients_string}', '{name_on_order}')
    """

    # -----------------------------
    # Submit Button
    # -----------------------------
    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered, "
            + name_on_order
            + "!",
            icon="✅"
        )
