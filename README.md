# Implögn Vísinței Datifing

[![CircleCI](https://circleci.com/gh/charlescsr/implogn-visintei-datifing.svg?style=svg)](https://circleci.com/gh/charlescsr/implogn-visintei-datifing) [![AGPL-3.0 License](https://img.shields.io/badge/license-AGPL-green.svg?style=flat)](LICENSE)

Platform to help with generating code for deployment of Data Science and ML models 

This is a Flask web app used to generate deployable code based around and ML model.

## Procedure:

* The user uploads the dataset
* The user selects the model from the dropdown list
* The requirements are sent to the server (Built on [FastAPI](https://github.com/tiangolo/fastapi)) where it is trained and returns the pickled model
* The HTML templates are also generated from the server.
* Finally the entire Flask application is zipped and sent to the user

## Setup

To set up this project, you require the following:

* Python (Preferably 3.8.x)
* Pipenv
  * Can be installed with ```python -m pip install pipenv```

Once all this is set up, just run:

```
$ pipenv shell
$ pipenv install
```
You have to first make sure the server is running first. You can find it [here](https://github.com/charlescsr/train_server)

Once the server is up and running, Start the web application by doing this:
```python app.py```
