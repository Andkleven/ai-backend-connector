from concurrent import futures

import time
from multiprocessing import Lock, Process, Value
from ctypes import c_bool
import numpy as np
from utils.utils import parse_options
from utils.constants import SIMU, TEST, PROD
from unity_simulation.unity_simulation import UnitySimulation
from unity_brain_server.unity_brain_server import UnityBrainServer
from robot_frontend.robot_frontend import RobotFrontend
from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink
from computer_vision.image_processer import ImageProcesser


IMAGE_CHANNELS = 3


class Game:
    def __init__(self, mode):
        self._mode = mode
        print(f'Starting game in {self._mode}-mode')

        self._game_data_mutex = Lock()

        if self._mode == PROD or self._mode == TEST:
            self._params = parse_options("params-prod.yaml")
        else:
            self._params = parse_options("params-simu.yaml")

        self._step_time = 1 / self._params['decision_rate']
        self._image_source, self._frontend = \
            self._get_image_source_and_frontend(self._mode, self._params)

        self._image_processer = ImageProcesser(self._params)
        if self._mode == PROD or self._mode == SIMU:
            self._brain_server = UnityBrainServer(self._params)

        self._step_start_time = time.time()
        self._last_log_time = time.time()
        self._reset_game_data()
        image_size = (
            self._params['simulation']['capture_width'],
            self._params['simulation']['capture_height'],
            IMAGE_CHANNELS)
        self._image = np.zeros(image_size, dtype=np.uint8)

        self._play_game = Value(c_bool, True)
        self._game_process = Process(
            target=self._start_game,
            args=(self._play_game,))
        self._game_process.start()

    def _get_image_source_and_frontend(self, mode, params):
        if mode == PROD or mode == TEST:
            image_source = GStreamerVideoSink(
                multicast_ip=params["camera"]["multicast_ip"],
                port=params["camera"]["port"])
            if mode == PROD:
                frontend = RobotFrontend(params)
            else:
                frontend = None
        elif mode == SIMU:
            simulation = UnitySimulation(params)
            frontend, image_source = simulation, simulation
        return image_source, frontend

    def get_game_data(self):
        if self._play_game.value is False:
            raise Exception("Game stopped")

        with self._game_data_mutex:
            return self._game_data.copy()

    def get_game_image_capture(self):
        """
        Get image capture from the game visualization

        return : numpy.array(float) or None
        """
        if self._play_game.value is False:
            raise Exception("Game stopped")

        image = self._image_processer.get_image()
        return image

    def _write_game_data(self, field_name, data):
        """
        Write data to given field in _game_data-object
        """
        with self._game_data_mutex:
            self._game_data[field_name] = data

    def _reset_game_data(self):
        """
        Reset the _game_data-object to initial state
        """
        with self._game_data_mutex:
            self._game_data = {
                "fps": -1,
                "totalDuration": -1,
                "imageCaptureDuration": -1,
                "obsCreationDuration": -1,
                "brainDuration": -1,
                "frontendDuration": -1,
                "status": "Initialized",
                "lowerObs": [],
                "upperObs": [],
                "angles": []
            }

    def _stop_robot(self):
        """
        Stop robot by sending frontend the stop command
        if frontend is used

        return : Doesn't return anything
        """
        if self._mode == PROD or self._mode == SIMU:
            # Stop the robot from moving
            if self._frontend.available is True:
                status = self._frontend.make_action(0)

    def _log_time(self, log_name=None, log_start=False, log_end=False):
        """
        Log time a step has taken to _game_data-object with given field name

        log_name : str
        log_start : boolean
        log_end : boolean
        return : Doesn't return anything
        """
        if log_name is not None:
            self._write_game_data(log_name, time.time() - self._last_log_time)
            self._last_log_time = time.time()
        if log_start:
            self._step_start_time = time.time()
        elif log_end:
            total_time = time.time() - self._step_start_time
            self._write_game_data(
                'totalDuration', total_time)
            self._write_game_data('fps', int(1 / total_time))

    def _get_image_from_image_source(self):
        """
        Get image from image source and set it to _image
        """
        if not self._image_source.frame_available():
            return
        self._image = self._image_source.frame()

    def _start_game(self, play_game):
        try:
            while play_game.value is True:
                self._reset_game_data()
                self._log_time(log_start=True)

                # 1) Get image
                self._get_image_from_image_source()
                self._log_time(log_name='imageCaptureDuration')

                # 2) Get observations from image
                # The _ and __ variables are placeholders for the second
                # robot and it's observations
                lower_obs, upper_obs, _, __ = \
                    self._image_processer.image_to_observations(
                        image=self._image)
                self._log_time(log_name='obsCreationDuration')

                # 2.1) We didn't get observations
                if lower_obs is None or upper_obs is None:
                    self._write_game_data('status', 'No observations')
                    self._stop_robot()
                    self._log_time(log_end=True)
                    with self._game_data_mutex:
                        wait_time = \
                            self._step_time - self._game_data['totalDuration']
                        if wait_time > 0:
                            time.sleep(wait_time)
                    continue
                # 2.2) We got observations
                else:
                    self._write_game_data('lowerObs', lower_obs)
                    self._write_game_data('upperObs', upper_obs)
                    self._write_game_data(
                        'angles', self._image_processer.angles)

                if self._mode == PROD or self._mode == SIMU:
                    # 3a) Get action from brain with the observations
                    action = self._brain_server.get_action(
                        lower_obs, upper_obs)
                    self._log_time(log_name='brainDuration')

                    # 4) Send the action to frontend
                    status = self._frontend.make_action(action)
                    self._write_game_data('status', 'Playing game')
                    self._log_time(log_name='frontendDuration', log_end=True)
                else:
                    # 3b) Just log, don't connect to brain server nor frontend
                    self._write_game_data('status', 'Running in test mode')
                    self._log_time(log_end=True)

                with self._game_data_mutex:
                    wait_time = \
                        self._step_time - self._game_data['totalDuration']
                if wait_time > 0:
                    time.sleep(wait_time)

            self._stop_robot()
            print("Game stopped")

        except KeyboardInterrupt:
            print("Keyboard Interrupt")

        except Exception as error:
            print('Got unexpected exception in "_start_game" in Game-class'
                  f'Message: {error}')

        finally:
            self.stop_game()
            print("Game stopped")

    def stop_game(self):
        print("Stopping game")
        self._play_game.value = False

        self._stop_robot()
        if self._image_source is not None:
            self._image_source.stop()
