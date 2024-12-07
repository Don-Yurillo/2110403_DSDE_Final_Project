import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


# This will change to be topic when data is ready
st.title("Gender Distribution by Affiliation")

try:
    with open(r'src\data\db-data\behind_the_name_data.json', 'r', encoding='utf-8') as file:  # Try UTF-8 first
        data = json.load(file)
except UnicodeDecodeError:
    try:
        with open(r'src\data\db-data\behind_the_name_data.json', 'r', encoding='latin-1') as file: # Try Latin-1 if UTF-8 fails
            data = json.load(file)
    except UnicodeDecodeError:  # Handle cases where neither encoding works
        st.error("Error: Could not decode the JSON file. Please check the file encoding.")
        st.stop()  # Stop execution to prevent further errors

except FileNotFoundError:
    st.error("Error: JSON file not found.")
    st.stop()


df = pd.DataFrame(data)

# Data Cleaning (Important!):
df.dropna(subset=['gender', 'affiliation'], inplace=True)  # Remove rows with missing gender or affiliation
df['gender'] = df['gender'].str.lower().str.strip()  # Standardize gender (e.g., "M" and "m" become "m")
df['affiliation'] = df['affiliation'].str.strip()  # Clean up affiliation strings
df['gender'] = df['gender'].replace(['m', 'f'],['Male', 'Female'])
# st.write(df.groupby('affiliation')['gender'].value_counts())

if not df.empty: # Check for empty DataFrame after cleaning
    affiliations = df['affiliation'].unique()
    # st.write(affiliations)
    selected_affiliation = st.sidebar.selectbox("Select Topic", affiliations)
    
    col1 , col2 = st.columns(2)
    with col1:
        selected_year1 = st.selectbox("Select Year1", ['2016', '2017', '2018', '2019', '2020', '2021'], index=1)
    with col2:
        selected_year2 = st.selectbox("Select Year2", ['2016', '2017', '2018', '2019', '2020', '2021'], index=2)
    
    filtered_df = df[df['affiliation'] == selected_affiliation]
    # st.write(filtered_df.groupby('affiliation')['gender'].value_counts())
    # st.write(filtered_df['gender'].value_counts())
    if not filtered_df.empty: # Check if the filtered DataFrame is empty
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=[f"Gender Distribution in {selected_year1}", f"Gender Distribution in {selected_year2}"])

        gender_counts = filtered_df['gender'].value_counts()
        # Pie Chart
        fig.add_trace(
            go.Pie(labels=filtered_df['gender'].unique(), 
                   values=filtered_df['gender'].value_counts(), # Count occurrences
                   name="Gender Distribution",
                   marker=dict(colors=px.colors.qualitative.Set2)),
            row=1, col=1
        )
       

        fig.add_trace(
            go.Pie(labels=filtered_df['gender'].unique(), 
                   values=filtered_df['gender'].value_counts(), # Count occurrences
                   name="Gender Distribution",
                   marker=dict(colors=px.colors.qualitative.Set2)),
            row=1, col=2
        )


        fig.update_layout(title_text=f"Gender Distribution in {selected_affiliation} will change to topic")
        st.plotly_chart(fig)
        # fig.update_traces(textinfo='value+label')  # Show both count and label on each slice
        # st.plotly_chart(fig)
    else:
        st.warning("No data found for the selected affiliation.")
else:
    st.warning("The dataset is empty after cleaning.  Check the data source.")
    
if not df.empty:
    affiliations = df['affiliation'].unique()
    gender_counts = df.groupby(['affiliation', 'gender']).size().unstack(fill_value=0).reset_index() #unstack converts to wide forma

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
