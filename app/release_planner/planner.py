from algorithms.evolve import Evolve
class Planner:
    def __init__(self):
        return

    def request_plans(self, features, team_capacity, num_releases):
        planning_model = Evolve(features, num_releases, team_capacity)
        generated_plans, max_penalty, max_benefit = planning_model.generate()

        release_plans = []
        for generated_plan in generated_plans:
            release_plans.append({
                "optimization_criteria": self.scale_penalty(generated_plan["penalty"], max_penalty),
                "releases": self.transform_releases(generated_plan["releases"])
            })

        return release_plans

    def scale_penalty(self, penalty, max_penalty):
        return (1 - (penalty / (max_penalty * 1.0)))

    def scale_benefit(self, benefit, max_benefit):
        return benefit / (max_benefit * 1.0)

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
