from app.release_planner.validator import ReleasePlanRequestValidator
import unittest

class ReleasePlanRequestValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.validator = ReleasePlanRequestValidator()

    def tearDown(self):
        pass

    def make_release_plan_request(self):
        return {
            "features": [
                {
                    "id": 1,
                    "priority": 1,
                    "business_value": 3,
                    "effort": 40
                },
                {
                    "id": 2,
                    "priority": 1,
                    "business_value": 3,
                    "effort": 40
                },
                {
                    "id": 3,
                    "priority": 1,
                    "business_value": 3,
                    "effort": 40
                },
                {
                    "id": 4,
                    "priority": 1,
                    "business_value": 3,
                    "effort": 40
                }
            ],
            "team_capacity": 100,
            "number_of_releases": 2
        }

    def test_validator_returns_true_for_a_valid_release_plan_request(self):
        release_plan_request = self.make_release_plan_request()

        self.assertTrue(self.validator.validate(release_plan_request))
        self.assertEquals(len(self.validator.errors()), 0)

    def test_validator_returns_false_if_features_are_not_specified(self):
        release_plan_request = self.make_release_plan_request()
        del release_plan_request["features"]

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("features is a required field" in self.validator.errors())

    def test_validator_returns_false_if_team_capacity_is_not_specified(self):
        release_plan_request = self.make_release_plan_request()
        del release_plan_request["team_capacity"]

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("team_capacity is a required field" in self.validator.errors())

    def test_validator_returns_false_if_number_of_releases_is_not_specified(self):
        release_plan_request = self.make_release_plan_request()
        del release_plan_request["number_of_releases"]

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("number_of_releases is a required field" in self.validator.errors())

    def test_validator_returns_false_if_team_capacity_is_not_an_integer(self):
        release_plan_request = self.make_release_plan_request()
        release_plan_request["team_capacity"] = "notaninteger"

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("The team_capacity field must be an integer" in self.validator.errors())

    def test_validator_returns_false_if_number_of_releases_is_not_an_integer(self):
        release_plan_request = self.make_release_plan_request()
        release_plan_request["number_of_releases"] = "notaninteger"

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("The number_of_releases field must be an integer" in self.validator.errors())

    def test_validator_returns_false_if_features_are_not_represented_as_a_list(self):
        release_plan_request = self.make_release_plan_request()
        release_plan_request["features"] = {}

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("The features field must be an array" in self.validator.errors())

    def test_validator_returns_false_if_number_of_releases_is_not_between_1_and_3(self):
        release_plan_request = self.make_release_plan_request()
        release_plan_request["number_of_releases"] = 10

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("The number of releases must be between 1 and 3" in self.validator.errors())

    def test_validator_returns_false_if_number_of_features_less_than_number_of_releases(self):
        release_plan_request = self.make_release_plan_request()
        del release_plan_request["features"][0]
        del release_plan_request["features"][1]
        release_plan_request["number_of_releases"] = 3

        self.assertFalse(self.validator.validate(release_plan_request))
        self.assertTrue("The number of features must be greater than or equal to the number of releases" in self.validator.errors())

    def test_validator_returns_false_if_any_of_the_features_is_invalid(self):
        release_plan_request = self.make_release_plan_request()
        release_plan_request["features"][0] = {}

        self.assertFalse(self.validator.validate(release_plan_request))

