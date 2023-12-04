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

def map_major_abbreviation(major_full_name):
    # Add more mappings as necessary and update majors.json and indexAllData.py to reflect the list
    major_abbreviations = {
        "Computer Science and Engineering": "CSE",
        "Electrical and Computer Engineering": "ECE",
        "Aerospace Engineering": "AEROENG",
        "Chemistry": "CHEM",
    }
    return major_abbreviations.get(major_full_name, major_full_name)

def search_courses(index, search_param, major_abbreviation=None, num_years=None):
    course_query = {
        "query": {
            "match": {
                "Class Description": search_param
            }
        },
        "sort": [
            {
                "Class Number.keyword": {
                    "order": "asc"
                }
            }
        ]
    }
    response = es.search(index=index, body=course_query, size=100)
    unique_class_names = set()
    results = []
    current_level = None

    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']
        class_major = hit['_source'].get('Major', '')

        level = int(class_number[0]) * 1000
        if current_level != level:
            current_level = level

        year_num_string = getRecommendedYear(class_number, num_years) if num_years else 'any year'

        if class_name and class_number and class_name not in unique_class_names and (not major_abbreviation or class_major == major_abbreviation):
            class_description = hit['_source']['Class Description']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number,
                "Major": class_major,
                "Year Number": year_num_string
            }
            results.append(result)
            unique_class_names.add(class_name)

    return results

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

@app.route('/majors.json')
def send_json():
    return send_from_directory('templates', 'majors.json')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    majorAbbreviation = request.form.get('majorDropdown')
    interests = request.form.get('textInterests')
    numYears = int(request.form.get('numYears'))
    geInterests = request.form.get('geInterests')

    # Map the major abbreviations to their full name
    mapped_major_abbreviation = map_major_abbreviation(majorAbbreviation)

    # Search for Major Courses that have been indexed in Elastic Search
    major_courses = search_courses("courses", interests, mapped_major_abbreviation, numYears)

    # Do the same thing but for GenEds
    gen_ed_courses = search_courses("geneds", geInterests, None, numYears)

    return render_template('submit_form.html', majorResults=major_courses, majorSearchParam=interests, genEdResults=gen_ed_courses, genEdSearchParam=geInterests)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
