# Import flask and template operators
from flask import Flask, make_response, jsonify
import werkzeug

# Define the WSGI application object
app = Flask(__name__, instance_relative_config = True)

# Configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(error):
    error_message = str(error.description)
    return make_response(jsonify({'error': error_message}), 400)

from app.release_planner.controllers import release_planner

app.register_blueprint(release_planner)
