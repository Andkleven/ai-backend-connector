from absl import app
from absl import flags

import time

from ai_robot.ai_robot import RobotFrontend
from utils.utils import parse_options


flags.DEFINE_string(
    "params_file",
    "params.yaml",
    "Specify the path to params.yaml file",
    short_name="p")

flags.DEFINE_integer(
    "action",
    0,
    "Specify the action to take",
    short_name="a")

flags.DEFINE_integer(
    "duration",
    100,
    "Specify the time in milliseconds how long to take the action for",
    short_name="d")

FLAGS = flags.FLAGS


# Example use:
# python ai_robot_move_calibration.py -p=params-prod.yaml -d=200 -a=4
def main(_):
    """
    Test communication between Robot and your PC.
    Connect PC to Arduino via serial port and send motor
    commands according to the keypresses
    """
    params_file = FLAGS.params_file
    params = parse_options(params_file)
    frontend = RobotFrontend(params['ai_robots']['robots'][0])

    action = FLAGS.action
    duration = FLAGS.duration

    try:
        status = frontend.make_action(action)
        time.sleep(duration / 1000)
        status = frontend.make_action(0)
    except KeyboardInterrupt:
        print("Closing")
    except Exception as error:
        print("ERROR")
        print(error)
    finally:
        print("Exiting")
        frontend.make_action(0)


if __name__ == '__main__':
    app.run(main)
