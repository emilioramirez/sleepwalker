Sleepwalker
============

A library for facility the move detection for sleepwalkers, so we can have fun
with random behavior of sleepy people.


Dependencies
-------------

Depends on [SimpleCV][4], which itself depends on OpenCV,
pygame, scipy, Pillow, etc. Until we can write a tutorial for that, Google will help.

  - [Install OpenCV on Ubuntu][1]
  - [Install ffmpeg on Ubuntu 14.04][2]
  - [Install SimpleCV on Virtualenv][3]

Roadmap
--------

### API

  1. Detect movements. [PROTOTYPE]
  1. Save a stream of images with movement detected. [DONE]
  1. Configuration.  [PROTOTYPE]
  1. Automatic Calibration of the camera-related parameters.

### Apps

  - Sleepwalker: use your webcam to save a video every time you wake up at night.
  - Security: use a fixed webcam to store a video every time something moves within its sight.

Wishlist
--------

 - Support for IP cameras.
 - Infrared camera.
 - Detect sound ( *sleeptalker* )


[1]:https://help.ubuntu.com/community/OpenCV
[2]:https://github.com/jayrambhia/Install-OpenCV/issues/28
[3]:https://github.com/sightmachine/SimpleCV#virtualenv
[4]:http://simplecv.org/
