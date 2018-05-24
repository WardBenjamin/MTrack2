from config import MAX_DISTANCE_NEW, MAX_DISTANCE_INTERPOLATED, TOLERANCE
from tracking_utility import interpolate_new_position, append_to_path, tracking_id
from math import sqrt

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
