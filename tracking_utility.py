import cv2 as cv

from config import MAX_PATH_LEN


def no_op():
    """
    No operation - passed into OpenCV when no logic needs to occur for an operation
    :return: None
    """
    pass


def id_iterator():
    """
    Iterator, used to generate the next tracking ID sequentially.
    :return:
    """
    # The current tracking ID (used so that the same ID may not be repeated twice)
    curr_id = 0
    while True:
        yield curr_id
        curr_id += 1


def append_to_path(path, item):
    """
    Appends a point item to the path list. Deletes the oldest entry if needed.
    :param path: List to append point to
    :param item: Point information
    :return: None
    """
    path.append([item[0], item[1]])

    # Delete the oldest path entry, if required
    if len(path) > MAX_PATH_LEN:
        del path[0]


def interpolate_new_position(path, image):
    # Ignores frames where the target wasn't seen
    path_x = [num[0] for num in path if num[0] > -1]
    path_y = [num[1] for num in path if num[1] > -1]

    # Gets an array with change of position for all targets
    x_vel = [(num - path_x[i - 1]) for i, num in enumerate(path_x[1:len(path_x)])]
    y_vel = [(num - path_y[i - 1]) for i, num in enumerate(path_y[1:len(path_y)])]

    # Finds the average to get average velocity
    x_avg = sum(x_vel) / len(x_vel) if len(x_vel) > 0 else 0
    y_avg = sum(y_vel) / len(y_vel) if len(y_vel) > 0 else 0

    # Adds average to the current position
    x = path_x[-1] + x_avg
    y = path_y[-1] + y_avg

    # Plots where it predicts the next will be
    cv.circle(image, (int(x), int(y)), 10, (0, 0, 255), thickness=-1)

    return [x, y]


tracking_id = id_iterator()
