import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import random
# from webcolors import hex_to_rgb
from sklearn.cluster import MiniBatchKMeans

st.set_page_config(page_title="Data Visualization", page_icon=":bar_chart:", layout="wide")

base_color_f = [255, 117, 255]  # Red for 'f'
base_color_m = [0, 117, 255]  # Blue for 'm'
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

st.title('Map')

@st.cache_data
def load_data():
    df = pd.read_json(r"src\data\db-data\predicted_data_with_country_lat_lon.json")
    # df['subject_code'] = df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    new_df = df.groupby(['affiliation', 'longitude', 'latitude'])['predict_gender'].value_counts().unstack(fill_value=0)
    # st.write(new_df)
    new_df['weight'] = new_df['m'] + new_df['f']
    new_df['radius'] = new_df['weight'] * 100

    new_df['color'] = new_df.apply(
        lambda row: calculate_color(row.get('f', 0), row.get('m', 0)), axis=1
    )
    
    new_df = new_df.reset_index()

    return new_df

df = load_data()
num_rows = df.shape[0]



# longitudes = [random.uniform(-180, 180) for _ in range(num_rows)]
# latitudes = [random.uniform(-90, 90) for _ in range(num_rows)]

# df['longitude'] = longitudes
# df['latitude'] = latitudes
st.write(df['color'])

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position="[longitude, latitude]",
    # get_color="color",
    get_color='color', #Red for clusters
    get_radius='radius',
    # radius_min_pixels=1,
    radius_max_pixels=50,
    opacity=0.6,
    pickable=True
)
view_state = pdk.ViewState(
    latitude=15.87,
    longitude=100.9925,
    zoom=10
)
deck = pdk.Deck(layers=[scatter_layer], initial_view_state=view_state, tooltip={"text": "Latitude: {latitude}\nLongitude: {longitude}\nAffiliation: {affiliation}\nPopulation: {weight}"})
st.pydeck_chart(deck)