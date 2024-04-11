#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
data = pd.read_csv('data/AB_NYC_2019.csv')


#######################
# Sidebar
with st.sidebar:
    st.title('🏂 NY Airbnb Dashboard')
    
    room_type_list = list(data.room_type.unique())
    selected_room_type = st.selectbox('Select a room type', room_type_list)
    
    price_range_list = ['< $50', '$50 - $100', '$100 - $150', '$150 - $200', '> $200']
    selected_price_range = st.selectbox('Select a price range', price_range_list)
    selected_price_column = 'price'
    if selected_price_range == '< $50':
        data_filtered = data[data[selected_price_column] < 50]
    elif selected_price_range == '$50 - $100':
        data_filtered = data[(data[selected_price_column] >= 50) & (data[selected_price_column] <= 100)]
    elif selected_price_range == '$100 - $150':
        data_filtered = data[(data[selected_price_column] > 100) & (data[selected_price_column] <= 150)]
    elif selected_price_range == '$150 - $200':
        data_filtered = data[(data[selected_price_column] > 150) & (data[selected_price_column] <= 200)]
    elif selected_price_range == '> $200':
        data_filtered = data[data[selected_price_column] > 200]
    else:
        data_filtered = data
    
    neighbourhood_group_list = list(data.neighbourhood_group.unique())
    selected_neighbourhood_group = st.selectbox('Select a neighbourhood group', neighbourhood_group_list)


#######################
# Plots

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.scatter_mapbox(input_df, lat='latitude', lon='longitude', color=input_column, hover_name='name',
                                   hover_data=['neighbourhood', 'room_type', 'price', 'host_name'],
                                   color_continuous_scale=input_color_theme,
                                   zoom=10,
                                   mapbox_style='carto-positron')
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    return choropleth