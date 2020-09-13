#!/usr/bin/env python3
from __future__ import print_function
import colorama
import os
from concurrent import futures

import time

from absl import app
from absl import logging
from absl import flags

from multiprocessing import Value, Array, Manager
from ctypes import c_bool, c_uint8
import numpy as np

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


def cursor_up(lines):
    return '\x1b[{0}A'.format(lines)


def cursor_down(lines):
    return '\x1b[{0}B'.format(lines)


def setup_variables(mode):
    if mode == PROD or mode == TEST:
        params = parse_options("params-prod.yaml")
    else:
        params = parse_options("params-simu.yaml")

    if 'simulation' in params:
        width = params["simulation"]["capture_width"]
        height = params["simulation"]["capture_height"]
    elif 'ai_video_streamer' in params:
        width = params["ai_video_streamer"]["capture_width"]
        height = params["ai_video_streamer"]["capture_height"]

    image_size = (width, height, 3)
    arr_size = width * height * 3

    shared_array = Array(c_uint8, arr_size)
    shared_image = np.frombuffer(
        shared_array.get_obj(),
        dtype=np.uint8)
    shared_image = np.reshape(shared_image, image_size)

    shared_state = Value(c_bool, True)

    process_manager = Manager()
    shared_data = process_manager.dict({
            "actualDuration": -1,
            "actualDurationFPS": -1,
            "totalDuration": -1,
            "totalDurationFPS": -1,
            "imageCaptureDuration": -1,
            "obsCreationDuration": -1,
            "brainDuration": -1,
            "frontendDuration": -1,
            "status": "Initialized",
            "lowerObs": [],
            "upperObs": [],
            "angles": []
        })

    return shared_image, shared_array, shared_state, shared_data


def print_game_data(shared_data):
    console_text = \
        f'Status: {shared_data["status"]} \n' \
        f'FPS 1: {shared_data["actualDurationFPS"]:04.1f} \n' \
        f'FPS 2: {shared_data["totalDurationFPS"]:04.1f} \n' \
        f'process time: {shared_data["actualDuration"]:05.3f} \n' \
        f'done time: {shared_data["totalDuration"]:05.3f} \n' \
        f'image cap dur: {shared_data["imageCaptureDuration"]:05.3f} \n' \
        f'obs dur: {shared_data["obsCreationDuration"]:05.3f} \n' \
        f'brain dur: {shared_data["brainDuration"]:05.3f} \n' \
        f'frontend dur: {shared_data["frontendDuration"]:05.3f}'
    line_jumps = console_text.count('\n')+2
    print(console_text)
    print(cursor_up(line_jumps))
    return line_jumps


def main(_):
    '''
    Connect to IP cam and print results
    '''
    mode = FLAGS.mode
    (shared_image,
     shared_array,
     shared_state,
     shared_data) = setup_variables(mode)
    game = Game(mode, shared_array, shared_state, shared_data)
    line_jumps = 0

    try:
        while True:
            with shared_array.get_lock():
                cv2.imshow('Game View', shared_image)
                cv2.waitKey(1)
            if 'status' not in shared_data:
                raise Exception("Error in game")
            line_jumps = print_game_data(shared_data)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(cursor_down(line_jumps))
        print("\nMain: Keyboard Interrupt")
    except Exception as error:
        print(cursor_down(line_jumps))
        print(f'Got unexpected exception in "main" Message: {error}')
    finally:
        with shared_state.get_lock():
            shared_state.value = False
        print("Main: Exiting")


if __name__ == "__main__":
    app.run(main)
