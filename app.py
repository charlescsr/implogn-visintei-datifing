from flask import Flask, render_template, send_file, request
import os
from pathlib import Path
import shutil

app = Flask(__name__)

main = "/home/codespace/workspace/fictional-octo-umbrella/"

app_file = """ 
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
"""

directory = "test_app"

path = os.path.join(main, directory)


def generate_code():
    os.mkdir(path)
    f = open(os.path.join(path, 'app.py'), 'w')
    f.write(app_file)
    f.close()


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create')
def create():
    return render_template("create.html")

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