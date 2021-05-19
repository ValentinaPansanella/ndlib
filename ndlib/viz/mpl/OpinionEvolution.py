import os
import matplotlib as mpl
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import future.utils
import seaborn as sns

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class OpinionEvolution(object):

    def __init__(self, model, trends):
        """
        :param model: The model object
        :param trends: The computed simulation trends
        """
        self.model = model
        self.srev = trends
        self.ylabel = "Opinion"

    def plot(self, filename=None):

        def clustering_naive(ops, thereshold=0.001):
            i = 0
            d = dict()
            for el in ops:
                d[i] = el
                i += 1
            sorted_ops = sorted(d.items(), key = lambda kv:(kv[1], kv[0]))
            labels = [0 for i in range(len(ops))]
            for i in range(len(sorted_ops)-1):
                dist = abs(sorted_ops[i][1]-sorted_ops[i+1][1])
                if dist < thereshold:
                    labels[sorted_ops[i+1][0]] = labels[sorted_ops[i][0]]
                else:
                    labels[sorted_ops[i+1][0]] = labels[sorted_ops[i][0]]+1
            return labels

        def avg_nclusters(ops):   
            labels = clustering_naive(ops)
            cluster_participation_dict = {}
            for l in labels:
                if l not in cluster_participation_dict:
                    cluster_participation_dict[l] = 1
                else:
                    cluster_participation_dict[l] += 1
            #computing effective number of clusters using function explained in the paper
            C_num = 0
            C_den = 0
            for k in cluster_participation_dict:
                C_num += cluster_participation_dict[k]
                C_den += ((cluster_participation_dict[k])**2)
            C_num = (C_num**2)
            C = C_num/C_den
            return C

        """
        Generates the plot

        :param filename: Output filename
        :param percentile: The percentile for the trend variance area
        """
        ops = list(self.srev[len(self.srev)-1]['status'].values())
        nclusters = avg_nclusters(ops)

        descr = ""
        infos = self.model.get_info()
        infos = infos.items()
        infos = list(infos)[:2]


        for t in infos:
            descr += "%s: %s, " % (t[0], t[1])
        descr = descr[:-2].replace("_", " ")

        nodes2opinions = {}
        node2col = {}

        last_it = self.srev[-1]['iteration'] + 1
        last_seen = {}

        for it in self.srev:
            sts = it['status']
            its = it['iteration']
            for n, v in sts.items():
                if n in nodes2opinions:
                    last_id = last_seen[n]
                    last_value = nodes2opinions[n][last_id]

                    for i in range(last_id, its):
                        nodes2opinions[n][i] = last_value

                    nodes2opinions[n][its] = v
                    last_seen[n] = its
                else:
                    nodes2opinions[n] = [0]*last_it
                    nodes2opinions[n][its] = v
                    last_seen[n] = 0
                    if v < 0.33:
                        node2col[n] = '#ff0000'
                    elif 0.33 <= v <= 0.66:
                        node2col[n] = '#00ff00'
                    else:
                        node2col[n] = '#0000ff'
        
        sns.set_style("whitegrid")
        plt.figure(figsize=(30,18))

        mx = 0
        for k, l in future.utils.iteritems(nodes2opinions):
            if mx < last_seen[k]:
                mx = last_seen[k]
            x = list(range(0, last_seen[k]))
            y = l[0:last_seen[k]]
            plt.plot(x, y, lw=1, alpha=0.5, color=node2col[k])

        descr = descr + ', nc: {:.5f}'.format(nclusters)
        plt.title(descr, fontsize=40)
        plt.xlabel("Iterations", fontsize=40)
        plt.ylabel(self.ylabel, fontsize=40)
        plt.legend(loc="best", fontsize=30)
        plt.tick_params(axis='both', which='major', labelsize=40, pad=8)                
        
        plt.tight_layout()
        if filename is not None:
            plt.savefig(filename, papertype = 'a4', bbox_inches='tight')
            plt.clf()
        else:
            plt.show()