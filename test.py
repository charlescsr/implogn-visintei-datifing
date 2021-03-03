import requests
import pickle
import numpy as np

site = "http://127.0.0.1:8000/model_set/"
X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
 
y = np.dot(X, np.array([1, 2])) + 3

csv_file = {"data": open('test.csv', 'rb')}

r = requests.post(site+"lr", files=csv_file)

print(r.status_code)

with open('model.pkl', 'wb') as fd:
    fd.write(r.content)

lr_clf = open('model.pkl', 'rb')
lr_mod = pickle.load(lr_clf)

acc_pickle = lr_mod.score(X, y)
print(acc_pickle)