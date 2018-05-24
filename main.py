import cv2 as cv
import sys

from process import process
from tracking_utility import no_op


# cap is the capture device of the image, meaning that it is used to get new images from the camera. The camera has a
# physical device identifier of /dev/video0 on the computer filesystem, so we provide that index. We also have the
# option of providing a URL for an MJPG stream.
if len(sys.argv) > 1:
    cap = cv.VideoCapture(sys.argv[1])
else:
    cap = cv.VideoCapture(0)

# Create a new window to display the video feed
cv.namedWindow('frame')

# These values are used to filter the camera image so that H is between Hmin and Hmax, S is between Smin and Smax, and
# V is between Vmin and Vmax.  If the HSV value falls outside of any of the ranges, then it is set to 0 (a black pixel).
# This is how we can filter for the color of the tracked object.
#
# List of properties for the sliders
names = ["H Min", "S Min", "V Min", "H Max", "S Max", "V Max"]
values = [0, 94, 152, 201, 255, 255]

# Create trackbars (sliders) on the image window to choose the values for the above values while the program is
# running (rather than hard coded). Defaults to values set above.
for index in range(6):
    cv.createTrackbar(names[index], 'frame', values[index], 255, no_op)

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
    image, masked, thresholded = process(frame)

    # Display the resulting frame
    cv.imshow('frame', frame)
    cv.imshow("mask", masked)
    cv.imshow("thresh", thresholded)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# When everything is complete, release the capture
cap.release()
cv.destroyAllWindows()
