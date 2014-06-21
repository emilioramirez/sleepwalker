import datetime
import getopt
import random
import sys
import time
import numpy as np

from collections import deque
from multiprocessing import Process
from SimpleCV import Image, Camera, VideoStream, Display, cv2
from subprocess import call

from detector import Detector

# Configuration
HELP_MSG = """record.py [options]

    -c <cam NR>   If you know which cam you want to use: set it here, else the first camera available is selected

    -x <cam Width>    The width of camera capture. Default is 640 pixels
    --width

    -y <cam Height>   The height of camera capture. Default is 480 pixels
    --height

    -o <output>       The name of the output file. Default is the timestmp
    --output

    -h <help>     Show this message

"""
BUFFER_NAME = '/media/Datos/buffer.avi'
BUFFER_LEN = 25  # 1 seg
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
DEFAULT_FPS = 25


class Watcher(object):

    def __init__(self,
                 camera_id,
                 show_display=False,
                 width=FRAME_WIDTH,
                 height=FRAME_HEIGHT):
        self.camera = Camera(camera_id,
                             prop_set={width: width, height: height})
        self.total_pixels = height * width
        self.display = None
        if show_display:
            self.display = Display((width, height))

    def frames_diff(self, frame_pre, frame, frame_post):
        """Frames must be Numpy arrays."""
        d1 = cv2.absdiff(frame_post, frame)
        d2 = cv2.absdiff(frame, frame_pre)
        return cv2.bitwise_and(d1, d2)

    def get_grey_image(self):
        """
        Get a frame with the camera, transform to greyscale and convert to Numpy
        array.

        """
        return self.camera.getImage().smooth().toGray().getNumpy()[:,:,0]

    def detect_motion(self, frame_pre, frame, frame_post):
        """
        Detect motion by counting the number of pixels that change in the given
        frames. If a threshold is passed, return True.

        TODO: Move to its own class.

        """
        motion = False
        NOISE_THRESHOLD = 1.10
        CHANGE_THRESHOLD = 18
        diff_matrix = self.frames_diff(frame_pre, frame, frame_post)
        if self.display:
            Image(diff_matrix).save(self.display)

        changed_pixels = len(diff_matrix[np.where(diff_matrix > NOISE_THRESHOLD)])
        change_rate = (changed_pixels * 100.0) / self.total_pixels
        if change_rate > CHANGE_THRESHOLD:
            motion = True
        #print diff_matrix.mean(), change_rate
        return motion

    def main_loop(self):
        EXTRA_TIME = 3  # seconds of extra video after motion stops.
        frame_pre = self.get_grey_image()
        frame = self.get_grey_image()
        frame_post = self.get_grey_image()
        video_buffer = []
        record_until = datetime.datetime.now()
        while True:
            now = datetime.datetime.now()
            if self.detect_motion(frame_pre, frame, frame_post):
                record_until = now + datetime.timedelta(seconds=EXTRA_TIME)

            frame_pre = frame
            frame = frame_post
            frame_post = self.get_grey_image()

            if now < record_until:
                video_buffer.append(frame)
            else:
                if video_buffer:
                    self.save_video(video_buffer, timestamp=record_until)
                video_buffer = []

    def save_video(self, video_buffer, timestamp):
        """Use avconv to process the video buffer."""
        timestamp = timestamp.isoformat()
        timestamp = timestamp[:timestamp.rfind('.')]
        buffer_fname = 'sleepwalker_data/buffer_%s.avi' % timestamp
        video_streamer = VideoStream(fps=5,
                                     filename=buffer_fname,
                                     framefill=False)
        map(video_streamer.writeFrame, map(Image, video_buffer))
        print "Saved video:", buffer_fname


if __name__ == '__main__':
    camera_id = 0
    width = 640
    height = 480
    output_fname = 'output_{0}.mp4'.format(time.ctime().replace(" ", "_"))

    try:
        opts, args = getopt.getopt(sys.argv,"hx:y:o:c:",["width=","height=", "output="])
    except getopt.GetoptError:
        print HELP_MSG
        sys.exit(2)

    # Get the specified command line arguments
    for opt, arg in opts:
        if opt == '-h':
            print HELP_MSG
            sys.exit()
        elif opt in ('-x', '--width'):
            width = arg
        elif opt in ('-y', '--height'):
            height = arg
        elif opt in ('-c'):
            camera_id = arg
        elif opt in ('-o', '--output'):
            output_fname = arg

    # Finally let's start
    watcher = Watcher(camera_id, output_fname, show_display=True, width=width,
                      height=height)
    watcher.main_loop()  # Main loop. Stops when 'q' is pressed.
