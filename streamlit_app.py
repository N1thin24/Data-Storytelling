import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import folium
from streamlit_folium import folium_static
import streamlit_folium as st_folium
import folium
from folium.plugins import MarkerCluster



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


centers = pd.read_csv('data/center_coordinates.csv')

#After new csv is created:
data = pd.read_csv('data/AB_NYC_2019_with_scores.csv')
# #For First TIME: 
# data = pd.read_csv('data/AB_NYC_2019.csv')
# # drop rows where price is 0
# data = data[data.price > 0]

# #for each data point, calculate the distance to each center based on latitude and longitude, assuming that neighbourhood_groups are same
# data['distance_to_center'] = data.apply(lambda row: centers[centers['neighbourhood_group'] == row['neighbourhood_group']].apply(lambda center: ((row['latitude'] - center['latitude'])**2 + (row['longitude'] - center['longitude'])**2)**0.5, axis=1).values[0], axis=1)

# # if distance_to_center is above the 10th percentile, set it to 0, else set it to 1
# data['close_to_center'] = data['distance_to_center'].apply(lambda x: 0 if x > data['distance_to_center'].quantile(0.1) else 1)


# data['normalized_price'] = data.groupby('neighbourhood_group')['price'].transform(lambda x: (x - x.mean()) / x.std())
# data['normalized_reviews'] = data.groupby('neighbourhood_group')['number_of_reviews'].transform(lambda x: (x - x.mean()) / x.std())
# data['best_deal_score'] = data['close_to_center']*data['number_of_reviews'] / (2*data['normalized_price'])




# #data to csv
# data.to_csv('data/AB_NYC_2019_with_scores.csv', index=False)


# Sidebar
with st.sidebar:
    st.title('🏂 NY Airbnb Dashboard')

    #store the input in a variable
    search_input = st.text_input('Search for keywords')

    selected_price_range = st.slider('Select a price range', min_value=0, max_value=10000, value=(0, 10000), step=5)
    low_range, high_range = selected_price_range
    
    room_type_list = list(data.room_type.unique())
    selected_room_type = st.multiselect('Select a room type', room_type_list, default=room_type_list)
    
    
    
    
    
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


        map_deals_df = input_df.loc[map_deals_idx]
        hover_text = map_deals_df.apply(lambda row: f"RECOMMENDED LISTING!<br>{row['name']}<br>Neighbourhood: {row['neighbourhood']}<br>Room Type: {row['room_type']}<br>Price: ${row['price']}<br>Host: {row['host_name']}<br>Min Nights: {row['minimum_nights']}<br>Reviews: {row['number_of_reviews']}", axis=1)


        choropleth.add_scattermapbox(
            lat=map_deals_df['latitude'], 
            lon=map_deals_df['longitude'],
            mode='markers',
            marker=dict(
                size=12,  # Adjust size to make these points stand out.
                color='gold',  # Adjust color to highlight these points.
                opacity=0.8,  # Optional: Adjust opacity to make these points semi-transparent.
            ),
            text=hover_text,
            hoverinfo='text',
            name='Best Deals'  # Optional: Provide a name for the legend.
        )

        center_text = centers.apply(lambda row: f"Touristic Center<br>{row['Attraction']}",axis=1)
        choropleth.add_scattermapbox(
            lat=centers['latitude'], 
            lon=centers['longitude'],
            mode='markers',
            marker=dict(
                size=20,  # Adjust size to make these points stand out.
                color='white',  # Adjust color to highlight these points.
                opacity=0.99,  # Optional: Adjust opacity to make these points semi-transparent.
            ),
            text=center_text,
            hoverinfo='text',
            name='Neighborhood Centers'  # Optional: Provide a name for the legend.
        )
        
        
        return choropleth

    #######################
    # Dashboard Main Panel
    # Dashboard Main Panel

    st.markdown("<h1 style='text-align: center;'>NY Airbnb Dashboard</h1>", unsafe_allow_html=True)
    data_filtered = data[(data.room_type.isin(selected_room_type)) & 
                            (data.neighbourhood_group.isin(selected_neighbourhood_group)) &
                            (data.name.str.contains(search_input, case=False, na=False)) &
                            (data.price >= low_range) & (data.price <= high_range)]
    data_sorted = data_filtered.sort_values(by='price')

    # Select the entry with the lowest price for each neighbourhood
    map_deals_indices = data_sorted.groupby('neighbourhood_group')['best_deal_score'].idxmax()
    map_deals_idx = map_deals_indices.tolist()

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
            fig = px.line_polar(best_deals, r='price', theta='neighbourhood_group', line_close=True, hover_data=['room_type'])
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
        #points = plotly_events(fig, click_event=True, hover_event=False)
        #print(points)
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