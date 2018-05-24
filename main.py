import cv2 as cv
import sys

# cap is the capture device of the image, meaning that it is used to get new images from the camera. The camera has a
# physical device identifier of /dev/video0 on the computer filesystem, so we provide that index. We also have the
# option of providing a URL for an MJPG stream.
if len(sys.argv) > 1:
    cap = cv.VideoCapture(sys.argv[1])
else:
    cap = cv.VideoCapture(0)

# Create a new window to display the video feed
cv.namedWindow('frame')


while True:
    # The image (pulled from the camera using OpenCV). This variable represents all of the pixel values coming off the
    # camera stream. The word "frame" represents a single image from a stream of images from a camera, so "frame" and
    # "image" are interchangeable. Although we don't usually need to refer to the values directly, some information on
    # the image: There are usually 3 indexes: a row, a column, and the color channel (usually 3 -- RGB: red, green, and
    # blue; or HSV: hue, saturation and value). The row index starts at 0 being the upper left, and increments left to
    # right in the image. the column index starts at 0 being the upper left, and increments top to bottom in the image
    # (note: potentially counter-intuitive). The channel is usually from 0 to 2, and the color order can vary.
    ret, image = cap.read()

    # Our operations on the frame come here
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv.imshow('frame', image)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# When everything is complete, release the capture
cap.release()
cv.destroyAllWindows()


# The main function is where the execution begins in the script
def main():

    # OpenCV has a build in video display to show the camera feed visually on the Jetson desktop

    # These values are used to filter the camera image so that H is between Hmin and Hmax, S is between Smin and Smax, and
    # V is between Vmin and Vmax.  If the HSV value falls outside of any of the ranges, then it is set to 0 (a black pixel).
    # This is how we can filter for the strong green LED that is reflecting back into the camera from the retroreflective tape.
    #
    # List of properties for the sliders
    names = ["H Min", "S Min", "V Min", "H Max", "S Max", "V Max"]

    # Create an easy sliderbar to choose the values for the above values while the program is running (rather than hard coded
    # in python)
    # Create new sliders on the image window defaulting to the values from the file
    for index, val in enumerate(values1.readlines()):
        cv2.createTrackbar(names[index], "image", int(val), 255, nothing)

    values1.close()
    # cv2.createTrackbar("Min Size", "image", 0, 10000, nothing)
    # cv2.createTrackbar("Max Size", "image", 0, 10000, nothing)

    # Keep capturing frames... forever...
    while True:
        # Get a frame from the camera
        # ret is a True or False value if the camera read was successful, and unsured in our code
        # by writing to image here, we are writing to the global variable because of the global image above
        ret, image = cap.read()

        # Get the values from the sliders and adjust the filter values properly
        # We call these green because the LED is green.  If the LEDs were a different color, then we'd change that here.
        lower_green = np.array([cv2.getTrackbarPos('H Min', 'image'), cv2.getTrackbarPos('S Min', 'image'),
                                cv2.getTrackbarPos('V Min', 'image')])  # HSV Value
        upper_green = np.array([cv2.getTrackbarPos('H Max', 'image'), cv2.getTrackbarPos('S Max', 'image'),
                                cv2.getTrackbarPos('V Max', 'image')])  # HSV Value

        # lower_green = np.array([83, 35, 157]) should be similar to above
        # upper_green = np.array([153, 166, 224])

        # Blur to reduce noise
        # The blur makes very small pixel regions of 5 by 5 "fuzz" into 0.  It removes spurious small regions that match the
        # HSV color range, which happens fairly often.  If we did not blur them away, the tracking algorithm may assign an ID
        # the small region, which we know is not a real vision target.
        # The actual values of the 5 by 5 that are used to filter are selected to follow the Gaussian distribution (a hill at the
        # center of the 5x5 (so at 3x3), that tapers off into 0 on all sides)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        # Convert Image to HSV so we can filter better
        # The original image is not in HSV format, but in RGB  (BGR is just a shifted ordering)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Mask the image to only include the colors we're looking for
        # A Mask is going to make a monochrome image (rather than RGB it is grayscale) where the pixel value is kept if within the range
        # and set to 0 if it out of the range.  This means that each pixel is 8 bits
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Threshold the image for the sake of all of the other things we have to do
        # The Thresholded image is now a binary mask, of 0 or 1 (still stored as 8 bits for memory purposes), so a pixel is either on or off.
        # the 1 is assigned for any pixel in range of 127 to 255, and assigned a 0 for values 0 to 126.
        ret, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        # Kernel is a matrix of 5x5 with all set to 1.  This is used as a way to remove small pixel regions in the thresh image
        # Each matrix entry is stored as an unsigned integer 8 bits (an unsigned character in C).  This data size was chosen to match
        # the thresh data size so that it uses less math computation than 32 bit values.
        kernel = np.ones((5, 5), np.uint8)

        # Eliminates small, meaningless, peasant edges
        thresh = cv2.erode(thresh, kernel, iterations=1)

        # Combines parts of polygons (allows us to see the target, even with blockage)
        # Dilate tries to grow a region so that neighboring regions may lump together into a single region.
        # If the two or more regions are too far apart in pixel size (beyond iterations=3), then the regions stay separated.
        thresh = cv2.dilate(thresh, kernel, iterations=3)

        # Find the contours (outlines) of all the shapes in the threshold
        # Contours are the bounding boxes along the edges of where the vision target is surrounded by 0 pixels
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Reduce the amount of points in each set of contours
        # We want to draw simplified bounding boxes around each of the vision targets, so we overwrite a contour with fewer data points
        for x in range(0, len(contours)):
            epsilon = 0.01 * cv2.arcLength(contours[x], True)
            contours[x] = cv2.approxPolyDP(contours[x], epsilon, True)

        # Eliminate contours by perimeter
        # This removes entries in contours that are too small, less than MIN_PERIMETER in bounding box length
        contours = [x for x in contours if not cv2.arcLength(x, True) < MIN_PERIMETER]

        # The bounding boxes of the current frame only
        bounding_boxes = []

        # Actually create the bounding boxes and draw them on screen
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)  # OpenCV determines the actual bounding box coordinates from the contour
            bounding_boxes.append(
                [x, y, w, h])  # We store it in an array, x, y are the upper left, and w, h are the width, height
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0),
                          2)  # draw in the image a rectangle (x+w, y+h) is the lower right corner
            # (0, 255, 0) is BGR to draw in green, 2 is the line thickness

        # We choose to draw the center point of the last few frames of the same tracked object on the screen, as a circle of
        # different sizes as the data gets older.  This is just a way to represent the motion of the target over the last few frames
        # on the computer screen.
        # Go over every path and draw circles for a visual representation. Radius is based on path index.
        for path in paths:
            for i, p in enumerate(path):
                cv2.circle(image, (int(p[0]), int(p[1])), i, (255, 0, 0), thickness=-1)
            # hull = cv2.convexHull(c)
            # hulls.append(hull)
            # cv2.drawContours(image, [hull], 0, (0, 255, 0), 3)

        # Verify which bounding box is which from frame to frame
        track(bounding_boxes)

        # Display the windows on the Jetson desktop GUI
        cv2.imshow("image", image)
        cv2.imshow("mask", mask)
        cv2.imshow("thresh", thresh)

        # Wait for the escape key and exit, otherwise we loop forever
        k = cv2.waitKey(1) & 0xFF

        if k == 27:
            break

    # Write the values of the current slider positions to the file
    # This gives us flexibility to remember the slider settings, which vary between different arenas because of the lighting conditions
    values2 = open("values.txt", "w")
    for name in names:
        values2.write(str(cv2.getTrackbarPos(name, 'image')) + "\n")

    # Close all windows, cleanly end the program
    values2.close()
    cv2.destroyAllWindows()