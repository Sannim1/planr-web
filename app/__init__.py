# Import flask and template operators
from flask import Flask, make_response, jsonify

# Define the WSGI application object
app = Flask(__name__, instance_relative_config = True)

# Configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

from app.release_planner.controllers import release_planner

app.register_blueprint(release_planner)
