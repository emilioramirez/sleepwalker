from collections import deque, namedtuple
from config import (FRAME_WIDTH, FRAME_HEIGHT, EXTRA_TIME, VIDEO_DIR,
                    VIDEO_PREFIX)
from datetime import datetime, timedelta
from multiprocessing import Process
from os import path
from SimpleCV import Image, Camera, VideoStream, Display
from subprocess import call

from detector import VideoFrame, Detector


class Watcher(object):

    def __init__(self,
                 camera_id=None,
                 show_display=False,
                 width=FRAME_WIDTH,
                 height=FRAME_HEIGHT,
                 extra_time=EXTRA_TIME,
                 video_directory=VIDEO_DIR,
                 video_prefix=VIDEO_PREFIX):
        self.camera = Camera(camera_id, prop_set={width: width, height: height})
        self.total_pixels = height * width
        self.detector = Detector()
        self.display = None
        if show_display:
            self.display = Display((width, height))
        self.extra_time_delta = timedelta(seconds=extra_time)
        self.video_prefix = path.join(video_directory, video_prefix)

    def get_frame(self):
        """
        Get a frame with the camera, transform to greyscale and convert to Numpy
        array.

        """
        now = datetime.now()
        image = self.camera.getImage().smooth().toGray()
        return VideoFrame(image=image, timestamp=now)

    def main_loop(self):
        frame_pre = self.get_frame()
        frame = self.get_frame()
        frame_post = self.get_frame()
        video_buffer = []
        record_until = datetime.now()
        while True:
            detect = self.detector.detect_motion(frame_pre, frame, frame_post)
            if detect['has_motion']:
                record_until = frame.timestamp + self.extra_time_delta

            if self.display:
                detect['difference_image'].save(self.display)

            if frame.timestamp < record_until:
                video_buffer.append(frame)
            else:
                if video_buffer:
                    self.save_video(video_buffer)
                video_buffer = []

            frame_pre = frame
            frame = frame_post
            frame_post = self.get_frame()

    def save_video(self, video_buffer):
        """Use avconv to process the video buffer."""
        if not video_buffer:
            return None
        timestamp = video_buffer[0].timestamp.isoformat()
        timestamp = timestamp[:timestamp.rfind('.')]
        buffer_fname = '%s_%s.avi' % (self.video_prefix, timestamp)
        start = video_buffer[0].timestamp
        end = video_buffer[-1].timestamp
        delta = (end - start).seconds
        if delta:
            fps = len(video_buffer) / delta
            print len(video_buffer), "frames in", delta, "seconds:", fps
            video_streamer = VideoStream(fps=fps,
                                         filename=buffer_fname,
                                         framefill=False)
            map(video_streamer.writeFrame, [frame.image for frame in video_buffer])
            print "Saved video:", buffer_fname

