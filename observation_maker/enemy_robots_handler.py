from observation_maker.robots_handler import RobotsHandler


class EnemyRobotsHandler(RobotsHandler):
    def __init__(self, world, renderer):
        super().__init__(world, renderer)
        self._robot_type = "enemy_robot"
