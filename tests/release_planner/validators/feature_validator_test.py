from app.release_planner.validator import FeatureValidator
import unittest


class FeatureValidatorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.validator = FeatureValidator()

    def tearDown(self):
        pass

    def test_validator_returns_true_for_a_valid_feature(self):
        feature = {
            "id": 1,
            "business_value": 2,
            "effort": 20,
            "priority": 20
        }

        self.assertTrue(self.validator.validate(feature))
        self.assertEquals(len(self.validator.errors()), 0)

    def test_validator_returns_false_for_an_improperly_represented_feature(self):
        feature = []

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "A feature must be represented as a JSON object" in self.validator.errors())

    def test_validator_returns_false_for_an_empty_feature_object(self):
        feature = {}

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "A feature object cannot be empty" in self.validator.errors())

    def test_validator_returns_false_if_the_id_field_is_missing(self):
        feature = {
            "business_value": 2,
            "effort": 20,
            "priority": 20
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "ID is a required field of a feature" in self.validator.errors())

    def test_validator_returns_false_if_the_priority_field_is_missing(self):
        feature = {
            "id": 1,
            "business_value": 2,
            "effort": 20
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "priority is a required field of feature:1" in self.validator.errors())

    def test_validator_returns_false_if_the_business_value_field_is_missing(self):
        feature = {
            "id": 1,
            "effort": 20,
            "priority": 2
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "business_value is a required field of feature:1" in self.validator.errors())

    def test_validator_returns_false_if_the_effort_field_is_missing(self):
        feature = {
            "id": 1,
            "business_value": 20,
            "priority": 2
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "effort is a required field of feature:1" in self.validator.errors())

    def test_validator_returns_false_if_the_id_field_is_not_an_integer(self):
        feature = {
            "id": "notaninteger",
            "business_value": 20,
            "effort": 20,
            "priority": 2
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "The ID field of a feature must be an integer" in self.validator.errors())

    def test_validator_returns_false_if_the_business_value_field_is_not_an_integer(self):
        feature = {
            "id": 1,
            "business_value": "notaninteger",
            "effort": 20,
            "priority": 2
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "The business_value field of feature:1 must be an integer" in self.validator.errors())

    def test_validator_returns_false_if_the_effort_field_is_not_an_integer(self):
        feature = {
            "id": 1,
            "business_value": 2,
            "effort": "notaninteger",
            "priority": 2
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "The effort field of feature:1 must be an integer" in self.validator.errors())

    def test_validator_returns_false_if_the_priority_field_is_not_an_integer(self):
        feature = {
            "id": 1,
            "business_value": 2,
            "effort": 20,
            "priority": "notaninteger"
        }

        self.assertFalse(self.validator.validate(feature))
        self.assertTrue(
            "The priority field of feature:1 must be an integer" in self.validator.errors())
