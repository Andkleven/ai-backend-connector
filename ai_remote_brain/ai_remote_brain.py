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

    def get_actions(self, robot_obs_dict):
        try:
            brain_req = rsc_pb2.BrainActionRequest()
            for aruco_id in robot_obs_dict.keys():
                obs = rsc_pb2.Observations(
                    lowerObservations=robot_obs_dict[aruco_id]['lower_obs'],
                    upperObservations=robot_obs_dict[aruco_id]['upper_obs'],
                    arucoMarkerID=aruco_id)
                brain_req.observations.append(obs)
            brain_res = self._stub.GetAction(brain_req)
            return self._robot_actions_to_dict(brain_res.actions)

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self._available.value = 0
                print("\n====\nUnityBrainServer cannot be reached!\n====\n")
                raise Exception("Cannot connect to UnityBrainServer")
        except Exception as e:
            raise e

    def _robot_actions_to_dict(self, robot_actions):
        robot_actions_dict = {}
        for action in robot_actions:
            robot_actions_dict[action.arucoMarkerID] = action.action
        return robot_actions_dict


# For testing
# Run this with "python -m ai_remote_brain.ai_remote_brain"
# From the project's root folder
def main(_):
    '''
    Connect to IP cam and print results
    '''
    params_file = FLAGS.params_file
    params = parse_options(params_file)

    brain_server = UnityBrainServer(params)

    robot_observations_dict = {
        2: {
            'lower_obs': [0] * 279,
            'upper_obs': [0] * 279},
        3: {
            'lower_obs': [0] * 279,
            'upper_obs': [0] * 279}}
    try:
        while True:
            response = brain_server.get_actions(robot_observations_dict)
            print(f'Got action:{response}')

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting")


if __name__ == "__main__":
    from absl import app
    from absl import flags
    from utils.utils import parse_options

    flags.DEFINE_string(
        "params_file",
        "params.yaml",
        "Specify the path to params.yaml file",
        short_name="p")

    FLAGS = flags.FLAGS
    app.run(main)
