import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="NY Airbnb Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
data = pd.read_csv('data/AB_NYC_2019.csv')

# Sidebar
with st.sidebar:
    st.title('🏂 NY Airbnb Dashboard')
    
    room_type_list = list(data.room_type.unique())
    selected_room_type = st.multiselect('Select a room type', room_type_list, default=room_type_list)
    
    
    selected_price_range = st.slider('Select a price range', min_value=0, max_value=10000, value=(0, 10000), step=5)
    low_range, high_range = selected_price_range
    

        
    
    neighbourhood_group_list = list(data.neighbourhood_group.unique())
    selected_neighbourhood_group = st.multiselect('Select a neighbourhood group', neighbourhood_group_list, default=neighbourhood_group_list)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']


# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.scatter_mapbox(input_df, lat='latitude', lon='longitude', color=input_column, hover_name='name',
                                   hover_data={'neighbourhood':True, 'room_type':True, 'price':True, 'host_name':True, 'neighbourhood_group':False, 
                                               'minimum_nights':True, 'number_of_reviews':True, 'last_review':False, 'reviews_per_month':False, 'calculated_host_listings_count':False, 
                                               'availability_365':False, 'latitude':False, 'longitude':False},
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

#######################
# Dashboard Main Panel
# Dashboard Main Panel

st.markdown("<h1 style='text-align: center;'>NY Airbnb Dashboard</h1>", unsafe_allow_html=True)
data_filtered = data[(data.room_type.isin(selected_room_type)) & 
                         (data.neighbourhood_group.isin(selected_neighbourhood_group)) &
                         (data.price >= low_range) & (data.price <= high_range)]

with st.container():
        # Add 3 cards (KPi) above the map
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('#### Total Listings')
        total_listings = len(data_filtered)
        st.markdown(f"<h1 style='text-align: center;'>{total_listings}</h1>", unsafe_allow_html=True)

    with col2:
        st.markdown('#### Average Price')
        average_price = data_filtered['price'].mean()
        st.markdown(f"<h1 style='text-align: center;'>${average_price:.2f}</h1>", unsafe_allow_html=True)

    with col3:
        st.markdown('#### Maximum Price')
        max_price = data_filtered['price'].max()
        st.markdown(f"<h1 style='text-align: center;'>${max_price}</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('#### Choropleth Map')
    choropleth = make_choropleth(data_filtered, 'price', 'neighbourhood_group', 'cividis')
    choropleth.update_layout(autosize=False, width=800, height=600)
    st.plotly_chart(choropleth, use_container_width=True)

# Create a new row for the charts
col3, col4 = st.columns(2)

with col3:
    st.markdown('#### Price Distribution')
    fig = px.histogram(data_filtered, x="price", color='neighbourhood_group', nbins=30)
    st.plotly_chart(fig)

with col4:
    # Add your second chart here
    st.markdown('#### Room Type Distribution')
    room_type_counts = data_filtered.groupby(['neighbourhood_group', 'room_type']).size().reset_index(name='count')
    fig2 = px.pie(room_type_counts, values='count', names='room_type')
    st.plotly_chart(fig2)
    
   
    
    
    