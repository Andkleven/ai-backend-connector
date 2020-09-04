from Box2D import (
    b2Vec2,
    b2CircleShape)


class BallHandler(object):
    def __init__(self, world, params):
        self._world = world
        self._good_balls = []
        self._bad_balls = []
        self._good_ball_transforms = []
        self._bad_ball_transforms = []
        self._ball_radius = params["image_processing"]["ball_radius"]

    def set_transforms(self, good_ball_transforms, bad_ball_transforms):
        self._good_ball_transforms = good_ball_transforms
        self._bad_ball_transforms = bad_ball_transforms

    def update(self):
        if self._good_ball_transforms is None:
            self._good_ball_transforms = []
        if self._bad_ball_transforms is None:
            self._bad_ball_transforms = []

        current_good_ball_count = len(self._good_balls)
        new_good_ball_count = len(self._good_ball_transforms)

        if new_good_ball_count > current_good_ball_count:
            new_balls_count = new_good_ball_count - current_good_ball_count
            for i in range(new_balls_count):
                new_ball = self._create_ball('good_ball')
                self._good_balls.append(new_ball)

        # Activate and deactivate balls if needed
        for ball, transform in zip(
                self._good_balls[:new_good_ball_count],
                self._good_ball_transforms):
            self._activate_ball(ball, transform)
        for ball in self._good_balls[new_good_ball_count:]:
            self._deactivate_ball(ball)

    def _create_ball(self, ball_type):
        # Create balls if needed and update their position
        ball = self._world.CreateStaticBody(
            shapes=b2CircleShape(pos=(0, 0), radius=self._ball_radius))
        ball.userData = {'type': ball_type}
        for fixture in ball.fixtures:
            fixture.sensor = True
        return ball

    def _activate_ball(self, ball, transform):
        ball.active = True
        ball.position = b2Vec2(transform[0], transform[1])

    def _deactivate_ball(self, ball):
        ball.active = False
        # Move the ball off the screen
        ball.position = b2Vec2(5000, 5000)
