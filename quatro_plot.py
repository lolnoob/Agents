import matplotlib.pyplot as plt
import os
import time
import re
import numpy as np


root = '/media/tsabala/TOURO/Agents/uniform3'
# root = '/src/pycharm/Agents/rsync/uniform'
for path in os.listdir(root):
    path = os.path.join(root, path)
    if os.path.isdir(path):
        for dir in os.listdir(path):
            dir = os.path.join(root, path, dir)
            if os.path.isdir(dir):
                print("is dir: " + dir)
                fig = plt.figure()
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
                    # #normalization
                    # list /= np.max(np.abs(list),axis=0)
                    datas.append(list)
                # title = "Lorem ipsum"

                ax = plt.subplot(211)
                ax2 = ax.twinx()
                labels = ('<w>', u"\u03C3(w)", '$<P^->$', '$<P^+>$')
                y_labels = ('average value <w>', u"\u03C3(w)", 'avg buyer payoff $<P^->$', 'avg seller payoff $<P^+>$')
                # for i in range(len(datas)):
                #     ax.plot(datas[i], label=labels[i])
                #     ax.set_ylabel(labels[i])
                l1, = ax.plot(datas[0], 'b-', label=labels[0])
                ax.set_ylabel(y_labels[0], color='b')
                l2, = ax2.plot(datas[1], 'g-', label=labels[1])
                ax2.set_ylabel(y_labels[1], color='g')
                ax.set_xlabel('time (10^5)')

                ax = plt.subplot(212)
                ax2 = ax.twinx()
                l3, = ax.plot(datas[2], 'r-', label=labels[2])
                ax.set_ylabel(y_labels[2], color='r')
                ax.set_xlabel('time (10^5)')
                l4, = ax2.plot(datas[3], 'c-', label=labels[3])
                ax2.set_ylabel(y_labels[3], color='c')

                # plt.title(title)
                # plt.ylabel(u"<w>, \u03C3(w)")
                plt.xlabel('time (10^5)')
                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
                # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2),
                #     ncol=2, fancybox=True, shadow=True)
                plt.figlegend((l1, l2, l3, l4), labels, loc = 'upper center', ncol=2)
                figname = "quatro.png"
                plt.savefig(os.path.join(path, dir, figname))
                plt.clf()