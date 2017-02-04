from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from validator import ReleasePlanRequestValidator
from planner import Planner

release_planner = Blueprint('release_planner', __name__, url_prefix = '/release_plans')

@release_planner.route('/', methods = ['GET'])
def get_index():
    return jsonify({'application': 'release_planner_service'})

@release_planner.route('/', methods = ['POST'])
def create_release_plans():
    validator = ReleasePlanRequestValidator()
    if not validator.validate(request.json):
        raise BadRequest(validator.errors()[0])

    planner = Planner()
    release_plans = planner.request_plans(request.json["features"], request.json["team_capacity"], request.json["number_of_releases"])
    return jsonify(release_plans), 201
