__author__ = 'sabat'

import random


class Agents:
    def __init__(self, size, k, seed=12345):
        random.seed(seed)
        self.size = size
        self.k = k
        self.buyers_grid = [None] * self.size
        self.sellers = [None] * self.size

    def setup(self):
        for i in range(self.size):
            row = [False] * self.size
            for agent in random.sample(range(self.size), self.k):
                row[agent] = True
            self.buyers_grid[i] = row

            self.sellers[i] = random.random()

    def buyer_payoff(self, index):
        result = 0.0
        for i in range(self.size):
            if self.buyers_grid[index][i]:
                result += self.sellers[i]
        return result

    def seller_payoff(self, index):
        result = 0
        for i in range(self.size):
            if self.buyers_grid[i][index]:
                result += 1
        return result * self.sellers[index]

    def buyer_update(self, index):
        value_old = 0
        value_new = 0
        old = 0
        new = 0
        while True:
            old = random.randint(0, self.size)
            if self.buyers_grid[index][old]:
                value_old = self.sellers[old]
                break

        while True:
            new = random.randint(0, self.size)
            if not self.buyers_grid[index][new]:
                value_new = self.sellers[new]
                break

        if value_new > value_old:
            self.buyers_grid[index][old] = False
            self.buyers_grid[index][new] = True

    def seller_update(self, index):
        compare_to = index
        while compare_to is index:
            compare_to = random.randint(0, self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[random.randint(0, self.size)] = random.random()


agents = Agents(5, 3)
agents.setup()
print(agents.buyers_grid)
print(agents.sellers)
