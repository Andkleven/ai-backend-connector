import grpc

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import proto.RobotSystemCommunication_pb2_grpc as rsc_pb2_grpc


class RobotFrontend:
    def __init__(self, robot_ip, port):
        self._robot_ip = robot_ip
        self._robot_port = port
        self._channel = grpc.insecure_channel(
            '{}:{}'.format(self._robot_ip, self._robot_port))
        self._stub = rsc_pb2_grpc.RobotFrontendStub(self._channel)

        self._robot_speed = 115
        self._turn_speed = 1

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
            l_motor = -self._robot_speed * self._turn_speed
            r_motor = self._robot_speed * self._turn_speed
        # Turn Anti Clockwise
        elif action == 4:
            l_motor = self._robot_speed * self._turn_speed
            r_motor = -self._robot_speed * self._turn_speed
        elif action == 5:
            l_motor = -self._robot_speed * self._turn_speed * 0.75
            r_motor = -self._robot_speed * self._turn_speed
        elif action == 6:
            l_motor = -self._robot_speed * self._turn_speed
            r_motor = -self._robot_speed * self._turn_speed * 0.75
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
