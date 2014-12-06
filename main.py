__author__ = 'sabat'

import random
import math
import threading


class Agents:
    def __init__(self, size, k, a, seed=12345):
        random.seed(seed)
        self.size = size
        self.k = k
        self.a = a
        self.buyers_grid = [None] * self.size
        self.sellers = [None] * self.size
        self.output = []

    def append_to_output(self, item):
        self.output.append(item)

    def setup(self):
        for i in range(self.size):
            row = [0] * self.k
            index = 0
            for agent in random.sample(range(self.size), self.k):
                row[index] = agent
                index += 1
            self.buyers_grid[i] = row

            self.sellers[i] = random.random()

    def buyer_payoff(self, index):
        result = 0.0
        for agent in range(self.buyers_grid[index]):
            result += self.sellers[agent]
        return result

    def count_buyers(self, index, start, end):
        result = 0
        if end > self.size:
            end = self.size
        for ii in range(start, end):
            if index in self.buyers_grid[ii]:
                result += 1
        return result

    class Thread(threading.Thread):
        def __init__(self, agents, params):
            threading.Thread.__init__(self)
            self.params = params
            self.agents = agents

        def run(self):
            self.agents.append_to_output(self.agents.count_buyers(self.params[0], self.params[1], self.params[2]))


    def seller_payoff(self, index):
        # result222 = 0
        processes = 8
        starts = []
        ends = []
        for ii in range(0, self.size, math.ceil(self.size / processes)):
            starts.append(ii)
        for ii in range(math.ceil(self.size / processes), self.size + math.ceil(self.size / processes),
                        math.ceil(self.size / processes)):
            ends.append(ii)
        indexes = [index] * math.floor(self.size / processes)
        params = list(zip(indexes, starts, ends))

        threads = []
        self.output = []
        for ii in range(processes):
            current = self.Thread(self, params[ii])
            threads.append(current)
            current.start()

        for t in threads:
            t.join()

        # with mp.Pool(processes) as pool:
        # pool_values = [pool.apply_async(self.count_buyers, args) for args in params]
        #     for value in pool_values:
        #         result222 += value.get()
        return sum(self.output) * self.sellers[index]

    def buyer_update(self, index):

        old = self.buyers_grid[index][random.randrange(0, self.k)]
        value_old = self.sellers[old]

        new = 0
        value_new = 0
        while True:
            new = random.randrange(0, self.size)
            if new not in self.buyers_grid[index]:
                value_new = self.sellers[new]
                break

        if value_new > value_old:
            self.buyers_grid[index].remove(old)
            self.buyers_grid[index].append(new)

    def seller_update(self, index):
        compare_to = index
        while compare_to is index:
            compare_to = random.randrange(0, self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[random.randrange(0, self.size)] = random.random()

    def iterate(self, steps):
        for i in range(steps):
            self.random_noise()
            if random.random() < self.a:
                self.seller_update(random.randrange(0, self.size))
            else:
                self.buyer_update(random.randrange(0, self.size))

    def get_average_w(self):
        return sum(self.sellers) / self.size


if __name__ == '__main__':
    agents = Agents(10000, 3, 0.1)
    agents.setup()
    f = open('output2.txt', 'w')
    for i in range(1000):
        print("Calculating: ", i)
        f.write(str(agents.get_average_w()) + "\n")
        agents.iterate(i * 10000)

    f.close()
