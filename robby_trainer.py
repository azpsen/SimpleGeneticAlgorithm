from random import random, choice, randrange
from sys import maxsize

POSSIBLE_ACTIONS = ["MoveNorth", "MoveSouth", "MoveEast", "MoveWest", "StayPut", "PickUpCan", "MoveRandom"]


class RobbyTrainer:
    def __init__(
            self,
            world,
            output_file,
            mutation_rate,
            crossover_func,
            selection_func,
            reward_func,
            can_fill_rate=0.25,
            steps=200
    ):

        self.world = world
        self.world.graphicsOff()

        self.output_file = output_file
        self.mutation_rate = mutation_rate
        self.crossover_func = crossover_func
        self.selection_func = selection_func
        self.reward_func = reward_func

        self.can_fill_rate = can_fill_rate
        self.steps = steps

    # ------------------------------------------------------------------------------------------------------------ #
    #                                           INITIALIZATION FUNCTIONS                                           #
    # ------------------------------------------------------------------------------------------------------------ #

    @staticmethod
    def generate_genome():
        # Generate a single completely random genome

        genome = ""
        for i in range(243):
            genome += str(randrange(0, 7))
        return genome

    @staticmethod
    def generate_population(size):
        # Generate a population of size random genomes

        return [RobbyTrainer.generate_genome() for _ in range(size + 1)]

    # ------------------------------------------------------------------------------------------------------------ #
    #                                               FITNESS HANDLERS                                               #
    # ------------------------------------------------------------------------------------------------------------ #

    def get_fitness(self, genome):
        # Return the fitness of a given genome based on cumulative reward of running STEPS times in a random world

        # Regenerate world and place Robby in the top left corner
        self.world.distributeCans(self.can_fill_rate)
        self.world.goto(0, 0)

        # Run STEPS times and sum the reward of the action of each step
        reward = 0
        for i in range(self.steps):
            # Get percept and find the corresponding action from current genome
            p = self.world.getPerceptCode()
            action = POSSIBLE_ACTIONS[int(genome[p])]

            # Get the reward value of the action taken
            reward += self.reward_func(self.world, action)

            # Have Robby make the move in the world
            self.world.performAction(action)

        return reward

    def sort_by_fitness(self, genomes):
        # Return a given list of genomes sorted by fitness values and the corresponding sorted list of fitness values

        tuples = [(self.get_fitness(g), g) for g in genomes]
        tuples.sort()
        sorted_fitness_values = [f for (f, g) in tuples]
        sorted_genomes = [g for (f, g) in tuples]
        return sorted_genomes, sorted_fitness_values

    # ------------------------------------------------------------------------------------------------------------ #
    #                                             MUTATION HANDLERS                                                #
    # ------------------------------------------------------------------------------------------------------------ #

    def mutate_genome(self, genome):
        # Replace each character in the given genome with a random one with probability MUTATION_RATE

        mutated_genome = list(genome)
        for i in range(len(genome)):
            if random() < self.mutation_rate:
                mutated_genome[i] = str(choice(range(0, 7)))
        return ''.join(mutated_genome)

    def mutate_generation(self, sorted_genomes, fitness_vals):
        # Take sorted lists of genomes and fitness values and return a new generation of crossed over/mutated genomes

        # Make all weights positive to allow for python random library weighted choice
        offset = abs(min(fitness_vals))
        weights = [v + offset for v in fitness_vals]

        # Build next generation by selecting parents, crossing over their genomes, mutating the result, and appending
        # it to the new generation
        next_generation = []
        for i in range(len(sorted_genomes) + 1):
            # Select two parents and create a child from their genomes
            parents = self.selection_func(sorted_genomes, weights)
            fresh_child = self.crossover_func(parents[0], parents[1])

            # Mutate crossed over child
            mutated_child = self.mutate_genome(fresh_child)

            # Add crossed over and mutated child to next generation
            next_generation.append(mutated_child)

        return next_generation

    # ------------------------------------------------------------------------------------------------------------ #
    #                                          OVERALL TRAINING HANDLER                                            #
    # ------------------------------------------------------------------------------------------------------------ #

    def train(self, pop_size, generations, print_interval=10, demo_interval=20):
        # Assess, cross over, and mutate a population a genomes for a specified number of generations
        # Return the all-time best genome found

        # Create population of random genomes of size pop_size
        population = RobbyTrainer.generate_population(pop_size)

        # Initialize all-time best genome variable with an empty genome and the lowest possible fitness value
        best_genome = ("", -maxsize - 1)

        # Open output file for writing the best genome's information
        f = open(self.output_file, 'w')

        # Run and mutate the population for n generations
        for i in range(generations):
            sorted_genomes, fitness_vals = self.sort_by_fitness(population)
            population = self.mutate_generation(sorted_genomes, fitness_vals)

            # Keep all-time best genome for final output
            if fitness_vals[-1] > best_genome[1]:
                best_genome = (sorted_genomes[-1], fitness_vals[-1])

            # Print out and write to a file information about the current generation
            if print_interval > 0 and i % print_interval == 0:
                avg_fitness = round(sum(fitness_vals) / len(fitness_vals), 2)
                out_string = f"{i} {avg_fitness} {best_genome[1]} {best_genome[0]}\n"
                f.write(out_string)

                print(f"Generation: {i}/{generations}")
                print(f"Average fitness this generation: {avg_fitness}")
                print(f"Best fitness this generation: {fitness_vals[-1]}")
                print('-' * 50)

            # Demo the current generation's best genome
            if demo_interval > 0 and i % demo_interval == 0:
                self.world.demo(sorted_genomes[-1], self.steps, self.can_fill_rate)
                self.world.graphicsOff()

        # Close output file
        f.close()

        return best_genome
