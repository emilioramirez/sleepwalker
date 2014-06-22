import numpy as np

from collections import namedtuple
from SimpleCV import Image, cv2

from config import (NOISE_THRESHOLD, CHANGE_THRESHOLD)


VideoFrame = namedtuple('VideoFrame', ('image', 'timestamp'))


class Detector():

    def __init__(self,
                 noise_threshold=NOISE_THRESHOLD,
                 change_threshold=CHANGE_THRESHOLD):
        self.noise_threshold = noise_threshold
        self.change_threshold = change_threshold


    def frames_diff(self, frame_pre, frame, frame_post):
        """Frames must be Numpy arrays."""
        d1 = cv2.absdiff(frame_post, frame)
        d2 = cv2.absdiff(frame, frame_pre)
        return cv2.bitwise_and(d1, d2)

    @staticmethod
    def frame_to_2d_array(frame):
        return frame.image.getNumpy()[:,:,0]

    def detect_motion(self, frame_pre, frame, frame_post):
        """
        Detect motion by counting the number of pixels that change in the given
        frames. If a threshold is passed, return True.

        TODO: Move to its own class.

        """
        frame_pre = self.frame_to_2d_array(frame_pre)
        frame = self.frame_to_2d_array(frame)
        frame_post = self.frame_to_2d_array(frame_post)

        diff_matrix = self.frames_diff(frame_pre, frame, frame_post)
        filtered_indexes = np.where(diff_matrix > self.noise_threshold)
        changed_pixels = len(diff_matrix[filtered_indexes])
        width, height = diff_matrix.shape
        change_rate = (changed_pixels * 100.0) / (width * height)
        return {'has_motion': change_rate > self.change_threshold,
                'difference_image': Image(diff_matrix)}
