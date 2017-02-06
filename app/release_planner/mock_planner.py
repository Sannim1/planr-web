import random

class Planner:
    def __init__(self):
        self._optimization_criteria = [0.2, 0.5, 0.8]
        return

    def request_plans(self, features, team_capacity, number_of_releases):
        release_plans = []
        for e in xrange(3):
            mock_releases = self.get_mock_releases(features, number_of_releases)
            release_plans.append({
                "optimization_criteria": self._optimization_criteria[e],
                "releases": mock_releases
            })
        return release_plans

    def get_mock_releases(self, features, number_of_releases):
        releases = []
        features_per_release = len(features) / number_of_releases
        features = list(features)
        for e in xrange(1, number_of_releases + 1):
            _features = features
            if e != number_of_releases:
                _features = random.sample(features, features_per_release)
                for _f in _features:
                    features.remove(_f)

            releases.append({
                "order": e,
                "features": _features
            })
        return releases
