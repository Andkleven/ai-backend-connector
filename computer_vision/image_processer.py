from computer_vision.aruco_marker_detector import ArucoMarkerDetector
from computer_vision.ball_detector import BallDetector
from observation_maker.observation_maker import ObservationMaker


class ImageProcesser():
    def __init__(self, params):
        self._aruco_detector = ArucoMarkerDetector(params)
        self._ball_detector = BallDetector(params)
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
        no_friendly_robots = None
        no_balls = None

        # 1) Detect aruco markers for own and enemy robots
        robot1_transform, robot2_transform, enemy_transforms = \
            self._aruco_detector.get_robot_transforms(image=image)
        if robot1_transform is None and robot2_transform is None:
            warning_text = "Could not locate friendly robot Aruco markers\n"
            no_friendly_robots = True

        # 2) Detect good and bad balls
        good_ball_transforms, bad_ball_transforms = \
            self._ball_detector.get_ball_transforms(image=image)
        if good_ball_transforms is None and bad_ball_transforms is None:
            warning_text = warning_text + 'Could not locate balls'
            no_balls = True

        # 3.1) No friendly robots or no balls detected
        if no_friendly_robots is True or no_balls is True:
            self._observation_maker.update_image(image, message=warning_text)
            return None, None, None, None

        # 3.2) Get observations for friendly robots
        low_obs_r1, up_obs_r1, low_obs_r2, up_obs_r2 = \
            self._observation_maker.get_observations(
                image=image,
                robot1_transform=robot1_transform,
                robot2_transform=robot2_transform,
                good_ball_transforms=good_ball_transforms,
                bad_ball_transforms=bad_ball_transforms,
                enemy_transforms=enemy_transforms)

        return low_obs_r1, up_obs_r1, low_obs_r2, up_obs_r2
