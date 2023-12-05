# CSE5914-Capstone
Capstone Project

API Documentation:

The API URL is https://content.osu.edu/v2/classes/search

valid parameters are:

    q = can be blank, or cse for CSE Classes, ise for ISE Classes, etc.
    campus = col for Columbus, etc.
    p = page number, starting at 1
    term = 1222 for Spring 2022, etc.
    academic-career = ugrad (for undergrad only classes)
    subject = (blank, or any major)

A valid query would be:  https://content.osu.edu/v2/classes/search?q=&campus=col&p=1&term=1222

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

To run the website:
1. Open an command prompt in administrator and enter the command: docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.9.0
2. Run indexAllData.py.
3. Run queryData.py.
4. Open the deployed server in a web browser.
