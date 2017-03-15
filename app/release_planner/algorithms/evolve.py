import random
import sys

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

class Evolve:
    def __init__(self, features, num_releases, team_capacity):
        self.transform_features(features)
        self.num_features = len(features)
        self.num_releases = num_releases
        self.team_capacity = team_capacity
        self.min_priority = 4

        self.initialize_algorithm()

    def initialize_algorithm(self):
        creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
        creator.create("Individual", list, fitness=creator.Fitness)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_feat", random.randint, 0, self.num_releases)

        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_feat, self.num_features)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.evalReleasePlan)
        self.toolbox.register("mate", self.cxSet)
        self.toolbox.register("mutate", self.mutSet)
        self.toolbox.register("select", tools.selNSGA2)

    def team_capacity_exceeds_sum_effort(self):
        sum_features_effort = 0
        for index in self.features:
            sum_features_effort += self.features[index][0]

        if self.team_capacity >= sum_features_effort:
            return True;
        return False;


    def generate(self):

        if self.team_capacity_exceeds_sum_effort():
            # the team capacity exceeds the sum of the required effort,
            # hence all of the features can be implemented in the first release
            release_plan = [1] * self.num_features
            release_plans = []
            min_penalty, max_penalty = 0, 0
            min_benefit, max_benefit = 100, 100
            release_plans.append({
                "penalty": min_penalty,
                "benefit": max_benefit,
                "releases": self.map_features_to_releases(release_plan)
            })
            return {
                "release_plans": release_plans,
                "min_penalty": min_penalty,
                "max_penalty": max_penalty,
                "min_benefit": min_benefit,
                "max_benefit": max_benefit,
                "num_valid_release_plans": 1
            }

        num_generations = 100
        population_size = 50
        num_children = 100
        crossover_rate = 0.7
        mutation_rate = 0.3

        population = self.toolbox.population(n = population_size)
        pareto_front = tools.ParetoFront()
        halloffame = tools.HallOfFame(num_generations*population_size)

        algorithms.eaMuPlusLambda(population, self.toolbox, population_size, num_children, crossover_rate, mutation_rate, num_generations, halloffame = halloffame, verbose = False)
        pareto_front.update(halloffame)

        release_plans = []
        min_penalty, max_penalty = 0, 0
        min_benefit, max_benefit = 0, 0
        for release_plan in pareto_front:
            penalty, benefit = release_plan.fitness.values

            if penalty < min_penalty: min_penalty = penalty
            if penalty > max_penalty: max_penalty = penalty

            if benefit < min_benefit: min_benefit = benefit
            if benefit > max_benefit: max_benefit = benefit

            release_plans.append({
                "penalty": penalty,
                "benefit": benefit,
                "releases": self.map_features_to_releases(release_plan)
            })

        return {
            "release_plans": release_plans,
            "min_penalty": min_penalty,
            "max_penalty": max_penalty,
            "min_benefit": min_benefit,
            "max_benefit": max_benefit,
            "num_valid_release_plans": len(halloffame)
        }

    def transform_features(self, features):
        self.features = {}
        self.feature_id_to_index = {}
        for index, feature in enumerate(features):
            preceded_by, coupled_with = None, None
            if "preceded_by" in feature:
                preceded_by = feature["preceded_by"]
            if "coupled_with" in feature:
                coupled_with = feature["coupled_with"]
            transformed_feature = (feature["effort"], feature["priority"],
                    feature["business_value"], feature["id"],
                    preceded_by, coupled_with)
            self.features[index] = transformed_feature
            self.feature_id_to_index[feature["id"]] = index
        return

    def evalReleasePlan(self, individual):
        effort = [0]*(self.num_releases+1)
        penalty = 0
        benefit = 0

        for feature, release in enumerate(individual):
            if self.features[feature][4] != None and self.features[feature][4] != self.features[feature][3]:
                precedenceIndex = self.feature_id_to_index[self.features[feature][4]]
                precedenceRelease = individual[precedenceIndex]
                if release < precedenceRelease or (release > precedenceRelease and precedenceRelease == 0):
                    return sys.maxint, 0

            if self.features[feature][5] != None and self.features[feature][5] != self.features[feature][3]:

                couplingIndex = self.feature_id_to_index[self.features[feature][5]]
                couplingRelease = individual[couplingIndex]
                if release != couplingRelease:
                    return sys.maxint, 0

            if release !=0:
                benefit += self.features[feature][2]*(self.num_releases - release + 1)
                effort[release] += self.features[feature][0]
                penalty += (self.min_priority + 1 - self.features[feature][1])*(release)
            else:
                penalty += (self.min_priority + 1 - self.features[feature][1])*(self.num_releases + 1)

            if effort[release] > self.team_capacity :
                return sys.maxint, 0


        return penalty, benefit


    def cxSet(self, ind1, ind2):
        """Apply a crossover operation on input sets."""

        if (self.num_features <= 2):
        	return ind1, ind2

        result_1 = ind1

        result_2 = ind2

        rnd1, rnd2 = random.sample(range(0, self.num_features - 1), 2)

        result_1[rnd1] = ind2[rnd1]
        result_1[rnd2] = ind2[rnd2]

        result_2[rnd1] = ind1[rnd1]
        result_2[rnd2] = ind1[rnd2]

        return result_1, result_2



    def mutSet(self, individual):

        individual[random.randint(0, self.num_features - 1)] = random.randint(0, self.num_releases)
        return individual,

    def map_features_to_releases(self, release_plan):
        releases = {}
        for index, release in enumerate(release_plan):
            if release not in releases:
                releases[release] = []
            feature_id = self.features[index][3]
            releases[release].append(feature_id)
        return releases
