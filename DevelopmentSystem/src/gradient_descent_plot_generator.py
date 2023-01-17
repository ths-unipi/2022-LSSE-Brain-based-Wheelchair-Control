import os
from matplotlib import pyplot as plt


class GradientDescentPlotGenerator:

    def __init__(self):
        self.image_path = os.path.join(os.path.abspath('..'), 'data', 'gradient_descent_plot.png')

    def generate_plot(self, losses: list):
        # plot
        plt.plot(range(1, len(losses) + 1), losses)
        plt.xlabel('Iterations')
        plt.ylabel('Loss Function')

        # save plot as PNG
        plt.savefig(self.image_path, dpi=300)

        # show the plot
        plt.show()
