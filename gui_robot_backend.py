from concurrent import futures

from absl import app
from absl import logging
from absl import flags
import time
import grpc
import cv2
import numpy as np
from multiprocessing import Process


from utils.constants import SIMU, TEST, PROD
from utils.utils import parse_options
from unity_simulation.unity_simulation import UnitySimulation
from robot_frontend.robot_frontend import RobotFrontend
from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink
from unity_brain_server.unity_brain_server import UnityBrainServer
from computer_vision.image_processer import ImageProcesser


flags.DEFINE_string(
    "params_file",
    "params.yaml",
    "Specify the path to params.yaml file",
    short_name="p")

flags.DEFINE_string(
    "mode",
    "prod",
    "Specify operation mode. 'simu', 'test', 'prod'",
    short_name="m")

FLAGS = flags.FLAGS


def _get_image_source_and_frontend(mode, params):
    image_source, frontend = None, None
    if mode == PROD or mode == TEST:
        image_source = GStreamerVideoSink(port=params["camera"]["port"])
        if mode == PROD:
            frontend = RobotFrontend(params)
    elif mode == SIMU:
        simulation = UnitySimulation(params)
        frontend, image_source = simulation, simulation
    return image_source, frontend


def main(_):
    '''
    Connect to IP cam and print results
    '''
    mode = FLAGS.mode
    params_file = FLAGS.params_file
    params = parse_options(params_file)

    image_source, frontend = _get_image_source_and_frontend(mode, params)
    image_processer = ImageProcesser(params)

    if mode == PROD or mode == SIMU:
        brain_server = UnityBrainServer(params)

    try:
        while True:
            start = time.time()

            # 1) Get image
            if not image_source.frame_available():
                continue
            image = image_source.frame()
            debug_image = image.copy()
            image_cap_time = time.time()
            image_cap_dur = image_cap_time - start

            # 2) Get observations from image
            lower_obs, upper_obs = image_processer.image_to_observations(
                image=image,
                debug_image=debug_image)
            observation_time = time.time()
            observation_dur = observation_time - image_cap_time

            if (lower_obs is not None and len(lower_obs) is 0) \
               or (upper_obs is not None and len(upper_obs) is 0):
                print('No observations', end='\r')
                if mode == PROD or mode == SIMU:
                    status = frontend.make_action(0)
                continue
            if mode == PROD or mode == SIMU:
                # 3) Get action from brain
                action = brain_server.get_action(lower_obs, upper_obs)
                brain_server_time = time.time()
                brain_server_dur = brain_server_time - observation_time

                # 4) Send the action to frontend
                status = frontend.make_action(action)
                frontend_time = time.time()
                frontend_dur = frontend_time - brain_server_time
                total_time = frontend_time - start
                fps = int(1 / total_time)
                print(
                    f'FPS: {fps:02} |'
                    f'total time: {total_time:05.3f} |'
                    f'image cap dur: {image_cap_dur:05.3f} |'
                    f'observation dur: {observation_dur:05.3f} |'
                    f'brain server dur: {brain_server_dur:05.3f} |'
                    f'frontend dur: {frontend_dur:05.3f}', end='\r')

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        if mode == PROD:
            status = frontend.make_action(0)
        print("Exiting")


if __name__ == "__main__":
    app.run(main)
