from __future__ import print_function
import numpy as np
import cv2

import grpc

import proto.RemoteImageToActions_pb2 as rita_pb2
import proto.RemoteImageToActions_pb2_grpc as rita_pb2_grpc


class RemoteImageProcessorClient():
    def __init__(self, params):
        # with open('temp/ssh_keys_local/cert_cli.pem', 'rb') as f:
        #     creds = grpc.ssl_channel_credentials(f.read())
        # channel = grpc.secure_channel('localhost:50054', creds)
        channel = grpc.insecure_channel('localhost:50054')
        self._stub = rita_pb2_grpc.ImageToActionsServerStub(channel)

    def _decode_image(self, image):
        image = np.frombuffer(image, dtype=np.uint8)
        return cv2.imdecode(image, flags=1)

    def _encode_image(self, image):
        _, jpg_image = cv2.imencode('.jpg', image)
        return jpg_image

    def image_to_actions(self, image):
        jpg_image = self._encode_image(image)
        jpg_image = jpg_image.tostring()
        request = rita_pb2.ActionsRequest(image=jpg_image)

        response = self._stub.ImageToActions(request)
        game_image = self._decode_image(response.image)
        return response.actions, game_image
