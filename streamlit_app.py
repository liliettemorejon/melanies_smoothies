import streamlit as st
from snowflake.snowpark.functions import col
import requests

# -----------------------------------
# Snowflake Connection
# -----------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------------
# Title + Intro
# -----------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------------
# Name Input
# -----------------------------------
name_on_order = st.text_input("Name on Smoothie Order:")

# -----------------------------------
# Pull Fruit Options Table
# Include SEARCH_ON column
# -----------------------------------
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON")) \
    .to_pandas()

# -----------------------------------
# Multiselect (GUI uses FRUIT_NAME)
# -----------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"],
    max_selections=5
)

# -----------------------------------
# If fruits selected
# -----------------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build ingredient string for insert
        ingredients_string += fruit_chosen + " "

        # -----------------------------------
        # Lookup SEARCH_ON value
        # -----------------------------------
        search_value = my_dataframe.loc[
            my_dataframe["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].values[0]

        # -----------------------------------
        # Display section header
        # -----------------------------------
        st.subheader(fruit_chosen + " Nutrition Information")

        # -----------------------------------
        # Call SmoothieFroot API
        # -----------------------------------
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_value}"
        )

        # -----------------------------------
        # Display nutrition dataframe
        # -----------------------------------
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # -----------------------------------
    # Build Insert Statement
    # -----------------------------------
    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (ingredients, name_on_order)
        VALUES
        ('{ingredients_string}', '{name_on_order}')
    """

    # -----------------------------------
    # Submit Button
    # -----------------------------------
    time_to_insert = st.button("Submit Order")

    # -----------------------------------
    # Insert if clicked
    # -----------------------------------
    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅"
        )
