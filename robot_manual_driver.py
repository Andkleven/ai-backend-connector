from absl import app
from absl import flags

import time
from multiprocessing import Process, Value, Array, Manager
from pynput import keyboard
from pynput.keyboard import Key

from robot_frontend.robot_frontend import RobotFrontend
# from utils import parse_options
# from robot_game.robot_game import RobotGame
# from robot_reporter.robot_reporter_servicer import RobotReporterServicer
# from robot_reporter.RobotReporter_pb2 import STRIKER, GOALIE

# flags.DEFINE_string(
#     "params_file",
#     "params.yaml",
#     "Specify the path to params.yaml file",
#     short_name="f")

# flags.DEFINE_string(
#     "robot_ip",
#     None,
#     "Specify the ip of the robot",
#     short_name="i")

# flags.DEFINE_string(
#     "robot_port",
#     None,
#     "Specify the port of the robot",
#     short_name="p")

# FLAGS = flags.FLAGS


class KeyboardActions():
    def __init__(self):
        self._action = Value("i", 0)
        self._p = Process(target=self._start, args=(self._action,))

    def _start(self, shared_value):
        print("Starting process")
        try:
            with keyboard.Listener(
                    on_press=self._on_press,
                    on_release=self._on_release) as listener:
                listener.join()
        except Exception as error:
            print("====ERROR =====")
            print(error)
            print("====ERROR =====")

    def start(self):
        self._p.start()

    def _get_action_for_key(self, key_value):
        action = 0
        # Going forward
        if key_value == 'w':
            action = 1
        # Going down
        elif key_value == 's':
            action = 2
        # Turn sharply right
        elif key_value == 'd':
            action = 3
        # Turn sharply left
        elif key_value == 'a':
            action = 4
        # Turn right and go forward
        elif key_value == 'q':
            action = 5
        # Turn left and go forward
        elif key_value == 'e':
            action = 6

        return action

    def _on_press(self, key):
        key_value = None
        try:
            key_value = key.char
        except AttributeError:
            pass
        self._action.value = self._get_action_for_key(key_value)

    def _on_release(self, key):
        self._action.value = 0

        if key == Key.esc:
            #  Stop listener
            return False

    def get_action(self):
        return self._action.value

    def close(self):
        self._p.terminate()


# def wait_for_robot_reporting(port):
#     robot_infos = Manager().dict()
#     server = RobotReporterServicer(
#         port,
#         robot_infos)
#     server.start_server()
#     count = 1
#     while len(robot_infos.keys()) < 1:
#         print(
#             "=== Waiting for robots to report to backend: {}".format(count),
#             end="\r")
#         time.sleep(1)
#         count += 1
#     print("=== {} reported to backend".format(
#         "Striker" if STRIKER in robot_infos.keys() else "Goalie"))
#     server.close_server()
#     return robot_infos


def main(_):
    """
    Test communication between Robot and your PC.
    Connect PC to Arduino via serial port and send motor
    commands according to the keypresses
    """
    # params_file = FLAGS.params_file
    # params = parse_options(params_file)

    robot_ip = '192.168.10.38'  # FLAGS.robot_ip
    robot_port = 50053  # FLAGS.robot_port

    # robot_infos = None
    # if robot_ip and robot_port:
    #     robot_infos = {}
    #     robot_infos[STRIKER] = {
    #         "ip_address": robot_ip,
    #         "port": robot_port}
    # else:
    #     robot_infos = wait_for_robot_reporting(
    #         params["robot_reporter"]["port"])

    # try:
    #     robot_game = RobotGame(
    #         params["game_params"],
    #         None,
    #         robot_infos)
    # except Exception as error:
    #     print("ERROR")
    #     print(error)
    #     quit()

    keyboard_actions = KeyboardActions()
    keyboard_actions.start()

    robot_frontend = RobotFrontend(robot_ip, robot_port)

    try:
        while True:
            action = keyboard_actions.get_action()
            status = robot_frontend.make_action(action)robot_frontend.make_action(action)
            # if STRIKER in robot_infos.keys():
            #     command_send = \
            #         robot_game.do_action(action, STRIKER)
            # elif GOALIE in robot_infos.keys():
            #     command_send = \
            #         robot_game.do_action(action, GOALIE)
            # else:
            #     raise Exception(
            #         "Striker or Goalie not found from robot_infos")

    except KeyboardInterrupt:
        print("Closing")
    except Exception as error:
        print("ERROR")
        print(error)
    finally:
        print("Exiting")
        # Stop robot's motors
        # if STRIKER in robot_infos.keys():
        #     robot_game.do_action(action, STRIKER)
        # elif GOALIE in robot_infos.keys():
        #     robot_game.do_action(action, GOALIE)
        keyboard_actions.close()
        # robot_game.close()
        # quit()


if __name__ == '__main__':
    app.run(main)
