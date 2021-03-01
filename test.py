import requests

site = "http://127.0.0.1:8000/model_set/"

csv_file = {"data": open('test.csv', 'rb')}

r = requests.post(site+"lr", files=csv_file)

print(r.status_code)
print(r.text)