import matplotlib.pyplot as plt
import os
import time
import re


# root = '/media/tsabala/TOURO/Agents/uniform3'
root = '/src/pycharm/Agents/rsync/uniform'
for path in os.listdir(root):
    path = os.path.join(root, path)
    if os.path.isdir(path):
        for dir in os.listdir(path):
            dir = os.path.join(root, path, dir)
            if os.path.isdir(dir):
                print("is dir: " + dir)
                fig = plt.figure()
                ax = plt.subplot(111)
                files = []
                datas = []
                for name in ['avg_w.txt', 'std_w.txt', 'avg_buyer_payoff.txt', 'avg_seller_payoff.txt']:
                    files.append(open(os.path.join(path, dir, name), 'r'))
                for file in files:
                    list = []
                    for line in file.readlines():
                        try:
                            list.append(float(line))
                        except ValueError:
                            pass
                    datas.append(list)
                title = "Lorem ipsum"
                labels = ['average w', u"\u03C3 (w)", 'avg buyer payoff', 'avg seller payoff']
                for i in range(len(datas)):
                    ax.plot(datas[i], label=labels[i])
                plt.title(title)
                plt.ylabel('<w>')
                plt.xlabel('time (10^5)')
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.35),
                    ncol=2, fancybox=True, shadow=True)
                figname = "quatro.png"
                plt.savefig(os.path.join(path, dir, figname))
                plt.clf()