#!/usr/bin/env python

import cv2
import gi
import numpy as np
from multiprocessing import Lock

gi.require_version('Gst', '1.0')
from gi.repository import Gst


class GStreamerVideoSink():
    """BlueRov video capture class constructor
    Attributes:
        port (int): Video UDP port
        video_codec (string): Source h264 parser
        video_decode (string): Transform YUV (12bits) to BGR (24bits)
        video_pipe (object): GStreamer top-level pipeline
        video_sink (object): Gstreamer sink element
        video_sink_conf (string): Sink configuration
        video_source (string): Udp source ip and port
    """

    def __init__(self, port=5200):
        """Summary
        Args:
            port (int, optional): UDP port
        """

        Gst.init(None)

        self.port = port
        self._width = 1080
        self._height = 1080
        self._frame = None
        self._mutex = Lock()

        # [Software component diagram](https://www.ardusub.com/software/components.html)
        # UDP video stream (:5600)
        self.video_source = 'udpsrc port={}'.format(self.port)
        # [Rasp raw image](http://picamera.readthedocs.io/en/release-0.7/recipes2.html#raw-image-capture-yuv-format)
        # Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        # self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        # self.video_codec = '! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264' # <-----
        self.video_codec = '! application/x-rtp,encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec' # <-----
        # Python don't have nibble, convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        # Create a sink to get data
        # self.video_sink_conf = \
        #     '! appsink emit-signals=true sync=false max-buffers=2 drop=true'
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false drop=true'

        self.video_pipe = None
        self.video_sink = None

        self._run()

    def _start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]
        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)

        # On every restart the appsink's name's suffix number increments by one
        # appsink0, appsink1, appsink2, ...
        for i in range(100):
            self.video_sink = self.video_pipe.get_by_name(f'appsink{i}')
            if self.video_sink is not None:
                print(f"Using appsink{i}")
                break

        if self.video_sink is None:
            throw("video_sink is NONE")

    @staticmethod
    def _gst_to_opencv(sample):
        """Transform byte array into np array
        Args:
            sample (TYPE): Description
        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

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
        """ Get Frame
        Returns:
            iterable: bool and image frame, cap.read() output
        """
        with self._mutex:
            new_frame = self._frame
        return new_frame

    def frame_available(self):
        """Check if frame is available
        Returns:
            bool: true if frame is available
        """
        with self._mutex:
            available = type(self._frame) != type(None)
        return available

    def stop(self):
        print("FREERESOURCES")
        self.video_pipe.set_state(Gst.State.NULL)
        self.video_pipe = None
        self.video_sink = None
        self._mutex = None

    def _run(self):
        """ Get frame to update _frame
        """
        self._start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])
        self.video_sink.connect('new-sample', self._callback)

    def _callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self._gst_to_opencv(sample)
        # new_frame = self._crop_center(new_frame, 1080, 1080)
        # new_frame = self._resize(new_frame, self._width, self._height)
        with self._mutex:
            self._frame = new_frame

        return Gst.FlowReturn.OK


if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one
    video = GStreamerVideoSink()

    while True:
        # Wait for the next frame
        if not video.frame_available():
            continue

        frame = video.frame()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
