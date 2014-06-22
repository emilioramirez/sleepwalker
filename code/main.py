import getopt
import sys
import time

from watcher import Watcher

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


if __name__ == '__main__':
    camera_id = 0
    width = 640
    height = 480

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
    watcher = Watcher(camera_id, show_display=True, width=int(width), height=int(height))
    watcher.main_loop()  # Main loop. Stops when 'q' is pressed.
