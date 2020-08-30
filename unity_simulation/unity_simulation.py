from concurrent import futures

import time
import random
import grpc
import cv2
import numpy as np
from multiprocessing import Process, Value

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc

import os


class UnitySimulation(rsc_pb2_grpc.SimulationServerServicer):
    def __init__(self, params):
        self._params = params
        self._host_ip = params["simulation"]["ip"]
        self._port = params["simulation"]["port"]
        self._capture_width = params["simulation"]["capture_width"]
        self._capture_height = params["simulation"]["capture_height"]
        self._jpeg_quality = params["simulation"]["jpeg_quality"]
        if params["simulation"]["image_type"] == "JPG":
            self._image_type = rsc_pb2.JPG
        elif params["simulation"]["image_type"] == "PNG":
            self._image_type = rsc_pb2.PNG
        else:
            raise Exception(
                '\n===\nUnidentified capture image tupe: '
                f'{params["simulation"]["image_type"]}\n===\n')

        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._host_ip, self._port))
        self._stub = rsc_pb2_grpc.SimulationServerStub(self._channel)

        self._available = Value('i', 1)

    @property
    def available(self):
        return self._available.value == 1

    def _decode_image(self, image):
        image = np.frombuffer(image, dtype=np.uint8)
        return cv2.imdecode(image, flags=1)

    def frame_available(self):
        return True

    def stop(self):
        self._available.value = 0

    def frame(self):
        try:
            request = rsc_pb2.SimulationScreenCaptureRequest(
                    widht=self._capture_width,
                    height=self._capture_height,
                    imageType=self._image_type,
                    jpgQuality=self._jpeg_quality)

            response = self._stub.GetScreenCapture(request)
            return self._decode_image(response.image)

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self._available.value = 0
                print("\n====\nUnitySimulation cannot be reached!\n====\n")
                raise Exception("Cannot connect to UnitySimulation")
        except Exception as e:
            raise e

    def make_action(self, action):
        try:
            action_req = rsc_pb2.SimulationActionRequest(action=action)
            action_res = self._stub.MakeAction(action_req)
            return action_res.status

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self._available.value = 0
                print("\n====\nUnitySimulation cannot be reached!\n====\n")
                raise Exception("Cannot connect to UnitySimulation")
        except Exception as e:
            raise e


# For testing
# Run this with "python -m unity_simulation.unity_simulation"
# From the project's root folder
def main(_):
    '''
    Connect to IP cam and print results
    '''
    params_file = FLAGS.params_file
    params = parse_options(params_file)

    unity_sim = UnitySimulation(params)

    try:
        while True:
            frame = unity_sim.frame()
            cv2.imshow('Unity screen capture', frame)
            cv2.waitKey(1)

            random_action = random.randint(0, 6)
            response = unity_sim.make_action(random_action)
            print(f'Response: {"OK" if response == 0 else "ERROR"}', end='\r')

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting")


if __name__ == "__main__":
    from absl import app
    from absl import flags
    from utils.utils import parse_options

    flags.DEFINE_string(
        "params_file",
        "params-simu.yaml",
        "Specify the path to params.yaml file",
        short_name="p")

    FLAGS = flags.FLAGS
    app.run(main)
