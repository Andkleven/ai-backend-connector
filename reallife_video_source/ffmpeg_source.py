#!/usr/bin/env python

import traceback
import cv2
import numpy as np
from multiprocessing import Process, Lock, Array
import ctypes
import time


COLOR_CHANNELS = 3


class VideoSource():
    def __init__(self, params):
        multicast_ip = params["ai_video_streamer"]["multicast_ip"]
        port = str(params["ai_video_streamer"]["port"])
        width = params['ai_video_streamer']['capture_width']
        height = params['ai_video_streamer']['capture_height']

        url = f'rtp://{multicast_ip}:{port}/'

        image_size = (width, height, COLOR_CHANNELS)
        arr_size = width * height * COLOR_CHANNELS
        self._shared_arr = Array(ctypes.c_uint8, arr_size)
        self._image_outside_thread = np.frombuffer(self._shared_arr.get_obj(),
                                                   dtype=np.uint8)
        self._image_outside_thread = np.reshape(self._image_outside_thread,
                                                image_size)

        self._p = Process(target=self._run,
                          args=(self._shared_arr, image_size, url))
        self._p.daemon = True
        self._p.start()

    def _crop_center(self, image, cropped_width, cropped_height):
        height, width, _ = image.shape
        startx = int((width - cropped_width) / 2)
        starty = int((height - cropped_height) / 2)

        stopx = startx + cropped_width
        stopy = starty + cropped_height
        image = image[starty:stopy, startx:stopx, :]
        return image

    def _resize(self, image, width, height):
        return cv2.resize(image, (width, height))

    def frame(self):
        """
        Get Frame
        Returns : numpy.array(int8)
            Image as a numpy array
        """
        with self._shared_arr.get_lock():
            return np.copy(self._image_outside_thread)

    def frame_available(self):
        """
        Check if frame is available
        Returns : boolean
            true if frame is available otherwise false
        """
        with self._shared_arr.get_lock():
            available = not isinstance(self._image_outside_thread,
                                       type(None))
        return available

    def stop(self):
        self._p.terminate()

    def _run(self, shared_array, image_size, url):
        """
        Get frame to update _frame
        """
        try:
            image_inside_thread = np.frombuffer(shared_array.get_obj(),
                                                dtype=np.uint8)
            image_inside_thread = np.reshape(image_inside_thread,
                                             image_size)

            cap = cv2.VideoCapture(url)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame is None:
                    print(f'No image from {url}')
                    continue
                with shared_array.get_lock():
                    image_inside_thread[:] = frame

        except Exception as error:
            print(f'Got unexpected exception in "main" Message: {error}')


# Main for testing video connection. Run with below command executed in
# project's root folder. Make sure 'params-prod.yaml' file has
# 'ai_video_streamer' group and correct parameters set.
# python -m reallife_video_source.ffmpeg_source
if __name__ == '__main__':
    from utils.utils import parse_options
    # Create the video object
    # Add port= if is necessary to use a different one
    params = parse_options("params-prod.yaml")
    video = VideoSource(params)

    try:
        while True:
            # Wait for the next frame
            if not video.frame_available():
                print("Frame not available")
                continue

            frame = video.frame()
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Closing")
    finally:
        video.stop()
        print("Exiting")
