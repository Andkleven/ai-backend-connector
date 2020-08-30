import os
import numpy as np
import pygame
from observation_maker.box2d_framework.framework import Framework
from Box2D import (
    b2RayCastCallback,
    b2Vec2,
    b2_pi,
    b2Color,
    b2CircleShape,
    b2PolygonShape)
import cv2
import time

from observation_maker.robot_handler import RobotHandler
from observation_maker.ball_handler import BallHandler
from utils.utils import print_observations
import ctypes
from multiprocessing import Lock, Array

import os


IMAGE_CHANNELS = 4


class ObservationMaker(Framework):
    name = "ObservationMaker"
    description = "Game visualization and observation making"

    def __init__(self, params):
        self._params = params
        self._width = params['simulation']['capture_width']
        self._height = params['simulation']['capture_height']

        # Pygame runs in another process than the scripts calling
        # for image data so we need to setup a multiprocessing-array
        # and link two numpy arrays to the multiprocessing-array. One
        # the created numpy arrays is called from the other process and
        # the other one is called from the other process.
        self._screen_capture_lock = Lock()
        self._image_size = \
            [self._width, self._height, IMAGE_CHANNELS]
        arr_size = int(np.prod(self._image_size))

        # The multiprocessing array used to share data between
        # two processes
        self._shared_arr = Array(ctypes.c_uint8, arr_size)

        # Numpy array used for calls outside pygame process
        self._image_non_pygame_process = np.frombuffer(
            self._shared_arr.get_obj(),
            dtype=np.uint8)
        self._image_non_pygame_process = \
            np.reshape(self._image_non_pygame_process, self._image_size)

        # Numpy array used for calls inside pygame process
        self._image_pygame_process = np.frombuffer(
            self._shared_arr.get_obj(),
            dtype=np.uint8)
        self._image_pygame_process = \
            np.reshape(self._image_pygame_process, self._image_size)

        super(ObservationMaker, self).__init__(
            width=self._width,
            height=self._height)

        self.world.gravity = (0, 0)

        # Create walls
        walls = self.world.CreateStaticBody(position=(0, 0))
        for edge_chain in params['arena']['walls']:
            walls.CreateEdgeChain(self._coords_mod(edge_chain))
            walls.userData = {'type': 'wall'}
            for fixture in walls.fixtures:
                fixture.sensor = True

        # Create goals
        self.good_goal = self.world.CreateStaticBody(position=(0, 0))
        self.good_goal.CreateEdgeChain(
            self._coords_mod(params['arena']['good_goal']))
        self.good_goal.userData = {'type': 'good_goal'}
        for fixture in self.good_goal.fixtures:
            fixture.sensor = True

        # Create ball handler
        self._ball_handler = BallHandler(self.world)

        # Create tank handler
        self._robot_handler = RobotHandler(
            self.world,
            self.renderer,
            params)

        self._message = None
        self._stepper = self.run(single_step=True)

    @property
    def angles(self):
        return self._robot_handler.angles

    def get_image(self):
        image = self.GetScreenCapture()
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return image

    def _coords_mod(self, opencv_coords_list):
        """
        Transforms OpenCV's coordinates to box2d's coordinates.
        OpenCV's coordinate [0, 0] is in top left corner and [max_x, max_y]
        is in lower right corder. In Box2D the [0, 0] is in the middle,
        [max_x / 2, max_y / 2] is in top right corner

        opencv_coords_list : list [[x1, y1], [x2, y2], [x3, y3], ... ]
            List of coordinate pairs in list

        return : list [[x1, y1], [x2, y2], [x3, y3], ... ]
            List of coordinate pairs in list
        """
        def mod(opencv_coords_list):
            return [
                    [coords[0] - self._width / 2,
                     -coords[1] + self._height / 2]
                    for coords in opencv_coords_list]

        if opencv_coords_list is None:
            return None
        if type(opencv_coords_list) is dict:
            opencv_coords_list['position'] = \
                mod([opencv_coords_list['position']])[0]
            return opencv_coords_list
        return mod(opencv_coords_list)

    def update_image(self, image, message):
        self.SetBackground(image)
        self._message = message
        self._ball_handler.set_transforms([], [])
        self._robot_handler.set_transforms([], [])
        self._make_step()

    def get_observations(
            self,
            image,
            robot1_transform,
            robot2_transform,
            good_ball_transforms,
            bad_ball_transforms,
            enemy_transforms):
        """
        Get observations made by the simulation
        """
        # Set background image to the simulation. Only needed
        # for visual purposes. Not needed for getting observations.
        self.SetBackground(image)

        # Setting transforms of balls and robot
        self._ball_handler.set_transforms(
            self._coords_mod(good_ball_transforms),
            self._coords_mod(bad_ball_transforms))
        # self._enemy_handler.update(enemy_transforms)
        self._robot_handler.set_transforms(
            self._coords_mod(robot1_transform),
            self._coords_mod(robot2_transform))

        # Run one step of the simulation
        self._make_step()

        # Get the observations created in the simulation step
        low_obs_r1, up_obs_r1 = self._robot_handler.get_observations()

        low_obs_r2 = None
        up_obs_r2 = None
        return low_obs_r1, up_obs_r1, low_obs_r2, up_obs_r2

    def Step(self, settings):
        super(ObservationMaker, self).Step(settings)
        if self._message is not None:
            self.DrawStringAt(540, 540, self._message)

        self._ball_handler.update()
        self._robot_handler.update()

        self._print_observations_to_screen()

        self._CaptureScreen()

    def _make_step(self):
        next(self._stepper)

    def _print_observations_to_screen(self):
        low_obs_r1, _ = self._robot_handler.get_observations()
        angles = [element * 180 / b2_pi
                  for element in self._robot_handler.angles]
        results_str = print_observations(
            low_obs_r1,
            angles,
            return_string=True,
            include_raw=False)
        results_str_arr = results_str.split("\n")
        y_start = 230
        for line in results_str_arr:
            # self.Print(line)
            self.DrawStringAt(50, y_start, line)
            y_start += 18

    def SetBackground(self, image):
        """
        Set the background image of pygame screen. The image needs to be
        transposed to show correctly in the game.
        """
        image = np.transpose(image, (1, 0, 2))
        self._background = pygame.surfarray.make_surface(image)

    def _CaptureScreen(self):
        """
        Save a screen capture to an multiprocess capable numpy array which
        can be read from other processes.
        """
        temp_image = np.frombuffer(self.screen.get_buffer(), dtype=np.uint8)
        temp_image = np.reshape(
            temp_image,
            (self.screen_width, self.screen_height, 4))
        with self._screen_capture_lock:
            # TODO: Is the following ".copy()" needed?
            self._image_pygame_process[:] = temp_image.copy()

    def GetScreenCapture(self):
        """
        Get an image capture of the observation simulation. The image is
        multiprocess capable numpy array.
        """
        with self._screen_capture_lock:
            return self._image_non_pygame_process
