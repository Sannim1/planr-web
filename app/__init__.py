# Import flask and template operators
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS, cross_origin
from werkzeug.exceptions import BadRequest

# Define the WSGI application object
app = Flask(__name__, instance_relative_config=True)
CORS(app)

# Configurations
app.config.from_object('config')


@app.before_request
def before_request():
    if request.method not in ["POST", "PUT", "PATCH"]:
        return
    if not request.is_json:
        raise BadRequest("The Content-Type of the request body should be JSON")

# HTTP error handling


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    error_message = str(error.description)
    return make_response(jsonify({'error': error_message}), 400)

from app.release_planner.controllers import release_planner

app.register_blueprint(release_planner)
