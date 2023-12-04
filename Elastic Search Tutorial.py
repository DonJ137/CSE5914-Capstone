#To run Elastic Search Locally: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0

#Run 'pip install -r requirements.txt' to ensure all dependencies have been downloaded

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
    # Get data from the form
    majorAbbreviation = request.form.get('majorDropdown')
    interests = request.form.get('textInterests')

    major_abbreviation_mapping = {
    "Accounting": "ACCTMIS",
    "Actuarial Science": "ACADAFF",
    "Aerospace Engineering": "AEROENG",
    "African American and African Studies": "AFAMAST",
    "Agribusiness and Applied Economics": "AEDECON",
    "Agricultural Communication": "AGRCOMM",
    "Agricultural Systems Management": "AGSYSMGT",
    "Ancient History and Classics": "CLASSICS",
    "Animal Sciences": "ANIMSCI",
    "Anthropology": "ANTHROP",
    "Arabic": "ARABIC",
    "Architecture": "ARCH",
    "Art": "ART",
    "Art Education": "ARTEDUC",
    "Astronomy and Astrophysics": "ASTRON",
    "Biochemistry": "BIOCHEM",
    "Biology": "BIOLOGY",
    "Biomedical Engineering": "BIOMEDE",
    "Chemical Engineering": "CHBE",
    "Chemistry": "CHEM",
    "Chinese": "CHINESE",
    "City and Regional Planning": "CRPLAN",
    "Civil Engineering": "CIVILEN",
    "Classics": "CLASSICS",
    "Communication": "COMM",
    "Comparative Studies": "COMPSTD",
    "Computer and Information Science": "CSE",
    "Computer Science and Engineering": "CSE",
    "Construction Systems Management": "CONSYSMT",
    "Criminology and Criminal Justice Studies": "CRIMJUST",
    "Dance": "DANCE",
    "Dental Hygiene": "DENTHYG",
    "Industrial Design": "DESIGN",
    "Interior Design": "DESIGN",
    "Visual Communication Design": "DESIGN",
    "Economics": "ECON",
    "Electrical and Computer Engineering": "ECE",
    "Engineering Physics": "ENGRPHY",
    "English": "ENGLISH",
    "Entomology": "ENTOMOL",
    "Environmental Engineering": "ENVENG",
    "Environmental Policy and Decision Making": "ESEPOL",
    "Environmental Science": "ENVSCI",
    "Evolution and Ecology": "EVOL",
    "Exercise Science Education": "EXEREDUC",
    "Film Studies": "FILMSTD",
    "Finance": "FINANCE",
    "Food Business Management": "FDBUSMGT",
    "Food Science and Technology": "FDSCITECH",
    "Food, Agricultural and Biological Engineering": "FABENG",
    "Forestry, Fisheries and Wildlife": "FFW",
    "French": "FRENCH",
    "Geography": "GEOG",
    "Earth Sciences": "EARTHSCI",
    "German": "GERMAN",
    "Health Information Management and Systems": "HIMS",
    "Health Sciences": "HLTHSC",
    "History": "HISTORY",
    "History of Art": "HISTART",
    "Hospitality Management": "HOSPMGT",
    "Human Development and Family Science": "HDFSCI",
    "Human Nutrition": "HN",
    "Human Resources": "HR",
    "Industrial and Systems Engineering": "ISE",
    "Information Systems": "IS",
    "International Business": "INTLBUS",
    "International Studies": "INTLSTDS",
    "Islamic Studies": "ISLAM",
    "Italian": "ITALIAN",
    "Japanese": "JAPANESE",
    "Journalism": "JOURNAL",
    "Korean": "KOREAN",
    "Landscape Architecture": "LARCH",
    "Linguistics": "LING",
    "Logistics Management": "LOGMGT",
    "Marketing": "MKTG",
    "Materials Science and Engineering": "MSE",
    "Mathematics": "MATH",
    "Mechanical Engineering": "MECHENG",
    "Medical Laboratory Science": "MEDLABSC",
    "Medieval and Renaissance Studies": "MEDREN",
    "Microbiology": "MICROBIO",
    "Modern Greek": "MODG",
    "Molecular Genetics": "MOLGEN",
    "Nursing": "NURSING",
    "Operations Management": "OPMT",
    "Natural Resource Management": "NRMT",
    "Philosophy": "PHILOS",
    "Physics": "PHYSICS",
    "Political Science": "POLITSC",
    "Portuguese": "PORTGSE",
    "Pre-Dentistry": "PRE-DENT",
    "Pre-Pharmacy": "PRE-PHARM",
    "Pre-Law": "PRE-LAW",
    "Pre-Medicine": "PRE-MED",
    "Pre-Optometry": "PRE-OPT",
    "Pre-Veterinary Medicine": "PRE-VETMED",
    "Professional Golf Management": "PGM",
    "Psychology": "PSYCH",
    "Radiologic Sciences and Therapy": "RADSCITHE",
    "Real Estate and Urban Analysis": "REUA",
    "Respiratory Therapy": "RESPITHE",
    "Insurance": "INSUR",
    "Russian": "RUSSIAN",
    "Social Work": "SOCWORK",
    "Sociology": "SOCIO",
    "Spanish": "SPANISH",
    "Education – Special Education": "ED-SPECED",
    "Speech and Hearing Science": "SPHHRNG",
    "Sport Industry": "SPORTIND",
    "Education – Technical Education and Training": "ED-TECHED",
    "Theatre": "THEATRE",
    "Welding Engineering": "WELDENG",
    "Women's, Gender and Sexuality Studies": "WGSST",
    "World Literatures": "WRLIT",
    "Zoology": "ZOOL"
}

    majorAbbreviation = major_abbreviation_mapping.get(majorAbbreviation)

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
    searchParams = []
    searchParams.append(majorAbbreviation + " 2")
    searchParams.append(majorAbbreviation + " 3")
    searchParams.append(majorAbbreviation + " 4")
    searchParams.append(majorAbbreviation + " 5")
    searchParam = interests

    courseQuery = {
        "match": {
            "Class Description": searchParam
        }
    }

    response = es.search(index="courses", query=courseQuery, size=100)  
    unique_class_names = set()
    results = []


    for hit in response['hits']['hits']:
        class_name = hit['_source']['Class Name']
        class_number = hit['_source']['Class Number']
        if class_name is not None and class_number is not None and class_name not in unique_class_names:
            class_description = hit['_source']['Class Description']
            result = {
                "Class Name": class_name,
                "Class Description": class_description,
                "Class Number": class_number
            }
            results.append(result)
            unique_class_names.add(class_name)

    return jsonify(results=results)


if __name__ == '__main__':
    app.run(debug=True)