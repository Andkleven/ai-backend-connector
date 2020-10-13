from __future__ import print_function
import numpy as np
import cv2

import grpc

import proto.RemoteImageToActions_pb2 as rita_pb2
import proto.RemoteImageToActions_pb2_grpc as rita_pb2_grpc


class RemoteImageProcessorClient():
    def __init__(self, params):
        with open('temp/ssh_keys/cert_cli.pem', 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        channel = grpc.secure_channel('localhost:50054', creds)
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


#                 # 2) Get observations from image
#                 # The _ and __ variables are placeholders for the second
#                 # robot and it's observations
#                 robot_observations_dict = \
#                     self._image_processor.image_to_observations(image=image)
#                 self._log_time(log_name='obsCreationDuration')

#                 # 2.1) We didn't get observations
#                 if not robot_observations_dict:
#                     self._shared_data['status'] = 'No observations'
#                     # print("\n\n=========== No observations\n\n")
#                     self._stop_robots()
#                     self._end_routine()
#                     continue
#                 # 2.2) We got observations
#                 for aruco_id in robot_observations_dict.keys():
#                     self._shared_data[f'robot_{aruco_id}_lower_obs'] = \
#                         robot_observations_dict[aruco_id]['lower_obs']
#                     self._shared_data[f'robot_{aruco_id}_upper_obs'] = \
#                         robot_observations_dict[aruco_id]['lower_obs']
#                     self._shared_data['angles'] = self._image_processor.angles

#                 if mode == PROD or mode == SIMU:
#                     # 3a) Get action from brain with the observations
#                     actions = brain_server.get_actions(robot_observations_dict)
#                     self._log_time(log_name='brainDuration')

#                     # 4) Send the action to frontend
#                     _ = self._frontend.make_actions(actions)
#                     self._shared_data['status'] = 'Playing game'
#                     self._log_time(log_name='frontendDuration')
#                 else:
#                     # 3b) Just log status, don't connect to
#                     # brain server nor frontend
#                     self._shared_data['status'] = 'Running in test mode'