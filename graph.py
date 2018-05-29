import matplotlib
from matplotlib import pyplot as plt

from matplotlib.figure import Figure

# draw the figure so the animations will work
fig_xt: Figure = plt.gcf()
fig_xt.show()
fig_xt.canvas.draw()

plt.xlim([0, 100])
plt.ylim([0, 100])

plt.subplot(2, 1, 1)
plt.title('A tale of 2 subplots')
plt.ylabel('Damped oscillation')

plt.subplot(2, 1, 2)
plt.xlabel('Time (s)')
plt.ylabel('Undamped')


def plot_data(x, y, t):
    plt.subplot(2, 1, 1)
    plt.plot([x], [t], '.-')
    plt.subplot(2, 1, 2)
    plt.plot([y], [t], '.-')

    # plt.pause(0.01)  # I ain't needed!!!

    # update canvas immediately
    fig_xt.canvas.draw()
