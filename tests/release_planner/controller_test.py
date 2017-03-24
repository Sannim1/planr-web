__author__ = "Abdulmusawwir Sanni"
from app import app
import unittest
import json


class ReleasePlannerRouteTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_index_route_returns_ok(self):
        result = self.app.get("release_plans/")

        self.assertEquals(result.status_code, 200)
        self.assertEquals(
            result.headers.get("Content-Type"), "application/json")

    def test_release_plan_requests_are_accepted(self):
        release_plan_request = json.dumps({
            "features": [
                {
                    "id": 1,
                    "priority": 10,
                    "business_value": 2,
                    "effort": 40
                },
                {
                    "id": 2,
                    "priority": 10,
                    "business_value": 2,
                    "effort": 40
                }
            ],
            "team_capacity": 300,
            "number_of_releases": 2
        })

        result = self.app.post("release_plans/",
                               data=release_plan_request,
                               content_type="application/json"
                               )

        self.assertEquals(result.status_code, 201)
        self.assertEquals(
            result.headers.get("Content-Type"), "application/json")

        response_body = json.loads(result.data)

        self.assertTrue("data" in response_body)
        self.assertTrue("metadata" in response_body)

        release_plan_one = response_body["data"][0]

        self.assertTrue("tradeoff" in release_plan_one)
        self.assertTrue("priority" in release_plan_one["tradeoff"])
        self.assertTrue("business_value" in release_plan_one["tradeoff"])
        self.assertTrue(
            isinstance(release_plan_one["tradeoff"]["priority"], float))
        self.assertTrue(
            isinstance(release_plan_one["tradeoff"]["business_value"], float))

        self.assertTrue("releases" in release_plan_one)
        self.assertTrue(len(release_plan_one["releases"]) <= 2)

        self.assertTrue("order" in release_plan_one["releases"][0])
        self.assertTrue("features" in release_plan_one["releases"][0])

        self.assertTrue("id" in release_plan_one["releases"][0]["features"][0])

    def test_non_JSON_release_plan_request_results_in_a_400_error(self):
        result = self.app.post("release_plans/", data="")

        self.assertEquals(result.status_code, 400)
        self.assertEquals(
            result.headers.get("Content-Type"), "application/json")

        response_body = json.loads(result.data)
        self.assertTrue("error" in response_body)

    def test_invalid_release_plan_requests_result_in_a_400_error(self):
        invalid_release_plan_request = json.dumps({
            "features": [
                {
                    "id": 1,
                    "priority": 10,
                    "business_value": 2,
                    "effort": 40
                },
                {
                    "id": 2,
                    "priority": 10,
                    "business_value": 2,
                    "effort": 40
                }
            ],
            "team_capacity": 300
        })

        result = self.app.post("release_plans/",
                               data=invalid_release_plan_request,
                               content_type="application/json"
                               )

        self.assertEquals(result.status_code, 400)
        self.assertEquals(
            result.headers.get("Content-Type"), "application/json")

        response_body = json.loads(result.data)
        self.assertTrue("error" in response_body)
