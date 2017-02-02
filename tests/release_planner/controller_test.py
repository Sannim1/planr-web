from app import app
import unittest, json

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
        self.assertEquals(result.headers.get("Content-Type"), "application/json")

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
            data = release_plan_request,
            content_type = "application/json"
        )

        self.assertEquals(result.status_code, 201)
        self.assertEquals(result.headers.get("Content-Type"), "application/json")
