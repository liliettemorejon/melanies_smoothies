import streamlit as st
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# NEW — Name input box
name_on_order = st.text_input('Name on Smoothie Order:')

# Pull fruit table into dataframe
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").to_pandas()


ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '


    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""


    #st.write(my_insert_stmt)
    #st.stop()


    # Submit button
    time_to_insert = st.button('Submit Order')


    # SECOND IF → dependent on button click
    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered, '+ name_on_order +'!' , icon="✅")

# New section to display smoothiefruit nutrition information
import requests

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# New section to display smoothiefruit nutrition information
import requests

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# st.text(smoothiefroot_response.json())

sf_df = st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)












