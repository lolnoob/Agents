__author__ = 'sabat'

import random
import math
import threading
import time
from queue import Queue

import numpy.random as nprnd


class Agents:
    def __init__(self, size, k, a, seed=12345, threads=4, p=None):
        self.size = size
        self.k = k
        self.a = a
        self.p = p
        if p is None:
            self.p = size / 1000000 // 10 ^ 6
        self.threads = threads
        self.buyers_grid = [None] * self.size
        self.sellers = [None] * self.size
        self.output = []
        self.input = None
        self.random = None
        self.lock = None

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

            self.sellers[i] = nprnd.random()

        self.input = Queue()
        self.lock = threading.Lock()
        for i in range(self.threads):
            print("Hello it's ", i)
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

        return sum(self.output) * (1 - self.sellers[index])

    def buyer_update(self, index):

        old = self.buyers_grid[index][nprnd.randint(self.k)]
        value_old = self.sellers[old]

        new_sellers = list(set(range(self.size)) - set(self.buyers_grid[index]))

        new = random.choice(new_sellers)
        value_new = self.sellers[new]

        if value_new > value_old:
            self.buyers_grid[index].remove(old)
            self.buyers_grid[index].append(new)

    def seller_update(self, index):
        compare_to = index
        while compare_to is index:
            compare_to = nprnd.randint(self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[nprnd.randint(self.size)] = nprnd.random()

    def iterate(self, steps):
        for i in range(steps):
            if nprnd.random() < self.p:
                self.random_noise()
            index = nprnd.randint(0, self.size)
            if nprnd.random() < self.a:
                self.seller_update(index)
            else:
                self.buyer_update(index)

    def get_average_w(self):
        return sum(self.sellers) / self.size


if __name__ == '__main__':
    n = 100000
    k = 3
    a = 0.3
    steps = 1000
    for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
        print('n={}, k={}, a={}, steps={}, p={}'.format(n, k, a, steps, p))
        agents = Agents(n, k, a, time.time(), 4, p)
        agents.setup()
        test = time.time()
        f = open('output_{}_n{}_k{}_a{}_steps{}_p{}.txt'.format(time.strftime('%Y%m%d-%H%M%S'), n, k, a, steps, p), 'w')
        for i in range(steps):
            average = agents.get_average_w()
            print("Calculating: ", i, " in time: ", str(test - time.time()), " with average: ", str(average))
            test = time.time()
            f.write(str(average) + "\n")
            agents.iterate(10000)

        f.close()
