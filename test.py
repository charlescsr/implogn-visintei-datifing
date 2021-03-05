import requests
import pickle
import numpy as np

site = "http://127.0.0.1:8000/create_html/"

csv_file = {"data": open('small_data.csv', 'rb')}

r = requests.post(site, files=csv_file)

print(r.status_code)
with open('templates.zip', 'wb') as f:
    f.write(r.content)