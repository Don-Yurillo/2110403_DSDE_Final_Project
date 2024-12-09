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
from plotly.subplots import make_subplots

st.set_page_config(page_title="Data Visualization", page_icon=":bar_chart:", layout="wide")

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
@st.cache_data
def load_data(filepath):
    data = loadJsonData(filepath)
    return pd.DataFrame(data)
predicted_data = load_data(r"src\data\db-data\predicted_data_with_country.json")

# @st.cache_data
# def transform_subject_codes(df):
#     df['subject_code'] = df['subject_code'].apply(lambda x: str(x)[0:2] + "00")
#     return df

@st.cache_data
def prepare_chart_data(df):
    df['predict_gender'] = df['predict_gender'].replace(['m', 'f'], ['Male', 'Female'])
    df['subject_code'] = df['subject_code'].apply(lambda x: str(x)[0:2] + "00")
    df.dropna(subset=['title'], inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def homePage():
    st.title("Data Visualization")
    st.markdown("This page displays the data visualization of the predicted data.")
    
    # data = loadJsonData(r"E:\Works\Intro-to-Data-Science\2110403_DSDE_Final_Project\src\data\db-data\predicted_data.json")
    # df = pd.DataFrame(data)

    st.write(predicted_data)

def pieChart(df):
    st.header("Gender Distribution by Topic")
    st.subheader("Pie Chart")
    pie_chart_df = prepare_chart_data(df)
    pie_chart_df = pd.DataFrame(pie_chart_df, columns=['title', 'name', 'subject_code', 'year', 'predict_gender'])
    # pie_chart_df['predict_gender'] = pie_chart_df['predict_gender'].replace(['m', 'f'],['Male', 'Female'])
    # # pie_chart_df['subject_code'] = pie_chart_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    # pie_chart_df = transform_subject_codes(pie_chart_df)
    # pie_chart_df.dropna(subset=['title'], inplace=True)
    # # st.write(pie_chart_df.info())
    # pie_chart_df = pie_chart_df.drop_duplicates()
    
    pie_chart_df_expander = st.expander("Data Table", expanded=False)
    with pie_chart_df_expander:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(pie_chart_df)
        with col2:
            value_count = pd.DataFrame(pie_chart_df, columns=['subject_code', 'year', 'predict_gender'])
            value_count['subject_code'] = value_count['subject_code'].apply(lambda x: subject_map[x])
            # st.write(value_count['predict_gender'].value_counts())
            st.write(value_count.groupby(['subject_code', 'year']).value_counts())
    
    st.sidebar.header("Gender Distribution by Topic")
    
    list_of_subjects = pie_chart_df['subject_code'].apply(lambda x: subject_map[x]).unique().tolist()
    list_of_subjects.append("All Topic")
    selected_subject_sidebar = st.sidebar.selectbox("Select Pie Chart Topic", list_of_subjects, index=len(list_of_subjects) - 1, key='pie')
    
    if selected_subject_sidebar == "All Topic":
        pie_chart_df = pie_chart_df
    else:
        pie_chart_df = pie_chart_df[pie_chart_df['subject_code'].apply(lambda x: subject_map[x]) == selected_subject_sidebar]
    
    # st.write(pie_chart_df)
    # pie_chart_df.loc[len(pie_chart_df)] = [np.nan, np.nan, np.nan, "All Years", np.nan]
    # pie_chart_df['year'] = pie_chart_df['year'].astype(str)
    # pie_chart_df = pie_chart_df.sort_values(by='year', ascending=False)
    
    # st.write(pie_chart_df[pie_chart_df['name'].isna()]) Will appear 1 because of the added row year: ALL
    list_of_years = pie_chart_df['year'].unique().tolist()
    list_of_years.append("All Years")

    col1 , col2 = st.columns(2)
    with col1:
        selectBox_year_1 = st.selectbox("",list_of_years, index=len(list_of_years) - 1, key='pie1')
    with col2:
        selectBox_year_2 = st.selectbox("",list_of_years, index=1, key='pie2')
    
    # filtered_pie_chart_df = pie_chart_df.copy()
    
    if not pie_chart_df.empty:
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=[f"Gender Distribution in {selectBox_year_1}", f"Gender Distribution in {selectBox_year_2}"])
        if selectBox_year_1 != "All Years":
            filtered_pie_chart_df1 = pie_chart_df[pie_chart_df['year'] == selectBox_year_1]
        else:
            filtered_pie_chart_df1 = pie_chart_df[pie_chart_df['year'] != "All Years"]
        
        filtered_pie_chart_df1 = filtered_pie_chart_df1.dropna(subset=['name'], axis=0)
        # st.write(filtered_pie_chart_df)
        year1_gender_count = filtered_pie_chart_df1['predict_gender'].value_counts().reset_index()
        year1_gender_count.columns = ['gender', 'count']
        total_year1 = year1_gender_count['count'].sum()
        year1_gender_count['percentage'] = year1_gender_count['count'].apply(lambda x: round((x / total_year1) * 100, 2))
                
        fig.add_trace(
            go.Pie(labels=year1_gender_count['gender'],
                values=year1_gender_count['count'], # Count occurrences
                name="Gender Distribution",
                marker=dict(colors=px.colors.qualitative.Set1)),
            row=1, col=1
        )
        
        if selectBox_year_2 != "All Years":
            filtered_pie_chart_df2 = pie_chart_df[pie_chart_df['year'] == selectBox_year_2]
        else:
            filtered_pie_chart_df2 = pie_chart_df[pie_chart_df['year'] != "All Years"]
        
        filtered_pie_chart_df2 = filtered_pie_chart_df2.dropna(subset=['name'], axis=0)
        # st.write(filtered_pie_chart_df)
        year2_gender_count = filtered_pie_chart_df2['predict_gender'].value_counts().reset_index()
        year2_gender_count.columns = ['gender', 'count']
        total_year2 = year2_gender_count['count'].sum()
        year2_gender_count['percentage'] = year2_gender_count['count'].apply(lambda x: round((x / total_year2) * 100, 2))
                
        fig.add_trace(
            go.Pie(labels=year2_gender_count['gender'],
                values=year2_gender_count['count'], # Count occurrences
                name="Gender Distribution",
                marker=dict(colors=px.colors.qualitative.Set1)),
            row=1, col=2
        )
        fig.update_layout(title_text=f"Gender Distribution in {selected_subject_sidebar}")
        st.plotly_chart(fig)
        col1, col2 = st.columns(2)
        with col1:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                st.write(year1_gender_count)
            with sub_col2:
                total_year1 = pd.DataFrame(total_year1, columns=['Total'], index=[0])
                st.write(total_year1)
        with col2:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                st.write(year2_gender_count)
            with sub_col2:
                total_year2 = pd.DataFrame(total_year2, columns=['Total'], index=[0])
                st.write(total_year2)

def lineChart(df):
    st.header("Gender Distribution Over Years")
    st.subheader("Line Chart")

    # prepare data
    line_chart_df = prepare_chart_data(df)
    # line_chart_df = pd.DataFrame(line_chart_df, columns=['title', 'name', 'subject_code', 'year', 'predict_gender'])
    # line_chart_df['predict_gender'] = line_chart_df['predict_gender'].replace(['m', 'f'],['Male', 'Female'])
    # line_chart_df = transform_subject_codes(line_chart_df)
    # line_chart_df.dropna(subset=['title'], inplace=True)
    # line_chart_df = line_chart_df.drop_duplicates()
    # # line_chart_df['subject_code'] = line_chart_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    # # st.write(pie_chart_df.info())
    # st.write(line_chart_df)
    line_chart_df = pd.DataFrame(line_chart_df, columns=['year', 'subject_code', 'predict_gender'])
    st.sidebar.header("Gender Distribution Over Years")
    selected_subject_sidebar = st.sidebar.selectbox("Select Line Chart Topic", ['All Topics', 'Life Sciences', 'Social Sciences', 'Physical Sciences', 'Health Sciences'], index=0,key='line')
    
    if selected_subject_sidebar == "All Topics":
        line_chart_df = line_chart_df
        
    elif selected_subject_sidebar == "Life Sciences": 
        line_chart_df = line_chart_df[line_chart_df['subject_code'].isin(["1000","1300", "2400", "2800", "3000"])]
        
    elif selected_subject_sidebar == "Social Sciences": 
        line_chart_df = line_chart_df[line_chart_df['subject_code'].isin(["1200","1400","1800","2000","3200","3300","3300"])]
        
    elif selected_subject_sidebar == "Physical Sciences": 
        line_chart_df = line_chart_df[line_chart_df['subject_code'].isin(["1500","1600","1700","1900","2100","2200","2300","2500","2600","3100"])]
        
    elif selected_subject_sidebar == "Health Sciences": 
        line_chart_df = line_chart_df[line_chart_df['subject_code'].isin(["2700" ,"2900" , "3400", "3500", "3600"])]
        
    # st.write(line_chart_df)
    group_line_chart_df = line_chart_df.groupby(['year', 'subject_code', 'predict_gender']).value_counts().reset_index(name='count')
    group_line_chart_df.columns = ['year', selected_subject_sidebar, 'gender', 'count']
    line_chart_expander = st.expander("Data Table", expanded=False)
    with line_chart_expander:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("Topic: {}".format(selected_subject_sidebar))
            group_line_chart_df['subject_name'] = group_line_chart_df[selected_subject_sidebar].apply(lambda x: subject_map[x])  
            st.write(group_line_chart_df)
        with col2:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                selected_year = st.selectbox(
                    "Select Year to view data",
                    options=group_line_chart_df['year'].unique() 
                )
            with sub_col2:
                selected_subject = st.selectbox(
                    "Select Subject to view data",
                    options=group_line_chart_df[selected_subject_sidebar].apply(lambda x: subject_map[x]).unique() 
                )
            if selected_subject == "All Topics":
                filtered_data = group_line_chart_df[(group_line_chart_df['year'] == selected_year)]
            else:
                filtered_data = group_line_chart_df[(group_line_chart_df['year'] == selected_year) & (group_line_chart_df[selected_subject_sidebar].apply(lambda x: subject_map[x]) == selected_subject)]
                
            st.write(f"Data for Year {selected_year}:")
            st.write(filtered_data)
    
    line_chart_df = line_chart_df.groupby(['year', 'predict_gender']).size().reset_index(name='count')
    line_chart_df.columns = ['year', 'gender', 'count']
    
    fig = px.line(
        line_chart_df,
        x = 'year',
        y = 'count',
        color='gender',
        color_discrete_map={'Female':'blue', 'Male':'red'},
        title="Gender Distribution Over Years",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Gender count",
    )

    st.plotly_chart(fig)
          
def barChart(df):
    st.header("Gender Distribution Stacked by Subject Code")
    st.subheader("Bar Chart")
    st.sidebar.header("Gender Distribution Stacked by Subject Code")
    
    bar_chart_df = prepare_chart_data(df)
    # bar_chart_df = pd.DataFrame(bar_chart_df, columns=['title', 'name', 'subject_code', 'year', 'predict_gender'])
    # bar_chart_df['predict_gender'] = bar_chart_df['predict_gender'].replace(['m', 'f'],['Male', 'Female'])
    # bar_chart_df = transform_subject_codes(bar_chart_df)
    # bar_chart_df.dropna(subset=['title'], inplace=True)
    # bar_chart_df = bar_chart_df.drop_duplicates()
    # # bar_chart_df['subject_code'] = bar_chart_df['subject_code'].apply(lambda x: str(x)[0:2]+str("00"))
    # # st.write(bar_chart_df)
    bar_chart_df = pd.DataFrame(bar_chart_df, columns=["subject_code", "predict_gender"])
    
    selected_subject_sidebar = st.sidebar.selectbox("Select Bar Chart Topic", ['All Topics', 'Life Sciences', 'Social Sciences', 'Physical Sciences', 'Health Sciences'], 
                                                    index=0, 
                                                    key='bar')
    
    if selected_subject_sidebar == "All Topics":
        bar_chart_df = bar_chart_df
        
    elif selected_subject_sidebar == "Life Sciences": 
        bar_chart_df = bar_chart_df[bar_chart_df['subject_code'].isin(["1000","1300", "2400", "2800", "3000"])]
        
    elif selected_subject_sidebar == "Social Sciences": 
        bar_chart_df = bar_chart_df[bar_chart_df['subject_code'].isin(["1200","1400","1800","2000","3200","3300","3300"])]
        
    elif selected_subject_sidebar == "Physical Sciences": 
        bar_chart_df = bar_chart_df[bar_chart_df['subject_code'].isin(["1500","1600","1700","1900","2100","2200","2300","2500","2600","3100"])]
        
    elif selected_subject_sidebar == "Health Sciences": 
        bar_chart_df = bar_chart_df[bar_chart_df['subject_code'].isin(["2700" ,"2900" , "3400", "3500", "3600"])]
        
    bar_chart_df = bar_chart_df.groupby(['subject_code', 'predict_gender']).value_counts().reset_index(name='count')
    bar_chart_df.columns = [selected_subject_sidebar, 'gender', 'count']
    
    total_female = bar_chart_df[bar_chart_df['gender'] == "Female"]['count'].sum()
    total_male = bar_chart_df[bar_chart_df['gender'] == "Male"]['count'].sum()
    total_person = bar_chart_df['count'].sum()
    
    bar_chart_df['normalized_count'] = bar_chart_df.apply(
        lambda row: ((row['count'] / total_female) * 100) if row['gender'] == "Female" else ((row['count'] / total_male) * 100), axis=1
    )
    bar_chart_df[selected_subject_sidebar] = bar_chart_df[selected_subject_sidebar].apply(lambda x: subject_map[x])
    # checkBox = st.checkbox("Show more data", value=False)
    # col1, col2 = st.columns(2)
    bar_chart_df_expander = st.expander("Data Table", expanded=False)
    with bar_chart_df_expander:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(bar_chart_df)
        with col2:
            selected_subject = st.selectbox(
                "Select Subject Code to view data",
                options=bar_chart_df[selected_subject_sidebar].unique() 
            )
            filtered_data = bar_chart_df[bar_chart_df[selected_subject_sidebar] == selected_subject][['gender', 'count']]
            filtered_data = pd.concat([filtered_data, pd.DataFrame([['Total', filtered_data['count'].sum()]], columns=filtered_data.columns)], ignore_index=True)
            st.write(f"Data for Subject Code {selected_subject}:")
            st.write(filtered_data)
 
    chart = alt.Chart(bar_chart_df).mark_bar().encode(
        x='gender',
        y='normalized_count',
        color='{}:N'.format(selected_subject_sidebar),  # Color by subject_code
        tooltip=['gender', 'count', selected_subject_sidebar]  # Tooltip to show details on hover
        
    ).properties(
        title='Gender Distribution Stacked by Subject Code',
        width=600,
        height=500
    )
    st.altair_chart(chart, use_container_width=True)
    
def mapVisualization(df):
    st.header("Map Visualization")
    st.subheader("Map")
    
    map_df = prepare_chart_data(df)
    map_df = pd.DataFrame(map_df, columns=['country', 'predict_gender'])

def dataVisualization():
    df = predicted_data.copy()
    # st.write(df)
    if df.empty:
        st.error("Error: Data is empty.")
        st.stop()
    
    st.title("Data Visualization")
    st.divider()
    
    pieChart(df)
    st.divider()
    
    lineChart(df)
    st.divider()
    
    barChart(df)
    st.divider()
    
    mapVisualization(df)
    
def main():
    st.sidebar.header("Choose Page:")
    choose_page = st.sidebar.selectbox("Page", ["Home", "Data Visualization"], index=1)
    
    if choose_page == "Home":
        homePage()
    elif choose_page == "Data Visualization":
        dataVisualization()


if __name__ == "__main__":
    main()
        
    