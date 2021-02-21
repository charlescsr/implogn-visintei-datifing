from flask import Flask, render_template #Anything else from flask can be added here

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create')
def create():
    return render_template("create.html")

if __name__ == '__main__':
    app.run(port=5000, debug=True)