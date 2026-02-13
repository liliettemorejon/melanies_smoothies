import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie Order:")

# Pull fruit table (NOW includes SEARCH_ON)
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas so we can use LOC
pd_df = my_dataframe.to_pandas()

# Multiselect uses FRUIT_NAME (GUI label)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# If user selects fruits
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build ingredient string for order insert
        ingredients_string += fruit_chosen + " "

        # 🔎 Get SEARCH_ON value from dataframe
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Show search mapping (lab debug line)
        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on,
            "."
        )

        # Section header
        st.subheader(fruit_chosen + " Nutrition Information")

        # API call using SEARCH_ON value
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        # Display JSON as dataframe
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Insert order statement
    my_insert_stmt = f"""
        insert into smoothies.public.orders
        (ingredients, name_on_order)
        values
        ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅"
        )
