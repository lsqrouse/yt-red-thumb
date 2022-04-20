import cv2
import numpy as np
import time
from os import listdir
from os.path import isfile, join

write = False

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
def main():
    mypath = './img/arrow/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    arrowcount = 0
    f = open("fails.txt", "w")
    for file in onlyfiles:
        print(str(file))
        img = cv2.imread(mypath + str(file))

        # remove everything other than red from iamge
        img_red = np.copy(img)
        img_red[(img_red[:, :, 0] > 50) | (img_red[:, :, 1] > 50) | (img_red[:, :, 2] < 90)] = 0
        # ihstack((cv2.resize(img, (650, 500)), cv2.resize(img_copy, (650, 500))))
        img = img_red


        foundarrow = False
        contours, hierarchy = cv2.findContours(preprocess(img), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        print("found contours")
        for cnt in contours:
            print("processing countour")
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
        if foundarrow:
            arrowcount += 1
        else:
            f.write(str(file) + " sides: " + str(sides) + " len of approx: " + str(len(approx)) +  '\n')
            if write:
                cv2.imwrite("./out/image-" + str(file) + ".png", img)

    perc = arrowcount * 1.0 / len(onlyfiles) * 100
    print("Found " + str(arrowcount) + " of " + str(len(onlyfiles)) + " arrows, " + str(perc) + "% success rate")
    f.close()
    cv2.waitKey(0)

main()