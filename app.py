from flask import Flask, render_template, send_file, request
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import shutil

app = Flask(__name__)

try:
    main = os.environ['LOCAL_PATH']

except Exception:
    main = os.environ['CS_PATH']

app_file = """ 
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
"""

base_html = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>{% block title %}<!-- Placeholder for Title -->{% endblock %}</title>
</head>

<body>    
    {% block content %}
    <!-- Placeholder for Page Content -->
    {% endblock %}
</body>

</html>
"""

directory = "test_app"
template_dir = "test_app/templates"
static_dir = "test_app/static"

path = os.path.join(main, directory)
template_path = os.path.join(main, template_dir)
static_path = os.path.join(main, static_dir)


def generate_code():
    file = request.files['dataset']
    file.save(secure_filename(file.filename))
    os.mkdir(path)
    os.mkdir(template_path)
    os.mkdir(static_path)
    data = file.filename
    shutil.move(data, static_path)
    f = open(os.path.join(path, 'app.py'), 'w')
    f.write(app_file)
    f.close()


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create')
def create():
    return render_template("create.html")

@app.route('/htm_create')
def htm_create():
    return render_template("htm_create.html")

@app.route('/generate', methods=["POST"])
def generate():
    generate_code()
    shutil.make_archive('application', 'zip', 'test_app')
    shutil.rmtree(path)
    f_name = Path('application.zip')

    return send_file(f_name, attachment_filename='application.zip', as_attachment=True)

@app.after_request
def delete_zip(response):
    if request.endpoint=="generate": 
        os.remove('application.zip')
    
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)