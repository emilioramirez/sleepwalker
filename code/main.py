import argparse
import time

from config import FRAME_HEIGHT, FRAME_WIDTH
from watcher import Watcher


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--show_display', action='store_true',
                        default=False, help='Show the frames difference (motion image).')
    parser.add_argument('-x', '--width', type=int, default=FRAME_WIDTH,
                        help='Set a frame width.')
    parser.add_argument('-y', '--height', type=int, default=FRAME_HEIGHT,
                        help='Set a frame height.')
    args = parser.parse_args()

    # Finally let's start
    watcher = Watcher(show_display=args.show_display,
                      width=args.width,
                      height=args.height)
    watcher.main_loop()  # Main loop. Stops when 'q' is pressed.
