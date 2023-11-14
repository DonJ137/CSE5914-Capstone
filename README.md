# CSE5914-Capstone
Capstone Project

https://content.osu.edu/v2/classes/search?q=#CSE&campus=col&term=2023

API Documentation


The API URL is https://content.osu.edu/v2/classes/search

valid parameters are:

    q=   (can be blank, or cse for CSE Classes)
    campus=   (col for Columbus)
    p=  (page #, starting at 1)
    term=  (1222 for Spring 2022)
    academic-career=ugrad (for undergrad only classes)
    subject=   (blank, or cse)

A valid query would be:  https://content.osu.edu/v2/classes/search?q=&campus=col&p=1&term=1222

For running the program, first run index_data.py and loadGenEdsInES.py. Then run query_data.py afterwards.
