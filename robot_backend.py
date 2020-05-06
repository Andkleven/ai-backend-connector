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

from robot_frontend.robot_frontend import RobotFrontend
from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink
from unity_brain_server.unity_brain_server import UnityBrainServer
from computer_vision.image_processer import ImageProcesser


VIDEO_PORT = 5200
# CAPTURE_WIDTH = 1080
# CAPTURE_HEIGHT = 1080
ROBOT_ARUCO_CODE = 2
CALIBRATION_PARAMS_FILE = 'computer_vision/unity_camera_calibration/calib-params.json'


def decode_image(image):
    image = np.frombuffer(image, dtype=np.uint8)
    return cv2.imdecode(image, flags=1)


def main(_):
    '''
    Connect to IP cam and print results
    '''
    image_source = GStreamerVideoSink(port=VIDEO_PORT)
    image_processer = ImageProcesser(
        ROBOT_ARUCO_CODE,
        CALIBRATION_PARAMS_FILE)
    brain_server = UnityBrainServer(
        host_ip="localhost",
        port="50052")
    robot_frontend = RobotFrontend(
        robot_ip="192.168.10.64",
        port=50053)

    try:
        while True:
            if not image_source.frame_available():
                continue
            image = image_source.frame()
            lower_obs, upper_obs = image_processer.image_to_observations(image)
            if len(lower_obs) is 0 or len(upper_obs) is 0:
                print('No observations', end='\r')
                status = robot_frontend.make_action(0)
                continue
            action = brain_server.get_action(lower_obs, upper_obs)
            status = robot_frontend.make_action(action)
            print(f' Working, status: {status}', end='\r')

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        status = robot_frontend.make_action(0)
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
