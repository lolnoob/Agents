__author__ = 'sabat'

import random
import math
import threading
import time
from queue import Queue

import numpy.random as nprnd


class Agents:
    def __init__(self, size, k, a, seed=12345, threads=4):
        random.seed(seed)
        self.size = size
        self.k = k
        self.a = a
        self.threads = threads
        self.buyers_grid = [None] * self.size
        self.sellers = [None] * self.size
        self.output = []
        self.input = None
        self.lock = None

    def setup(self):
        for i in range(self.size):
            row = [0] * self.k
            index = 0
            for agent in random.sample(range(self.size), self.k):
                row[index] = agent
                index += 1
            self.buyers_grid[i] = row

            self.sellers[i] = random.random()

            self.input = Queue()
            self.lock = threading.Lock()
            for i in range(4):
                t = threading.Thread(target=self.worker)
                t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
                t.start()

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

    def worker(self):
        self_input = self.input
        while True:
            params = self_input.get()
            result = self.count_buyers(params[0], params[1], params[2])
            with self.lock:
                self.output.append(result)
            self_input.task_done()

    def seller_payoff(self, index):
        ceil = math.ceil(self.size / self.threads)
        starts = [x for x in range(0, self.size, ceil)]
        ends = [x for x in range(ceil, self.size + ceil, ceil)]
        indexes = [index] * math.floor(self.size / self.threads)
        params = list(zip(indexes, starts, ends))

        self.output = []
        [self.input.put(param) for param in params]
        self.input.join()

        return sum(self.output) * self.sellers[index]

    # def buyer_update(self, index):
    #
    # old = self.buyers_grid[index][nprnd.randint(self.k)]
    # value_old = self.sellers[old]
    #
    #     new_sellers = list(set(range(self.size)) - set(self.buyers_grid[index]))
    #
    #     new = random.choice(new_sellers)
    #     value_new = self.sellers[new]
    #
    #     if value_new > value_old:
    #         self.buyers_grid[index].remove(old)
    #         self.buyers_grid[index].append(new)

    def seller_update(self, index):
        compare_to = index
        while compare_to is index:
            compare_to = nprnd.randint(self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[nprnd.randint(self.size)] = nprnd.random()

    def iterate(self, steps):
        f = open('output1.txt', 'w')

        nprnd_randint = nprnd.randint
        random_choice = random.choice
        self_size = self.size
        for i in range(steps):
            if i % 10000 == 0:
                print("Calculating: ", i / 10000, )
                f.write(str(agents.get_average_w()) + "\n")

            self.random_noise()
            if nprnd.random() < self.a:
                self.seller_update(nprnd_randint(self_size))
            else:
                # self.buyer_update(nprnd.randint(self.size))
                index = nprnd_randint(self_size)
                buyers_grid = self.buyers_grid[index]
                old = random_choice(buyers_grid)
                value_old = self.sellers[old]

                new_sellers = list(set(range(self_size)) - set(buyers_grid))

                new = random_choice(new_sellers)
                value_new = self.sellers[new]

                if value_new > value_old:
                    buyers_grid.remove(old)
                    buyers_grid.append(new)
        f.close()

    def get_average_w(self):
        return sum(self.sellers) / self.size


if __name__ == '__main__':
    agents = Agents(10000, 3, 0.1, time.gmtime(), 1)
    agents.setup()
    test = time.time()
    agents.iterate(1000000)
    print("Hello, ", str(test - time.time()))
