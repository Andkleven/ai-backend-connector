from concurrent import futures

import time
import random
import grpc
from multiprocessing import Value

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


class UnityBrainServer(rsc_pb2_grpc.BrainServerServicer):
    def __init__(self, params):
        self._host_ip = params["brain_server"]["ip"]
        self._port = params["brain_server"]["port"]
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._host_ip, self._port))
        self._stub = rsc_pb2_grpc.BrainServerStub(self._channel)

        self._available = Value('i', 1)

    @property
    def available(self):
        return self._available.value == 1

    def get_action(self, lower_observations, upper_observations):
        try:
            brain_req = rsc_pb2.BrainActionRequest(
                lowerObservations=lower_observations,
                upperObservations=upper_observations)
            brain_res = self._stub.GetAction(brain_req)
            return brain_res.action

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self._available.value = 0
                print("\n====\nUnityBrainServer cannot be reached!\n====\n")
                raise Exception("Cannot connect to UnityBrainServer")
        except Exception as e:
            raise e


# For testing
# Run this with "python -m unity_brain_server.unity_brain_server"
# From the project's root folder
def main(_):
    '''
    Connect to IP cam and print results
    '''
    brain_server = UnityBrainServer(
        host_ip="localhost",
        port="50052")

    try:
        while True:
            lower_obs = [0] * 35
            upper_obs = [0] * 35
            response = brain_server.get_action(lower_obs, upper_obs)
            print(f'Got action:{response}')

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
