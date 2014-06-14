import datetime
import getopt
import random
import sys
import time

from collections import deque
from multiprocessing import Process
from SimpleCV import Camera, VideoStream, Display, cv2
from subprocess import call

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
BUFFER_NAME = 'buffer.avi'
BUFFER_LEN = 100
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
DEFAULT_FPS = 25

class Watcher(object):

    def __init__(self,
                 camera_id,
                 output_fname,
                 show_display=False,
                 width=FRAME_WIDTH,
                 height=FRAME_HEIGHT,
                 fps=24,
                 video_buffer_fname=BUFFER_NAME,
                 buffer_len=BUFFER_LEN):
        self.video_streamer = VideoStream(fps=DEFAULT_FPS, filename=BUFFER_NAME,
                                          framefill=False)
        self.camera = Camera(camera_id,
                             prop_set={width: width, height: height})
        self.display = None
        if show_display:
            self.display = Display((width, height))
        self.film_buffer_fname = video_buffer_fname
        self.buffer = deque([], buffer_len)
        self.movement_flag = False
        self.fps = fps

    def detect_movement(self):
        """Process the current buffer and return True if movement is detected"""
        return False if random.randint(0, 100) < 80 else True

    def start(self):
        while True:
            self.fill_buffer()
            if self.detect_movement():
                """Dump buffer to a file."""
                map(self.video_streamer.writeFrame, self.buffer)
                self.movement_flag = True
                print('Movement')
            else:
                if self.movement_flag:
                    # Movement stoped. Save film.
                    self.process_film()
                self.buffer.clear()
                self.movement_flag = False
                print('No movement')

    def fill_buffer(self):
        while len(self.buffer) < self.buffer.maxlen:
            frame = self.camera.getImage()
            self.buffer.append(frame)
            if self.display:
                frame.save(self.display)
        return

    def save_film_to_disk(self):
        """Use avconv to process the video buffer."""
        now = datetime.datetime.now()
        output_fname = '%s_watcher.avi' % now.isoformat()
        encoding_params = " -i {0} -c:v mpeg4 -b:v 700k -r 24 {1}".format(
            self.film_buffer_fname, output_fname)
        self.film_buffer_fname = '%s_buffer.avi' % now.isoformat()
        call('avconv' + encoding_params, shell=True)
        self.video_streamer = VideoStream(fps=self.fps,
                                          filename=self.film_buffer_fname,
                                          framefill=False)

    def process_film(self):
        process = Process(target=watcher.save_film_to_disk)
        process.start()


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
    watcher.start()  # Main loop. Stops when 'q' is pressed.
