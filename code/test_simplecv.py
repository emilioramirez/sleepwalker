import getopt
import sys
import time

from collections import deque
from multiprocessing import Process
from SimpleCV import Camera, VideoStream, Display, cv2


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
FRAME_WIDTH = 800
FRAME_HEIGHT = 600

class Watcher(object):

    def __init__(self,
                 camera_id,
                 output_fname,
                 show_display=False,
                 width=FRAME_WIDTH,
                 height=FRAME_HEIGHT,
                 fps=24,
                 video_buffer_fname=BUFFER_NAME):
        self.video_streamer = VideoStream(fps=fps, filename=BUFFER_NAME,
                                          framefill=True)
        self.camera = Camera(camera_id,
                             prop_set={width: width, height: height})
        self.display = None
        if show_display:
            self.display = Display((width, height))
        self.video_buffer_fname = video_buffer_fname

    def start(self):
        while True:
            frame = self.camera.getImage()
            self.video_streamer.writeFrame(frame)
            if self.display:
                frame.save(self.display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    @staticmethod
    def save_film_to_disk(self, buffer_name, output_fname):
        """Use avconv to process the video buffer."""
        encoding_params = " -i {0} -c:v mpeg4 -b:v 700k -r 24 {1}".format(
            self.video_buffer_fname, output_fname)
        call('avconv' + encoding_params, shell=True)


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
    process = Process(target=watcher.save_film_to_disk,
                      args=(watcher.video_buffer_fname, output_fname))
    process.start()
