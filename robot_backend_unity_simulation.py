from concurrent import futures

from absl import app
from absl import logging
from absl import flags
import time
import grpc
import cv2
import numpy as np
from multiprocessing import Process

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc

from utils.utils import parse_options
from unity_simulation.unity_simulation import UnitySimulation
from unity_brain_server.unity_brain_server import UnityBrainServer
from computer_vision.image_processer import ImageProcesser


CAPTURE_WIDTH = 1080
CAPTURE_HEIGHT = 1080
ROBOT_ARUCO_CODE = 1
CALIBRATION_PARAMS_FILE = \
    'computer_vision/unity_camera_calibration/calib-params.json'


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


def decode_image(image):
    image = np.frombuffer(image, dtype=np.uint8)
    return cv2.imdecode(image, flags=1)


def main(_):
    '''
    Connect to IP cam and print results
    '''
    mode = FLAGS.mode
    params_file = FLAGS.params_file
    params = parse_options(params_file)

    unity_sim = UnitySimulation(
        host_ip="localhost",
        port="50051")
    image_processer = ImageProcesser(
        ROBOT_ARUCO_CODE,
        CALIBRATION_PARAMS_FILE)
    brain_server = UnityBrainServer(
        host_ip="localhost",
        port="50052")

    try:
        while True:
            start = time.time()
            image = unity_sim.get_screen_capture(CAPTURE_WIDTH, CAPTURE_HEIGHT)
            image = decode_image(image)
            image_cap_time = time.time()
            image_cap_dur = image_cap_time - start
            lower_obs, upper_obs = image_processer.image_to_observations(image)
            observation_time = time.time()
            observation_dur = observation_time - image_cap_time
            if (lower_obs is not None and len(lower_obs) is 0) \
               or (upper_obs is not None and len(upper_obs) is 0):
                print(f'observation dur: {observation_dur:05.3f} |', end='\r')
                continue
            action = brain_server.get_action(lower_obs, upper_obs)
            brain_server_time = time.time()
            brain_server_dur = brain_server_time - observation_time
            status = unity_sim.make_action(action)
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
        print("Exiting")


if __name__ == "__main__":
    FLAGS = flags.FLAGS
    app.run(main)
