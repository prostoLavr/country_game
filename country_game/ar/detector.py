import cv2
import numpy as np


class Detector:
    cam = cv2.VideoCapture(0)

    def _get_preprop_img(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.blur(gray, (3, 3))
        return gray_blurred

    def _get_mask_img(self, img, color):
        hsv_min = None
        hsv_max = None
        if color == "green":
            hsv_min = np.array((33, 65, 56), np.uint8)
            hsv_max = np.array((83, 255, 255), np.uint8)
        elif color == "yellow":
            hsv_min = np.array((8, 174, 50), np.uint8)
            hsv_max = np.array((47, 255, 255), np.uint8)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(hsv, hsv_min, hsv_max)
        # thresh = cv2.medianBlur(thresh, 10)
        thresh = cv2.GaussianBlur(thresh, (5, 5), 20)
        return thresh

    def _get_circle_rect(self, coord, image):
        # print(coord)
        x, y, r = coord
        # print(image.shape)

        return image[max(0, y - r // 2):min(y + r // 2, 480),
        max(x - r // 2, 0):min(x + r // 2, 640)]

    def _get_mean_color(self, image):
        avg_color = np.mean(image, axis=(0, 1))
        # print(avg_color)
        # calculate mean color HSV
        # print(cv2.cvtColor(np.array([[avg_color]],  dtype=np.uint8),
        # cv2.COLOR_BGR2HSV))
        return cv2.cvtColor(
            np.array([[avg_color]], dtype=np.uint8), cv2.COLOR_BGR2HSV
            )[0][0]

    def _img_with_circles(self, detected, image):
        detected = np.uint16(np.around(detected))

        for pt in detected[0, :]:
            a, b, r = pt[0], pt[1], pt[2]

            cv2.circle(image, (a, b), r, (0, 255, 0), 2)

        return image

    def __init__(self):
        pass

    def get_raw_frame(self):
        return self.cam.read()[1]

    def detect(self, frame=None):
        if frame is None:
            _, frame = self.cam.read()
        img = frame.copy()

        #frame = self._get_preprop_img(img)
        green_img = self._get_mask_img(img, "green")
        red_img = self._get_mask_img(img, "yellow")
        detected_red_circles = cv2.HoughCircles(red_img,
                                                cv2.HOUGH_GRADIENT, 1, 30, param1=50,
                                                param2=18, minRadius=5, maxRadius=30)
        detected_green_circles = cv2.HoughCircles(green_img,
                                                  cv2.HOUGH_GRADIENT, 1, 30, param1=50,
                                                  param2=18, minRadius=5, maxRadius=30)
        detected_circles = None
        if detected_green_circles is not None:
            detected_circles = detected_green_circles
        if detected_red_circles is not None:
            detected_circles = detected_red_circles
        if detected_green_circles is not None and detected_red_circles is not None:
            detected_circles = np.concatenate([detected_green_circles, detected_red_circles], axis=1)

        if detected_circles is not None:
            img = self._img_with_circles(detected_circles, img)
            cv2.imshow("Detected Circle", img)
            detects = []
            for crl in detected_circles[0]:
                crl = np.round(crl)
                crl_rect_image = self._get_circle_rect(
                    np.round(crl).astype(int), img
                    )
                avg_hsv_color = self._get_mean_color(crl_rect_image)
                color = None
                if 0 <= avg_hsv_color[0] <= 30 and avg_hsv_color[1] > 50 and \
                        avg_hsv_color[2] > 50:
                    color = "red"
                elif (30 <= avg_hsv_color[0] <= 90 and avg_hsv_color[1] > 50
                      and \
                        avg_hsv_color[2] > 50):
                    color = "green"
                detects.append([crl[0], crl[1], crl[2], color])
            return detects
        else:
            return []
