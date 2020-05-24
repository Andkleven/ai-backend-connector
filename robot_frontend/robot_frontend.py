import grpc

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


class RobotFrontend:
    def __init__(self, params):
        self._robot_ip = params["robot"]["ip"]
        self._robot_port = params["robot"]["port"]
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._robot_ip, self._robot_port))
        self._stub = rsc_pb2_grpc.RobotFrontendStub(self._channel)

        self._robot_speed = params["robot"]["robot_speed"]
        self._turn_speed = params["robot"]["turn_speed"]
        self._move_turn_speed = params["robot"]["move_turn_speed"]

    def _get_motor_speeds(self, action):
        l_motor = None
        r_motor = None

        # Forward
        if action == 1:
            # negative speed is forward in bot's orientation
            l_motor = -self._robot_speed
            r_motor = -self._robot_speed
        # Backward
        elif action == 2:
            l_motor = self._robot_speed
            r_motor = self._robot_speed
        # Turn Clockwise
        elif action == 3:
            l_motor = -self._turn_speed
            r_motor = self._turn_speed
        # Turn Anti Clockwise
        elif action == 4:
            l_motor = self._turn_speed
            r_motor = -self._turn_speed
        # Turn right and go forward
        elif action == 5:
            l_motor = -self._move_turn_speed
            r_motor = -self._robot_speed
        # Turn left and go forward
        elif action == 6:
            l_motor = -self._robot_speed
            r_motor = -self._move_turn_speed
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
        l_motor_speed, r_motor_speed = self._get_motor_speeds(action)
        motor_values = rsc_pb2.RobotActionRequest(
            leftMotorAction=l_motor_speed,
            rightMotorAction=r_motor_speed)
        response = self._stub.MakeAction(motor_values)
        return response.status
