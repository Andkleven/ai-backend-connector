import cv2


def blur_and_hsv(image):
    blurred_frame = cv2.GaussianBlur(image, (5, 5), 0)
    hsv_image = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
    return hsv_image
