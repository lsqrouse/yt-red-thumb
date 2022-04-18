import cv2, numpy as np, argparse

img = cv2.imread("img/arrow/keralis.JPG")
img = cv2.resize(img, (1280, 720))

img_copy = np.copy(img)

img_copy[(img_copy[:, :, 0] > 50) | (img_copy[:, :, 1] > 50) | (img_copy[:, :, 2] < 90)] = 0

img_2 = np.hstack((cv2.resize(img, (650, 500)), cv2.resize(img_copy, (650, 500))))
cv2.imshow("Color Image VS Color Extracted Image", img_2)

cv2.waitKey(0)
cv2.destroyAllWindows()