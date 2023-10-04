import robby


def generate_genome():
    pass


def mutate_genome(genome):
    pass


def crossover_genomes(g1, g2):
    pass


def fitness(genome):
    pass


def sort_by_fitness(genomes):
    tuples = [(fitness(g), g) for g in genomes]
    tuples.sort()
    sorted_fitness_values = [f for (f, g) in tuples]
    sorted_genomes = [g for (f, g) in tuples]
    return sorted_genomes, sorted_fitness_values


rw = robby.World(10, 10)

rw.demo(rw.strategyM)