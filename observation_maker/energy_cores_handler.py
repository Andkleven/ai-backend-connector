from Box2D import (
    b2Vec2,
    b2CircleShape,
    b2PolygonShape)


class EnergyCoresHandler(object):
    def __init__(self, world, params):
        self._world = world
        self._pos_ecores = []
        self._neg_ecores = []
        self._ecore_radius = params["image_processing"]["ball_radius"]

    def set_transforms(self, pos_ecore_trans, neg_ecore_trans):
        self._handle_group(pos_ecore_trans,
                           self._pos_ecores,
                           'positive_energy_core')
        self._handle_group(neg_ecore_trans,
                           self._neg_ecores,
                           'negative_energy_core')

    def update(self):
        pass

    def get_ecore_counts(self):
        return len(self._neg_ecores), len(self._pos_ecores)

    def _handle_group(self, new_ecore_trans, ecore_arr, tag_name):
        current_ecore_count = len(ecore_arr)
        new_ecore_count = len(new_ecore_trans)

        if new_ecore_count > current_ecore_count:
            new_ecores_to_create = new_ecore_count - current_ecore_count
            for i in range(new_ecores_to_create):
                new_ecore = self._create_ball(tag_name)
                ecore_arr.append(new_ecore)
        # Activate and deactivate balls if needed
        for ecore, transform in zip(
                ecore_arr[:new_ecore_count],
                new_ecore_trans):
            self._activate_ball(ecore, transform)
        for ecore in ecore_arr[new_ecore_count:]:
            self._deactivate_ball(ecore)

    def _create_ball(self, ball_type):
        # Create balls if needed and update their position
        ball = self._world.CreateStaticBody(
            shapes=b2CircleShape(pos=(0, 0), radius=self._ecore_radius))
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
