import crossover
import fitness
import robby
import selection
from robby_trainer import RobbyTrainer


if __name__ == '__main__':
    world = robby.World(10, 10)

    rt = RobbyTrainer(
        world=world,
        output_file="robby.txt",
        mutation_rate=0.005,
        crossover_func=crossover.KPointCrossover(crossover_rate=1, num_points=2),
        selection_func=selection.RankedChoiceSelection(),
        reward_func=fitness.RewardCanCollecting(),
        can_fill_rate=0.25,
        steps=200
    )

    # Train the population for the specified number of generations
    best = rt.train(pop_size=200, generations=500, print_interval=10, demo_interval=50)

    # Get the average fitness value of the hardcoded genome over 20 trials
    hc = sum(
        [rt.get_fitness(
            "6563536562523532526563536561513531512523532521513531516563536"
            "5625235325265635365605035305025235325205035305015135315125235"
            "3252151353151050353050252353252050353050656353656252353252656"
            "353656151353151252353252151353151656353656252353252656353454"
        ) for _ in range(20)]
    ) / 20

    print("Best fitness value: ", best[1])
    print("Best genome: ", best[0])
    print("Average fitness of hardcoded genome: ", hc)

    world.demo(best[0], steps=400, init=0.25)
