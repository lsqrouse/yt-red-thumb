import cv2
import numpy as np
import time
from os import listdir
from os.path import isfile, join
framewidth = 640
frameHeight = 480
def empty(a):
    pass
# cv2.namedWindow("Parameters")
# cv2.resizeWindow("Parameters", 640, 240)
# cv2.createTrackbar("Thres1", "Parameters", 150, 255, empty)
# cv2.createTrackbar("Thres2", "Parameters", 255, 255, empty)
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
            cv2.imwrite("./out/image-" + str(file) + ".png", img)

    perc = arrowcount * 1.0 / len(onlyfiles) * 100
    print("Found " + str(arrowcount) + " of " + str(len(onlyfiles)) + " arrows, " + str(perc) + "% success rate")
    f.close()
    cv2.waitKey(0)
def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_BGR2GRAY)
        imageBlank = np.zeros((height,  width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_BGR2GRAY)
        hor = np.hstack(imgArray)
        ver = hor
    return ver
def test():
    img = cv2.imread("colored_arrows.jpg")
    # cv2.imshow("res", img)
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img, (7, 7), 1)
    thres1 = cv2.getTrackbarPos("Thres1", "Parameters")
    thres2 = cv2.getTrackbarPos("Thres2", "Parameters")
    img_canny = cv2.Canny(img_blur, thres1, thres2)
    print("getting stack")
    imgStack = stackImages(0.8, ([img, img_blur]))
    print("got stack")
    cv2.imshow("result.png", imgStack)
    print("showing stack")
    # kernel =  np.ones((3, 3))
    # img_dilate = cv2.dilate(img_canny, kernel, iterations=2)
    # img_erode = cv2.erode(img_dilate, kernel, iterations=1)
main()