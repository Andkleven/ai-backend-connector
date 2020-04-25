from concurrent import futures

import time
import random
import grpc

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


class UnityBrainServer(rsc_pb2_grpc.BrainServerServicer):
    def __init__(self, host_ip, port):
        self._host_ip = host_ip
        self._port = port
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._host_ip, self._port))
        self._stub = rsc_pb2_grpc.BrainServerStub(self._channel)

    def get_action(self, lower_observations, upper_observations):
        brain_req = rsc_pb2.BrainActionRequest(
            lowerObservations=lower_observations,
            upperObservations=upper_observations)
        brain_res = self._stub.GetAction(brain_req)
        return brain_res.action
