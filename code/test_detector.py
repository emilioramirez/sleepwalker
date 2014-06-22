from SimpleCV import Camera, Display, time
from detector import Detector

cam = Camera()
disp = Display()
det = Detector()

FPS = 25
TIME_TO_SLEEP = 1.0 / FPS

while disp.isNotDone():
    previous = cam.getImage() #grab a frame
    time.sleep(TIME_TO_SLEEP) #wait for half a second
    current = cam.getImage() #grab another frame
    
    MESSAGE = ""
    if det.has_motion(previous, current):
        MESSAGE = "Motion Detected"

    det.last_diff.show()
    print det.last_mean, MESSAGE

    if disp.mouseLeft:
        break