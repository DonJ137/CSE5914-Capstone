from elasticsearch import Elasticsearch
import requests
import json

es = Elasticsearch('http://localhost:9200')

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

def create_index():
    if not es.indices.exists(index="courses"):
        es.indices.create(index="courses", mappings=mappings)

def index_data(majorAbbreviation):
    url = f"https://content.osu.edu/v2/classes/search?q={majorAbbreviation}&campus=col&term=1238"
    r = requests.get(url)

    if r.status_code == 200:
        json_data = r.json()
        numberOfPages = json_data.get("data", {}).get("totalPages", int)
        currentPageNum = 1
        urlPrefix = f"https://content.osu.edu/v2/classes/search?q={majorAbbreviation}&campus=col&term=1238&p="
        urlCurrent = urlPrefix + str(currentPageNum)

        while currentPageNum <= numberOfPages:
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

if __name__ == "__main__":
    create_index()
    majorAbbreviation = "cse"  # This is just an example, replace it with the actual major abbreviation
    index_data(majorAbbreviation)
