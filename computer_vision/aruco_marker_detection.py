import cv2
from cv2 import aruco
import numpy as np
import math


def get_aruco_marker_pos_and_rot(
        image,
        aruco_code,
        aruco_dict,
        parameters,
        camera_calib_params,
        size_of_marker,
        only_z_rot=True,
        length_of_axis=0.05):
    '''
    Get the position and rotation of the aruco marker to be
    detected

    Returns:
        x and y positions are in pixel coordinates from
        zero to image height/width in pixels.
        tuple
            pos_and_rot : [x, y] [rot_x, rot_y, rot_z]
    '''
    mtx = np.array(camera_calib_params["mtx"], dtype=np.float32)
    dist = np.array(camera_calib_params["dist"], dtype=np.float32)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, detected_ids, rejected_img_points = aruco.detectMarkers(
        image,
        aruco_dict,
        parameters=parameters)

    # rvecs, tvecs = None
    # if detected_ids:
    rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
        corners,
        size_of_marker,
        mtx,
        dist)

    robot_pos, robot_rot = _get_aruco_pos_and_rot(
        detected_ids=detected_ids,
        aruco_code=aruco_code,
        corners=corners,
        rvecs=rvecs,
        only_z_rot=only_z_rot)

    # Show image showing the detected aruco markers
    if tvecs is not None and rvecs is not None:
        _drawDetectedMarkers(image, corners, detected_ids, tvecs,
                             rvecs, mtx, dist, length_of_axis,
                             rejected_img_points)

    return robot_pos, robot_rot


def _get_aruco_pos_and_rot(
        detected_ids,
        aruco_code,
        corners,
        rvecs,
        only_z_rot):
    """
    Calculates rotation matrix to euler angles
    The result is the same as MATLAB except the order
    of the euler angles ( x and z are swapped ).
    https://www.learnopencv.com/rotation-matrix-to-euler-angles/

    Args:
        detected_ids ([int]): Detected aruco marker ids
        aruco_code (int): Robot's aruco marker
        corners (?): List of Detected aruco marker corner's
                     from aruco.detectMarkers
        rvecs (?): ?

    Returns:
        x and y positions are in pixel coordinates from
        zero to image height/width in pixels.
        Rotations are from -180 to 180 degrees
        tuple
            pos_and_rot : numpy array[x, y] numpy array[rot_x, rot_y, rot_z]

    """
    if (detected_ids is None or
            corners is None or
            rvecs is None):
        return None, None

    robot_pos = None
    robot_rot = None

    for id, corner_list, rvec in zip(detected_ids, corners, rvecs):
        center = np.mean(corner_list[0], axis=0, dtype=np.float32)
        dst, jacobian = cv2.Rodrigues(rvec[0])
        euler_angles = _rotation_matrix_to_euler_angles(dst)

        if id == aruco_code:
            robot_pos = center
            if only_z_rot:
                robot_rot = np.array([euler_angles[2]])
            else:
                robot_rot = euler_angles
            break

    return robot_pos, robot_rot


def _is_rotation_matrix(matrix):
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


def _rotation_matrix_to_euler_angles(rotation_matrix):
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
    assert _is_rotation_matrix(rotation_matrix)
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
        image, corners, detected_ids, tvecs,
        rvecs, mtx, dist, length_of_axis, rejected_img_points):
    """
    Draw axis to the detected aruco markers
    Draw Squares around detected aruco markers
    Draw the rejected aruco markers candidates
    """
    imaxis = aruco.drawDetectedMarkers(image, corners, detected_ids)
    for i in range(len(tvecs)):
        imaxis = aruco.drawAxis(
            imaxis,
            mtx,
            dist,
            rvecs[i],
            tvecs[i],
            length_of_axis)

    aruco.drawDetectedMarkers(image, corners, detected_ids)
    aruco.drawDetectedMarkers(
        image,
        rejected_img_points,
        borderColor=(100, 0, 240))
