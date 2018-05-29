import matplotlib
from matplotlib import pyplot as plt

matplotlib.use('GTKAgg')


def run_plot_thread():

    global scaled_data

    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.hold(True)

    # Wait for our first data point to be available
    while len(scaled_data) != 3 or isinstance(scaled_data[2], str):
        pass

    x = scaled_data[0]
    y = scaled_data[1]

    plt.show(False)
    plt.draw()

    background = fig.canvas.copy_from_bbox(ax.bbox)

    points = ax.plot(x, y, 'o')[0]

    while True:
        if len(scaled_data) == 3 and not isinstance(scaled_data[2], str):

            # update the xy data
            x = scaled_data[0]
            y = scaled_data[1]
            z = scaled_data[2]
            points.set_data(x, y)

            # restore background
            fig.canvas.restore_region(background)

            # redraw just the points
            ax.draw_artist(points)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)

            #
            # else:
            #     # redraw everything
            #     fig.canvas.draw()

        plt.close(fig)