import json
import math
import numpy as np
import cv2
from cv2 import aruco


BORDER_COLOR = (100, 0, 240)


class ArucoMarkerDetector():
    def __init__(self, params):
        self._aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self._robot1_aruco_code = params["robot"]["robot1_aruco_code"]
        self._robot2_aruco_code = params["robot"]["robot2_aruco_code"]
        self._aruco_detector_parameters = aruco.DetectorParameters_create()

        with open(params["camera"]["calib_params"]) as json_file:
            camera_calib_params = json.load(json_file)
        self._size_of_marker = params["robot"]["aruco_marker_size"]

        self._mtx = np.array(camera_calib_params["mtx"], dtype=np.float32)
        self._dist = np.array(camera_calib_params["dist"], dtype=np.float32)

        self._length_of_axis = 0.05

    def get_robot_transforms(self, image):
        '''
        Detect aruco markers from given image and return robot game object

        image : numpy.array( numpy.array( float ) )
        return : numpy.array( numpy.array( float ) )
        '''
        if image is None:
            raise("No image for get_robot_transforms-method")

        robot_transforms = self._get_aruco_marker_transforms(image=image)

        robot1_transform = None
        robot2_transform = None
        enemy_transforms = None

        for transform in robot_transforms:
            if transform['aruco_id'] == self._robot1_aruco_code:
                if robot1_transform is None: robot1_transform = {}
                robot1_transform = transform
            elif transform['aruco_id'] == self._robot2_aruco_code:
                if robot2_transform is None: robot2_transform = {}
                robot2_transform = transform
            else:
                if enemy_transforms is None: enemy_transforms = []
                enemy_transforms.append(transform)

        return robot1_transform, robot2_transform, enemy_transforms

    def _get_aruco_marker_transforms(self, image):
        '''
        Get the position and rotation for all detected aruco markers.
        '''
        corners, detected_ids, rejected_img_points = aruco.detectMarkers(
            image,
            self._aruco_dict,
            parameters=self._aruco_detector_parameters)

        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
            corners,
            self._size_of_marker,
            self._mtx,
            self._dist)

        # Draw detected aruco markers to image
        if tvecs is not None and rvecs is not None:
            self._drawDetectedMarkers(
                image, corners, detected_ids, tvecs,
                rvecs, rejected_img_points)

        transforms = self._aruco_poses_to_transforms(
            detected_ids=detected_ids,
            corners=corners,
            rvecs=rvecs)

        return transforms

    def _aruco_poses_to_transforms(
            self,
            detected_ids,
            corners,
            rvecs,
            only_z_rot=True):
        """
        Calculates rotation matrix to euler angles
        The result is the same as MATLAB except the order
        of the euler angles ( x and z are swapped ).
        https://www.learnopencv.com/rotation-matrix-to-euler-angles/

        Args:
            detected_ids ([int]): Detected aruco marker ids
            corners (?): List of Detected aruco marker corner's
                        from aruco.detectMarkers
            rvecs (?): ?

        Returns : list(dictionary)
            aruco_id : int
            position : numpy array[x, y]
                x and y positions are in pixel coordinates from
                zero to image height/width in pixels.
            rotation : numpy array[rot_x, rot_y, rot_z] or
                        numpy array[rot_z]
                Rotations are from -180 to 180 degrees
        """
        transforms = []

        if detected_ids is None or corners is None or rvecs is None:
            return transforms

        for id, corner_list, rvec in zip(detected_ids, corners, rvecs):
            robot_trans_dict = {}
            robot_trans_dict['aruco_id'] = id
            center = np.mean(corner_list[0], axis=0, dtype=np.float32)
            robot_trans_dict['position'] = center
            dst, jacobian = cv2.Rodrigues(rvec[0])
            euler_angles = self._rotation_matrix_to_euler_angles(dst)

            if only_z_rot:
                robot_trans_dict['rotation'] = np.array([euler_angles[2]])
            else:
                robot_trans_dict['rotation'] = euler_angles
            transforms.append(robot_trans_dict)

        return transforms

    def _is_rotation_matrix(self, matrix):
        """
        Checks if a matrix is a valid rotation matrix.
        https://www.learnopencv.com/rotation-matrix-to-euler-angles/

        Args:
            matrix (?): OpenCV matrix

        Returns:
            boolean: Is the input matrix rotation matrix
        """
        r_t = np.transpose(matrix)
        should_be_identity = np.dot(r_t, matrix)
        identity = np.identity(3, dtype=matrix.dtype)
        n = np.linalg.norm(identity - should_be_identity)
        return n < 1e-6

    def _rotation_matrix_to_euler_angles(self, rotation_matrix):
        """
        Calculates rotation matrix to euler angles
        The result is the same as MATLAB except the order
        of the euler angles ( x and z are swapped ).
        https://www.learnopencv.com/rotation-matrix-to-euler-angles/

        Args:
            rotation_matrix (int): Rotation matrix to transform

        Returns:
            numpy array [3]: x, y and z euler rotations
        """
        assert self._is_rotation_matrix(rotation_matrix)
        sy = math.sqrt(
            rotation_matrix[0, 0] * rotation_matrix[0, 0] +
            rotation_matrix[1, 0] * rotation_matrix[1, 0])
        singular = sy < 1e-6
        if not singular:
            x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = 0

        return np.array([
                math.degrees(x),
                math.degrees(y),
                math.degrees(z)],
            dtype=np.float32)

    def _drawDetectedMarkers(
            self,
            image,
            corners,
            detected_ids,
            tvecs,
            rvecs,
            rejected_img_points):
        """
        Draw axis to the detected aruco markers
        Draw Squares around detected aruco markers
        Draw the rejected aruco markers candidates
        """
        imaxis = aruco.drawDetectedMarkers(image, corners, detected_ids)
        for i in range(len(tvecs)):
            imaxis = aruco.drawAxis(
                imaxis,
                self._mtx,
                self._dist,
                rvecs[i],
                tvecs[i],
                self._length_of_axis)

        aruco.drawDetectedMarkers(image, corners, detected_ids)
        aruco.drawDetectedMarkers(
            image,
            rejected_img_points,
            borderColor=BORDER_COLOR)
