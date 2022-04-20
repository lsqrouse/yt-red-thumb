import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
import random_words
import random
import requests
import shutil
import cv2
import numpy as np
import time
from os import listdir
from os.path import isfile, join
thumb_prefix = './img/to_parse/'

img_count = 0

used_words = {}

def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_canny = cv2.Canny(img_blur, 25, 200)
    #25 200 = 48
    kernel = np.ones((3, 3))
    img_dilate = cv2.dilate(img_canny, kernel, iterations=3)
    img_erode = cv2.erode(img_dilate, kernel, iterations=3)
    return img_erode
def find_tip(points, convex_hull):
    length = len(points)
    indices = np.setdiff1d(range(length), convex_hull)
    for i in range(2):
        j = indices[i] + 2
        if j > length - 1:
            j = length - j
        if np.all(points[j] == points[indices[i - 1] - 2]):
            return tuple(points[j])
def parse_image(filename):
    print("parsing " +  str(filename))
    img = cv2.imread(thumb_prefix + filename)

    # remove everything other than red from iamge
    img_red = np.copy(img)

    try:
        img_red[(img_red[:, :, 0] > 50) | (img_red[:, :, 1] > 50) | (img_red[:, :, 2] < 90)] = 0
        # ihstack((cv2.resize(img, (650, 500)), cv2.resize(img_copy, (650, 500))))
        img = img_red


        foundarrow = False
        contours, hierarchy = cv2.findContours(preprocess(img), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
            hull = cv2.convexHull(approx, returnPoints=False)
            sides = len(hull)
            if 6 > sides > 3 and sides + 2 == len(approx):
                arrow_tip = find_tip(approx[:,0,:], hull.squeeze())
                if arrow_tip:
                    foundarrow = True
                    cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)
                    cv2.circle(img, arrow_tip, 3, (0, 0, 255), cv2.FILLED)
    except:
        print(filename)
    if foundarrow:
        return True
    return False

resp = parse_image("j1-zO0UX604.jpg")
print(resp)
