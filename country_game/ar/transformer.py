import cv2 as cv
import numpy as np

from country_game.ar.detector import Detector


class Transformer:

    def __init__(self, width: int = 1920, height: int = 1080):
        self.w = width
        self.h = height

        detector = Detector()
        reds = []
        greens = []
        while len(reds) != 1 or len(greens) != 3:
            detections = detector.detect()
            reds = [
                (detection[0], detection[1])
                for detection in detections if detection[3] == 'red'
            ]
            greens = [
                (detection[0], detection[1])
                for detection in detections if detection[3] == 'greens'
            ]
            print(greens)
        red = reds[0]
        greens.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
        print(greens)
        gr2 = greens[0]
        gr1 = greens[1]
        gr3 = greens[2]
        src = np.float32([red, gr1, gr2, gr3])
        dst = np.float32([[0, 0], [self.w, 0], [0, self.h], [self.w, self.h]])

        self.m = cv.getPerspectiveTransform(src, dst)

    def transform(self, img):
        # img = cv.imread('arnto.jpg')
        dst = cv.warpPerspective(img, self.m, (self.w, self.h))
        return dst


if __name__ == '__main__':
    trans = Transformer()
    detector = Detector()
    while True:
        frame = detector.get_raw_frame()
        frame = trans.transform(frame)
        detects = detector.detect(frame)
        print(detects)
