'''
Module for geometric calculation functions
'''
import shapely
from shapely.geometry import LineString, Point, Polygon
from math import cos
from math import sin
from math import pi

from computer_vision.game_object import GameObject

START_OFFSET = 50
RED = (0, 0, 255)
GREEN = (0, 255, 0)


def _create_line(coordinates, angle, dist):
    angle = angle * pi / 180.0
    line = LineString([
        (coordinates[0] + START_OFFSET * sin(angle),
         coordinates[1] + START_OFFSET * cos(angle)),
        (coordinates[0] + dist * sin(angle),
         coordinates[1] + dist * cos(angle))
    ])
    return line


def _get_ray_angles_for_robot_rotation(robot_rotation, angles):
    local_rotation = robot_rotation - 90
    ray_angles = angles
    for i in range(len(ray_angles)):
        ray_angles[i] = ray_angles[i] - local_rotation + 90

    return ray_angles


def get_ray_angles(max_angle_per_side, number_of_rays_per_side):
    anglesOut = []
    delta = max_angle_per_side / number_of_rays_per_side

    for i in range(number_of_rays_per_side):
        anglesOut.append(-max_angle_per_side + i * delta)

    anglesOut.append(0)

    for i in range(number_of_rays_per_side):
        anglesOut.append((i + 1) * delta)

    # Angles created in Python are wrong way around compared to Unity
    anglesOut.reverse()

    return anglesOut


def create_fat_rays(robot_obj, angles, ray_length, ray_width, front_ray_width):
    ray_angles = _get_ray_angles_for_robot_rotation(robot_obj.rotation, angles)
    center_ray_index = int((len(angles) - 1) / 2)
    fat_rays = []
    for idx, angle in enumerate(ray_angles):
        cast_width, cast_color = \
            (front_ray_width, RED) \
            if idx is center_ray_index \
            else (ray_width, GREEN)
        fat_ray = _create_line(robot_obj.coords[0], angle, ray_length)
        fat_ray_obj = GameObject(
            [*fat_ray.coords],
            cast_color,
            buffer_distance=cast_width,
            name="Fat ray")
        fat_rays.append(fat_ray_obj)
    return fat_rays
