from concurrent import futures
import traceback
import logging
import cv2
import numpy as np
import grpc

import proto.RemoteImageToActions_pb2 as rita_pb2
import proto.RemoteImageToActions_pb2_grpc as rita_pb2_grpc

from computer_vision.image_processor import ImageProcessor
from ai_remote_brain.ai_remote_brain import UnityBrainServer


class RemoteImageToActions(rita_pb2_grpc.ImageToActionsServerServicer):
    def __init__(self, params):
        super().__init__()
        self._image_processor = ImageProcessor(params)
        self._brain_server = UnityBrainServer(params)

    def ImageToActions(self, request, context):
        try:
            jpg_image = request.image
            image = self._decode_image(jpg_image)
            robot_actions = self._get_actions(image)

            game_image = self._image_processor.get_image()
            response = rita_pb2.ActionsResponse(
                image=self._encode_image(game_image),
                actions=robot_actions)
            return response
        except Exception as error:
            traceback.print_exc()
            print(error)

    def _get_actions(self, image):
        robot_observations_dict = \
                    self._image_processor.image_to_observations(image=image)
        if not robot_observations_dict:
            return []

        actions = self._brain_server.get_actions(robot_observations_dict)
        robot_actions = self._to_robot_actions(actions)
        return robot_actions

    def _to_robot_actions(self, actions):
        robot_actions = []
        for aruco_id in actions.keys():
            robot_action = rita_pb2.RobotAction(action=actions[aruco_id],
                                                arucoMarkerID=aruco_id)
            robot_actions.append(robot_action)
        return robot_actions

    def _decode_image(self, image):
        image = np.frombuffer(image, dtype=np.uint8)
        return cv2.imdecode(image, flags=1)

    def _encode_image(self, image_buf):
        _, image = cv2.imencode('.jpg', image_buf)
        return image.tobytes()

    def stop(self):
        self._image_processor.stop()


class RemoteImageProcessorServer():
    def __init__(self, params):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
        with open('temp/ssh_keys_local/key.pem', 'rb') as f:
            private_key = f.read()
        with open('temp/ssh_keys_local/cert.pem', 'rb') as f:
            certificate_chain = f.read()
        server_credentials = grpc.ssl_server_credentials(
            ((private_key, certificate_chain),))

        self._class = RemoteImageToActions(params)
        rita_pb2_grpc.add_ImageToActionsServerServicer_to_server(
            self._class,
            self._server)
        self._server.add_secure_port('0.0.0.0:50054', server_credentials)

    def start(self):
        # try:
        self._server.start()
        self._server.wait_for_termination()
        # except KeyboardInterrupt:
        #     print("Keyboard Interrupt")
        #     self._class.stop()
        #     self._server.stop(0)


# python -m computer_vision.remote_image_processor_server
def main():
    params = parse_options("params-prod.yaml")
    server = RemoteImageProcessorServer(params)
    server.start()


# def main2():
#     params = parse_options("params-prod.yaml")
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
#     with open('temp/ssh_keys_local/key.pem', 'rb') as f:
#         private_key = f.read()
#     with open('temp/ssh_keys_local/cert.pem', 'rb') as f:
#         certificate_chain = f.read()
#     server_credentials = grpc.ssl_server_credentials(
#         ((private_key, certificate_chain),))

#     rita_pb2_grpc.add_ImageToActionsServerServicer_to_server(
#         RemoteImageToActions(params),
#         server)
#     server.add_secure_port('0.0.0.0:50054', server_credentials)
#     server.start()
#     server.wait_for_termination()


if __name__ == '__main__':
    from utils.utils import parse_options

    main()
