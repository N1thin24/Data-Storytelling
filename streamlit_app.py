import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

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

    # Add a radio button for page selection
    page = st.sidebar.radio("Go to", ['Dashboard', 'Comparison'])

    

# Display the selected page
if page == 'Dashboard':
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
    data_sorted = data_filtered.sort_values(by='price')
    # Select the entry with the lowest price for each neighbourhood


    best_deals = data_sorted.loc[data_sorted.groupby('neighbourhood_group')['price'].idxmin()].reset_index(drop=True) 
    best_deals['color'] = 'yellow'
    best_deals['marker'] = 'star'

    with st.container():
            # Add 3 cards (KPi) above the map
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<h4 style='text-align: center;'>Total Listings</h4>", unsafe_allow_html=True)
            total_listings = len(data_filtered)
            st.markdown(f"<h1 style='text-align: center; border:4px solid white; padding:10px;'>{total_listings}</h1>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h4 style='text-align: center;'>Average Price</h4>", unsafe_allow_html=True)
            average_price = data_filtered['price'].mean()
            st.markdown(f"<h1 style='text-align: center; border:4px solid white; padding:10px;'>{average_price:.2f} $</h1>", unsafe_allow_html=True)

        with col3:
            st.markdown("<h4 style='text-align: center;'>Maximum Price</h4>", unsafe_allow_html=True)
            max_price = data_filtered['price'].max()
            st.markdown(f"<h1 style='text-align: center; border:4px solid white; padding:10px;'>{max_price} $</h1>", unsafe_allow_html=True)

    with st.container():

        col1, col2 = st.columns([4,2])
        with col1:
            # Create the choropleth map
            choropleth = make_choropleth(data_filtered, 'price', 'neighbourhood_group', 'cividis')

            # Update the layout to use mapbox and set the style to "carto-positron"
            choropleth.update_layout(
                mapbox_style="carto-darkmatter",
                mapbox=dict(
                    bearing=0,
                    center=dict(
                        lat=data_filtered['latitude'].mean(), 
                        lon=data_filtered['longitude'].mean()
                    ),
                    pitch=0,
                    zoom=10
                ),
                autosize=False, 
                width=800, 
                height=600,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    font=dict(
                        color="white"
                    )
                ), 
                margin=dict(t=50)
            )

            # Display the map
            st.plotly_chart(choropleth, use_container_width=True)
        with col2:     

            # Create a radar chart
            fig = px.line_polar(best_deals, r='price', theta='neighbourhood_group', line_close=True)
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        tickfont=dict(
                            color='black'
                        ),
                    ),
                    angularaxis=dict(
                        tickfont=dict(
                            color='white'
                        ),
                    )
                )
            )
            fig.update_traces(line=dict(width=4))

            st.plotly_chart(fig)
            

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

elif page == 'Comparison':

    data_filtered = data[(data.room_type.isin(selected_room_type)) & 
                            (data.neighbourhood_group.isin(selected_neighbourhood_group)) &
                            (data.price >= low_range) & (data.price <= high_range)]
    data_sorted = data_filtered.sort_values(by='price')
    # Select the entry with the lowest price for each neighbourhood


    best_deals = data_sorted.loc[data_sorted.groupby('neighbourhood_group')['price'].idxmin()].reset_index(drop=True) 
    best_deals['color'] = 'yellow'
    best_deals['marker'] = 'star'
    import folium
    from streamlit_folium import folium_static

    # Create the map
    m = folium.Map(location=[data_filtered['latitude'].mean(), data_filtered['longitude'].mean()], zoom_start=10)

    # Add points to the map
    for idx, row in data_filtered.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=row['neighbourhood_group']).add_to(m)

    # Display the map in Streamlit
    folium_static(m)
            
    
        
        
        