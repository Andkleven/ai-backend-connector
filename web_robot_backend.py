from flask import (
    Flask,
    render_template,
    request,
    Response,
    make_response,
    jsonify)
import cv2
import time

from game.game import Game


GAME = None
MAX_FPS = 24

app = Flask(__name__, template_folder='./html_templates')


def generate_image():
    while True:
        if GAME is None:
            continue

        start_time = time.time()
        frame = GAME.get_game_image_capture()
        if frame is None:
            print("Cannot get image from source", end='\r')
            continue

        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        if not flag:
            print("Problem converting image to jpg", end='\r')
            continue

        process_time = time.time() - start_time
        if process_time < (1 / MAX_FPS):
            time.sleep((1 / MAX_FPS) - process_time)

        yield(
            b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game_data')
def game_data():
    if GAME is None:
        data = {"status": "Game not initialized"}
    else:
        data = GAME.get_game_data()
        if data is None:
            data = {"status": "No data"}
    return make_response(jsonify(data), 200)


@app.route('/video_feed')
def video_feed():
    return Response(generate_image(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start_game', methods=['POST'])
def start_game():
    global GAME

    request_json = request.json

    if GAME is not None:
        print("Stopping game before start")
        GAME.stop_game()
        GAME = None
    GAME = Game(request_json['gameMode'])
    return Response(status=200)


@app.route('/stop_game', methods=['POST'])
def stop_game():
    global GAME
    if GAME is not None:
        print("Stopping game")
        GAME.stop_game()
        GAME = None
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
