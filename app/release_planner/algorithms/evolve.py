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

    def generate(self):
        num_generations = 100
        population_size = 50
        num_children = 100
        crossover_rate = 0.7
        mutation_rate = 0.3

        population = self.toolbox.population(n = population_size)
        pareto_front = tools.ParetoFront()


        algorithms.eaMuPlusLambda(population, self.toolbox, population_size, num_children, crossover_rate, mutation_rate, num_generations, halloffame = pareto_front, verbose = False)

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
            "max_benefit": max_benefit
        }


    def transform_features(self, features):
        self.features = {}
        for index, feature in enumerate(features):
            self.features[index] = (feature["effort"], feature["priority"],
                    feature["business_value"], feature["id"],
                    feature["preceded_by"], feature["coupled_with"])
        return

    def getFeatureIndex(self, featureID):
        for i in range(len(self.features)):
            if self.features[i][3] == featureID:
                return i
        return None

    def evalReleasePlan(self, individual):
        effort = [0]*(self.num_releases+1)
        penalty = 0
        benefit = 0

        

        sum_features_effort = 0
        is_all_features_on_first_release = True
        for feature, release in enumerate(individual):
            sum_features_effort += self.features[feature][0]
            if release != 1:
                is_all_features_on_first_release = False

        if self.team_capacity >= sum_features_effort and not is_all_features_on_first_release:
            return 10000,0

        
        for feature, release in enumerate(individual):
            if self.features[feature][4] != None:
                precedenceIndex = getFeatureIndex(self.features[feature][4])
                precedenceRelease = individual[precedenceIndex]
                if release < precedenceRelease:
                    return sys.maxint, 0

            if self.features[feature][5] != None:
                couplingIndex = getFeatureIndex(self.features[feature][5])
                couplingRelease = individual[precedenceIndex]
                if release != precedenceRelease:
                    return sys.maxint, 0

            if release!=0:
                benefit += self.features[feature][2]*(self.num_releases - release + 1)
                effort[release] += self.features[feature][0]
            if effort[release] > self.team_capacity :
                return sys.maxint, 0
                
            for feature2, release2 in enumerate(individual):
                if feature2 < feature:
                    if release == 0 or release2 == 0:
                        if release == 0:
                            penalty += self.features[feature][1]*self.num_releases
                        if release2 == 0:
                            penalty += self.features[feature2][1]*self.num_releases
                    elif (self.features[feature][1]-self.features[feature2][1])*(release - release2) > 0:
                        penalty += 0
                    elif release == release2:
                        penalty += abs(self.features[feature][1]-self.features[feature2][1])
                    elif self.features[feature][1] == self.features[feature2][1]:
                        penalty += abs(release - release2)
                    else:
                        penalty += (self.features[feature][1]-self.features[feature2][1])*(release2 - release)
                        
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
