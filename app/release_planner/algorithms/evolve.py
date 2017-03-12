import random
import sys

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

class Evolve:
    def __init__(self, features, num_releases, team_capacity):
        self.transform_features(features)
        self.features_for_initial_release_plan = []
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

        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.get_feature_for_initial_release_plan, self.num_features)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.evalReleasePlan)
        self.toolbox.register("mate", self.cxSet)
        self.toolbox.register("mutate", self.mutSet)
        self.toolbox.register("select", tools.selNSGA2)

    def get_feature_for_initial_release_plan(self):
        if len(self.features_for_initial_release_plan) == 0:
            self.features_for_initial_release_plan = self.get_initial_release_plan()
        return self.features_for_initial_release_plan.pop(0)

    def get_initial_release_plan(self):
        implemented_features = []
        feasible_features = self.initial_feasible_features[:]
        release_plan = [0] * len(self.features)
        # initialize remaining effort with team capacity
        remaining_effort = {}
        for index in xrange(1, self.num_releases + 1):
            remaining_effort[index] = self.team_capacity

        for release_number in xrange(1, self.num_releases + 1):
            while True:
                if len(feasible_features) == 0:
                    break
                random_index = random.randint(0, len(feasible_features) - 1)
                random_feasible_feature = feasible_features[random_index]
                combined_effort = self.get_combined_effort(random_feasible_feature)
                if remaining_effort[release_number] < combined_effort:
                    break
                coupled_features = self.get_coupled_features(random_feasible_feature)
                dependent_features = []
                for coupled_feature in coupled_features:
                    release_plan[coupled_feature] = release_number
                    implemented_features.append(coupled_feature)
                    dependent_features += self.get_depending_features(coupled_feature)
                for dependent_feature in dependent_features:
                    if not self.is_feasible_feature(dependent_feature, implemented_features):
                        continue
                    dependent_couple = self.get_coupled_features(dependent_feature)
                    min_dependent_couple = min(dependent_couple)
                    if min_dependent_couple not in feasible_features:
                        feasible_features.append(min_dependent_couple)
                del feasible_features[random_index]
                remaining_effort[release_number] -= combined_effort
        return release_plan

    def get_combined_effort(self, feature_index):
        if feature_index not in self.coupling_map:
            return self.features[feature_index][0]
        combined_effort = 0
        for coupled_feature in self.coupling_map[feature_index]:
            combined_effort += self.features[coupled_feature][0]
        return combined_effort

    def get_coupled_features(self, feature_index):
        if feature_index not in self.coupling_map:
            return [feature_index]
        return self.coupling_map[feature_index]

    def get_depending_features(self, feature_index):
        if feature_index not in self.precedence_map:
            return []
        return self.precedence_map[feature_index]

    def is_feasible_feature(self, feature_index, implemented_features):
        coupled_features = self.get_coupled_features(feature_index)
        for feature in coupled_features:
            preceded_by = self.features[feature][4]
            if preceded_by == None:
                continue
            preceded_by_index = self.feature_id_to_index[preceded_by]
            if preceded_by_index not in implemented_features:
                return False
        return True

    def team_capacity_exceeds_sum_effort(self):
        sum_features_effort = 0
        for index in self.features:
            sum_features_effort += self.features[index][0]

        if self.team_capacity >= sum_features_effort:
            return True;
        return False;

    def custom_algorithm(self, pop, toolbox, mu, CXPB, MUTPB, NGEN, halloffame):
        # Evaluate the entire population
        fitnesses = map(toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        halloffame.update(pop)

        for g in range(NGEN):
            # Select the next generation individuals
            selected_population = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            selected_population = map(toolbox.clone, selected_population)

            # Apply crossover and mutation
            offspring = algorithms.varAnd(selected_population, toolbox, CXPB, MUTPB)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # The population is replaced by selected population and offspring
            pop[:] = toolbox.select(selected_population + offspring, mu)

            # Insert best individuals in the halloffame
            halloffame.update(pop)

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
        # num_children = 100
        crossover_rate = 0.9
        mutation_rate = 0.2

        population = self.toolbox.population(n = population_size)
        pareto_front = tools.ParetoFront()
        halloffame = tools.HallOfFame(num_generations*population_size)

        self.custom_algorithm(population, self.toolbox, population_size, crossover_rate, mutation_rate, num_generations, halloffame)
        pareto_front.update(halloffame)

        release_plans = []
        min_penalty, max_penalty = -1, 0
        min_benefit, max_benefit = -1, 0
        for release_plan in pareto_front:
            penalty, benefit = release_plan.fitness.values

            if penalty < min_penalty or min_penalty == -1: min_penalty = penalty
            if penalty > max_penalty: max_penalty = penalty

            if benefit < min_benefit or min_benefit == -1: min_benefit = benefit
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
        self.create_coupling_map()
        self.create_precedence_map()
        self.initialize_feasible_features()
        return

    def create_coupling_map(self):
        coupling_graph = {}
        for index, feature in self.features.items():
            if feature[5] == None:
                continue
            coupled_with = self.feature_id_to_index[feature[5]]
            if index not in coupling_graph:
                coupling_graph[index] = set()
            if coupled_with not in coupling_graph:
                coupling_graph[coupled_with] = set()
            coupling_graph[index].add(coupled_with)
            coupling_graph[coupled_with].add(index)
        for node in coupling_graph:
            coupling_graph[node] = list(coupling_graph[node])

        self.coupling_map = {}
        for index in self.features:
            if ((index in self.coupling_map) or (index not in coupling_graph)):
                continue
            open_list = [index]
            path = []
            while len(open_list) > 0:
                current_node = open_list.pop()
                path.append(current_node)
                for neighbor in coupling_graph[current_node]:
                    if ((neighbor in path) or (neighbor in open_list)):
                        continue
                    open_list.append(neighbor)
            for node in path:
                self.coupling_map[node] = path
        return

    def create_precedence_map(self):
        self.precedence_map = {}
        for index, feature in self.features.items():
            if feature[4] == None:
                continue
            preceded_by = self.feature_id_to_index[feature[4]]
            if self.is_coupled_with(index, preceded_by):
               continue
            if (preceded_by not in self.precedence_map):
                self.precedence_map[preceded_by] = []
            self.precedence_map[preceded_by].append(index)
        return

    def is_coupled_with(self, feature_1, feature_2):
        if feature_1 not in self.coupling_map:
            return False
        return feature_2 in self.coupling_map[feature_1]

    def initialize_feasible_features(self):
        self.initial_feasible_features = []
        for index,feature in self.features.items():
            # check feature is not preceded by another feature
            if feature[4] != None:
                continue
            if index not in self.coupling_map:
                self.initial_feasible_features.append(index)
                continue
            if index != min(self.coupling_map[index]):
                continue
            feature_can_be_initialized = True
            for coupled_feature_index in self.coupling_map[index]:
                coupled_feature = self.features[coupled_feature_index]
                coupled_feature_preceded_by = coupled_feature[4]
                if (coupled_feature_preceded_by != None) and (not self.is_coupled_with(coupled_feature_index, coupled_feature_preceded_by)):
                    feature_can_be_initialized = False
                    break
            if feature_can_be_initialized:
                self.initial_feasible_features.append(index)
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
