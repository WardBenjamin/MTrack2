# The MAX_DISTANCE_NEW value is used to track new targets coming within the view of the camera. In order to ensure the
# tracking IDs stay the same for the same target, we set a larger value here to allow for some uncertainty that occurs
# from how the target enters the field of view. This represents the maximum difference between the interpolated target
# and the actual target IF the actual target doesn't have a previous path (aka we can't interpolate the value)
MAX_DISTANCE_NEW = 200

# The MAX_DISTANCE_INTERPOLATED value is used to track targets that have been within the camera field of view for 2 or
# more frames. This is the maximum difference between the interpolated target and the actual target IF the actual target
# has at least 2 frames to interpolate from
MAX_DISTANCE_INTERPOLATED = 100

# Maximum number of points stored in each path, based on the last MAX_PATH_LEN frames from the camera. We are using 7
# because the view becomes confusing/too busy to be useful when more information is presented.
MAX_PATH_LEN = 7

# This represents the minimum perimeter of each box for it to be considered valid. This prevents us from tracking
# objects that are too small or vision targets that are too distant. As smaller perimeters are allowed, we will also
# make mistakes and track targets that do not really exist (are not real field targets, just artifacts from what the
# camera happens to be looking at).
MIN_PERIMETER = 50

# The amount of times that a target must be absent for it's ID and path to be removed from the list. This gives us some
# time lag before we lose track of a target, which is helpful for sudden motions of the camera that settle quickly.
TOLERANCE = 3
