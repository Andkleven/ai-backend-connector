from absl import app
from absl import flags

import time
from multiprocessing import Process, Value, Array, Manager
from pynput import keyboard
from pynput.keyboard import Key

from robot_frontend.robot_frontend import RobotFrontend
from utils.utils import parse_options


flags.DEFINE_string(
    "params_file",
    "params.yaml",
    "Specify the path to params.yaml file",
    short_name="p")

FLAGS = flags.FLAGS


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


def main(_):
    """
    Test communication between Robot and your PC.
    Connect PC to Arduino via serial port and send motor
    commands according to the keypresses
    """
    params_file = FLAGS.params_file
    params = parse_options(params_file)

    frontend = RobotFrontend(params)

    keyboard_actions = KeyboardActions()
    keyboard_actions.start()

    try:
        while True:
            action = keyboard_actions.get_action()
            status = frontend.make_action(action)

    except KeyboardInterrupt:
        print("Closing")
    except Exception as error:
        print("ERROR")
        print(error)
    finally:
        print("Exiting")
        keyboard_actions.close()
        frontend.make_action(0)


if __name__ == '__main__':
    app.run(main)
