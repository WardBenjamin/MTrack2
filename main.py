import threading

import cv2 as cv
import sys

from graph import plot_data
from process import process
from tracking_utility import no_op
from mtrackmath import compute
from mtrackmath import origin

# cap is the capture device of the image, meaning that it is used to get new images from the camera. The camera has a
# physical device identifier of /dev/video0 on the computer filesystem, so we provide that index. We also have the
# option of providing a URL for an MJPG stream.

if len(sys.argv) > 1:
    cap = cv.VideoCapture(sys.argv[1])
else:
    cap = cv.VideoCapture(0)

# Create a new window to display the video feed
cv.namedWindow("frame")

# Create a new window for trackbars
cv.namedWindow("bars", cv.WINDOW_NORMAL)

# These values are used to filter the camera image so that H is between Hmin and Hmax, S is between Smin and Smax, and
# V is between Vmin and Vmax.  If the HSV value falls outside of any of the ranges, then it is set to 0 (a black pixel).
# This is how we can filter for the color of the tracked object.
#
# List of properties for the sliders
names = ["H Min", "S Min", "V Min", "H Max", "S Max", "V Max"]
values = [0, 94, 152, 201, 255, 255]


def on_win_click(event, x, y, flags, params):
    global current_point
    global points
    global raw_x
    global raw_y
    if event == cv.EVENT_LBUTTONUP:
        if current_point >= len(points) - 1:
            current_point = 0
        points[current_point] = x
        points[current_point + 1] = y
        current_point += 2
    raw_x = x
    raw_y = y


# These values are used to define the 2d plane mapped to pixel coordinates
points = [1, 0, 2, 0, 0, 1, 0, 2]
# This is used to keep track of which points is being set. If equal to len(points), no points are currently set
current_point = 0
# Used for scaling units
scales = [1, 1]

scaled_data = []

# Used for converting raw pixel data to real data
raw_x = 0
raw_y = 0

# Create trackbars (sliders) on the image window to choose the values for the above values while the program is
# running (rather than hard coded). Defaults to values set above.
for index in range(6):
    cv.createTrackbar(names[index], "bars", values[index], 255, no_op)

# Trackbars for X and Y Scaling, here is in cm, output file is in meters
cv.createTrackbar("X Scale", "bars", 1000, 1000, no_op)
cv.createTrackbar("Y Scale", "bars", 1000, 1000, no_op)

cv.setMouseCallback("frame", on_win_click, )



while True:
    # image is pulled from the camera using OpenCV. This variable represents all of the pixel values coming off the
    # camera stream. The word "frame" represents a single image from a stream of images from a camera, so "frame" and
    # "image" are interchangeable. Although we don't usually need to refer to the values directly, some information on
    # the image: There are usually 3 indexes: a row, a column, and the color channel (usually 3 -- RGB: red, green, and
    # blue; or HSV: hue, saturation and value). The row index starts at 0 being the upper left, and increments left to
    # right in the image. the column index starts at 0 being the upper left, and increments top to bottom in the image
    # (note: potentially counter-intuitive). The channel is usually from 0 to 2, and the color order can vary.
    #
    # ret is a True or False value if the camera read was successful (unused)
    ret, frame = cap.read()

    # Our operations on the frame come here
    image, masked, thresholded, path = process(frame)
    if path is not None:
        raw_x = path[-1][0]
        raw_y = path[-1][1]

    # Drawing lines to indicate the xy coord plane
    drawn_frame = image
    cv.arrowedLine(drawn_frame, (points[0], points[1]), (points[2], points[3]), (255, 0, 0), 5)
    cv.arrowedLine(drawn_frame, (points[4], points[5]), (points[6], points[7]), (0, 0, 255), 5)
    cv.circle(drawn_frame, (points[0], points[1]), 5, (255, 0, 0), -1)
    cv.circle(drawn_frame, (points[4], points[5]), 5, (0, 0, 255), -1)

    # Drawing the origin of xy coord plane
    org_data = origin(points)
    cv.circle(drawn_frame, (int(org_data[0]), int(org_data[1])), 5, (0, 255, 0), -1)

    cv.circle(drawn_frame, (int(raw_x), int(raw_y)), 5, (0, 255, 255), -1)

    # Getting scaling data from trackbar
    scales = [cv.getTrackbarPos("X Scale", "bars") / 1000, cv.getTrackbarPos("Y Scale", "bars") / 1000]

    # Processing data
    scaled_data = compute(points, org_data, [raw_x, raw_y, scales[0], scales[1]])

    if len(scaled_data) == 3 and not isinstance(scaled_data[2], str):
        plot_data(scaled_data[0], scaled_data[1], scaled_data[2])

    # Display the resulting frame
    cv.imshow("frame", drawn_frame)
    cv.imshow("mask", masked)
    cv.imshow("thresh", thresholded)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is complete, release the capture
cap.release()
cv.destroyAllWindows()
