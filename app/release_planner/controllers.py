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
    release_plans, metadata = planner.request_plans(request.json["features"], request.json["team_capacity"], request.json["number_of_releases"])

    response = {}
    response["data"] = release_plans
    response["metadata"] = metadata

    return jsonify(response), 201
