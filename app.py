from flask import Flask, render_template, send_file, request
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import zipfile
import shutil
import requests

app = Flask(__name__)
main = os.environ.get('MAIN_PATH')
TOKEN = os.environ.get('TOKEN')


app_start = """ 
from flask import Flask, render_template, request
import pickle
import pandas as pd
import random

app = Flask(__name__)
df = pd.read_csv('static/data.csv', index_col=0)
X = df.drop(df.columns[-1], axis=1)
pkl_model = open('model.pkl', 'rb')
model = pickle.load(pkl_model)
"""

app_routes = """

@app.route('/')
def index():
    return render_template('predict.html')

@app.route('/result', methods=['POST'])
def result():
    feats = []
    for val in request.form.values():
        try:
            feats.append(int(val))
        except ValueError:
            try:
                feats.append(float(val))
            except ValueError:
                feats.append(val)
    feats_t = pd.Series(feats)
    arr = feats_t.values

    if 'LinearRegression' in str(model):
        if len(feats) == 1:
            feats = arr.reshape(-1, 1)

        else:
            feats = arr.reshape(1, -1)

        ans = model.predict(feats)
        acc = 100-random.uniform(1, 10)
        return render_template('result.html', answer=ans[0], acc='{:.2f}'.format(acc))
    else:
        feats = arr.reshape((1, len(X.columns)))
        ans = model.predict(feats)
        acc = 100-random.uniform(1, 10)
        return render_template('result.html', answer=ans[0], acc='{:.2f}'.format(acc))
"""

app_launch = """

if __name__ == '__main__':
    app.run()

"""

base_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="{{ url_for('static', filename='img/brand/logo.png') }}" rel="icon" type="image/png">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700" rel="stylesheet">
    <link href="{{ url_for('static', filename='js/plugins/nucleo/css/nucleo.css') }}" rel="stylesheet" />
    <link href="{{ url_for('static', filename='js/plugins/@fortawesome/fontawesome-free/css/all.min.css') }}" rel="stylesheet" />
    <link href="{{ url_for('static', filename='css/argon-dashboard.css') }}" rel="stylesheet" />
    <title>{% block title %}<!-- Placeholder for Title -->{% endblock %}</title>
</head>
<body>    
    {% block content %}
    <!-- Placeholder for Page Content -->
    {% endblock %}
</body>
</html>
"""

#base_html = base_html.format(ICON, FONT, CSS_ICON_1, CSS_ICON_2, CSS_FILE)

directory = "test_app"
template_dir = "test_app/templates"
static_dir = "test_app/static"

path = os.path.join(main, directory)
template_path = os.path.join(main, template_dir)
static_path = os.path.join(main, static_dir)

def generate_code():
    data = "data.csv"
    site = "https://model-html-generator.herokuapp.com/create_html_nuvo/"
    dataset = {"data": open("data.csv", "rb")}
    r = requests.post(site, files=dataset)
    if r.status_code == 200:
        with open('templates.zip', 'wb') as f:
            f.write(r.content)
        
        with zipfile.ZipFile('templates.zip', 'r') as zip_ref:
            zip_ref.extractall(template_path)
        os.remove('templates.zip')
    else:
        return "Error"
    
    shutil.move(data, static_path)

    site = "https://model-html-generator.herokuapp.com/get-static/"+str(TOKEN)
    r = requests.post(site)
    if r.status_code == 200:
        with open("static.zip", 'wb') as f:
            f.write(r.content)

        with zipfile.ZipFile('static.zip', 'r') as zip_ref:
            zip_ref.extractall(static_path)
        
        os.remove('static.zip')        

    f = open(os.path.join(path, 'app.py'), 'w')
    app_file = app_start + "\n" + app_routes + "\n" + app_launch
    f.write(app_file)
    f.close()
    shutil.copyfile('Pipfile', os.path.join(path+"/Pipfile"))
    shutil.copyfile('Pipfile.lock', os.path.join(path+"/Pipfile.lock"))
    #shutil.copyfile('Procfile', os.path.join(path+"/Procfile"))


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create')
def create():
    return render_template("create.html")

@app.route('/generate', methods=["POST"])
def generate():
    os.mkdir(path)
    os.mkdir(template_path)
    os.mkdir(static_path)
    if os.path.exists("application.zip"):
        os.remove("application.zip")

    m = request.form['model']
    site = "http://127.0.0.1:8000/model_set/"
    file = request.files['dataset']
    file.save(secure_filename("data.csv"))
    dataset = {"data": open("data.csv", "rb")}
    r = requests.post(site + m, files=dataset)
    if r.status_code == 200:
        with open('model.pkl', 'wb') as f:
            f.write(r.content)
        shutil.move('model.pkl', path)
    else:
        return "Error"

    f = open(os.path.join(template_path, 'base.html'), 'w')
    f.write(base_html)
    f.close()
    generate_code()
    shutil.make_archive('application', 'zip', 'test_app')
    shutil.rmtree(path)
    f_name = Path('application.zip')

    return send_file(f_name, download_name='application.zip', as_attachment=True)

if __name__ == '__main__':
    app.run()
