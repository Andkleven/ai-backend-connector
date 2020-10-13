from concurrent import futures
import traceback
import logging
import cv2
import numpy as np

import grpc

import proto.RemoteImageToActions_pb2 as rita_pb2
import proto.RemoteImageToActions_pb2_grpc as rita_pb2_grpc


class RemoteImageToActions(rita_pb2_grpc.ImageToActionsServerServicer):

    def ImageToActions(self, request, context):
        try:
            jpg_image = request.image
            image = self._decode_image(jpg_image)

            game_image = self._encode_image(image)
            game_image = game_image.tostring()
            robot_actions = rita_pb2.RobotAction(action=0, arucoMarkerID=2)
            robot_actions = rita_pb2.RobotAction(action=1, arucoMarkerID=3)

            response = rita_pb2.ActionsResponse(image=game_image,
                                                actions=[robot_actions])
            return response
        except Exception as error:
            traceback.print_exc()
            print(error)

    def _decode_image(self, image):
        image = np.frombuffer(image, dtype=np.uint8)
        return cv2.imdecode(image, flags=1)

    def _encode_image(self, image_buf):
        _, image = cv2.imencode('.jpg', image_buf)
        return image


class RemoteImageProcessorServer():
    def __init__(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
        with open('temp/ssh_keys/key.pem', 'rb') as f:
            private_key = f.read()
        with open('temp/ssh_keys/cert.pem', 'rb') as f:
            certificate_chain = f.read()
        server_credentials = grpc.ssl_server_credentials(
            ((private_key, certificate_chain),))

        rita_pb2_grpc.add_ImageToActionsServerServicer_to_server(
            RemoteImageToActions(),
            self._server)
        self._server.add_secure_port('localhost:50054', server_credentials)

    def start(self):
        self._server.start()
        self._server.wait_for_termination()


# python -m computer_vision.remote_image_processor_server
def main():
    server = RemoteImageProcessorServer()
    server.start()


if __name__ == '__main__':
    main()
