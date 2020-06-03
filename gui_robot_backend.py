from concurrent import futures

from absl import app
from absl import logging
from absl import flags

from utils.constants import SIMU, TEST, PROD
from utils.utils import parse_options
from computer_vision.visualization_utils import show_visualizations
from game.game import Game


flags.DEFINE_string(
    "mode",
    "prod",
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
            show_visualizations(frame)

            data = game.get_game_data()
            if data is None:
                data = {"status": "No data"}
            else:
                print(
                    f'FPS: {data["fps"]:02} |'
                    f'total time: {data["totalDur"]:05.3f} |'
                    f'image cap dur: {data["imageCapDur"]:05.3f} |'
                    f'observation dur: {data["obsDur"]:05.3f} |'
                    f'brain server dur: {data["brainDur"]:05.3f} |'
                    f'frontend dur: {data["frontendDur"]:05.3f}', end='\r')
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        game.stop_game()
        print("Exiting")


if __name__ == "__main__":
    app.run(main)
