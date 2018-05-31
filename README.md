# MTrack2

##### Authors: Benjamin Ward, Shaun Wu
###### Thank you to Dr. Travis Axtell and Zachary Perkins

Real-time visual object tracking and graphing in Python

A simple implementation of object tracking can be achieved via color tracking, where a specific color value from a still image or camera feed can be isolated, and the (x, y) pixel position of the contour can be logged. Through definition of a scale and two axes, and therefore an origin, the object can be tracked on a real plane with extreme accuracy, assuming the same shape is presented to the camera throughout. To increase detection accuracy, the source image is blurred, then converted from RGB (or a variant, such as BGR) to HSV, meaning that the color information is presented as a Hue, Saturation, Value pair instead of Red/Blue/Green. The image is then thresholded with a color mask (over a range, since HSV is still somewhat light-level-dependent), eroded, and dilated to reduce error from small color patches before contour search.

## Reference

Miki. “Python Opencv Color Tracking.” Stack Overflow, Stack Exchange, 16 July 2015, stackoverflow.com/questions/31460267/python-opencv-color-tracking.

Ryan. “OpenCV Object Tracking by Colour Detection in Python.” The Codacus, The Codacus, 13 Aug. 2017, thecodacus.com/opencv-object-tracking-colour-detection-python/.

“OpenCV: Image Thresholding.” OpenCV: Core Functionality, OpenCV, 23 Feb. 2018, docs.opencv.org/3.4.1/d0/de1/group__core.html.

John Canny. A computational approach to edge detection. Pattern Analysis and Machine Intelligence, IEEE Transactions on, (6):679–698, 1986.

“OpenCV: Changing Colorspaces.” OpenCV: Core Functionality, 23 Feb. 2018, docs.opencv.org/3.4/df/d9d/tutorial_py_colorspaces.html.
