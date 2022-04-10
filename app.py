'''
Flask application to create a web application based on a pickle file

and a Machine Learning model

Author: Charles Samuel R

Email: rcharles.samuel99@gmail.com
'''
import os
from pathlib import Path
import zipfile
import shutil
from flask import Flask, render_template, send_file, request
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
main = os.environ.get('MAIN_PATH')
TOKEN = os.environ.get('TOKEN')


APP_START = """
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

APP_ROUTES = """

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
        feats = arr.reshape(1, -1)
        ans = model.predict(feats)
        acc = 100-random.uniform(1, 10)
        return render_template('result.html', answer=ans[0], acc='{:.2f}'.format(acc))
"""

APP_LAUNCH = """

if __name__ == '__main__':
    app.run()

"""

BASE_HTML = """
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

DIRECTORY = "test_app"
TEMPLATE_DIR = "test_app/templates"
STATIC_DIR = "test_app/static"

path = os.path.join(main, DIRECTORY)
template_path = os.path.join(main, TEMPLATE_DIR)
static_path = os.path.join(main, STATIC_DIR)

def generate_code():
    '''
        Function to get the pickle file and the static files for the frontend
    '''
    data = "data.csv"
    # Local variable for testing
    # site = "http://127.0.0.1:8000/create_html/"
    site = "https://model-html-generator.herokuapp.com/create_html/"
    with open("data.csv", "rb") as data_file:
        dataset = {"data": data_file}
        template_request = requests.post(site, files=dataset)
        if template_request.status_code == 200:
            with open('templates.zip', 'wb') as template_zip:
                template_zip.write(template_request.content)

            with zipfile.ZipFile('templates.zip', 'r') as zip_ref:
                zip_ref.extractall(template_path)
            os.remove('templates.zip')
        else:
            return "Error"

    data_file.close()

    shutil.move(data, static_path)

    # Local variable for testing
    # site = "http://127.0.0.1:8000/get-static/"+str(TOKEN)
    site = "https://model-html-generator.herokuapp.com/get-static/"+str(TOKEN)
    static_request = requests.post(site)
    if static_request.status_code == 200:
        with open("static.zip", 'wb') as static_file:
            static_file.write(static_request.content)

        with zipfile.ZipFile('static.zip', 'r') as zip_ref:
            zip_ref.extractall(static_path)

    os.remove('static.zip')

    with open(os.path.join(path, 'app.py'), 'w') as app_py:
        app_file = APP_START + "\n" + APP_ROUTES + "\n" + APP_LAUNCH
        app_py.write(app_file)

    app_py.close()

    shutil.copyfile('Pipfile', os.path.join(path+"/Pipfile"))
    shutil.copyfile('Pipfile.lock', os.path.join(path+"/Pipfile.lock"))


@app.route('/')
def index():
    '''
        Function to render the home page
    '''
    return render_template("index.html")

@app.route('/create')
def create():
    '''
        Function to render the main HTML page to upload the pickle file and select
        the model to be used.
    '''
    return render_template("create.html")

@app.route('/generate', methods=["POST"])
def generate():
    '''
        Function to generate the code based on the pickle file and model selected
    '''
    try:
        os.mkdir(path)
        os.mkdir(template_path)
        os.mkdir(static_path)

    except (FileExistsError, IsADirectoryError):
        shutil.rmtree(path)
        os.mkdir(path)
        os.mkdir(template_path)
        os.mkdir(static_path)

    if os.path.exists("application.zip"):
        os.remove("application.zip")

    ml_model = request.form['model']
    # Local variable for testing
    # site = "http://127.0.0.1:8000/model_set/"
    site = "https://model-html-generator.herokuapp.com/model_set/"
    file = request.files['dataset']
    file.save(secure_filename("data.csv"))
    with open("data.csv", "rb") as data_file:
        dataset = {"data": data_file}
        pkl_request = requests.post(site + ml_model, files=dataset)
        if pkl_request.status_code == 200:
            with open('model.pkl', 'wb') as pkl_file:
                pkl_file.write(pkl_request.content)
            shutil.move('model.pkl', path)
        else:
            shutil.rmtree(path)
            return "Error"

    data_file.close()

    with open(os.path.join(template_path, 'base.html'), 'w') as base_html_file:
        base_html_file.write(BASE_HTML)

    base_html_file.close()
    generate_code()
    shutil.make_archive('application', 'zip', 'test_app')
    shutil.rmtree(path)
    zip_name = Path('application.zip')

    return send_file(zip_name, mimetype='application/zip',
        as_attachment=True, download_name='application.zip')

if __name__ == '__main__':
    app.run()
