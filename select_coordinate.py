# -*- coding: utf-8 -*-
import cv2

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Selected coordinates: ({x}, {y})")

image = cv2.imread("image.jpg")
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_callback)

while True:
    cv2.imshow("Image", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()