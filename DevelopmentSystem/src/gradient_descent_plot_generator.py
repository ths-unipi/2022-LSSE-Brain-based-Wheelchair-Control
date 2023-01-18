import os
from matplotlib import pyplot as plt


class GradientDescentPlotGenerator:

    def __init__(self):
        self._image_path = os.path.join(os.path.abspath('..'), 'data', 'gradient_descent_plot.png')

    def generate_plot(self, losses: list):
        # plot
        plt.plot(range(1, len(losses) + 1), losses)
        plt.xlabel('Iterations')
        plt.ylabel('Loss Function')

        # save plot as PNG
        plt.savefig(self._image_path, dpi=300)
        print('[+] Gradient Descent Plot exported')

        # show the plot
        # plt.show()
