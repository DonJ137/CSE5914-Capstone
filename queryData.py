from flask import Flask, request, jsonify, render_template, send_from_directory
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch('http://localhost:9200')

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
    # Get data from the form
    majorAbbreviation = request.form.get('majorDropdown')
    interests = request.form.get('textInterests')
    numSemesters = request.form.get('numYears')
    geInterests = request.form.get('geInterests')

    if majorAbbreviation is None or interests is None:
        return jsonify(results="Major or interests not provided")
    
    ### For Major Courses ###

    # Define a parameter to search for classes with a specific keyword in the description
    searchParam = interests

    courseQuery = {
        "query": {
            "match": {
                "Class Description": searchParam
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

    # Perform the search, increasing the size limit to ensure you capture more results if necessary
    response = es.search(index="courses", body=courseQuery, size=100)
    unique_class_names = set()
    results = []

    # Initialize a variable to keep track of the current level
    current_level = None

    print("Search Results for", searchParam, "Classes Sorted by Course Number:")
    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']

        # Check if we've moved to a new level
        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level
            print("\n==== {} Level Classes ====\n".format(current_level))

        if class_name is not None and class_number is not None and class_name not in unique_class_names:
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
            results.append(result)
            unique_class_names.add(class_name)


    ### For Gen Ed Courses ###

    # Define a parameter to search for classes with a specific keyword in the description
    genEdSearchParam = geInterests

    genEdQuery = {
        "query": {
            "match": {
                "Class Description": genEdSearchParam
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

    # Perform the search, increasing the size limit to ensure you capture more results if necessary
    response = es.search(index="geneds", body=genEdQuery, size=100)
    gen_ed_class_names = set()
    genEdResults = []

    # Initialize a variable to keep track of the current level
    current_level = None

    print("Search Results for", genEdSearchParam, "Classes Sorted by Course Number:")
    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']

        # Check if we've moved to a new level
        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level
            print("\n==== {} Level Classes ====\n".format(current_level))

        if class_name is not None and class_number is not None and class_name not in gen_ed_class_names:
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
            genEdResults.append(result)
            gen_ed_class_names.add(class_name)

    return render_template('submit_form.html', results=results, searchParam=searchParam, genEdResults=genEdResults, genEdSearchParam=genEdSearchParam)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
