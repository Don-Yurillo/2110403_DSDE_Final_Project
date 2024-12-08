import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import altair as alt
from pymongo import MongoClient

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


def startPage():
    st.title("Data Visualization")
    st.markdown("This page displays the data visualization of the predicted data.")

# Data loadding functions from JSON files
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

#Data loading functions from MongoDB [NOT RECOMMENDED!!!!!!]
def loadMongoData(db_name, collection_name):
    try:
        # db_name = db_name
        # collection_name = collection_name
        connection_string = 'mongodb+srv://Don-Yurillo:12345@dataprep.6ns0k.mongodb.net/{}?retryWrites=true&w=majority'.format(db_name)
        client = MongoClient(connection_string)
        
        db = client[db_name]
        collection = db[collection_name]
        
        data = collection.find()
        data_list = list(data)

        for document in data_list:
            if "_id" in document:
                del document["_id"]
        
        return data_list
        
    except Exception as e:
        st.error("Error: Could not connect to the MongoDB database.")
        st.stop()

# PreLoader Path
predicted_data = loadJsonData(r"E:\Works\Intro-to-Data-Science\2110403_DSDE_Final_Project\src\data\db-data\predicted_data.json")
predicted_data = pd.DataFrame(predicted_data)


def homePage():
    st.title("Data Visualization")
    st.markdown("This page displays the data visualization of the predicted data.")
    
    # data = loadJsonData(r"E:\Works\Intro-to-Data-Science\2110403_DSDE_Final_Project\src\data\db-data\predicted_data.json")
    # df = pd.DataFrame(data)

    st.write(predicted_data)
    
def dataVisualization():
    df = predicted_data
    st.write(df)
    # predicted_data = loadMongoData("paper_data", "predicted_data")
    # df = pd.DataFrame(predicted_data)
    # st.write(df)

def main():
    st.set_page_config(page_title="Data Visualization", page_icon=":bar_chart:", layout="wide")
    st.sidebar.write("Choose Page:")
    choose_page = st.sidebar.selectbox("Page", ["Home", "Data Preparation", "Model Building", "Data Visualization"], index=0)
    
    if choose_page == "Home":
        homePage()
    elif choose_page == "Data Preparation":
        pass
    elif choose_page == "Model Building":
        pass
    elif choose_page == "Data Visualization":
        dataVisualization()


if __name__ == "__main__":
    main()
        
    