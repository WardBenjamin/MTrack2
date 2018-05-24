from config import MAX_DISTANCE_NEW, MAX_DISTANCE_INTERPOLATED, TOLERANCE, MIN_PERIMETER
from tracking_utility import interpolate_new_position, append_to_path, tracking_id
from math import sqrt

import numpy as np
import cv2 as cv

# A list of tracking IDs for each target. As new targets are in the camera field of view, they are each given an integer
# ID, starting from 0. Once a target is out of camera view, OpenCV loses its ID.  The value keeps incrementing (never
# repeats) as the program runs for a longer time and targets enter field of view and depart the field of view.
ids = []

# A list of lists of points representing the paths that each target has followed over MAX_PATH_LEN frames. This is
# represented as an array of arrays of arrays, I.E. Each path is stored as an array, and each point inside said path is
# also stored as an array. Used for interpolation. Synced up with ids such that paths[0] represents the same target that
# ids[0] does paths is used to draw circles of where the target has moved over the last few frames of the video, which
# is convenient for humans to understand the motion of the robot relative to the target.
paths = []


def process(frame):
    # Get the values from the sliders and adjust the filter values properly
    # We call these green because the LED is green.  If the LEDs were a different color, then we'd change that here.
    lower_green = np.array([cv.getTrackbarPos('H Min', 'frame'), cv.getTrackbarPos('S Min', 'frame'),
                            cv.getTrackbarPos('V Min', 'frame')])  # HSV Value
    upper_green = np.array([cv.getTrackbarPos('H Max', 'frame'), cv.getTrackbarPos('S Max', 'frame'),
                            cv.getTrackbarPos('V Max', 'frame')])  # HSV Value

    # Blur to reduce noise
    # The blur makes very small pixel regions of 5 by 5 "fuzz" into 0.  It removes spurious small regions that match the
    # HSV color range, which happens fairly often.  If we did not blur them away, the tracking algorithm may assign
    # an ID to the small region, which we know is not a real vision target. The actual values of the 5 by 5 that are
    # used to filter are selected to follow the Gaussian distribution (a hill at the center of the 5x5 (so at 3x3), that
    # tapers off into 0 on all sides)
    image = cv.GaussianBlur(frame, (5, 5), 0)

    # Convert Image to HSV so we can filter better
    # The original image is not in HSV format, but in RGB (BGR is just a shifted ordering)
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Mask the image to only include the colors we're looking for
    # A Mask is going to make a monochrome image (rather than RGB it is grayscale) where the pixel value is kept if
    # within the range and set to 0 if it out of the range.  This means that each pixel is 8 bits
    mask = cv.inRange(hsv, lower_green, upper_green)

    # Threshold the image for the sake of all of the other things we have to do
    # The thresholded image is now a binary mask, of 0 or 1 (still stored as 8 bits for memory purposes), so a pixel is
    # either on or off. The 1 is assigned for any pixel in range of 127 to 255, and assigned a 0 for values 0 to 126.
    ret, thresh = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)

    # Kernel is a matrix of 5x5 with all set to 1.  This is used as a way to remove small pixel regions in the thresh
    # image. Each matrix entry is stored as an unsigned integer 8 bits (an unsigned character in C).  This data size was
    # chosen to match the thresh data size so that it uses less math computation than 32 bit values.
    kernel = np.ones((5, 5), np.uint8)

    # Eliminates small, meaningless, peasant edges
    thresh = cv.erode(thresh, kernel, iterations=1)

    # Combines parts of polygons (allows us to see the target, even with blockage)
    # Dilate tries to grow a region so that neighboring regions may lump together into a single region.
    # If the two or more regions are too far apart in pixel size (beyond iterations=3), then the regions stay separated.
    thresh = cv.dilate(thresh, kernel, iterations=3)
    #
    # # Find the contours (outlines) of all the shapes in the threshold
    # # Contours are the bounding boxes along the edges of where the vision target is surrounded by 0 pixels
    # contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #
    # # Reduce the amount of points in each set of contours. We want to draw simplified bounding boxes around each of the
    # # vision targets, so we overwrite a contour with fewer data points
    # for x in range(0, len(contours)):
    #     epsilon = 0.01 * cv.arcLength(contours[x], True)
    #     contours[x] = cv.approxPolyDP(contours[x], epsilon, True)
    #
    # # Eliminate contours by perimeter
    # # This removes entries in contours that are too small, less than MIN_PERIMETER in bounding box length
    # contours = [x for x in contours if not cv.arcLength(x, True) < MIN_PERIMETER]
    #
    # # The bounding boxes of the current frame only
    # bounding_boxes = []
    #
    # # Actually create the bounding boxes and draw them on screen
    # for c in contours:
    #     # OpenCV determines the actual bounding box coordinates from the contour
    #     x, y, w, h = cv.boundingRect(c)
    #
    #     # We store it in an array, x, y are the upper left, and w, h are the width, height
    #     bounding_boxes.append([x, y, w, h])
    #
    #     # Draw in the image a rectangle (x+w, y+h) is the lower right corner. (0, 255, 0) is BGR to draw in green, and
    #     # the 2 represents the line thickness
    #     cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #
    # # We choose to draw the center point of the last few frames of the same tracked object on the screen, as a circle of
    # # different sizes as the data gets older.  This is just a way to represent the motion of the target over the last
    # # few frames on the computer screen.
    # # Go over every path and draw circles for a visual representation. Radius is based on path index.
    # for path in paths:
    #     for i, p in enumerate(path):
    #         cv.circle(image, (int(p[0]), int(p[1])), i, (255, 0, 0), thickness=-1)
    #     # hull = cv2.convexHull(c)
    #     # hulls.append(hull)
    #     # cv2.drawContours(image, [hull], 0, (0, 255, 0), 3)
    #
    # # Verify which bounding box is which from frame to frame
    # track(bounding_boxes)

    return image, mask, thresh


def track(boxes):
    all_matched = (len(boxes) == 0 and len(paths) == 0)

    if not all_matched:
        num_matched = 0
        matched_boxes = []

        for x, path in enumerate(paths):
            # Where it guesses it will be next frame given the path over the last few frames
            possible_locations = interpolate_new_position(path)

            # Possible matched boxes. Algorithm works by comparing the interpolated box to the actual box
            # and adds it if it is within MAX_DISTANCE_INTERPOLATED pixels
            possible_results = []

            for i, box in enumerate(boxes):
                bx = box[0] + box[2] / 2.0  # Center x coordinate
                by = box[1] + box[3] / 2.0  # Center y coordinate
                px = possible_locations[0]
                py = possible_locations[1]

                # Distance between where it is and where it thinks it will be
                dx = abs(bx - px)
                dy = abs(by - py)

                # Distance formula
                dist = sqrt(dx ** 2 + dy ** 2)

                # If we have nothing to go off of for interpolation, let the maximum distance be higher.
                max_dist = MAX_DISTANCE_NEW if len(path) < 2 else MAX_DISTANCE_INTERPOLATED

                if dist <= max_dist:  # Do nothing if it isn't
                    # Checks to make sure that the result found hasn't already been added to the list of matches
                    found = False
                    for box_id in matched_boxes:
                        if box_id == i:
                            found = True
                    if not found:
                        # When a match is found, store its index in the list "boxes", its distance from the
                        # interpolated target, and it's center coordinate.
                        possible_results.append([i, dist, bx, by])

            # Proceeds to further eliminate if there is more than one box by which one is the closest
            if len(possible_results) > 0:  # There are possible results
                distances = [i[1] for i in possible_results]  # All the distances for the possible results
                best = distances.index(min(distances))  # Index of the possibleResult with the smallest distance
                optimal_solution = possible_results[best]  # the one with minimum miss distance

                # Append the index of the best box in "boxes" to the list of matched boxes
                matched_boxes.append(optimal_solution[0])

                # Add the center coordinates of the object to it's path
                append_to_path(path, [optimal_solution[2], optimal_solution[3]])
                num_matched += 1

                # Labels it on screen to make things all pretty-like
                cv.putText(image, str(ids[x]), (int(optimal_solution[2]), int(optimal_solution[3] + 10)),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))  # Labels the value with the ID

            # If the box isn't found, we can take one of two paths.
            else:
                # If the final TOLERANCE number of coordinates in the list are equal to -1, -1, we eliminate the box.
                # Because -1 would never occur as an actual coordinate, this allows us to only delete the box if WE
                # have set the coordinate ourselves. This allows us to implement a tolerance system, wherein the box
                # will only disappear if it is absent for TOLERANCE amount of frames.
                if (len(path) >= TOLERANCE) and (
                        sum([1 for num in path[-TOLERANCE:len(path)] if sum(num) == -2]) == TOLERANCE):
                    del paths[x]
                    del ids[x]
                # If we haven't reached our max tolerance, then add another -1, -1
                else:
                    append_to_path(path, [-1, -1])

        # TODO: Output this to something else somehow
        # # Temporary code to communicate with the robot
        # id_arr = NumberArray.from_list(ids)
        # vision.putValue("IDS", id_arr)
        #
        # bounding_arr = NumberArray()
        # for box in matchedBoxes:
        #     for i in range(0, len(boxes[box])):
        #         bounding_arr.append(boxes[box][i])
        #
        # vision.putValue("BOUNDING_COORDINATES", bounding_arr)

        # If there are extra, unmatched boxes
        if num_matched < len(boxes):
            # Delete all the found ones from the list of boxes so we don't add ones we've already found
            for index in sorted(matched_boxes, reverse=True):
                del boxes[index]

            # Give each new box a tracking ID and a path
            for box in boxes:
                ids.append(tracking_id.next())
                cx = box[0] + box[2] / 2.0
                cy = box[1] + box[3] / 2.0
                paths.append([[cx, cy]])

    else:
        print("Something really terrible happened")
