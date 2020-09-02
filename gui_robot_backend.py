import os
from concurrent import futures

import time

from absl import app
from absl import logging
from absl import flags

import cv2
from utils.constants import SIMU, TEST, PROD
from utils.utils import parse_options

# https://www.pygame.org/wiki/HeadlessNoWindowsNeeded
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'true'
from game.game import Game


flags.DEFINE_string(
    "mode",
    "test",
    "Specify operation mode. 'simu', 'test', 'prod'",
    short_name="m")

FLAGS = flags.FLAGS


def main(_):
    '''
    Connect to IP cam and print results
    '''
    mode = FLAGS.mode

    game = Game(mode)
    try:
        while True:
            frame = game.get_game_image_capture()
            if frame is None:
                print("Cannot get image from source", end='\r')
                continue
            cv2.imshow('Game View', frame)
            cv2.waitKey(1)

            data = game.get_game_data()
            if data is None:
                data = {"status": "No data"}
            else:
                print(
                    f'FPS: {data["fps"]:02} |'
                    f'total time: {data["totalDuration"]:05.3f} |'
                    f'image cap dur: {data["imageCaptureDuration"]:05.3f} |'
                    f'observation dur: {data["obsCreationDuration"]:05.3f} |'
                    f'brain server dur: {data["brainDuration"]:05.3f} |'
                    f'frontend dur: {data["frontendDuration"]:05.3f}', end='\r')
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nMain: Keyboard Interrupt")
    except Exception as error:
        print(f'Got unexpected exception in "main" Message: {error}')
    finally:
        game.stop_game()
        print("Main: Exiting")


if __name__ == "__main__":
    app.run(main)
