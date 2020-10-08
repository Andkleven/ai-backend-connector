#!/usr/bin/env python3
import os
from flask import (
    Flask,
    render_template,
    request,
    Response,
    make_response,
    jsonify)
import json
from json import JSONEncoder
import cv2
import time
from multiprocessing import Value, Array, Manager
from ctypes import c_bool, c_uint8
import numpy as np
from utils.constants import SIMU, TEST, PROD
from utils.utils import parse_options

# https://www.pygame.org/wiki/HeadlessNoWindowsNeeded
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'true'
from game.game import Game


GAME = None
SHARED_IMAGE = None
SHARED_ARRAY = None
SHARED_STATE = None
SHARED_DATA = None

MAX_FPS = 24

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


app = Flask(
    __name__,
    # static_url_path='',
    static_folder='./web/static',
    template_folder='./web/html_templates')


def _setup_variables(mode):
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


def _generate_image():
    while True:
        if GAME is None:
            break
        if SHARED_STATE.value is False:
            raise Exception("Error in game")

        start_time = time.time()
        with SHARED_ARRAY.get_lock():
            (flag, encodedImage) = cv2.imencode(".jpg", SHARED_IMAGE)

        if not flag:
            print("Problem converting image to jpg", end='\r')
            continue

        yield(
            b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


def _stop_game():
    global GAME, SHARED_STATE
    print("Stopping game")
    with SHARED_STATE.get_lock():
        SHARED_STATE.value = False
    GAME = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game_data')
def game_data():
    "=== game_data"
    if GAME is None:
        # data = jsonify({"status": "Game not initialized"})
        data = json.dumps({"status": "Game not initialized"})
    else:
        # data = jsonify(SHARED_DATA.copy())
        data = json.dumps(SHARED_DATA.copy(), cls=NumpyArrayEncoder)
    return make_response(data, 200)


@app.route('/video_feed')
def video_feed():
    return Response(_generate_image(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start_game', methods=['POST'])
def start_game():
    global GAME, SHARED_IMAGE, SHARED_ARRAY, SHARED_STATE, SHARED_DATA

    request_json = request.json

    if GAME is not None:
        _stop_game()
    mode = request_json['gameMode']

    (SHARED_IMAGE,
     SHARED_ARRAY,
     SHARED_STATE,
     SHARED_DATA) = _setup_variables(mode)
    GAME = Game(mode, SHARED_ARRAY, SHARED_STATE, SHARED_DATA)
    return Response(status=200)


@app.route('/stop_game', methods=['POST'])
def stop_game():
    if GAME is not None:
        _stop_game()
    return Response(status=200)


def start_webserver(host, port):
    app.run(
        host=host,
        port=port,
        debug=True,
        threaded=True,
        use_reloader=False)


if __name__ == '__main__':
    start_webserver(host='0.0.0.0', port='8080')
