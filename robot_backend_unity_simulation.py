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

from unity_simulation.unity_simulation import UnitySimulation
from unity_brain_server.unity_brain_server import UnityBrainServer
from computer_vision.image_processer import ImageProcesser


CAPTURE_WIDTH = 512
CAPTURE_HEIGHT = 512
ROBOT_ARUCO_CODE = 1
CALIBRATION_PARAMS_FILE = 'computer_vision/unity_camera_calibration/calib-params.json'
DEBUG = True


def decode_image(image):
    image = np.frombuffer(image, dtype=np.uint8)
    return cv2.imdecode(image, flags=1)


def main(_):
    '''
    Connect to IP cam and print results
    '''
    unity_sim = UnitySimulation(
        host_ip="localhost",
        port="50051")
    image_processer = ImageProcesser(
        ROBOT_ARUCO_CODE,
        CALIBRATION_PARAMS_FILE,
        debug=DEBUG)
    brain_server = UnityBrainServer(
        host_ip="localhost",
        port="50052")

    try:
        while True:
            image = unity_sim.get_screen_capture(CAPTURE_WIDTH, CAPTURE_HEIGHT)
            image = decode_image(image)
            lower_obs, upper_obs = image_processer.image_to_observations(image)
            if len(lower_obs) is 0 or len(upper_obs) is 0:
                print('No observations', end='\r')
                continue
            action = brain_server.get_action(lower_obs, upper_obs)
            status = unity_sim.make_action(action)
            print('Working', end='\r')

    except KeyboardInterrupt:
        print("Exiting")


if __name__ == "__main__":
    from absl import app
    from absl import flags
    # from utils import parse_options

    flags.DEFINE_string(
        "params_file",
        "params.yaml",
        "Specify the path to params.yaml file",
        short_name="p")

    FLAGS = flags.FLAGS
    app.run(main)
