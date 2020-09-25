import grpc
from multiprocessing import Value
import socket

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


UDP_CONNECTION = "udp"
GRPC_CONNECTION = "grpc"


class RobotFrontend:
    def __init__(self, params):
        self._robot_ip = params["ip"]
        self._robot_port = params["port"]
        self._robot_conn_type = params["connection_type"]
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._robot_ip, self._robot_port))
        self._stub = rsc_pb2_grpc.RobotFrontendStub(self._channel)

        self._robot_speed = params["robot_speed"]
        self._turn_speed = params["turn_speed"]
        self._move_turn_speed = params["move_turn_speed"]
        self._action_timeout = int(params["action_timeout"])
        self._available = Value('i', 1)

    @property
    def available(self):
        return self._available.value == 1

    def _get_motor_speeds(self, action):
        l_motor = None
        r_motor = None

        # Forward
        if action == 1:
            # negative speed is forward in bot's orientation
            l_motor = self._robot_speed
            r_motor = self._robot_speed
        # Backward
        elif action == 2:
            l_motor = -self._robot_speed
            r_motor = -self._robot_speed
        # Turn Clockwise
        elif action == 3:
            l_motor = self._turn_speed
            r_motor = -self._turn_speed
        # Turn Anti Clockwise
        elif action == 4:
            l_motor = -self._turn_speed
            r_motor = self._turn_speed
        # Turn right and go forward
        elif action == 5:
            l_motor = self._move_turn_speed
            r_motor = self._robot_speed
        # Turn left and go forward
        elif action == 6:
            l_motor = self._robot_speed
            r_motor = self._move_turn_speed
        # No action
        elif action == 0:
            l_motor = 0
            r_motor = 0
        else:
            raise Exception("Unknown action {}".format(action))
        # print("Action {}, L: {}, R: {}".format(
        #     action, int(l_motor), int(r_motor)))
        return int(l_motor), int(r_motor)

    def make_action(self, action):
        '''
        Send motor values to robot
        '''
        try:
            l_motor_speed, r_motor_speed = self._get_motor_speeds(action)
            motor_values = rsc_pb2.RobotRequest(
                reqId=1,
                act=rsc_pb2.RobotActionRequest(
                    leftMotorAction=l_motor_speed,
                    rightMotorAction=r_motor_speed,
                    actionTimeout=self._action_timeout))

            if self._robot_conn_type.lower() == GRPC_CONNECTION:
                response = self._stub.MakeAction(motor_values)
                response = response.status
            elif self._robot_conn_type.lower() == UDP_CONNECTION:
                sock = socket.socket(socket.AF_INET,  # Internet
                                     socket.SOCK_DGRAM)  # UDP
                sock.sendto(motor_values.SerializeToString(),
                            (self._robot_ip, self._robot_port))
                response = "OK"
            return response

        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.UNAVAILABLE:
                self._available.value = 0
                print("\n====\nRobotFrontend cannot be reached!\n====\n")
                raise Exception("Cannot connect to RobotFrontend")
        except Exception as error:
            raise error
