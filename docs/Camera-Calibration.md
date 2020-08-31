# Camera Calibration
For the Aruco Marker detection to work well the camera feeding the images to the AI Backend Connector has to be calibrated

1. Create chessboard PDF if you are calibrating real world camera. This is not used if you calibrate the AI Simulation's camera.
    ```sh
    python -m computer_vision.camera_calibration -m=gen_chessboard
    ```
1. In real world print the Chessboard image to an A4-paper. In AI Simulation use the `CameraCalibrationImage`-GameObject in `AIBackendConnectorTest`-scene.
1. Place the Chessboard image to the camera's image and save the image.
1. Change the A4-Chessboard's place, angle and distance from the camera and save the image. Repeat 10 times. Place the all the images to some folder.
1. Create calibration parameters for the camera by running the following script. Set the calibration image folder with argument `-i`
    ```sh
    python -m computer_vision.camera_calibration -m=calibration -i=[path/to/calibration-images-without-brackets]
    ```
1. Rename the created `calib-params.json`-file to describe the calibrated camera. Place the file under `computer_vision/camera_calibration_params`-folder
1. Update the location to `params-prod.yaml` or `params-simu.yaml`-file's section `camera/calib_params` or `simulation/calib_params`
