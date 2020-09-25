from Box2D import (
    b2Vec2,
    b2_pi,
    b2Color,
    b2PolygonShape)


ROBOT_VERTICES = [(35, 45), (35, -45), (-35, -45), (-35, 45)]


class RobotsHandler(object):
    def __init__(self, world, renderer):
        self._world = world
        self._renderer = renderer
        # A dictionary in which the aruco marker is the key and the
        # value is the robot's Box2D StaticBody
        self._robots = {}
        self._robot_type = "Unknown"

    def set_transforms(self, trans_dict):
        # No robots discovered
        if not trans_dict:
            for aruco_id in self._robots.keys():
                self._deactivate_robot(self._robots[aruco_id])
        # Robots discovered
        else:
            for aruco_id in trans_dict.keys():
                # We have a new robot so create new
                if aruco_id not in self._robots.keys():
                    new_robot = self._create_robot(aruco_id, self._robot_type)
                    self._robots[aruco_id] = new_robot
                # Update robot transform
                self._update_robot_transform(
                    self._robots[aruco_id],
                    trans_dict[aruco_id]['position'],
                    trans_dict[aruco_id]['rotation'])

            # Deactivate missing robots
            for aruco_id in self._robots.keys():
                if aruco_id not in trans_dict.keys():
                    self._deactivate_robot(self._robots[aruco_id])

    def _update_robot_transform(self, robot, position, rotation):
        robot.active = True
        robot.position = b2Vec2(position[0], position[1])
        robot.angle = -rotation[0] * b2_pi / 180

    def get_vertices_for_all(self):
        pass

    def get_color(self):
        return self._color

    def update(self):
        pass

    def _create_robot(self, aruco_id, robot_type):
        robot = self._world.CreateStaticBody(
            position=(0, 0),
            shapes=b2PolygonShape(vertices=ROBOT_VERTICES))
        robot.userData = {
            'aruco_id': aruco_id,
            'type': self._robot_type}
        for fixture in robot.fixtures:
            fixture.sensor = True
        return robot

    def _deactivate_robot(self, robot):
        robot.active = False
        # Move the robot off the screen
        robot.position = b2Vec2(5000, 5000)
