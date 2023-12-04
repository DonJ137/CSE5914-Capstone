#To run Elastic Search Locally: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0

#Run 'pip install -r requirements.txt' to ensure all dependencies have been downloaded

from elasticsearch import Elasticsearch
import requests
import json
from flask import Flask, request, jsonify, render_template, send_from_directory

# Create a Flask app instance
app = Flask(__name__)

# Connect to Elasticsearch Cluster
es = Elasticsearch('http://localhost:9200')
es.info().body

# Define mappings for Elasticsearch indices
mappings = {
    "properties": {
            #Equivalent to "catalogNumber" in JSON file
            "Class Number": {
                "type": "text",
                "fields": {
                    "keyword": { "type": "keyword" }  # This creates a keyword sub-field
                }
            },
            #Equivalent to "title" in JSON file
            "Class Name": {"type": "text"},
            #Equivalent to "description" in JSON file
            "Class Description": {"type": "text"},
            #Equivalent to "academicCareer" in JSON file
            "Class Type": {"type": "text"},
            #Equivalent to "subject" in JSON file
            "Major": {"type": "text"},
    }
}

# Function to create an index
def create_index(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, mappings=mappings)

# Function to index data
def index_data(url, index_name):
    r = requests.get(url)
    if r.status_code == 200:
        json_data = r.json()
        numberOfPages = json_data.get("data", {}).get("totalPages", int)
        currentPageNum = 1
        urlPrefix = url + "&p="

        while currentPageNum <= numberOfPages:
            urlCurrent = urlPrefix + str(currentPageNum)
            print(urlCurrent)  # For debugging
            r = requests.get(urlCurrent)
            json_data = r.json()
            courses_data = json_data.get("data", {}).get("courses", [])

            for course in courses_data:
                document = {
                    "Class Number": course['course']['catalogNumber'],
                    "Class Name": course['course']['title'],
                    "Class Description": course['course']['description'],
                    "Class Type": course['course']['academicCareer'],
                    "Major": course['course']['subject'],
                }
                es.index(index=index_name, document=document)

            currentPageNum += 1
    else:
        print(f"Failed to fetch data from the API. Status code: {r.status_code}")

if __name__ == "__main__":
    # Create indices
    create_index("courses")
    create_index("geneds")

    # Indexing course data
    majorList = ["CSE", "ISE", "ECE", "CHEM", "AEROENG"]  # List of Majors, add as needed and update queryData.py and majors.json accordingly
    for major in majorList:
        url = f"https://content.osu.edu/v2/classes/search?q={major}&campus=col&term=1238"
        index_data(url, "courses")

    # Indexing GEs
    gened_url = "https://content.osu.edu/v2/classes/search?q=&campus=col&term=1238&class-attribute=ge2"
    index_data(gened_url, "geneds")