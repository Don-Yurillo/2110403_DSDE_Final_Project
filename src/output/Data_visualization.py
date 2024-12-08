#  ? note: you should run collection_loader.ipynb before executing this file
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from geopy.geocoders import Nominatim
import geopandas as gpd
import pydeck as pdk
from shapely.geometry import Point
import random
import altair as alt

subject_map = {
    "1000": "Multidisciplinary",
    "1100": "Agricultural and Biological Sciences",
    "1200": "Arts and Humanities",
    "1300": "Biochemistry, Genetics and Molecular Biology",
    "1400": "Business, Management and Accounting",
    "1500": "Chemical Engineering",
    "1600": "Chemistry",
    "1700": "Computer Science",
    "1800": "Decision Sciences",
    "1900": "Earth and Planetary Sciences",
    "2000": "Economics, Econometrics and Finance",
    "2100": "Energy",
    "2200": "Engineering",
    "2300": "Environmental Science",
    "2400": "Immunology and Microbiology",
    "2500": "Materials Science",
    "2600": "Mathematics",
    "2700": "Medicine",
    "2800": "Neuroscience",
    "2900": "Nursing",
    "3000": "Pharmacology, Toxicology and Pharmaceutics",
    "3100": "Physics and Astronomy",
    "3200": "Psychology",
    "3300": "Social Sciences",
    "3400": "Veterinary",
    "3500": "Dentistry",
    "3600": "Health Professions"
}

def loadJsonData(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except UnicodeDecodeError:
        try:
            with open(filename, 'r', encoding='latin-1') as file:
                data = json.load(file)
        except UnicodeDecodeError:
            st.error("Error: Could not decode the JSON file. Please check the file encoding.")
            st.stop()
    except FileNotFoundError:
        st.error("Error: JSON file not found.")
        st.stop()
        
    return data

# Data Loading
predicted_data = loadJsonData(r'src\data\db-data\predicted_data.json')


# This will change to be topic when data is ready
st.title("Gender Distribution by Topic")

df = pd.DataFrame(predicted_data)
allYearGenderCount = df.groupby('affiliation')['predict_gender'].value_counts()

# st.write(total_gender_count)
# st.write(df)

# Data Cleaning (Important!):
df.dropna(subset=['predict_gender', 'affiliation'], inplace=True)  # Remove rows with missing gender or affiliation
df['predict_gender'] = df['predict_gender'].str.lower().str.strip()  # Standardize gender (e.g., "M" and "m" become "m")
df['affiliation'] = df['affiliation'].str.strip()  # Clean up affiliation strings
df['predict_gender'] = df['predict_gender'].replace(['m', 'f'],['Male', 'Female'])
# st.write(df.groupby('affiliation')['gender'].value_counts())

if not df.empty: # Check for empty DataFrame after cleaning
    subject_df = pd.DataFrame(df, columns=["subject_code"])
    subject_df['subject_code'] = subject_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    # subject_df['subject_code'] = subject_df['subject_code'].apply(lambda x: subject_map[x])
    # subject_list = subject_df['subject_code'].unique()
    # st.write(affiliations)
    selected_subject_sidebar = st.sidebar.selectbox("Select Topic", subject_df['subject_code'].apply(lambda x: subject_map[x]).unique())
    
    st.write(selected_subject_sidebar)
    
    selected_subject = df[subject_df['subject_code'].apply(lambda x: subject_map[x]) == selected_subject_sidebar]
    selected_subject.loc[len(selected_subject)] = [np.nan, np.nan, np.nan, np.nan, np.nan, "All", np.nan]
    selected_subject['year'] = selected_subject['year'].astype(str)
    selected_subject = selected_subject.sort_values(by='year', ascending=False)
    # st.write(selected_subject[selected_subject['name'].isna()])
    col1 , col2 = st.columns(2)
    with col1:
        selected_year1 = st.selectbox("",selected_subject['year'].unique(), index=0)
    with col2:
        selected_year2 = st.selectbox("",selected_subject['year'].unique(), index=1)
    
    filtered_subject_df = selected_subject
    
    if not filtered_subject_df.empty: # Check if the filtered DataFrame is empty
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=[f"Gender Distribution in {selected_year1}", f"Gender Distribution in {selected_year2}"])
        
        if selected_year1 == "All":
            filtered_year_1 = filtered_subject_df
        else:
            filtered_year_1 = filtered_subject_df[filtered_subject_df['year'] == selected_year1]
        filtered_year_1 = filtered_year_1.dropna(subset=['name'])
        # st.write(filtered_year_1[filtered_year_1['name'].isna()])
        
        gender_counts_year1 = filtered_year_1['predict_gender'].value_counts().reset_index()
        gender_counts_year1.columns = ['gender', 'count']
        total_gender_counts_year1 = gender_counts_year1['count'].sum()
        gender_counts_year1['percentage'] = gender_counts_year1['count'].apply(lambda x: round((x / total_gender_counts_year1) * 100, 2))
        # Pie Chart
        fig.add_trace(
            go.Pie(labels=gender_counts_year1['gender'],
                   values=gender_counts_year1['count'], # Count occurrences
                   name="Gender Distribution",
                   marker=dict(colors=px.colors.qualitative.Set1)),
            row=1, col=1
        )
       
        if selected_year2 == "All":
            filtered_year_2 = filtered_subject_df
        else:
            filtered_year_2 = filtered_subject_df[filtered_subject_df['year'] == selected_year2]
        filtered_year_2 = filtered_year_2.dropna(subset=['name'])
        
        gender_counts_year2 = filtered_year_2['predict_gender'].value_counts().reset_index()
        gender_counts_year2.columns = ['gender', 'count']
        total_gender_counts_year2 = gender_counts_year2['count'].sum()
        gender_counts_year2['percentage'] = gender_counts_year2['count'].apply(lambda x: round((x / total_gender_counts_year2) * 100, 2))
        fig.add_trace(
            go.Pie(labels=gender_counts_year2['gender'], 
                   values=gender_counts_year2['count'], # Count occurrences
                   name="Gender Distribution",
                   marker=dict(colors=px.colors.qualitative.Set1)),
            row=1, col=2
        )
        fig.update_layout(title_text=f"Gender Distribution in {selected_subject_sidebar}")
        st.plotly_chart(fig)
        col1 , col2 = st.columns(2)
        with col1:
            st.dataframe(gender_counts_year1, width=300)
        with col2:
            st.dataframe(gender_counts_year2, width=300)
        # fig.update_traces(textinfo='value+label')  # Show both count and label on each slice
        # st.plotly_chart(fig)
    else:
        st.warning("No data found for the selected topic.")
else:
    st.warning("The dataset is empty after cleaning.  Check the data source.")
    
if not df.empty:
    st.title("Line Graph")

    chart_df = pd.DataFrame(df, columns=["year","subject_code", "predict_gender"])
    chart_df['subject_code'] = chart_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    selectBox = st.selectbox("Select Topic", ['All Topics', 'Life Sciences', 'Social Sciences', 'Physical Sciences', 'Health Sciences'], index=0,key='line')
    if selectBox == "All Topics":
        chart_df = chart_df
    if selectBox == "Life Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1000","1300", "2400", "2800", "3000"])]
    if selectBox == "Social Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1200","1400","1800","2000","3200","3300","3300"])]
    if selectBox == "Physical Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1500","1600","1700","1900","2100","2200","2300","2500","2600","3100"])]
    if selectBox == "Health Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["2700" ,"2900" , "3400", "3500", "3600"])]
        
    chart_df = chart_df.groupby(['year', 'predict_gender']).size().reset_index(name='count')
    chart_df.columns = ['year', 'gender', 'count']
    # print(chart_df.head())
    
    fig = px.line(
        chart_df,
        x = 'year',
        y = 'count',
        color='gender',
        title="Gender Distribution Over Years"
    )

    st.plotly_chart(fig)
else:
    st.warning("The dataset is empty after cleaning.  Check the data source.")
    
if not df.empty:
    affiliations = df['affiliation'].unique()
    gender_counts = df.groupby(['affiliation', 'predict_gender']).size().unstack(fill_value=0).reset_index() #unstack converts to wide forma

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=gender_counts['affiliation'],
        y=gender_counts['Female'],
        name='Female',
        marker_color= px.colors.qualitative.Set2[0]
    ))
    fig.add_trace(go.Bar(
        x=gender_counts['affiliation'],
        y=gender_counts['Male'],
        name='Male',
        marker_color= px.colors.qualitative.Set2[1]
    ))

    fig.update_layout(barmode='stack',  # Set barmode to 'stack'
                      xaxis_title='Affiliation',
                      yaxis_title='Number of People',
                      title='Gender Distribution by Affiliation (Stacked Bar Chart)')

    st.plotly_chart(fig)
else:
    st.warning("The dataset is empty after cleaning.  Check the data source.")
    


if not df.empty:
    
    chart_df = pd.DataFrame(df, columns=["subject_code", "predict_gender"])
    chart_df['subject_code'] = chart_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    selectBox = st.selectbox("Select Topic", ['All Topics', 'Life Sciences', 'Social Sciences', 'Physical Sciences', 'Health Sciences'], index=0)
    if selectBox == "All Topics":
        chart_df = chart_df
    if selectBox == "Life Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1000","1300", "2400", "2800", "3000"])]
    if selectBox == "Social Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1200","1400","1800","2000","3200","3300","3300"])]
    if selectBox == "Physical Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["1500","1600","1700","1900","2100","2200","2300","2500","2600","3100"])]
    if selectBox == "Health Sciences": 
        chart_df = chart_df[chart_df['subject_code'].isin(["2700" ,"2900" , "3400", "3500", "3600"])]
    
    chart_df = chart_df.groupby(['subject_code', 'predict_gender']).value_counts().reset_index(name='count')
    chart_df.columns = [selectBox, 'gender', 'count']
    
    total_female = chart_df[chart_df['gender'] == "Female"]['count'].sum()
    total_male = chart_df[chart_df['gender'] == "Male"]['count'].sum()
    total_person = chart_df['count'].sum()
    
    chart_df['normalized_count'] = chart_df.apply(
        lambda row: ((row['count'] / total_female) * 100) if row['gender'] == "Female" else ((row['count'] / total_male) * 100), axis=1
    )
    chart_df[selectBox] = chart_df[selectBox].apply(lambda x: subject_map[x])
    
    checkBox = st.checkbox("Show more data", value=False)
    col1, col2 = st.columns(2)

    if checkBox:
        with col1:
                st.write(chart_df)
        with col2:
            selected_subject = st.selectbox(
                "Select Subject Code to view data",
                options=chart_df[selectBox].unique() 
            )
            filtered_data = chart_df[chart_df[selectBox] == selected_subject][['gender', 'count']]

            # Display the filtered data
            st.write(f"Data for Subject Code {selected_subject}:")
            st.write(filtered_data)
    
    chart = alt.Chart(chart_df).mark_bar().encode(
        x='gender',
        y='normalized_count',
        color='{}:N'.format(selectBox),  # Color by subject_code
        tooltip=['gender', 'count', selectBox]  # Tooltip to show details on hover
        
    ).properties(
        title='Gender Distribution Stacked by Subject Code'
    )
    st.altair_chart(chart, use_container_width=True)
    
else:
    st.warning("The dataset is empty after cleaning.  Check the data source.")


# # Streamlit app title
# st.title("Cluster Map from JSON Data")

# # Upload the JSON file
# use_data = []
# random_strings = ["m", "f"]

# # @st.cache_data
# # def load_data():
# #     data = pd.read_json('paper_data.cu_paper_data_pub.json')
# #     return data
# # # Load data
# # data = load_data()
# map_data = loadJsonData(r'src\data\db-data\predicted_data.json')
# map_data = pd.DataFrame(map_data)

# if map_data is not None:
#     st.write("Parsed Data:", map_data.head())
 
#     # Convert to a DataFrame
#     df = pd.DataFrame(map_data, columns=["predict_gender", "affiliation"])

#     # Function to get random points within country boundaries
#     def generate_random_points(country_name, num_points=1):
#         # Geocode country to get coordinates (latitude, longitude)
#         geolocator = Nominatim(user_agent="geoapi")
#         location = geolocator.geocode(country_name)
        
#         # Load world map shapefiles (from local path)
#         world = gpd.read_file(r"src\data\map-data\ne_110m_admin_0_countries.shp")  # Use your local path to the shapefile
#         # print(world.columns)
#         # st.write("Parsed Data:", world.head())
#         # Filter to get the country boundary
#         country = world[world.NAME_LONG == country_name]
        
#         # If country found, generate random points within the boundary
#         if not country.empty:
#             polygon = country.geometry.iloc[0]
#             points = []
            
#             # Generate random points inside the country boundary
#             for _ in range(num_points):
#                 while True:
#                     # Generate random latitude and longitude
#                     lon = random.uniform(polygon.bounds[0], polygon.bounds[2])
#                     lat = random.uniform(polygon.bounds[1], polygon.bounds[3])
#                     point = Point(lon, lat)
                    
#                     # Check if point is inside the country's boundary
#                     if polygon.contains(point):
#                         points.append((lat, lon))
#                         break
#             return points
#         else:
#             return []

#     # Generate random points for each country
#     random_coords = []
#     for _, row in df.iterrows():
#         country = row['affiliation']
#         gender = row['predict_gender']
#         points = generate_random_points(country, num_points=3)  # You can generate more points
#         for lat, lon in points:
#             random_coords.append({"Gender": gender, "Country": country, "Lat": lat, "Lon": lon})

#     # Convert the random coordinates to a DataFrame
#     coords_df = pd.DataFrame(random_coords)
    
#     coords_df['Color'] = coords_df['Gender'].apply(lambda x: [255, 0, 0] if x == 'f' else [0, 0, 255])
    
#     # Streamlit app
#     st.title("Randomized Gender and Country Map")

#     # Show data table
#     st.write("### Data")
#     st.dataframe(coords_df)

#     # Pydeck map with 2D view
#     st.write("### Map")
#     view_state = pdk.ViewState(
#         latitude=coords_df["Lat"].mean(),
#         longitude=coords_df["Lon"].mean(),
#         zoom=1,
#         pitch=0  # Set pitch to 0 for 2D view
#     )

#     # Layer for gender visualization
#     layer = pdk.Layer(
#         "ScatterplotLayer",
#         data=coords_df,
#         get_position=["Lon", "Lat"],
#         get_color="Color",  # Conditional color based on Gender
#         get_radius=90000,
#         opacity=0.2,
#         pickable=True,
#     )

#     # Render map
#     r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Country}"})
#     st.pydeck_chart(r)