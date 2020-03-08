from concurrent import futures

import time
import grpc
import cv2
import numpy as np
from multiprocessing import Process

import proto.RobotBackendCommunication_pb2 as rbc_pb2
import proto.RobotBackendCommunication_pb2_grpc as rbc_pb2_grpc


class UnitySimulationCamera(rbc_pb2_grpc.RobotBackendCommunicatorServicer):
    def __init__(self, host_ip, port):
        self._host_ip = host_ip
        self._port = port

    def _start_server(self):
        self._unity_sim_cam_server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=1))
        rbc_pb2_grpc.add_RobotBackendCommunicatorServicer_to_server(
            self, self._unity_sim_cam_server)
        self._unity_sim_cam_server.add_insecure_port(
            "[::]:{}".format(self._port))
        self._unity_sim_cam_server.start()
        print("=== UnitySimulationCamera server running at port {} ...".format(
            self._port))

        try:
            while True:
                time.sleep(60*60*60)
        except KeyboardInterrupt:
            print("UnitySimulationCamera server Stopped ...")
        finally:
            self._unity_sim_cam_server.stop(0)

    def start_server(self):
        self._process = Process(target=self._start_server)
        self._process.start()

    def close_server(self):
        print("=== Closing UnitySimulationCamera server ...")
        self._process.terminate()

    def GetAction(self, request, context):
        jpg_as_np = np.frombuffer(request.image, dtype=np.uint8)
        frame = cv2.imdecode(jpg_as_np, flags=1)

        # display processed video
        cv2.imshow('Processed Image', frame)
        cv2.waitKey(1)

        return rbc_pb2.AgentAction(action=0)


# For testing
# Run this with "python -m ip_cam_connection.ip_cam_connector"
# From the project's root folder
def main(_):
    '''
    Connect to IP cam and print results
    '''
    unity_sim_cam = UnitySimulationCamera(
        host_ip="localhost",
        port="50051")
    unity_sim_cam.start_server()

    try:
        while True:
            time.sleep(60*60*60)
    except KeyboardInterrupt:
        print("Stopping UnitySimulationCamera server ...")


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
