#To run Elastic Search Locally: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0


#Connect to ES Cluster
from elasticsearch import Elasticsearch

es = Elasticsearch('https://localhost:9200', ca_certs="http_ca.crt", basic_auth=("elastic", "0eCjuIZGIrFNI09vhq9_"))
es.info().body


#Create an index for indexing documents
mappings = {
        "properties": {
            #Equivalent to "academicGroup" in JSON file
            #"Class Group": {"type": "text"},
            #Equivalent to "catalogNumber" in JSON file
            "Class Number": {"type": "text"},
            #Equivalent to "title" in JSON file
            "Class Name": {"type": "text"},
            #Equivalent to "description" in JSON file
            "Class Description": {"type": "text"},
            #Equivalent to "academicCareer" in JSON file
            "Class Type": {"type": "text"},
    }
}

if not es.indices.exists(index="courses"):
    es.indices.create(index="courses", mappings=mappings)


#Get the information from the relevant url by making a request call to the API
import requests
import json

url = "https://content.osu.edu/v2/classes/search?q=cse&campus=col&term=1238"
r = requests.get(url)

#Check if the request to the API was successful or not
if r.status_code == 200:
    json_data = r.json()
    
    #Extract the courses section from the JSON data
    courses_data = json_data.get("data", {}).get("courses", [])
    #Iterate through the courses and index each document
    for course in courses_data:
        document = {
            #"Class Group": course['course']['academicGroup'],
            "Class Number": course['course']['catalogNumber'],
            "Class Name": course['course']['title'],
            "Class Description": course['course']['description'],
            "Class Type": course['course']['academicCareer'],
        }
        #Index the document in Elasticsearch
        es.index(index="courses", document=document)
        # print(f"Indexed document: {document}")
else:
    print(f"Failed to fetch data from the API. Status code: {r.status_code}")

# Define a parameter to search for classes with a specific keyword in the description
searchParam = "software"

courseQuery = {
    "match": {
        # "query" : searchParam,
        # "fields" : ["Class Name", "Class Description"]
        "Class Description" : searchParam
    }
}

# Perform the search, using query rather than body since body is deprecated
response = es.search(index="courses", query=courseQuery)  

# Create a set to store unique class IDs
unique_class_names = set()

# Print search results without duplicates
print("Got %d Hits:" % response['hits']['total']['value'])
# print(response['hits']['hits'])
print("Search Results for", searchParam, "Classes:")
for hit in response['hits']['hits']:
    class_name = hit['_source']['Class Name']
    """
    if class_name not in unique_class_names:
        class_description = hit['_source']['Class Description']
        print(f"Class Name: {class_name}")
        print(f"Class Description: {class_description}")
        print("-----------------------")
        # Add the class name to the set to mark it as processed
        unique_class_names.add(class_name)
    """
    class_description = hit['_source']['Class Description']
    print(f"Class Name: {class_name}")
    print(f"Class Description: {class_description}")
    print("-----------------------")
    # Add the class name to the set to mark it as processed
    unique_class_names.add(class_name)