from random import shuffle
from Solution import Solution
from itertools import chain
import random


class HillClimbing():
    """docstring for HillClimbing"""
    def __init__(self, sol):
        self.sol = sol

    def climb(self):
        for i in range(10000):
            next_sol = self.random_permutation()
            # print(next_sol.score(), self.sol.score())
            if next_sol.score() >= self.sol.score():
                self.sol = next_sol
                print(next_sol.score())
                next_sol.save()

    def sequences(self):
        sequences = []
        current = []

        threshold = random.rand(5)

        for slide in self.sol.slides:
            if len(current) == 0:
                current.append(slide)
            elif slide.score(current[-1]) > threshold:
                current.append(slide)
            else:
                sequences.append(current)
                current = [slide]
        if len(current) > 0:
            sequences.append(current)

        return sequences

    def random_permutation(self):
        sequences = self.sequences()
        # print(sequences, "\n")
        shuffle(sequences)
        # print(sequences, "\n")
        next_sol = Solution()
        next_sol.slides = list(chain.from_iterable(sequences))
        # print(next_sol.slides,"\n\n")
        return next_sol
        