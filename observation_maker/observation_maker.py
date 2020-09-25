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

from observation_maker.friendly_robots_handler import FriendlyRobotsHandler
from observation_maker.enemy_robots_handler import EnemyRobotsHandler
from observation_maker.energy_cores_handler import EnergyCoresHandler
from utils.utils import print_observations
import ctypes
from multiprocessing import Lock, Array
from ruamel.yaml.comments import CommentedSeq
import os


IMAGE_CHANNELS = 4
VALID_LIST_TYPES = (CommentedSeq, list, np.ndarray)


class ObservationMaker(Framework):
    name = "ObservationMaker"
    description = "Game visualization and observation making"

    def __init__(self, params):
        self._params = params
        if 'simulation' in params:
            self._width = params['simulation']['capture_width']
            self._height = params['simulation']['capture_height']
        elif 'ai_video_streamer' in params:
            self._width = params['ai_video_streamer']['capture_width']
            self._height = params['ai_video_streamer']['capture_height']

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
        self.friendly_goal = self.world.CreateStaticBody(position=(0, 0))
        self.friendly_goal.CreateEdgeChain(
            self._coords_mod(params['arena']['friendly_goal']))
        self.friendly_goal.userData = {'type': 'friendly_goal'}
        for fixture in self.friendly_goal.fixtures:
            fixture.sensor = True

        self.enemy_goal = self.world.CreateStaticBody(position=(0, 0))
        self.enemy_goal.CreateEdgeChain(
            self._coords_mod(params['arena']['enemy_goal']))
        self.enemy_goal.userData = {'type': 'enemy_goal'}
        for fixture in self.enemy_goal.fixtures:
            fixture.sensor = True

        # Create energy cores handler
        self._ecores_handler = EnergyCoresHandler(self.world, params)

        # Create friendly robots handler
        self._friendly_robots_handler = FriendlyRobotsHandler(
            self.world,
            self.renderer,
            params)

        # Create enemy robots handler
        self._enemy_robots_handler = EnemyRobotsHandler(
            self.world,
            self.renderer)

        self._message = None
        self._stepper = self.run(single_step=True)

    @property
    def angles(self):
        return self._friendly_robots_handler.angles

    def get_image(self):
        image = self.GetScreenCapture()
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return image

    def _coords_mod(self, opencv_coords):
        """
        Transforms OpenCV's coordinates to box2d's coordinates.
        OpenCV's coordinate [0, 0] is in top left corner and [max_x, max_y]
        is in lower right corder. In Box2D the [0, 0] is in the middle,
        [max_x / 2, max_y / 2] is in top right corner

        opencv_coords : list [[x1, y1], [x2, y2], [x3, y3], ... ]
            List of coordinate pairs in list

        return : list [[x1, y1], [x2, y2], [x3, y3], ... ]
            List of coordinate pairs in list
        """
        def mod(opencv_coords):
            # If list in the list
            if isinstance(opencv_coords[0], VALID_LIST_TYPES):
                return [[coords[0] - self._width / 2,
                        -coords[1] + self._height / 2]
                        for coords in opencv_coords]
            # If scalars in the list
            else:
                return [opencv_coords[0] - self._width / 2,
                        -opencv_coords[1] + self._height / 2]

        if not opencv_coords:
            return opencv_coords
        elif isinstance(opencv_coords, dict):
            for key in opencv_coords.keys():
                opencv_coords[key]['position'] = \
                    mod(opencv_coords[key]['position'])
            return opencv_coords
        elif isinstance(opencv_coords, VALID_LIST_TYPES):
            return mod(opencv_coords)
        else:
            raise Exception('\n=====\nUnsupported data type. Expected a dict or '
                            f'a list but got: {type(opencv_coords)}\n=====\n'
                            f'{opencv_coords}\n=====\n')

    def update_image(self, image, message):
        self.SetBackground(image)
        self._message = message
        self._ecores_handler.set_transforms([], [])
        self._friendly_robots_handler.set_transforms({})
        self._enemy_robots_handler.set_transforms({})
        self._make_step()

    def get_observations(
            self,
            image,
            friendly_trans_dict,
            enemy_trans_dict,
            pos_ecore_transforms,
            neg_ecore_transforms):
        """
        Get observations made by the simulation
        """
        # Set background image to the simulation. Only needed
        # for visual purposes. Not needed for getting observations.
        self.SetBackground(image)

        self._ecores_handler.set_transforms(
            self._coords_mod(pos_ecore_transforms),
            self._coords_mod(neg_ecore_transforms))
        self._enemy_robots_handler.set_transforms(
            self._coords_mod(enemy_trans_dict))
        self._friendly_robots_handler.set_transforms(
            self._coords_mod(friendly_trans_dict))

        # Run one step of the simulation
        self._make_step()

        # Get the observations created in the simulation step
        robot_observations_dict = \
            self._friendly_robots_handler.get_observations()

        return robot_observations_dict

    def Step(self, settings):
        """
        Called by super class
        """
        self._ecores_handler.update()
        self._enemy_robots_handler.update()
        self._friendly_robots_handler.update()
        super(ObservationMaker, self).Step(settings)
        # self._overdraw_with_colors()

        if self._message is not None:
            self.DrawStringAt(540, 540, self._message)
            self._message = None
        self._print_observations_to_screen()
        self._CaptureScreen()

    def _make_step(self):
        next(self._stepper)

    # def _overdraw_with_colors(self):
    #     self.world.renderer.DrawSolidPolygon([[0, 0], [500, 0], [0, 1080]], b2Color(1, 0, 1))

    def _print_observations_to_screen(self):
        robot_obs_dict = \
            self._friendly_robots_handler.get_observations()
        if not robot_obs_dict:
            return
        neg_ecores, pos_ecores = self._ecores_handler.get_ecore_counts()
        results_str = f'Neg Ecores: {neg_ecores} | Pos Ecores: {pos_ecores}\n'
        aruco_id = next(iter(robot_obs_dict))
        results_str = \
            results_str + f'Lower observations for robot: {aruco_id}\n'
        results_str = results_str + \
            f'{"|".join(self._friendly_robots_handler.lower_tags)}\n'

        angles = [element * 180 / b2_pi
                  for element in self._friendly_robots_handler.angles]
        results_str = results_str + print_observations(
            robot_obs_dict[aruco_id]['lower_obs'],
            angles,
            return_string=True,
            include_raw=False)
        results_str_arr = results_str.split("\n")
        y_start = 230
        for line in results_str_arr:
            self.DrawStringAt(30, y_start, line, b2Color(0, 0, 0))
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
