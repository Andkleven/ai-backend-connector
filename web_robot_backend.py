from flask import Flask, render_template, Response
import cv2
import time

from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink


app = Flask(__name__, template_folder='./html_templates')

IMAGE_SOURCE = None
FPS = 24


def generate():
    while True:
        start_time = time.time()
        if not IMAGE_SOURCE.frame_available():
            continue
        frame = IMAGE_SOURCE.frame()

        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        if not flag:
            continue

        process_time = time.time() - start_time
        if process_time < (1 / FPS):
            time.sleep((1 / FPS) - process_time)

        yield(
            b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    IMAGE_SOURCE = GStreamerVideoSink(5200)

    app.run(
        host='0.0.0.0',
        port='8080',
        debug=True,
        threaded=True,
        use_reloader=False)
