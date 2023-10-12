from random import choices


class SelectionFunc:
    # Base class, if used will select the first *count* parents from population

    def __call__(self, population, weights, count=2):
        return population[:count]


class RankedChoiceSelection(SelectionFunc):
    # Randomly select *count* parents from population weighted by *weights*

    def __call__(self, population, weights, count=2):
        return choices(population=population, weights=weights, k=count)


class UniformSelection(SelectionFunc):
    # Randomly select *count* parents from population with a uniform distribution

    def __call__(self, population, weights, count=2):
        return choices(population=population, k=count)


class NBestSelection(SelectionFunc):
    # Select the n best parents from the given population

    def __call__(self, population, weights, count=2):
        return [population[-i] for i in range(count)]
