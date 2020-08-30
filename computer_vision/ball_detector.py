import numpy as np
import cv2
import imutils


ITERATIONS = 2


class BallDetector():
    def __init__(self, params):
        self._min_ball_area_to_detect = \
            params["image_processing"]["min_ball_area_to_detect"]

        # Value ranges for HSV-values in OpenCV
        # H: 0-179, S: 0-255, V: 0-255
        self._low_ball_color = np.array(
            params["image_processing"]["ball_low_color"], dtype=np.float32)
        self._high_ball_color = np.array(
            params["image_processing"]["ball_high_color"], dtype=np.float32)

    def get_ball_transforms(self, image):
        if image is None:
            return None, None

        hsv_image = self._blur_and_hsv(image)

        good_ball_image, good_ball_mask = self._find_balls_by_color(
            hsv_image,
            image,
            self._low_ball_color,
            self._high_ball_color)
        good_ball_coordinates = self._find_center_points(
            good_ball_mask,
            self._min_ball_area_to_detect)

        bad_ball_coordinates = None

        # Show ball mask to see in detail the ball detection
        if False:
            cv2.imshow('good_all_mask', good_ball_mask)
            cv2.imshow('bad_ball_mask', bad_ball_mask)

        return good_ball_coordinates, bad_ball_coordinates

    def _find_balls_by_color(
            self,
            hsv_image,
            orig_image,
            low_color,
            high_color):
        """
        """
        color_mask = cv2.inRange(hsv_image, low_color, high_color)
        color_mask = cv2.erode(color_mask, None, iterations=ITERATIONS)
        color_mask = cv2.dilate(color_mask, None, iterations=ITERATIONS)
        color_image = cv2.bitwise_and(orig_image, orig_image, mask=color_mask)
        return color_image, color_mask

    def _find_center_points(
            self,
            color_mask,
            min_ball_area_to_detect,
            orig_image=None):
        """
        """
        center_points = []
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
            center_points.append([center_x, center_y])

        if len(center_points) == 0:
            center_points = np.array(center_points, dtype=np.float32)
            # center_points = np.reshape(center_points, (-1, 1, 2))
        return center_points

    def _blur_and_hsv(self, image):
        blurred_frame = cv2.GaussianBlur(image, (5, 5), 0)
        hsv_image = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        return hsv_image
