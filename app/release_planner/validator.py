class ReleasePlannerValidator:
    def __init__(self):
        self._errors = []
        self._required_fields = ["team_capacity", "number_of_releases", "features"]
        return

    def validate(self, request):
        if not request.is_json:
            self.add_error("The release planning request should be JSON")
            return False
        for required_field in self._required_fields:
            if required_field not in request.json:
                error_message = str(required_field) + " is a required field"
                self.add_error(error_message)
                return False
        if not isinstance(request.json['team_capacity'], int):
            self.add_error("The team_capacity field must be an intger")
            return False
        if not isinstance(request.json['number_of_releases'], int):
            self.add_error("The number_of_releases field must be an intger")
            return False
        if not isinstance(request.json['features'], list):
            self.add_error("The features field must be an array")
            return False
        if (request.json['number_of_releases'] < 1) or (request.json['number_of_releases'] > 3):
            self.add_error("The number of releases should be between 1 and 3")
            return False
        if len(request.json['features']) < request.json['number_of_releases']:
            self.add_error("The number of features must be greater than or equal to the number of releases")
            return False

        feature_validator = FeatureValidator()
        for feature in request.json['features']:
            if not feature_validator.validate(feature):
                self.add_error(feature_validator.errors()[0])
                return False

        return True

    def add_error(self, error_message):
        self._errors.append(error_message)

    def errors(self):
        return self._errors

class FeatureValidator:
    def __init__(self):
        self._errors = []
        self._required_fields = ["id", "business_value", "effort", "priority"]
        return

    def validate(self, feature):
        if not isinstance(feature, dict):
            self.add_error("A feature must be represented as a JSON object")
            return False
        if len(feature) == 0:
            self.add_error("A feature object cannot be empty")
            return False
        for required_field in self._required_fields:
            if required_field not in feature:
                error_message = str(required_field) + " is a required field of a feature"
                self.add_error(error_message)
                return False
        if not isinstance(feature["id"], int):
            self.add_error("The ID field of a feature must be an integer")
            return False
        if not isinstance(feature["business_value"], int):
            self.add_error("The business_value field of feature:" + str(feature['id']) + " must be an integer")
            return False
        if not isinstance(feature["effort"], int):
            self.add_error("The effort field of feature:" + str(feature['id']) + " must be an integer")
            return False
        if not isinstance(feature["priority"], int):
            self.add_error("The priority field of feature:" + str(feature['id']) + " must be an integer")
            return False

        return True

    def add_error(self, error_message):
        self._errors.append(error_message)

    def errors(self):
        return self._errors

