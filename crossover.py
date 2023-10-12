from random import randrange, random, choice


class CrossoverFunc:
    # Base class, if used will simply return the first provided genome

    def __call__(self, g1, g2):
        return g1


class SinglePointCrossover(CrossoverFunc):
    # Generate offspring genome as a combination of the parent genomes before and after a randomly chosen point

    def __init__(self, crossover_rate=1):
        self.crossover_rate = crossover_rate

    def __call__(self, g1, g2):
        # Only crossover when guided to by crossover_rate
        if random() > self.crossover_rate:
            return g1

        # Generate crossover point and create offspring genome from g1 before point and g2 after
        point = randrange(len(g1))
        offspring_genome = g1[:point] + g2[point:]
        return offspring_genome


class KPointCrossover(CrossoverFunc):
    # Generate offspring genome based on k alternating random-sized parts of the given parent genomes

    def __init__(self, crossover_rate=1, num_points=2):
        self.crossover_rate = crossover_rate
        self.num_points = num_points

    def __call__(self, g1, g2):
        # Only crossover when guided to by crossover_rate
        if random() > self.crossover_rate:
            return g1

        offspring_genome = ""
        last_point = 0
        using_g1 = True

        # Generate k points and build the new genome based on alternating parent genomes per point range
        for _ in range(self.num_points - 1):
            next_point = randrange(last_point, len(g1))
            offspring_genome += g1[last_point:next_point] if using_g1 else g2[last_point:next_point]
            last_point = next_point
            using_g1 = not using_g1

        # Make sure the sequence adds the last bit of the parent genome - otherwise it will be too short
        offspring_genome += g1[last_point:] if using_g1 else g2[last_point:]

        return offspring_genome


class UniformCrossover(CrossoverFunc):
    # Generate offspring genome by randomly choosing from either parent for each character in genome

    def __init__(self, crossover_rate=1):
        self.crossover_rate = crossover_rate

    def __call__(self, g1, g2):
        # Only crossover when guided to by crossover_rate
        if random() > self.crossover_rate:
            return g1

        # Iterate over length of genome and add to offspring from either parent based on a random choice
        offspring_genome = ""
        for i in range(len(g1)):
            use_g1 = choice([True, False])
            offspring_genome += g1[i] if use_g1 else g2[i]
        return offspring_genome
