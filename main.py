import sys, io
from random import randrange, choice, choices, random

import robby


POP_SIZE = 200
GENERATIONS = 500
STEPS = 200
DEMO_STEPS = 500
CAN_FILL_RATE = .25
DEMO_CAN_FILL_RATE = .5
CROSSOVER_RATE = 1
MUTATION_RATE = 0.005
OUTPUT_FILE = "robby.txt"

world = robby.World(10, 10)
world.graphicsOff()


def generate_genome():
    genome = ""
    for i in range(243):
        genome += str(randrange(0, 7))
    return genome


def generate_population(size):
    return [generate_genome() for _ in range(size+1)]


def mutate_genome(genome):
    mutated_genome = list(genome)
    for i in range(len(genome)):
        if random() < MUTATION_RATE:
            mutated_genome[i] = str(choice(range(0, 7)))
    return ''.join(mutated_genome)


def single_point_crossover(g1, g2):
    # Generate offspring genome as a combination of the parent genomes before and after a randomly chosen point

    # Only crossover when guided to by CROSSOVER_RATE
    if random() > CROSSOVER_RATE:
        return g1

    # Generate crossover point and create offspring genome from g1 before point and g2 after
    point = randrange(len(g1))
    offspring_genome = g1[:point] + g2[point:]
    return offspring_genome


def k_point_crossover(g1, g2, k=2):
    # Generate offspring genome based on k alternating random-sized parts of the parent genomes

    # Only crossover when guided to by CROSSOVER_RATE
    if random() > CROSSOVER_RATE:
        return g1

    offspring_genome = ""
    last_point = 0
    using_g1 = True

    # Generate k points and build the new genome based on alternating parent genomes per point range
    for _ in range(k-1):
        next_point = randrange(last_point, len(g1))
        offspring_genome += g1[last_point:next_point] if using_g1 else g2[last_point:next_point]
        last_point = next_point
        using_g1 = not using_g1

    # Make sure the sequence adds the last bit of the parent genome - otherwise it will be too short
    offspring_genome += g1[last_point:] if using_g1 else g2[last_point:]

    return offspring_genome


def uniform_crossover(g1, g2):
    # Generate offspring genome by randomly choosing from either parent for each character in genome

    # Only crossover when guided to by CROSSOVER_RATE
    if random() > CROSSOVER_RATE:
        return g1

    # Iterate over length of genome and add to offspring from either parent based on a random choice
    offspring_genome = ""
    for i in range(len(g1)):
        use_g1 = choice([True, False])
        offspring_genome += g1[i] if use_g1 else g2[i]
    return offspring_genome


def ranked_choice_parent_selection(population, weights):
    return choices(population=population, weights=weights, k=2)


def uniform_parent_selection(population, weights):
    return choices(population=population, k=2)


def best_parent_selection(population, weights):
    return [population[-1], population[-2]]


def get_reward(action):
    # Return the reward value of an action

    # Decode percept into the values of each cell around Robby
    percept = world.getPercept()
    n = percept[0]
    s = percept[1]
    e = percept[2]
    w = percept[3]
    h = percept[4]

    # Decide value of each action
    # Currently only giving reward for picking up cans, no penalty or reward for any other action

    # Robby runs into a wall
    if action == "MoveNorth" and world.robbyRow == world.topRow or \
            action == "MoveSouth" and world.robbyRow == world.bottomRow or \
            action == "MoveEast" and world.robbyCol == world.rightCol or \
            action == "MoveWest" and world.robbyCol == world.leftCol:
        return -0

    # Robby moves into a cell containing a can
    if action == "MoveNorth" and n == "C" or \
            action == "MoveSouth" and s == "C" or \
            action == "MoveEast" and e == "C" or \
            action == "MoveWest" and w == "C":
        return +0

    # Robby picks up a can
    if action == "PickUpCan" and h == "C":
        return +1

    # Robby tries to pick up a can in an empty cell
    if action == "PickUpCan" and h == "E":
        return -0

    return 0


def fitness(genome):
    # Return the fitness of a given genome based on cumulative reward of running STEPS times in a random world

    # Regenerate world and place Robby in the top left corner
    world.distributeCans(CAN_FILL_RATE)
    world.goto(0, 0)

    # Run STEPS times and sum the reward of the action of each step
    reward = 0
    for i in range(STEPS):
        # Get percept and find the corresponding action from current genome
        p = world.getPerceptCode()
        action = robby.POSSIBLE_ACTIONS[int(genome[p])]

        # Get the reward value of the action taken
        reward += get_reward(action)

        # Have Robby make the move in the world
        world.performAction(action)

    return reward


def sort_by_fitness(genomes):
    # Return a given list of genomes sorted by fitness values and the corresponding sorted list of fitness values

    tuples = [(fitness(g), g) for g in genomes]
    tuples.sort()
    sorted_fitness_values = [f for (f, g) in tuples]
    sorted_genomes = [g for (f, g) in tuples]
    return sorted_genomes, sorted_fitness_values


def mutate_generation(sorted_genomes, fitness_vals, crossover_func=single_point_crossover, selection_func=ranked_choice_parent_selection):
    # Take a sorted list of genomes and fitness values and create a new generation of crossed over and mutated genomes

    # Make all weights positive to allow for python random library weighted choice
    offset = abs(min(fitness_vals))
    weights = [v + offset for v in fitness_vals]

    # Build next generation by selecting parents, crossing over their genomes, mutating the result, and appending
    # it to the new generation
    next_generation = []
    for i in range(len(sorted_genomes) + 1):
        # Select two parents and create a child from their genomes
        parents = selection_func(sorted_genomes, weights)
        fresh_child = crossover_func(parents[0], parents[1])

        # Mutate crossed over child
        mutated_child = mutate_genome(fresh_child)

        # Add crossed over and mutated child to next generation
        next_generation.append(mutated_child)

    return next_generation


def train(population, generations, crossover_func=single_point_crossover, selection_func=ranked_choice_parent_selection, print_interval=10, demo_interval=20):
    # Assess, cross over, and mutate a population a genomes for a specified number of generations
    # Return the all-time best genome found

    # Initialize all-time best genome variable with an empty genome and the lowest possible fitness value
    best_genome = ("", -sys.maxsize - 1)

    # Open output file for writing the best genome's information
    f = open(OUTPUT_FILE, 'w')

    # Run and mutate the population for n generations
    for i in range(generations):
        sorted_genomes, fitness_vals = sort_by_fitness(population)
        population = mutate_generation(sorted_genomes, fitness_vals, crossover_func, selection_func)

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
            world.demo(sorted_genomes[-1], STEPS, CAN_FILL_RATE)
            world.graphicsOff()

    # Close output file
    f.close()

    return best_genome


if __name__ == '__main__':
    # Generate initial population of random genomes
    r_pop = generate_population(POP_SIZE)

    # Train the population for the specified number of generations
    best = train(r_pop, GENERATIONS, crossover_func=k_point_crossover, selection_func=ranked_choice_parent_selection)

    # Get the fitness value of the hardcoded genome
    hc = sum([fitness("656353656252353252656353656151353151252353252151353151656353656252353252656353656050353050252353252050353050151353151252353252151353151050353050252353252050353050656353656252353252656353656151353151252353252151353151656353656252353252656353454") for _ in range(20)]) / 20

    print("Best fitness value: ", best[1])
    print("Best genome: ", best[0])
    print("Average fitness of hardcoded genome: ", hc)

    world.demo(best[0], DEMO_STEPS, CAN_FILL_RATE)
