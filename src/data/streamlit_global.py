import json
import pandas as pd
import pydeck as pdk
import streamlit as st
from geopy.geocoders import Nominatim
import geopandas as gpd
from shapely.geometry import Point
import random

# Streamlit app title
st.title("Cluster Map from JSON Data")

# # Upload the JSON file
@st.cache_data
def load_data():
    data = pd.read_json('db-data\predicted_data.json')
    return data
# Load data
df2 = load_data()
df = df2.head(40)

st.title("Country-Based Clustering Map")

# Sample data
# df = pd.DataFrame({
#     'affiliation': ['United States', 'United States', 'Australia', 'Australia', 'Australia'],
#     "subject_code": ['2707', '2707', '2707', '2707', '2707'],
#     'predict_gender': ['m', 'f', 'f', 'f', 'm'] 
# })
base_color_f = [255, 0, 0]  # Red for 'f'
base_color_m = [0, 0, 255]  # Blue for 'm'

#count the gender and subject_code
map_gender = df.groupby('affiliation')['predict_gender'].value_counts().unstack(fill_value=0)
map_subject = df.groupby('affiliation')['subject_code'].value_counts().unstack(fill_value=0)

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapi")

# Function to geocode country names
def geocode_country(country):
    location = geolocator.geocode(country)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Add latitude and longitude to the dfset
with st.spinner("Geocoding countries..."):
    df[['latitude', 'longitude']] = df['affiliation'].apply(lambda x: geocode_country(x)).apply(pd.Series)

# Drop rows where geocoding failed
df = df.dropna(subset=['latitude', 'longitude'])

# Define colors for each gender
def calculate_color(f_count, m_count):
    total = f_count + m_count
    if total == 0:
        return [128, 128, 128]  # Neutral gray for no data
    f_ratio = f_count / total
    m_ratio = m_count / total
    blended_color = [
        int(f_ratio * base_color_f[0] + m_ratio * base_color_m[0]),
        int(f_ratio * base_color_f[1] + m_ratio * base_color_m[1]),
        int(f_ratio * base_color_f[2] + m_ratio * base_color_m[2]),
    ]
    return blended_color

map_gender['color'] = map_gender.apply(
    lambda row: calculate_color(row.get('f', 0), row.get('m', 0)), axis=1
)


# Define radius
def calculate_radius(topic_count):
    base_radius = 700000  # Minimum radius
    scale_factor = 10000   # Adjust scale factor based on your needs
    return base_radius + topic_count * scale_factor
map_subject['total'] = map_subject.sum(axis=1)  # Total topic count per affiliation
map_subject['radius'] = map_subject['total'].apply(calculate_radius)

df = df.merge(map_gender['color'], left_on='affiliation', right_index=True)
df = df.merge(map_subject['radius'], left_on='affiliation', right_index=True)
# Define the ScatterplotLayer
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_fill_color='color',
    get_radius='radius',
    opacity=0.1,
    pickable=True
)

# Define the view
view_state = pdk.ViewState(
    latitude=0,
    longitude=0,
    zoom=1,
    pitch=0
)

# Create the Deck
deck = pdk.Deck(
    layers=[scatterplot_layer],
    initial_view_state=view_state,
    tooltip={"text": "Country: {country}\nGroup: {group}"}
)

# Display the map in Streamlit
st.pydeck_chart(deck)

# Optionally, display the data table
if st.checkbox("Show Data Table"):
    st.write(df)