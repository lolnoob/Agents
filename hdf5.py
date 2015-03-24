import numpy as np
import numpy.random
import matplotlib.pyplot as plt

# Generate some test data
file_path = "/home/tomek/Studia/magisterka/agents/outputs/20150320/20150320_184936_history_n1000000_k3_a0.25_steps1100000_steps2100000_p1e-06.txt.npy"
data = np.load(file_path)
# data = np.array([[1, 2, 3], [4, 5, 6]])
for i in range(0, 200, 2):
    x = data[i+1]
    y = data[i]
    plt.clf()
    # heatmap, xedges, yedges = np.histogram2d(x, y, bins=[100, 100], range=[[0.0, 50.], [0., 1.]])
    heatmap, xedges, yedges = np.histogram2d(x, y, 50)
    extent = [xedges[0], xedges[-1], yedges[0], 100*yedges[-1]]
    # extent = [0., 4., 0., 1.0]
    heatmap = np.rot90(heatmap)
    heatmap = np.flipud(heatmap)
    # fig2 = plt.figure()
    plt.pcolormesh(xedges,yedges,heatmap)
    plt.xlabel('x')
    plt.ylabel('y')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    plt.savefig('/home/tomek/Studia/magisterka/agents/outputs/histogram/'+str(i).zfill(3)+'.png')

# plt.clf()
# plt.imshow(heatmap, extent=extent)
# plt.show()
#
# plt.clf()
# hist, bins = np.histogram(x, bins=10)
# width = 0.7 * (bins[1] - bins[0])
# center = (bins[:-1] + bins[1:]) / 2
# plt.bar(center, hist, align='center', width=width)
# plt.show()