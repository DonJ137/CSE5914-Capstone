from flask import Flask, request, jsonify, render_template, send_from_directory

# Create a Flask app instance
app = Flask(__name__)

#Connect to ES Cluster
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')
es.info().body

#Create an index for indexing documents
mappings = {
        "properties": {
            #Equivalent to "academicGroup" in JSON file
            #"Class Group": {"type": "text"},
            #Equivalent to "catalogNumber" in JSON file
            "Class Number": {"type": "text",
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

if not es.indices.exists(index="geneds"):
    es.indices.create(index="geneds", mappings=mappings)

import requests
import json

# Fetch data from the relevant URL by making a request call to the API
url = f"https://content.osu.edu/v2/classes/search?q=&campus=col&term=1238&class-attribute=ge2"
r = requests.get(url)

if r.status_code == 200:
    json_data = r.json()
    numberOfPages = json_data.get("data", {}).get("totalPages", int)
    currentPageNum = 1
    urlPrefix = f"https://content.osu.edu/v2/classes/search?q=&campus=col&term=1238&class-attribute=ge2&p="
    urlCurrent = urlPrefix + str(currentPageNum)

    while currentPageNum <= numberOfPages:
        print(urlCurrent)
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
            es.index(index="geneds", document=document)

        currentPageNum += 1
        urlCurrent = urlPrefix + str(currentPageNum)
else:
    print(f"Failed to fetch data from the API. Status code: {r.status_code}")

