from concurrent import futures

import time
import random
import grpc
import cv2
import numpy as np
from multiprocessing import Process

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


class UnitySimulation(rsc_pb2_grpc.SimulationServerServicer):
    def __init__(self, host_ip, port):
        self._host_ip = host_ip
        self._port = port
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._host_ip, self._port))
        self._stub = rsc_pb2_grpc.SimulationServerStub(self._channel)

    def get_screen_capture(
            self,
            capture_width,
            capture_height,
            image_type=rsc_pb2.JPG,
            jpeg_quality=75):

        jpeg_quality = 75
        image_type = rsc_pb2.JPG

        request = rsc_pb2.SimulationScreenCaptureRequest(
                widht=capture_width,
                height=capture_height,
                imageType=image_type,
                jpgQuality=jpeg_quality)

        response = self._stub.GetScreenCapture(request)
        return response.image

    def make_action(self, action):
        action_req = rsc_pb2.SimulationActionRequest(action=action)
        action_res = self._stub.MakeAction(action_req)
        return action_res.status


# For testing
# Run this with "python -m unity_simulation.unity_simulation"
# From the project's root folder
def main(_):
    '''
    Connect to IP cam and print results
    '''
    unity_sim = UnitySimulation(
        host_ip="localhost",
        port="50051")

    try:
        while True:
            image = unity_sim.get_screen_capture(1080, 1080)
            jpg_as_np = np.frombuffer(image, dtype=np.uint8)
            frame = cv2.imdecode(jpg_as_np, flags=1)
            cv2.imshow('Unity screen capture', frame)
            cv2.waitKey(1)

            random_action = random.randint(0, 6)
            response = unity_sim.make_action(random_action)
            print(f'Response: {"OK" if response is 0 else "ERROR"}')

            time.sleep(0.1)
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
