'''
Reference code
https://mecaruco.readthedocs.io/en/latest/notebooks_rst/aruco_calibration.html
'''

from absl import app
from absl import flags

import numpy as np
import cv2
import os
from cv2 import aruco
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import json


flags.DEFINE_string(
    "mode",
    "calibration",
    "Specify calibrations mode. Either: 'calibration' or 'gen_chessboard'",
    short_name="m")
flags.DEFINE_string(
    "image_folder",
    "computer_vision/unity_camera_calibration/",
    "Specify the folder which has the calibration images",
    short_name="i")

FLAGS = flags.FLAGS


def _read_chessboards(images, aruco_dict, board):
    """
    Charuco base pose estimation.
    """
    print("POSE ESTIMATION STARTS:")
    all_corners = []
    all_ids = []
    decimator = 0
    # SUB PIXEL CORNER DETECTION CRITERION
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        100,
        0.0001)

    for im in images:
        print("=> Processing image {0}".format(im))
        frame = cv2.imread(im)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray,
            aruco_dict)

        if len(corners) > 0:
            # SUB PIXEL DETECTION
            for corner in corners:
                cv2.cornerSubPix(gray, corner,
                                 winSize=(20, 20),
                                 zeroZone=(-1, -1),
                                 criteria=criteria)
            res2 = cv2.aruco.interpolateCornersCharuco(
                corners,
                ids,
                gray,
                board)
            if (
                    res2[1] is not None and
                    res2[2] is not None and
                    len(res2[1]) > 3 and
                    decimator % 1 == 0):
                all_corners.append(res2[1])
                all_ids.append(res2[2])

        decimator += 1

    imsize = gray.shape
    return all_corners, all_ids, imsize


def _calibrate_camera(allCorners, allIds, imsize, aruco_dict, board):
    """
    Calibrates the camera using the dected corners.
    """
    print("CAMERA CALIBRATION")

    camera_matrix_init = np.array([[2000., 0., imsize[0]/2.],
                                   [0., 2000., imsize[1]/2.],
                                   [0., 0., 1.]],
                                  dtype=np.float32)

    dist_coeffs_init = np.zeros((5, 1))
    flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL)
    (ret, camera_matrix, distortion_coefficients0,
     rotation_vectors, translation_vectors,
     std_deviations_intrinsics, std_deviations_extrinsics,
     per_view_errors) = cv2.aruco.calibrateCameraCharucoExtended(
                      charucoCorners=allCorners,
                      charucoIds=allIds,
                      board=board,
                      imageSize=imsize,
                      cameraMatrix=camera_matrix_init,
                      distCoeffs=dist_coeffs_init,
                      flags=flags,
                      criteria=(
                          cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT,
                          10000,
                          1e-9))

    return (
        ret,
        camera_matrix,
        distortion_coefficients0,
        rotation_vectors,
        translation_vectors)


def save_charuco_chessboard():
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    board = aruco.CharucoBoard_create(11, 8, 10, 7, aruco_dict)
    imboard = board.draw((500, 500))
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.imshow(imboard, cmap=mpl.cm.gray, interpolation="nearest")
    ax.axis("off")
    plt.savefig("camera_calibration/charuco_chessboard.pdf")


def calibrate_camera(image_folder):
    images = [
        image_folder + f for f in os.listdir(
            image_folder) if f.endswith(".png") or f.endswith(".jpg")]
    print(images)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    board = aruco.CharucoBoard_create(11, 8, 10, 7, aruco_dict)
    allCorners, allIds, imsize = _read_chessboards(images, aruco_dict, board)
    ret, mtx, dist, rvecs, tvecs = _calibrate_camera(
        allCorners,
        allIds,
        imsize,
        aruco_dict,
        board)

    camera_calibration_params = {
        "ret": ret,
        "mtx": mtx.tolist(),
        "dist": dist.tolist(),
    }

    calib_params_file = os.path.join(image_folder, "calib-params.json")
    with open(calib_params_file, 'w') as f:
        json.dump(camera_calibration_params, f)


def start(_):
    mode = FLAGS.mode

    if mode == "gen_chessboard":
        save_charuco_chessboard()
    elif mode == "calibration":
        image_folder = FLAGS.image_folder
        calibrate_camera(image_folder)


if __name__ == "__main__":
    app.run(start)
