import numpy as np
import cv2 as cv

class Transformer:
    w = 1280
    h = 720 

    def __init__(self):
        src = np.float32([[312,281],[1089,219],[314,644],[1098,644]])
        dst = np.float32([[0,0],[self.w,0],[0,self.h],[self.w,self.h]])
 
        self.m = cv.getPerspectiveTransform(pts1,pts2)
 
    def transform(img):
        # img = cv.imread('arnto.jpg')
        dst = cv.warpPerspective(img, self.m, (self.w,self.h))
        return dst

