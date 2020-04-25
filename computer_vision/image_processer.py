import cv2
from cv2 import aruco
import numpy as np
import json

from computer_vision.image_utils import blur_and_hsv
from computer_vision.aruco_marker_detection import get_aruco_marker_pos_and_rot
from computer_vision.ball_detection import (
    find_balls_by_color,
    find_center_points)


class ImageProcesser():
    def __init__(self, aruco_code, calibration_params_file, debug):
        self._aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self._debug = debug
        self._aruco_code = aruco_code
        self._parameters = aruco.DetectorParameters_create()
        self._camera_calib_params = None
        with open(calibration_params_file) as json_file:
            self._camera_calib_params = json.load(json_file)
        self._size_of_marker = 0.15

        # Value ranges for HSV-values in OpenCV
        # H: 0-179, S: 0-255, V: 0-255
        self._low_ball_color = np.array([100, 100, 100], dtype=np.float32)
        self._high_ball_color = np.array([173, 255, 255], dtype=np.float32)

    def image_to_observations(self, image):
        robot_pos, robot_rot = self._get_robot_coordinates(
            image=image,
            aruco_code=self._aruco_code,
            debug=self._debug)

        ball_pos = self._get_ball_coordinates(
            image=image,
            debug=self._debug)

        # lower_obs, upper_obs = self._get_observations(
        #     image=image,
        #     robot_pos=robot_pos,
        #     robot_rot=robot_rot,
        #     ball_pos=ball_pos,
        #     ball_rot=ball_rot)
        # return lower_obs, upper_obs

        # print(robot_pos)
        # print(robot_rot)
        # print(ball_pos)
        print(
            f'Robot Pos: {["{0:0.0f}".format(i) for i in robot_pos]} '
            f'Robot Rot: {["{0:0.0f}".format(i) for i in robot_rot]} ',
            f'Ball Pos: {["{0:0.0f}".format(i) for i in ball_pos[0]]}',
            end='\r')
        return [], []

    def _get_robot_coordinates(
            self,
            image,
            aruco_code,
            debug=False):
        '''
        Detect aruco markers from given image and return robot coordinates
        '''
        if image is None:
            return None

        robot_pos, robot_rot = get_aruco_marker_pos_and_rot(
            image=image,
            aruco_code=self._aruco_code,
            aruco_dict=self._aruco_dict,
            parameters=self._parameters,
            camera_calib_params=self._camera_calib_params,
            size_of_marker=self._size_of_marker,
            debug=debug)

        return robot_pos, robot_rot

    def _get_ball_coordinates(self, image, debug=False):
        if image is None:
            return None

        hsv_image = blur_and_hsv(image)

        ball_image, ball_mask = find_balls_by_color(
            hsv_image,
            image,
            self._low_ball_color,
            self._high_ball_color)

        cv2.imshow('ball_mask', ball_mask)
        cv2.waitKey(1)

        ball_coordinates = find_center_points(ball_mask)

        if debug:
            for coordinate in ball_coordinates:
                cv2.circle(image, (
                    coordinate[0],
                    coordinate[1]), 5, (0, 0, 255), -1)
            cv2.imshow('Ball Coordinates', image)
        return ball_coordinates

    def _get_observations(
            self,
            image,
            robot_pos,
            robot_rot,
            ball_pos,
            ball_rot):
        '''
        Create observation array for Brain server
        '''
        pass
