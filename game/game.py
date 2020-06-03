from concurrent import futures
import time
from threading import Lock, Thread

from utils.utils import parse_options
from utils.constants import SIMU, TEST, PROD
from unity_simulation.unity_simulation import UnitySimulation
from unity_brain_server.unity_brain_server import UnityBrainServer
from robot_frontend.robot_frontend import RobotFrontend
from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink
from computer_vision.image_processer import ImageProcesser


class Game:
    def __init__(self, mode):
        self._mode = mode
        print(f'Starting game in {self._mode}-mode')
        self._image_mutex = Lock()
        self._game_data_mutex = Lock()

        if self._mode == PROD or self._mode == TEST:
            self._params = parse_options("params-prod.yaml")
        else:
            self._params = parse_options("params-simu.yaml")

        self._image_source, self._frontend = \
            self._get_image_source_and_frontend(
                self._mode,
                self._params)

        self._image_processer = ImageProcesser(self._params)
        if self._mode == PROD or self._mode == SIMU:
            self._brain_server = UnityBrainServer(self._params)
        else:
            self._brain_server = None

        self._game_data = None
        self._image = None
        self._debug_image = None

        self._play_game = True

        self._game_thread = Thread(target=self._start_game)
        self._game_thread.start()

    def _get_image_source_and_frontend(self, mode, params):
        image_source, frontend = None, None
        if mode == PROD or mode == TEST:
            image_source = GStreamerVideoSink(port=params["camera"]["port"])
            if mode == PROD:
                frontend = RobotFrontend(params)
        elif mode == SIMU:
            simulation = UnitySimulation(params)
            frontend, image_source = simulation, simulation
        return image_source, frontend

    def get_game_data(self):
        with self._game_data_mutex:
            return self._game_data.copy() \
                   if self._game_data is not None \
                   else None

    def get_game_image_capture(self):
        with self._image_mutex:
            if self._debug_image is not None:
                return self._debug_image.copy()
            elif self._image is not None:
                return self._image.copy()
            else:
                return None

    def _start_game(self):
        while self._play_game:
            start = time.time()

            # 1) Get image
            with self._image_mutex:
                if not self._image_source.frame_available():
                    continue
                self._image = self._image_source.frame()
                self._debug_image = self._image.copy()

                image_cap_time = time.time()
                image_cap_dur = image_cap_time - start

                # 2) Get observations from image
                lower_obs, upper_obs, angles = \
                    self._image_processer.image_to_observations(
                        image=self._image,
                        debug_image=self._debug_image)
                observation_time = time.time()
                observation_dur = observation_time - image_cap_time

            if (lower_obs is None or len(lower_obs) is 0) \
               or (upper_obs is None or len(upper_obs) is 0):
                with self._game_data_mutex:
                    self._game_data = {
                        "fps": -1,
                        "totalDur": -1,
                        "imageCapDur": image_cap_dur,
                        "obsDur": observation_dur,
                        "brainDur": -1,
                        "frontendDur": -1,
                        "noObservations": True,
                        "Status": "No observations",
                        "lowerObs": [],
                        "upperObs": [],
                        "angles": angles
                    }
                if self._mode == PROD or self._mode == SIMU:
                    status = self._frontend.make_action(0)
                continue

            if self._mode == PROD or self._mode == SIMU:
                # 3) Get action from brain
                action = self._brain_server.get_action(lower_obs, upper_obs)
                brain_server_time = time.time()
                brain_server_dur = brain_server_time - observation_time

                # 4) Send the action to frontend
                status = self._frontend.make_action(action)
                frontend_time = time.time()
                frontend_dur = frontend_time - brain_server_time
                total_time = frontend_time - start
                fps = int(1 / total_time)
                with self._game_data_mutex:
                    self._game_data = {
                        "fps": fps,
                        "totalDur": total_time,
                        "imageCapDur": image_cap_dur,
                        "obsDur": observation_dur,
                        "brainDur": brain_server_dur,
                        "frontendDur": frontend_dur,
                        "noObservations": False,
                        "Status": "Playing game",
                        "lowerObs": "",
                        "upperObs": "",
                        "angles": angles
                    }
            else:
                total_time = time.time() - start
                fps = int(1 / total_time)
                with self._game_data_mutex:
                    self._game_data = {
                        "fps": fps,
                        "totalDur": total_time,
                        "imageCapDur": image_cap_dur,
                        "obsDur": observation_dur,
                        "brainDur": -1,
                        "frontendDur": -1,
                        "noObservations": False,
                        "Status": "Running in test mode",
                        "lowerObs": lower_obs,
                        "upperObs": upper_obs,
                        "angles": angles
                    }

        if self._mode == PROD or self._mode == SIMU:
            status = self._frontend.make_action(0)
        print("Game stopped")

    def stop_game(self):
        print("Stopping game")
        self._play_game = False

        if self._mode == PROD:
            self._frontend.make_action(0)

        if self._image_source is not None:
            self._image_source.stop()
