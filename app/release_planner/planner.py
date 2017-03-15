from algorithms.evolve import Evolve

class Planner:
    def __init__(self):
        return

    def request_plans(self, features, team_capacity, num_releases):
        features = self.sanitize_features(features)
        planning_model = Evolve(features, num_releases, team_capacity)
        generated = planning_model.generate()
        generated_plans = generated["release_plans"]
        min_benefit = generated["min_benefit"]
        max_benefit = generated["max_benefit"]
        min_penalty = generated["min_penalty"]
        max_penalty = generated["max_penalty"]
        num_valid_generated_plans = generated["num_valid_release_plans"]

        release_plans = []
        for generated_plan in generated_plans:
            release_plans.append({
                "tradeoff": {
                    "priority": self.scale_penalty(generated_plan["penalty"], min_penalty, max_penalty),
                    "business_value": self.scale_benefit(generated_plan["benefit"], min_benefit, max_benefit)
                },
                "releases": self.transform_releases(generated_plan["releases"])
            })

        metadata = {}
        metadata["optimal_release_plans"] = len(release_plans)
        metadata["all_release_plans"] = num_valid_generated_plans

        return release_plans, metadata

    def sanitize_features(self, features):
        # loop through all of the features and check that a feature is not
        # preceded by or coupled with itself
        for feature in features:
            if "preceded_by" in feature:
                if feature["id"] == feature["preceded_by"]:
                    feature["preceded_by"] = None
            if "coupled_with" in feature:
                if feature["id"] == feature["coupled_with"]:
                    feature["coupled_with"] = None
        return features

    def scale_penalty(self, penalty, min_penalty, max_penalty):
        scaled_value = 1
        if max_penalty != min_penalty:
            scaled_value = (max_penalty - penalty) / ((max_penalty - min_penalty) * 1.0)
        return scaled_value * 100.

    def scale_benefit(self, benefit, min_benefit, max_benefit):
        scaled_value = 1
        if max_benefit != min_benefit:
            scaled_value = (benefit - min_benefit) / ((max_benefit - min_benefit) * 1.0)
        return scaled_value * 100.

    def transform_releases(self, generated_releases):
        releases = []
        for order, _features in generated_releases.items():
            features = []
            for feature_id in _features:
                features.append({"id": feature_id})
            releases.append({
                "order": order,
                "features": features
            })
        return releases
