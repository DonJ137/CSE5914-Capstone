#To run Elastic Search Locally: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0

#Run 'pip3 install -r requirements.txt' to ensure all dependencies have been downloaded

from flask import Flask, request, jsonify, render_template, send_from_directory

# Create a Flask app instance
app = Flask(__name__)

#Connect to ES Cluster
from elasticsearch import Elasticsearch

# es = Elasticsearch('https://localhost:9200', ca_certs="http_ca.crt", basic_auth=("elastic", "0eCjuIZGIrFNI09vhq9_"))
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
    }
}

if not es.indices.exists(index="courses"):
    es.indices.create(index="courses", mappings=mappings)

import requests
import json


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape.js')
def send_js():
    return send_from_directory('templates', 'scrape.js')

@app.route('/majors.json')
def send_json():
    return send_from_directory('templates', 'majors.json')

@app.route('/submit_form', methods=['POST'])
def submit_form():

    # Get data from the form (major, major interests, ge interests)
    majorAbbreviation = request.form.get('majorDropdown')
    interests = request.form.get('textInterests')
    GEinterests = request.form.get('GEInterests')

    # hardcoded major abbreviation
    majorAbbreviation = "cse"

    if majorAbbreviation is None or interests is None:
        return jsonify(results="Major or interests not provided")

    # Fetch data from the relevant URL by making a request call to the API
    url = f"https://content.osu.edu/v2/classes/search?q={majorAbbreviation}&campus=col&term=1238"
    r = requests.get(url)

    if r.status_code == 200:
        json_data = r.json()
        numberOfPages = json_data.get("data", {}).get("totalPages", int)
        currentPageNum = 1
        urlPrefix = f"https://content.osu.edu/v2/classes/search?q={majorAbbreviation}&campus=col&term=1238&p="
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
                }
                es.index(index="courses", document=document)

            currentPageNum += 1
            urlCurrent = urlPrefix + str(currentPageNum)
    else:
        print(f"Failed to fetch data from the API. Status code: {r.status_code}")

    # Define a parameter to search for classes with a specific keyword in the description
    searchParamMajorCourses = interests
    SearchParamGECourses = GEinterests

    # creating the query for major courses
    courseQueryMajorCourses = {
      "query": {
          "match": {
              "Class Description" : searchParamMajorCourses
          }
      },
      "sort": [  # Add a sort parameter to sort by Class Number in ascending order
          {
              "Class Number.keyword": {  # Use the .keyword variant to sort text fields
                  "order": "asc"
              }
          }
      ]
    }

    # creating another query for GE courses
    courseQueryGECourses = {
      "query": {
          "match": {
              "Class Description" : SearchParamGECourses
          }
      },
      "sort": [  # Add a sort parameter to sort by Class Number in ascending order
          {
              "Class Number.keyword": {  # Use the .keyword variant to sort text fields
                  "order": "asc"
              }
          }
      ]
    }

    ######## FOR MAJOR COURSES ######



    # Perform the search, increasing the size limit to ensure you capture more results if necessary
    response = es.search(index="courses", body=courseQueryMajorCourses, size=100)  
    unique_class_names_Major = set()
    majorResults = []
    
    # Initialize a variable to keep track of the current level
    current_level = None

    print("Search Results for Major Courses (param: ", searchParamMajorCourses, ") - Classes Sorted by Course Number:")
    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']
        
        # Check if we've moved to a new level
        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level
            print("\n==== {} Level Classes ====\n".format(current_level))
        
        if class_name is not None and class_number is not None and class_name not in unique_class_names_Major:
            class_description = hit['_source']['Class Description']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number
            }
            print(f"Class Number: {class_number}")
            print(f"Class Name: {class_name}")
            print(f"Class Description: {class_description}")
            print("-----------------------")
            majorResults.append(result)
            unique_class_names_Major.add(class_name)







    ###### FOR GE COURSES #######

    # Perform the search, increasing the size limit to ensure you capture more results if necessary
    response = es.search(index="courses", body=courseQueryGECourses, size=100)  
    unique_class_names_GE = set()
    GEResults = []
    
    # Initialize a variable to keep track of the current level
    current_level = None

    print("Search Results for GE Courses (param: ", SearchParamGECourses, ") - Classes Sorted by Course Number:")
    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']
        
        # Check if we've moved to a new level
        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level
            print("\n==== {} Level Classes ====\n".format(current_level))
        
        if class_name is not None and class_number is not None and class_name not in unique_class_names_GE:
            class_description = hit['_source']['Class Description']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number
            }
            print(f"Class Number: {class_number}")
            print(f"Class Name: {class_name}")
            print(f"Class Description: {class_description}")
            print("-----------------------")
            GEResults.append(result)
            unique_class_names_GE.add(class_name)



    # returning the 
    return render_template('submit_form.html', majorResults=majorResults, searchParamMajorCourses=searchParamMajorCourses, 
    GEResults=GEResults, SearchParamGECourses=SearchParamGECourses)

if __name__ == '__main__':
    app.run(debug=True)