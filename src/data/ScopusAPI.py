import requests
import itertools
import time
from pymongo import MongoClient

# Replace with your API key from Elsevier
API_KEY = "9dd590e8ec8a8513452bd2912d8b0e9d"
BASE_URL = 'https://api.elsevier.com/content/search/scopus'

# MongoDB connection
client = MongoClient('mongodb+srv://Don-Yurillo:12345@dataprep.6ns0k.mongodb.net/')  # Replace with your MongoDB connection string
db = client['paper_data']  # Replace with your database name
collection = db['scopus_paper_data_ENGI'] # Replace with your collection name

start = 100
count = 25

def get_subject_areas(issn):
    """Retrieves subject areas from Elsevier API based on ISSN."""
    url = f"http://api.elsevier.com/content/serial/title/issn/{issn}?apiKey={API_KEY}&field=subject-area"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            subject_areas = [
                area['@code']
                for entry in data['serial-metadata-response']['entry']
                for area in entry['subject-area']
            ]
            return subject_areas
        except (KeyError, json.JSONDecodeError):
            print(f"Error parsing subject area data for ISSN: {issn}")
            return []  # Return empty list if there's an error
    else:
        print(f"Failed to fetch subject area data for ISSN: {issn}. Status code: {response.status_code}")
        return []

def get_metadata_from_crossref(doi, scopus_affiliations):
    CROSSREF_API_URL = f"https://api.crossref.org/works/{doi}"
    response = requests.get(CROSSREF_API_URL)
    author_list = []
    if response.status_code == 200:
        data = response.json()
        authors = data.get('message', {}).get('author', [])
        for author, country in itertools.zip_longest(authors, scopus_affiliations, fillvalue=None):  # Zip here!
            if author is None:
                continue
            given_name = author.get('given', '')
            if given_name :
                first_name = given_name.split()[0]
            else : continue
            affiliation = 'Unknown'
            if author.get('affiliation'):
                affiliation_list = author.get('affiliation', [])
                if affiliation_list:
                    affiliation = affiliation_list[0].get('name', 'Unknown')

            # Use the provided country if available, otherwise use affiliation
            author_country = country if country else affiliation  # Prioritize country
            author_list.append({"author": first_name, "affiliation": author_country}) # Changed

        return author_list
    else:
        print(f"Failed to fetch CrossRef data for DOI {doi}. Status code: {response.status_code}")
        return []


    # Function to query Scopus and store in MongoDB
def query_scopus():

    query_params = {
        'query': 'PUBYEAR = 2017 AND ( LIMIT-TO ( SUBJAREA , "ENGI" ))',
        'apiKey': API_KEY,
        'start': start, # Start at 0
        'count': count # Reduced count for testing
    }

    response = requests.get(BASE_URL, params=query_params)

    if response.status_code == 200:
        data = response.json()
        entries = data.get('search-results', {}).get('entry', [])

        for entry in entries:
            doi = entry.get('prism:doi', 'N/A')
            issn = entry.get('prism:issn')
            eIssn= entry.get('prism:eIssn')
            affiliations = [] # Keep affiliations separate

            if issn:  # Check if ISSN is available
                subject_codes = get_subject_areas(issn)
            elif eIssn:
                subject_codes = get_subject_areas(eIssn)
            else:
                subject_codes = []  # Or a default value like ["N/A"]
                print(f"No ISSN or EISSN available for entry: {entry.get('dc:title', 'N/A')}")

            if 'affiliation' in entry:
                for aff in entry['affiliation']:
                    country = aff.get('affiliation-country', 'Unknown')
                    affiliations.append(country)
            if doi != 'N/A':
                author_list = get_metadata_from_crossref(doi, affiliations)
                if author_list: # Only proceed if author data was retrieved successfully
                    mongo_doc = {
                        "title": entry.get('dc:title', 'N/A'),
                        "author_list": author_list,
                        "subject_code": subject_codes, # Using the fixed subject code for now.
                        "publication_type": entry.get('prism:aggregationType', 'Unknown'),
                        "cited_count": int(entry.get('citedby-count', 0)), # Convert to integer, default to 0
                        "year": int(entry.get('prism:coverDate', 'N/A').split('-')[0]),  # Convert year to integer
                        "doi": doi,
                        "issn": issn,
                        "eissn": eIssn,
                    }
                    collection.insert_one(mongo_doc)  # Insert into MongoDB
                    # print(f"Inserted document: {mongo_doc}")
                    print("Insert Successful")
            else:
                print("No DOI available for this entry.")
            print("-" * 40)



    else:
        print(f"Failed to fetch Scopus data. Status code: {response.status_code} {response.json()}")


# Execute the Scopus query
for i in range(0, 40):
    print("Now position: ", start)
    query_scopus()
    start += 25
    # time.sleep(1)