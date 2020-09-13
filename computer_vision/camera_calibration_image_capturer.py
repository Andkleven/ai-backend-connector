
#!/usr/bin/env python
import time
import cv2
import gi
from reallife_camera_source.gstreamer_video_sink import GStreamerVideoSink
from utils.utils import parse_options

gi.require_version('Gst', '1.0')
from gi.repository import Gst


TIME_INTERVAL = 3


if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one
    params = parse_options("params-prod.yaml")
    video = GStreamerVideoSink(params)

    counter = 0
    last_time = time.time()
    while True:
        # Wait for the next frame
        if not video.frame_available():
            continue

        frame = video.frame()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time_now = time.time()
        time_from_last = time_now - last_time
        if time_from_last > TIME_INTERVAL:
            image_name = f'./calibration_image_{counter}.png'
            print(f"==== GOT IMAGE: {image_name}")
            temp_frame = frame.copy()
            temp_frame[:] = (255, 0, 0)
            cv2.imshow('frame', temp_frame)
            if cv2.waitKey(150) & 0xFF == ord('q'):
                break
            cv2.imwrite(image_name, frame)

            cv2.imshow('frame', frame)
            if cv2.waitKey(500) & 0xFF == ord('q'):
                break

            counter += 1
            last_time = time_now
