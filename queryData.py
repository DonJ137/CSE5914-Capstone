from flask import Flask, request, jsonify, render_template, send_from_directory
from elasticsearch import Elasticsearch
import math

app = Flask(__name__)
es = Elasticsearch('http://localhost:9200')

def getRecommendedYear(class_number, numYears):
    # Calculate the recommended year
    temp_class_number = 0.0
    for character in class_number:
        if character.isalpha():
            temp_class_number = float(class_number[:-1])
            break
    if (temp_class_number == 0.0):
        temp_class_number = float(class_number)
    class_number_int = temp_class_number
    year_denominator = 5000 / numYears
    year_num = math.floor(class_number_int / year_denominator)
    year_num_string = str()
    if year_num == 0:
        year_num = 1
    if year_num == 2 and numYears == 4:
        year_num_string = "2 or 3"
    else:
        year_num_string = str(year_num)
    if temp_class_number < 2500 and temp_class_number > 2000 and numYears == 4:
        year_num_string = "1 or 2"
    return year_num_string

@app.route('/')
def index():
    return render_template('index.html')

class_data_storage = []  # A simple list to store class data

@app.route('/add-to-schedule', methods=['POST'])
def add_to_schedule():
    data = request.get_json()
    class_data_storage.append(data)
    return jsonify({"message": "Class information added"})

@app.route('/remove-from-schedule/<class_number>', methods=['DELETE'])
def remove_from_schedule(class_number):
    global class_data_storage
    class_data_storage = [c for c in class_data_storage if c['classNumber'] != class_number]
    return jsonify({"message": "Class removed from schedule"})

@app.route('/generated_schedule.html')
def schedule():
    return render_template('generated_schedule.html', classes=class_data_storage)

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
    numYears = int(request.form.get('numYears'))
    geInterests = request.form.get('geInterests')
    
    ### For Major Courses ###
    
    # Major Mappings, update with majors.json as necessary
    if majorAbbreviation == "Computer Science and Engineering":
        majorAbbreviation = "CSE"
    elif majorAbbreviation == "Electrical and Computer Engineering":
        majorAbbreviation = "ECE"
    elif majorAbbreviation == "Aerospace Engineering":
        majorAbbreviation = "AEROENG"
    elif majorAbbreviation == "Chemistry":
        majorAbbreviation = "CHEM"

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
        class_major = hit['_source']['Major']

        # Check if we've moved to a new level
        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level
            print("\n==== {} Level Classes ====\n".format(current_level))

        # Calculate the recommended year
        year_num_string = getRecommendedYear(class_number, numYears)

        if class_name is not None and class_number is not None and class_name not in unique_class_names and class_major == majorAbbreviation:
            class_description = hit['_source']['Class Description']
            # class_major = hit['_source']['Major']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number,
                "Major": class_major,
                "Year Number": year_num_string
            }
            

            print(f"Class Number: {class_number}")
            print(f"Class Name: {class_name}")
            print(f"Class Description: {class_description}")
            print(f"Major: {class_major}")
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

        # Calculate the recommended year
        year_num_string = getRecommendedYear(class_number, numYears)

        if class_name is not None and class_number is not None and class_name not in gen_ed_class_names:
            class_description = hit['_source']['Class Description']
            class_major = hit['_source']['Major']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number,
                "Major": class_major,
                "Year Number": year_num_string
            }
            print(f"Class Number: {class_number}")
            print(f"Class Name: {class_name}")
            print(f"Class Description: {class_description}")
            print(f"Major: {class_major}")
            print("-----------------------")
            genEdResults.append(result)
            gen_ed_class_names.add(class_name)

    return render_template('submit_form.html', results=results, searchParam=searchParam, genEdResults=genEdResults, genEdSearchParam=genEdSearchParam)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
