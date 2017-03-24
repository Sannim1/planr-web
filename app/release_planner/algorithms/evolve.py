__author__ = "Nikolaos Kaloumenos, Bingquan Wang and Abdulmusawwir Sanni"
import random
import sys
from deap import algorithms
from deap import base
from deap import creator
from deap import tools


class Evolve:

    """ Initialization Operations """

    def __init__(self, features, num_releases, team_capacity):
        """Constructor of the GA

            featuers : VSTS's work item's info
            num_releases : Number of releases specified by the user
            team_capacity : Team capacity in hours as specified by the user
        """
        self.transform_features(features)
        self.features_for_initial_release_plan = []
        self.num_features = len(features)
        self.num_releases = num_releases
        self.team_capacity = team_capacity
        self.min_priority = 4   # Currently on VSTS
        self.initialize_algorithm()

    def transform_features(self, features):
        """Gets VSTS work items to create feature items for the algorithms,
           creates feature relation maps,
           initialize a list of initial feasible features

           features : The work items, as given by the VSTS
        """
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
        """Creates a map that shows the coupled features"""

        # Create a graph where nodes are features
        # and edges are coupling contraints
        coupling_graph = {}
        for index, feature in self.features.items():
            if feature[5] == None:  # if coupled_with == None
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

        # Create a coupling map (node information), based on the generated
        # graph
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
        """Creates a map that shows the dependent features of a feature"""

        self.precedence_map = {}
        for index, feature in self.features.items():
            if feature[4] == None:  # if preceded_by == None
                continue
            preceded_by = self.feature_id_to_index[feature[4]]
            if self.is_coupled_with(index, preceded_by):
                continue
            if (preceded_by not in self.precedence_map):
                self.precedence_map[preceded_by] = []
            self.precedence_map[preceded_by].append(index)
        return

    def initialize_feasible_features(self):
        """Creates the list of initial feasible features"""

        self.initial_feasible_features = []
        for index, feature in self.features.items():
            # if preceded_by != None then it's not feasible
            if feature[4] != None:
                continue
            # if preceded_by == None and it's not coupled with other features
            # then it's feasible
            if index not in self.coupling_map:
                self.initial_feasible_features.append(index)
                continue
            # if it's not the first feature in its coupling group then we have
            # already covered it
            if index != min(self.coupling_map[index]):
                continue
            feature_can_be_initialized = True

            # Check if all the coupled features are not preceded by others
            for coupled_feature_index in self.coupling_map[index]:
                coupled_feature = self.features[coupled_feature_index]
                # coupled_feature_preceded_by = coupled_feature["preceded_by"]
                coupled_feature_preceded_by = coupled_feature[4]
                if (coupled_feature_preceded_by != None) and (not self.is_coupled_with(coupled_feature_index, coupled_feature_preceded_by)):
                    feature_can_be_initialized = False
                    break
            if feature_can_be_initialized:
                self.initial_feasible_features.append(index)
        return

    def initialize_algorithm(self):
        """Specifies the containers of individual and population, registers evolutionary tools """

        creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
        creator.create("Individual", list, fitness=creator.Fitness)
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,
                              self.get_feature_for_initial_release_plan, self.num_features)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evalReleasePlan)
        self.toolbox.register("mate", self.cxSet)
        self.toolbox.register("mutate", self.mutSet)
        self.toolbox.register("select", tools.selNSGA2)

    def get_feature_for_initial_release_plan(self):
        """Pops the first feature from a randomly generated release plan"""

        if len(self.features_for_initial_release_plan) == 0:
            self.features_for_initial_release_plan = self.get_initial_release_plan()
        return self.features_for_initial_release_plan.pop(0)

    def get_initial_release_plan(self):
        """Randomly generates a valid release plan"""

        implemented_features = []
        feasible_features = self.initial_feasible_features[:]
        release_plan = [0] * len(self.features)
        remaining_effort = {}
        # Initialize effort in each release = 0
        for index in xrange(1, self.num_releases + 1):
            remaining_effort[index] = self.team_capacity
        # for every release
        for release_number in xrange(1, self.num_releases + 1):
            while True:
                # if there is no available feasible feature then terminate
                if len(feasible_features) == 0:
                    break
                # Select a random features from the feasible feature list
                random_index = random.randint(0, len(feasible_features) - 1)
                random_feasible_feature = feasible_features[random_index]
                # Get the effort of the feature and its coupled one if they
                # exist
                combined_effort = self.get_combined_effort(
                    random_feasible_feature)
                # if the effort of the feature(or features) is greater than the
                # remaining effort of the release
                if remaining_effort[release_number] < combined_effort:
                    break   # then break and move to the next release
                coupled_features = self.get_coupled_features(
                    random_feasible_feature)
                dependent_features = []
                # Assign feature(or features) to release
                # Update implemented features list
                for coupled_feature in coupled_features:
                    release_plan[coupled_feature] = release_number
                    implemented_features.append(coupled_feature)
                    dependent_features += self.get_depending_features(
                        coupled_feature)
                # Check if depedent features are feasible and add them to the
                # list of feasible features
                for dependent_feature in dependent_features:
                    if not self.is_feasible_feature(dependent_feature, implemented_features):
                        continue
                    dependent_couple = self.get_coupled_features(
                        dependent_feature)
                    min_dependent_couple = min(dependent_couple)
                    if min_dependent_couple not in feasible_features:
                        feasible_features.append(min_dependent_couple)
                del feasible_features[random_index]
                # Update remaining effort
                remaining_effort[release_number] -= combined_effort
        return release_plan

    """ Genetic Algorithm Operations """

    def evalReleasePlan(self, individual):
        """Evaluates how fit a release plan is

            individual : release plan to be evaluated
        """
        effort = [0]*(self.num_releases+1)
        penalty = 0
        benefit = 0
        for feature, release in enumerate(individual):
            # Check if feature is preceded by 'other' feature
            if self.features[feature][4] != None and self.features[feature][4] != self.features[feature][3]:
                precedenceIndex = self.feature_id_to_index[
                    self.features[feature][4]]
                precedenceRelease = individual[precedenceIndex]
                # if the implementation of the preceded feature(parent) is
                # after the dependent(child)
                if release < precedenceRelease or (release > precedenceRelease and precedenceRelease == 0):
                    return sys.maxint, 0    # then the release plan is invalid
            # Check if feature is coupled with 'other' feature
            if self.features[feature][5] != None and self.features[feature][5] != self.features[feature][3]:
                couplingIndex = self.feature_id_to_index[
                    self.features[feature][5]]
                couplingRelease = individual[couplingIndex]
                # if the implementations of the coupled features are not the
                # same
                if release != couplingRelease:
                    return sys.maxint, 0    # then the release plan is invalid
            # if feature is implemented, update benefit, effort and penalty of
            # the release
            if release != 0:
                benefit += self.features[feature][2] * \
                    (self.num_releases - release + 1)
                effort[release] += self.features[feature][0]
                penalty += (self.min_priority + 1 -
                            self.features[feature][1])*(release)
            # if feature is not implemented, update penalty of the release
            else:
                penalty += (self.min_priority + 1 -
                            self.features[feature][1])*(self.num_releases + 1)
            # if the sum effort of the features implemented in a release is
            # greater than team capacity
            if effort[release] > self.team_capacity:
                return sys.maxint, 0    # then the release plan is invalid
        return penalty, benefit

    def cxSet(self, ind1, ind2):
        """Crossovers release plans to generate 2 offsprings that share their characteristics

            ind1, ind2 : parent release plans to be crossovered
        """
        if (self.num_features <= 2):
            return ind1, ind2
        result_1 = ind1
        result_2 = ind2
        rnd1, rnd2 = random.sample(range(0, self.num_features - 1), 2)
        result_1[:rnd1] = ind2[:rnd1]
        result_2[:rnd2] = ind1[:rnd2]
        return result_1, result_2

    def mutSet(self, individual):
        """Mutates a release plan to introduce variance in solutions

            individual : release plan to be mutated
        """

        # Randomly switch the implementation's release of two features with
        # each other
        rnd1, rnd2 = random.sample(range(0, self.num_features - 1), 2)
        tmp = individual[rnd1]
        individual[rnd1] = individual[rnd2]
        individual[rnd2] = tmp
        return individual

    def custom_algorithm(self, pop, toolbox, mu, CXPB, MUTPB, NGEN, halloffame):
        """Implementation of the core of the Genetic Algorithm

            pop : the initial population
            toolbox : an abstract container consisting of specified evolutionary tools
            mu : population size
            CXPB : crossover rate
            MUTPB : mutation rate
            NGEN : number of generations
            halloffame : list of best individuals generated
        """

        # Evaluate the entire population
        fitnesses = map(toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        halloffame.update(pop)  # Register best individuals in halloffame
        for g in range(NGEN):
            # Select the next generation individuals
            selected_population = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            selected_population = map(toolbox.clone, selected_population)
            # Apply crossover and mutation
            offspring = algorithms.varAnd(
                selected_population, toolbox, CXPB, MUTPB)
            # Evaluate the newly generated offsprings
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            # Population is replaced by selecting the fittest individual from
            # previous population and offsprings
            pop[:] = toolbox.select(selected_population + offspring, mu)
            halloffame.update(pop)  # Update halloffame with best offsprings

    """ Run-time Operation """

    def generate(self):
        """This method runs the GA to return sub-optimal release plans"""

        # if team capacity exceeds the sum of the required effort,
        # it implies all of the features can be implemented in the first
        # release
        if self.team_capacity_exceeds_sum_effort():
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
        crossover_rate = 0.9
        mutation_rate = 1 / self.num_features
        # Initialize population of first generation
        population = self.toolbox.population(n=population_size)
        pareto_front = tools.ParetoFront()
        halloffame = tools.HallOfFame(num_generations*population_size)
        # Run the GA
        self.custom_algorithm(population, self.toolbox, population_size,
                              crossover_rate, mutation_rate, num_generations, halloffame)
        # From the best individuals, keep the non-dominated ones
        pareto_front.update(halloffame)
        release_plans = []
        min_penalty, max_penalty = -1, 0
        min_benefit, max_benefit = -1, 0
        for release_plan in pareto_front:
            penalty, benefit = release_plan.fitness.values
            if penalty < min_penalty or min_penalty == -1:
                min_penalty = penalty
            if penalty > max_penalty:
                max_penalty = penalty
            if benefit < min_benefit or min_benefit == -1:
                min_benefit = benefit
            if benefit > max_benefit:
                max_benefit = benefit
            release_plans.append({
                "penalty": penalty,
                "benefit": benefit,
                "releases": self.map_features_to_releases(release_plan)
            })

        # Return release plans with metadata
        return {
            "release_plans": release_plans,
            "min_penalty": min_penalty,
            "max_penalty": max_penalty,
            "min_benefit": min_benefit,
            "max_benefit": max_benefit,
            "num_valid_release_plans": len(halloffame)
        }

    """ Helper functions """

    def get_combined_effort(self, feature_index):
        """Returns the combined effort of all the coupled feature to this feature

            feature_index : the index of the featuere in the algorithm's feature item list
        """
        if feature_index not in self.coupling_map:
            return self.features[feature_index][0]
        combined_effort = 0
        for coupled_feature in self.coupling_map[feature_index]:
            combined_effort += self.features[coupled_feature][0]
        return combined_effort

    def get_coupled_features(self, feature_index):
        """Returns the list of coupled feature to this feature

            feature_index : the index of the featuere in the algorithm's feature item list
        """
        if feature_index not in self.coupling_map:
            return [feature_index]
        return self.coupling_map[feature_index]

    def get_depending_features(self, feature_index):
        """Returns the list of features that are dependent to this feature

            feature_index : the index of the featuere in the algorithm's feature item list
        """
        if feature_index not in self.precedence_map:
            return []
        return self.precedence_map[feature_index]

    def is_feasible_feature(self, feature_index, implemented_features):
        """Checks if feature is feasible based on its constraints

            feature_index: the index of the featuere in the algorithm's feature item list
            implemented_features: a list of the implemented features up to that point
        """
        coupled_features = self.get_coupled_features(feature_index)
        for feature in coupled_features:
            # preceded_by = feature["preceded_by"]
            preceded_by = self.features[feature][4]
            if preceded_by == None:
                continue
            preceded_by_index = self.feature_id_to_index[preceded_by]
            if preceded_by_index not in implemented_features:
                return False
        return True

    def team_capacity_exceeds_sum_effort(self):
        """Checks if team capacity is greater equal to the sum effort of all features"""

        sum_features_effort = 0
        for index in self.features:
            # sum_features_effort += feature["effort"]
            sum_features_effort += self.features[index][0]
        if self.team_capacity >= sum_features_effort:
            return True
        return False

    def is_coupled_with(self, feature_1, feature_2):
        """Checks if features are coupled

            feature_1, feature_2 : featuers to be checked
        """
        if feature_1 not in self.coupling_map:
            return False
        return feature_2 in self.coupling_map[feature_1]

    def map_features_to_releases(self, release_plan):
        """Transforms single release plan into list of releases containing ids of the features

            release_plan : a release plan representation as used during the GA processing
        """
        releases = {}
        for index, release in enumerate(release_plan):
            if release not in releases:
                releases[release] = []
            feature_id = self.features[index][3]
            releases[release].append(feature_id)
        return releases
