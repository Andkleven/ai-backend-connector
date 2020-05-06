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

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2
FONT_DEFAULT_COLOR = (0, 0, 255)

# LOW_COLOR = [100, 100, 100]  # For simulation
# HIGH_COLOR = [173, 255, 255]  # For simulation
LOW_COLOR = [160, 90, 20]  # For real life
HIGH_COLOR = [180, 255, 255]  # For real life

BALL_RADIUS = 25


class ImageProcesser():
    def __init__(self, aruco_code, calibration_params_file):
        self._aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self._aruco_code = aruco_code
        self._parameters = aruco.DetectorParameters_create()
        self._camera_calib_params = None
        with open(calibration_params_file) as json_file:
            self._camera_calib_params = json.load(json_file)
        self._size_of_marker = 0.15

        # Value ranges for HSV-values in OpenCV
        # H: 0-179, S: 0-255, V: 0-255
        self._low_ball_color = np.array(LOW_COLOR, dtype=np.float32)
        self._high_ball_color = np.array(HIGH_COLOR, dtype=np.float32)

        # Angle order comes from Unity simulation's angle order
        self._angles = [0, -30, 30, -60, 60, -90, 90]
        self._ray_length = 500

        self._goal_objects = [GameObject(
            [[0, 885], [1080, 885], [1080, 1080], [0, 1080]],
            GREEN, name="goal")]
        self._wall_objects = [
            GameObject([[25, 25], [25, 1055]], BLUE, name="wall"),
            GameObject([[25, 1055], [1055, 1055]], BLUE, name="wall"),
            GameObject([[1055, 1055], [1055, 25]], BLUE, name="wall"),
            GameObject([[1055, 25], [25, 25]], BLUE, name="wall")]

    def image_to_observations(self, image):
        self._visualize_item(image, *self._wall_objects)
        self._visualize_item(image, *self._goal_objects)

        robot_obj = self._get_robot_object(
            image=image,
            aruco_code=self._aruco_code)

        if robot_obj is None:
            warning = "Could not locate robot's Aruco marker"
            print(warning, end='')
            self._visualize_item(image, warning, text_pos=(50, 50))
            self._show_visualizations(image)
            return [], []

        ball_objs = self._get_ball_objects(image=image)
        if ball_objs is None:
            warning = "Could not locate ball"
            print(warning, end='')
            self._visualize_item(image, warning, text_pos=(50, 50))
            self._show_visualizations(image)
            return [], []

        lower_obs, upper_obs = self._get_observations(
            robot_obj=robot_obj,
            ball_objs=ball_objs,
            image=image)

        self._show_visualizations(image)

        return lower_obs, upper_obs

    def _get_robot_object(
            self,
            image,
            aruco_code):
        '''
        Detect aruco markers from given image and return robot game object
        '''
        if image is None:
            return None

        robot_pos, robot_rot = get_aruco_marker_pos_and_rot(
            image=image,
            aruco_code=self._aruco_code,
            aruco_dict=self._aruco_dict,
            parameters=self._parameters,
            camera_calib_params=self._camera_calib_params,
            size_of_marker=self._size_of_marker)

        if robot_pos is not None:
            robot_obj = GameObject([robot_pos], RED, rotation=robot_rot, name="Robot")
            self._visualize_item(image, robot_obj)
        else:
            robot_obj = None

        return robot_obj

    def _get_ball_objects(self, image):
        if image is None:
            return None

        hsv_image = blur_and_hsv(image)

        ball_image, ball_mask = find_balls_by_color(
            hsv_image,
            image,
            self._low_ball_color,
            self._high_ball_color)

        ball_coordinates = find_center_points(ball_mask)

        if ball_coordinates is not None:
            ball_objs = [
                GameObject(ball, BLACK, buffer_distance=BALL_RADIUS, name="Ball")
                for ball in ball_coordinates]
            self._visualize_item(
                image,
                *ball_objs)
        else:
            ball_objs = None

        return ball_objs

    def _visualize_item(self, image, *args, **kwargs):
        for item in args:
            if isinstance(item, GameObject):
                item.draw_object_on_image(image)
            elif isinstance(item, str):
                if 'text_color' in kwargs:
                    text_color = kwargs['text_color']
                else:
                    text_color = FONT_DEFAULT_COLOR
                for i, line in enumerate(item.split('\n')):
                    x, y0, dy = kwargs['text_pos'][0], kwargs['text_pos'][1], 25
                    y = y0 + i*dy
                    cv2.putText(
                        image, line, (x, y), FONT, FONT_SCALE,
                        text_color, FONT_THICKNESS)

    def _show_visualizations(self, image):
        cv2.imshow('Game', image)
        cv2.waitKey(1)

    def _get_observations(
            self,
            robot_obj,
            ball_objs,
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
            robot_obj,
            self._angles[:],
            self._ray_length,
            20)

        objects_for_detection = [
            ball_objs,
            self._goal_objects,
            self._wall_objects]
        lower_obs = get_observations_for_objects(
            robot_obj,
            sectors,
            self._ray_length,
            objects_for_detection)

        objects_for_detection = [
            [],
            self._goal_objects,
            self._wall_objects]
        upper_obs = get_observations_for_objects(
            robot_obj,
            sectors,
            self._ray_length,
            objects_for_detection)

        lower_obs_str = print_observations(
            lower_obs,
            self._angles,
            return_string=True,
            include_raw=False)
        lower_obs_str = \
            'Lower obs\n| Ball | Goal | Wall | Nothing | Distance |\n' \
            f'{lower_obs_str}'

        upper_obs_str = print_observations(
            upper_obs,
            self._angles,
            return_string=True,
            include_raw=False)
        upper_obs_str = \
            'Upper obs\n| Ball | Goal | Wall | Nothing | Distance |\n' \
            f'{upper_obs_str}'

        self._visualize_item(image, *sectors)
        self._visualize_item(image, lower_obs_str, text_pos=(50, 50))
        self._visualize_item(image, upper_obs_str, text_pos=(50, 350))

        return lower_obs, upper_obs
