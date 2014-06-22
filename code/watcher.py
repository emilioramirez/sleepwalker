import os
import time

from collections import deque, namedtuple
from config import (FRAME_WIDTH, FRAME_HEIGHT, EXTRA_TIME, VIDEO_DIR,
                    VIDEO_PREFIX, DO_COMPRESS)
from datetime import datetime, timedelta
from multiprocessing import Process
from SimpleCV import Image, Camera, VideoStream, Display
from subprocess import call

from detector import VideoFrame, Detector


class Watcher(object):

    def __init__(self,
                 camera_id=0,
                 show_display=False,
                 width=FRAME_WIDTH,
                 height=FRAME_HEIGHT,
                 extra_time=EXTRA_TIME,
                 video_directory=VIDEO_DIR,
                 video_prefix=VIDEO_PREFIX,
                 do_compress=DO_COMPRESS):

        self.camera = Camera(0, prop_set={"width":width, "height":height})
        # In case the camera didn't support the resolution given, check:
        width = self.camera.getProperty('width')
        height = self.camera.getProperty('height')
        self.total_pixels = height * width

        self.detector = Detector()
        self.display = None
        if show_display:
            self.display = Display((width, height), title="Sleepwalker")
        self.extra_time_delta = timedelta(seconds=extra_time)
        self.video_prefix = os.path.join(video_directory, video_prefix)
        self.do_compress = do_compress

    def get_frame(self):
        """
        Get a frame with the camera, transform to greyscale and convert to Numpy
        array.

        """
        now = datetime.now()
        image = self.camera.getImage().toGray()
        return VideoFrame(image=image, timestamp=now)

    def main_loop(self):
        record_until = datetime.now()
        frame_pre = self.get_frame()
        frame = self.get_frame()
        frame_post = self.get_frame()
        video_buffer = []

        #t0 = frame_pre.timestamp
        #t1 = frame.timestamp
        #t2 = frame_post.timestamp
        #mu2 = (t2 - t1).microseconds
        #mu1 = (t1 - t0).microseconds
        #delta = (mu2 + mu1) / 2
        #n = 0
        while True:
            if self.display:
                frame.image.save(self.display)
            detect = self.detector.detect_motion(frame_pre, frame, frame_post)
            if detect['has_motion']:
                record_until = frame.timestamp + self.extra_time_delta

            if frame.timestamp < record_until:
                video_buffer.append(frame)
            else:
                if video_buffer:
                    buffer_fname = self.save_video(video_buffer)
                    if self.do_compress and buffer_fname:
                        proc = Process(target=self.compress_video,
                                       args=(buffer_fname,))
                        proc.start()
                del video_buffer
                video_buffer = []

            #old_delta = delta
            #
            #t0 = frame_pre.timestamp
            #t1 = frame.timestamp
            #t2 = frame_post.timestamp
            #mu2 = (t2 - t1).microseconds
            #mu1 = (t1 - t0).microseconds
            #new_value = (mu2 + mu1) / 2
            #
            #
            #delta = (n * old_delta + new_value) / (n + 1.0)
            #
            #print "delta:", delta, '(new value: %f)'%new_value
            #n += 1

            frame_pre = frame
            frame = frame_post
            time.sleep(0.075)
            frame_post = self.get_frame()

    def save_video(self, video_buffer):
        """Use avconv to process the video buffer."""
        buffer_fname = None
        if not video_buffer:
            return None
        start = video_buffer[0].timestamp
        end = video_buffer[-1].timestamp
        delta = (end - start).seconds
        if delta:
            fps = len(video_buffer) / delta
            print len(video_buffer), "frames in", delta, "seconds:", fps
            timestamp = video_buffer[0].timestamp.isoformat()
            timestamp = timestamp[:timestamp.rfind('.')]
            buffer_fname = '%s%s.avi' % (self.video_prefix, timestamp)
            video_streamer = VideoStream(fps=fps,
                                         filename=buffer_fname,
                                         framefill=False)
            map(video_streamer.writeFrame, [frame.image for frame in video_buffer])
            print "- Video buffer saved:", buffer_fname
        return buffer_fname


    def compress_video(self, input_fname):
        output_fname = input_fname + '.mp4'
        log_fname = output_fname + '.log'
        params = '-i %s -c:a copy -c:v libx264 -crf 23 %s 2> %s' % (
            input_fname, output_fname, log_fname)
        call('avconv ' + params, shell=True)
        os.remove(input_fname)
        print "\t- Video buffer removed:", input_fname
        print "\t- Compressed video saved:", output_fname
