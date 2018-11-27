import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

class HistogramGenerator(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.logger.info('HistogramGenerator Loaded')

    def generate_histogram(self,title_dataset_map):

        num_datasets = len(title_dataset_map)

        fig, axs = plt.subplots(1, num_datasets, sharey=True, tight_layout=True)

        for index, title in enumerate(title_dataset_map.keys()):

            dataset = title_dataset_map[title]

            axs[index].hist(dataset, bins=10, )

            axs[index].set_xlim([-1,1])

        plt.show()    