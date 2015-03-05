import matplotlib.pyplot as plt
import os
import time
import re


root = 'outputs/'
for path in os.listdir('outputs/'):
    path = os.path.join(root, path)
    # print("I am in " + filename)
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".txt"):
                data_path = os.path.join(path, filename)
                print(data_path)
                f = open(data_path, 'r')

                n = re.search('_n(.+?)_k', filename).group(1)
                k = re.search('_k(.+?)_a', filename).group(1)
                a = re.search('_a(.+?)_steps', filename).group(1)
                p = re.search('_p(.+?).txt', filename).group(1)
                title = "n={}, k={}, a={}, p={}".format(n,k,a,p)

                plt.plot(list(map(float, f.readlines())))
                plt.title(title)
                plt.ylabel('<w>')
                plt.xlabel('time (10^5)')
                figname = os.path.splitext(filename)[0] + ".png"
                plt.savefig(os.path.join(path, figname))
                plt.clf()