import cv2
from cv2 import aruco
import numpy as np
import json

from computer_vision.image_utils import blur_and_hsv
from computer_vision.aruco_marker_detection import get_aruco_marker_pos_and_rot
from computer_vision.ball_detection import (
    find_balls_by_color,
    find_center_points)
from computer_vision.geometry_utils import create_sectors, create_fat_rays
from computer_vision.game_object import GameObject
from computer_vision.observation_utils import (
    get_observations_for_objects,
    print_observations)


# Blue, green, red
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)


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

        # self._angles = [-90, -60, -30, 0, 30, 60, 90]
        self._angles = [0, -30, 30, -60, 60, -90, 90]
        self._ray_length = 500

        self._goal_objects = [GameObject(
            [[0, 900], [1080, 900], [1080, 1080], [0, 1080]],
            GREEN, name="goal")]
        self._wall_objects = [
            GameObject([[0, 0], [0, 1080]], BLUE, name="wall"),
            GameObject([[0, 1080], [1080, 1080]], BLUE, name="wall"),
            GameObject([[1080, 1080], [1080, 0]], BLUE, name="wall"),
            GameObject([[1080, 0], [0, 0]], BLUE, name="wall")
        ]

    def image_to_observations(self, image):
        robot_pos, robot_rot = self._get_robot_coordinates(
            image=image,
            aruco_code=self._aruco_code,
            debug=False)  # self._debug)

        if robot_pos is None or len(robot_pos) == 0:
            print("Could not locate robot's Aruco marker")
            return [], []

        ball_pos = self._get_ball_coordinates(
            image=image,
            debug=False)  # self._debug)

        lower_obs, upper_obs = self._get_observations(
            robot_pos=robot_pos,
            robot_rot=robot_rot,
            ball_pos=ball_pos,
            debug=self._debug,
            image=image)

        # print(
        #     f'Robot Pos: {["{0:0.0f}".format(i) for i in robot_pos]} '
        #     f'Robot Rot: {["{0:0.0f}".format(i) for i in robot_rot]} '
        #     f'Ball Pos: {["{0:0.0f}".format(i) for i in ball_pos[0]]}')
        # end='\r')
        # print(
        #     f'lower_obs: {["{0:0.0f}".format(i) for i in lower_obs]}\n'
        #     f'upper_obs: {["{0:0.0f}".format(i) for i in upper_obs]}')

        return lower_obs, upper_obs

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

        ball_coordinates = find_center_points(ball_mask)

        if debug:
            cv2.imshow('ball_mask', ball_mask)
            cv2.waitKey(1)

            for coordinate in ball_coordinates:
                cv2.circle(image, (
                    coordinate[0],
                    coordinate[1]), 5, (0, 0, 255), -1)
            cv2.imshow('Ball Coordinates', image)
        return ball_coordinates

    def _visualize_scene(
            self,
            image,
            robot,
            ball,
            sectors,
            goals,
            walls,
            lower_obs,
            upper_obs):
        robot.draw_object_on_image(image)
        ball.draw_object_on_image(image)

        for sector in sectors:
            sector.draw_object_on_image(image)

        for goal in goals:
            goal.draw_object_on_image(image)

        for wall in walls:
            wall.draw_object_on_image(image)

        lower_obs_str = print_observations(
            lower_obs,
            self._angles,
            return_string=True,
            include_raw=False)
        y0, dy = 50, 25
        for i, line in enumerate(lower_obs_str.split('\n')):
            y = y0 + i*dy
            cv2.putText(image, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 3)
        upper_obs_str = print_observations(
            upper_obs,
            self._angles,
            return_string=True,
            include_raw=False)

        y0, dy = 500, 25
        for i, line in enumerate(upper_obs_str.split('\n')):
            y = y0 + i*dy
            cv2.putText(image, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 3)

        cv2.imshow('Unity screen capture', image)
        cv2.waitKey(1)

    def _get_observations(
            self,
            robot_pos,
            robot_rot,
            ball_pos,
            debug=False,
            image=None):
        '''
        Create observation array for Brain server
        '''
        # sectors = create_sectors(
        #     robot_pos,
        #     robot_rot,
        #     self._angles[:],
        #     self._ray_length)

        sectors = create_fat_rays(
            robot_pos,
            robot_rot,
            self._angles[:],
            self._ray_length,
            20)

        robot_point = GameObject([robot_pos], RED)
        ball_object = GameObject(ball_pos, BLACK, buffer_distance=50)

        objects_for_detection = [
            [ball_object],
            self._goal_objects,
            self._wall_objects]
        lower_obs = get_observations_for_objects(
            robot_point,
            sectors,
            self._ray_length,
            objects_for_detection)

        objects_for_detection = [
            [],
            self._goal_objects,
            self._wall_objects]
        upper_obs = get_observations_for_objects(
            robot_point,
            sectors,
            self._ray_length,
            objects_for_detection)

        self._visualize_scene(
            image,
            robot_point,
            ball_object,
            sectors,
            self._goal_objects,
            self._wall_objects,
            lower_obs,
            upper_obs)

        return lower_obs, upper_obs
