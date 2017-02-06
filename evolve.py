import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


NBR_FEAT = 20
NBR_RELEASE = 4

TEAM_CAP = 50


#random.seed(64)

#Create the feature dictionary: feature name is an integer, and value is
#a (effort, value) 2-uple
features = {} 

for i in range(NBR_FEAT):
    features[i] = (random.randint(1,10), random.randint(1, 4), random.uniform(0, 100))


#Individual is a RP
creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", list, fitness=creator.Fitness)

toolbox = base.Toolbox()
toolbox.register("attr_feat", random.randint, 0, NBR_RELEASE)

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_feat, NBR_FEAT)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalReleasePlan(individual):
    effort = [0]*(NBR_RELEASE+1)
    penalty = 0
    benefit = 0
    
    for feature, release in enumerate(individual):
    	for feature2, release2 in enumerate(individual):
            if feature2 < feature:
                if (features[feature][1]-features[feature2][1])*(release - release2) > 0:
                    penalty += 0
                elif release == release2:
                    penalty += abs(features[feature][1]-features[feature2][1])
                elif features[feature][1] == features[feature2][1]:
                    penalty += abs(release - release2)
                else:
                    penalty += (features[feature][1]-features[feature2][1])*(release2 - release)
                    
        if release!=0:
            benefit += features[feature][2]*(NBR_RELEASE - release + 1)
            effort[release] += features[feature][0]
        if effort[release] > TEAM_CAP :
            return 10000, 0
    return penalty, benefit


def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets."""

    if (NBR_FEAT < 2):
    	return ind1, ind2

    result_1 = ind1

    result_2 = ind2
    
    rnd1, rnd2 = random.sample(range(0, NBR_FEAT-1), 2)
    
    result_1[rnd1] = ind2[rnd1]
    result_1[rnd2] = ind2[rnd2]

    result_2[rnd1] = ind1[rnd1]
    result_2[rnd2] = ind1[rnd2]

    return result_1, result_2



def mutSet(individual):
    '''
    fromIndex = random.randint(0, NBR_FEAT-1) 
    toIndex = random.randint(0, NBR_FEAT-1)
    
    if fromIndex == toIndex:
        return individual
    else:
        tmp = individual[fromIndex]
        individual[fromIndex] = individual[toIndex]
        individual[toIndex] = tmp
    return individual
    '''
    individual[random.randint(0, NBR_FEAT-1)] = random.randint(0, NBR_RELEASE)
    return individual,

toolbox.register("evaluate", evalReleasePlan)
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

def main():
    random.seed(64)
    NGEN = 100
    MU = 50
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.3

    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    #stats.register("solution", numpy.)
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
            stats, halloffame=hof)
    
    return pop, stats, hof
                 
if __name__ == "__main__":
    pop,stats,hof = main()

for i in hof:
    print i, i.fitness.values

print "last pop"
print pop[len(pop)-1], pop[len(pop)-1].fitness.values

'''
    _, _, hof = main()
    '''
'''
    print hof[len(hof)-1].fitness.values[0]
    print hof[len(hof)-1].fitness.values[1]
    print hof[len(hof)-1]

    print hof[0].fitness.values[0]
    print hof[0].fitness.values[1]
    print hof[0]'''
'''
    from matplotlib import pyplot as plt
    effort = [i.fitness.values[0] for i in hof]
    bvalue = [i.fitness.values[1] for i in hof]
    plt.plot(effort, bvalue, 'bo')
    plt.xlabel("Penalty")
    plt.ylabel("Bussiness Value")
    plt.show()

'''
'''
    for i in hof:
    	print i;
	'''
	# print hof
    # print hof(len(hof)-1).fitness.values[0]
    # print hof(len(hof)-1).fitness.values[1]
    







