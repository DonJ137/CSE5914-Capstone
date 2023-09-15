#To run Elastic Search Locally: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0


#Connect to ES Cluster
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elastic:ttf6n-dJr9VVhE62JUX=@localhost:9200")
es.info().body


#Create an index for indexing documents
mappings = {
        "properties": {
            "Class Type": {"type": "text"},
            "Class Number": {"type": "integer"},
            "Class Name": {"type": "text"},
            "Class Summary": {"type": "text"},
    }
}

es.indices.create(index="classes", mappings=mappings)


#Get the information from the relevant url by making a request call to the API
import requests
import json

url = "https://content.osu.edu/v2/classes/search?q=#CSE&campus=col&term=2023"
r = requests.get(url)
content = r.json()
print(content)
