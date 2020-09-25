import numpy as np
import cv2
import imutils


ITERATIONS = 2


class EnergyCoreDetector():
    def __init__(self, params):
        self._min_ball_area_to_detect = \
            params["image_processing"]["min_ball_area_to_detect"]

        # Value ranges for HSV-values in OpenCV
        # H: 0-179, S: 0-255, V: 0-255
        self._pos_ecore_low_color = np.array(
            params["image_processing"]["pos_energy_core_low_color"],
            dtype=np.float32)
        self._pos_ecore_high_color = np.array(
            params["image_processing"]["pos_energy_core_high_color"],
            dtype=np.float32)

        self._neg_ecore_low_color = np.array(
            params["image_processing"]["neg_energy_core_low_color"],
            dtype=np.float32)
        self._neg_ecore_high_color = np.array(
            params["image_processing"]["neg_energy_core_high_color"],
            dtype=np.float32)

    def get_ecore_transforms(self, image):
        if image is None:
            return None, None

        hsv_image = self._blur_and_hsv(image)
        pos_ecore_coordinates = self._image_to_center_points(
            hsv_image,
            image,
            self._pos_ecore_low_color,
            self._pos_ecore_high_color)
        neg_ecore_coordinates = self._image_to_center_points(
            hsv_image,
            image,
            self._neg_ecore_low_color,
            self._neg_ecore_high_color)

        return pos_ecore_coordinates, neg_ecore_coordinates

    def _image_to_center_points(
            self,
            hsv_image,
            orig_image,
            low_color,
            high_color,
            debug_name=False):
        ecore_image, ecore_mask = self._find_ecores_by_color(
            hsv_image, orig_image, low_color, high_color)
        ecore_coordinates = self._find_center_points(
            ecore_mask, self._min_ball_area_to_detect)

        # Show ball mask to see in detail the ball detection
        if debug_name:
            cv2.imshow(debug_name, ecore_mask)
            cv2.waitKey(1)
        return ecore_coordinates

    def _find_ecores_by_color(
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
            if cv2.contourArea(contour) < min_ball_area_to_detect:
                continue

            if orig_image is not None:
                cv2.drawContours(orig_image, contour, -1, GREEN, 3)
            # compute the center of the contour
            moments = cv2.moments(contour)
            center_x = int(moments["m10"] / moments["m00"])
            center_y = int(moments["m01"] / moments["m00"])
            center_points.append([center_x, center_y])

        return center_points

    def _blur_and_hsv(self, image):
        blurred_frame = cv2.GaussianBlur(image, (5, 5), 0)
        hsv_image = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        return hsv_image
