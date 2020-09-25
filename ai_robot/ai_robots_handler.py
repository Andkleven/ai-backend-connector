from ai_robot.ai_robot import RobotFrontend


class AIRobotsHandler():
    def __init__(self, params):
        self._ai_robots = {}
        for robot_params in params["ai_robots"]["robots"]:
            ai_robot = RobotFrontend(robot_params)
            aruco_id = robot_params["aruco_code"]
            self._ai_robots[aruco_id] = ai_robot

    def make_actions(self, actions_dict):
        for aruco_id in actions_dict.keys():
            self._ai_robots[aruco_id].make_action(actions_dict[aruco_id])

    def available(self):
        available = True
        for aruco_id in actions_dict.keys():
            if self._ai_robots[aruco_id].available is False:
                available = False
        return available
