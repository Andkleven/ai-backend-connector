import cv2
import imutils
import numpy as np


ITERATIONS = 2
GREEN = (0, 255, 0)


def find_balls_by_color(hsv_image, orig_image, low_color, high_color):
    color_mask = cv2.inRange(hsv_image, low_color, high_color)
    color_mask = cv2.erode(color_mask, None, iterations=ITERATIONS)
    color_mask = cv2.dilate(color_mask, None, iterations=ITERATIONS)
    color_image = cv2.bitwise_and(orig_image, orig_image, mask=color_mask)
    return color_image, color_mask


def find_center_points(color_mask, min_ball_area_to_detect, orig_image=None):
    center_points = None
    contours = cv2.findContours(
        color_mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    for contour in contours:
        # Uncomment the below print to see the right
        # value for min_ball_area_to_detect
        # print("Ball area detected: {}".format(cv2.contourArea(contour)))
        if (cv2.contourArea(contour) < min_ball_area_to_detect):
            continue

        if orig_image is not None:
            cv2.drawContours(orig_image, contour, -1, GREEN, 3)
        # compute the center of the contour
        moments = cv2.moments(contour)
        center_x = int(moments["m10"] / moments["m00"])
        center_y = int(moments["m01"] / moments["m00"])
        if center_points is None:
            center_points = []
        center_points.append([center_x, center_y])

    if center_points is not None:
        center_points = np.array(center_points, dtype=np.float32)
        center_points = np.reshape(center_points, (-1, 1, 2))
    return center_points
