from computer_vision.aruco_marker_detector import ArucoMarkerDetector
from computer_vision.ecore_detector import EnergyCoreDetector
from observation_maker.observation_maker import ObservationMaker

import cv2
import numpy as np


class ImageProcesser():
    def __init__(self, params):
        self._params = params
        self._aruco_detector = ArucoMarkerDetector(params)
        self._ecore_detector = EnergyCoreDetector(params)
        self._observation_maker = ObservationMaker(params)

    @property
    def angles(self):
        """
        return : list(float)
            list of angles
        """
        return self._observation_maker.angles

    def get_image(self):
        image = self._observation_maker.get_image()
        return image

    def image_to_observations(self, image):
        """
        Create observations for the neural network from input image.
        """
        if image is None:
            raise 'No image given to "image_to_observations"-method'
        warning_text = ''

        # Mask goal area to stop robot from moving when ball is in goal
        # pts = np.array(self._params['arena']['enemy_goal'])
        # cv2.fillPoly(image, [pts], (0, 0, 255))
        # pts = np.array(self._params['arena']['friendly_goal'])
        # cv2.fillPoly(image, [pts], (255, 0, 0))

        # 1) Detect aruco markers for own and enemy robots
        friendly_trans_dict, enemy_trans_dict = \
            self._aruco_detector.get_robot_transforms(image=image)

        # 2) Detect good and bad balls
        pos_ecore_transforms, neg_ecore_transforms = \
            self._ecore_detector.get_ecore_transforms(image=image)

        # 3.1) No friendly robots or no balls detected
        if ((not pos_ecore_transforms and not neg_ecore_transforms) or not
           friendly_trans_dict):
            if not friendly_trans_dict:
                warning_text = \
                    "Could not locate friendly robot Aruco markers\n"
            if not pos_ecore_transforms and not neg_ecore_transforms:
                warning_text = warning_text + 'Could not locate balls'
            self._observation_maker.update_image(image, message=warning_text)
            return {}

        # 3.2) Get observations for friendly robots
        robot_observations_dict = self._observation_maker.get_observations(
            image=image,
            friendly_trans_dict=friendly_trans_dict,
            pos_ecore_transforms=pos_ecore_transforms,
            neg_ecore_transforms=neg_ecore_transforms,
            enemy_trans_dict=enemy_trans_dict)

        return robot_observations_dict
