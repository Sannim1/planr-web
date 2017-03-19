class ReleasePlanRequestValidator:
    def __init__(self):
        self._errors = []
        self._required_fields = ["team_capacity", "number_of_releases", "features"]
        return

    def validate(self, release_plan_request):
        """
            Validate a JSON release plan request by checking the existence of required fields and
            that fields have an appropriate data type.
        """
        for required_field in self._required_fields:
            if required_field not in release_plan_request:
                error_message = str(required_field) + " is a required field"
                self.add_error(error_message)
                return False
        if not isinstance(release_plan_request['team_capacity'], int):
            self.add_error("The team_capacity field must be an integer")
            return False
        if not isinstance(release_plan_request['number_of_releases'], int):
            self.add_error("The number_of_releases field must be an integer")
            return False
        if not isinstance(release_plan_request['features'], list):
            self.add_error("The features field must be an array")
            return False
        if (release_plan_request['number_of_releases'] < 1) or (release_plan_request['number_of_releases'] > 3):
            self.add_error("The number of releases must be between 1 and 3")
            return False
        if len(release_plan_request['features']) < release_plan_request['number_of_releases']:
            self.add_error("The number of features must be greater than or equal to the number of releases")
            return False

        # instantitate a validator to handle the specifics of validating a Feature object
        feature_validator = FeatureValidator()
        feature_ids = []
        # validate required feature fields
        for feature in release_plan_request['features']:
            if not feature_validator.validate(feature):
                self.add_error(feature_validator.errors()[0])
                return False
            feature_ids.append(feature["id"])

        # validate optional feature fields
        for feature in release_plan_request['features']:
            if not feature_validator.validate_precedence(feature, feature_ids):
                self.add_error(feature_validator.errors()[0])
                return False

            if not feature_validator.validate_coupling(feature, feature_ids):
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
        self._required_fields = ["business_value", "effort", "priority"]
        return

    def validate(self, feature):
        """
            Validate a feature object by checking the existence of required fields and
            that fields have an appropriate data type.
        """
        if not isinstance(feature, dict):
            self.add_error("A feature must be represented as a JSON object")
            return False
        if len(feature) == 0:
            self.add_error("A feature object cannot be empty")
            return False
        if "id" not in feature:
            self.add_error("ID is a required field of a feature")
            return False
        if not isinstance(feature["id"], int):
            self.add_error("The ID field of a feature must be an integer")
            return False
        for required_field in self._required_fields:
            if required_field not in feature:
                error_message = str(required_field) + " is a required field of feature:" + str(feature['id'])
                self.add_error(error_message)
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

    def validate_precedence(self, feature, feature_ids):
        if "preceded_by" not in feature:
            return True
        if not isinstance(feature["preceded_by"], int):
            self.add_error("The preceded_by field of feature:{0} must be an integer".format(feature["id"]))
            return False
        if feature["preceded_by"] not in feature_ids:
            self.add_error("Feature:{0} can only be preceded by a feature in the same release plan request".format(feature["id"]))
            return False

        return True

    def validate_coupling(self, feature, feature_ids):
        if "coupled_with" not in feature:
            return True
        if not isinstance(feature["coupled_with"], int):
            self.add_error("The coupled_with field of feature:{0} must be an integer".format(feature["id"]))
            return False
        if feature["coupled_with"] not in feature_ids:
            self.add_error("Feature:{0} can only be coupled with a feature in the same release plan request".format(feature["id"]))
            return False

        return True

    def add_error(self, error_message):
        self._errors.append(error_message)

    def errors(self):
        return self._errors
