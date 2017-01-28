from flask import Blueprint, request, jsonify
from validator import ReleasePlannerValidator
from werkzeug.exceptions import BadRequest

release_planner = Blueprint('release_planner', __name__, url_prefix = '/release_plans')

@release_planner.route('/', methods = ['GET'])
def get_index():
    return jsonify({'application': 'release_planner_service'})

@release_planner.route('/', methods = ['POST'])
def create_release_plans():
    validator = ReleasePlannerValidator()
    if not validator.validate(request):
        raise BadRequest(validator.errors()[0])

    return jsonify(request.json), 201
