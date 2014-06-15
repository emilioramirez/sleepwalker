

class Detector():
    
    THRESHOLD_MULTIPLIER = 2.0
    NOISE_LEVEL = 2.0

    def __init__(self, noise_level=NOISE_LEVEL, threshold_multiplier=THRESHOLD_MULTIPLIER):
        self.threshold_multiplier = threshold_multiplier
        self.noise_level = noise_level
        self.last_diff = None
        self.last_mean = None

    def calculate_threshold(self):
        return self.threshold

    def calculate_diff(self, prev_img, next_img):
        return next_img - prev_img

    def calculate_matrix(self, img):
        return img.getNumpy()

    def calculate_mean(self, matrix):
        return matrix.mean()

    def has_motion(self, prev_img, next_img):
        """
        Detect motion between two SimpleCV.Image
        """
        self.last_diff = self.calculate_diff(prev_img, next_img)
        matrix = self.calculate_matrix(self.last_diff)
        self.last_mean = self.calculate_mean(matrix)

        if self.last_mean >= (self.threshold_multiplier * self.noise_level):
            return True
        else:
            return False