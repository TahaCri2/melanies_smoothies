import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Query the fruit options from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()


# Multiselect for choosing ingredients
ingredients_LIST = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

if ingredients_LIST:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_LIST:
        ingredients_string += fruit_chosen + ' '
        
        # Get the 'SEARCH_ON' value for the chosen fruit
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        # Display the nutrition information subheader
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Make the API request using the 'search_on' value
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        if fruityvice_response.status_code == 200:
            st.json(fruityvice_response.json())

    # SQL insert statement for the chosen ingredients
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients)
            VALUES ('{ingredients_string.strip()}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
