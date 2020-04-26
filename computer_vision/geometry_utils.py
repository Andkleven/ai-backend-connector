'''
Module for geometric calculation functions
'''
import shapely
from shapely.geometry import LineString, Point, Polygon
from math import cos
from math import sin
from math import pi

from computer_vision.game_object import GameObject


def _get_ray_angles(robot_rotation, angles):
    local_rotation = robot_rotation - 90
    ray_angles = angles
    for i in range(len(ray_angles)):
        ray_angles[i] = ray_angles[i] - local_rotation + 90

    return ray_angles


def _create_line(coordinates, angle, dist):
    angle = angle * pi / 180.0
    line = LineString([
        (coordinates[0], coordinates[1]),
        (coordinates[0] + dist * sin(angle),
         coordinates[1] + dist * cos(angle))
    ])
    return line


def _create_sector_vectors(local_origo, angles, ray_length):
    sector_vectors = []
    for angle in angles:
        sector_vector = _create_line(local_origo.coords[0], angle, ray_length)
        sector_vectors.append(sector_vector)

    return sector_vectors


def create_sectors(robot_pos, robot_rot, angles, ray_length):
    local_origo = GameObject([robot_pos], (0, 255, 0), name="Robot origo")
    ray_angles = _get_ray_angles(robot_rot, angles)
    sector_vectors = _create_sector_vectors(
        local_origo,
        ray_angles,
        ray_length)
    sector_points_array = []
    sectors = []

    for i in range(len(sector_vectors) - 1):
        sector_points_array.append([
            local_origo.coords[0],
            sector_vectors[i].coords[1],
            sector_vectors[i + 1].coords[1]])

    for sector_points in sector_points_array:
        sectors.append(GameObject(sector_points, (0, 255, 255), name="sector"))

    return sectors


def create_fat_rays(robot_pos, robot_rot, angles, ray_length, ray_width):
    local_origo = GameObject([robot_pos], (0, 255, 0), name="Robot origo")
    ray_angles = _get_ray_angles(robot_rot, angles)

    thin_rays = []
    for angle in ray_angles:
        thin_ray = _create_line(local_origo.coords[0], angle, ray_length)
        thin_ray_obj = GameObject(
            [*thin_ray.coords],
            (0, 255, 0),
            buffer_distance=ray_width,
            name="Thin ray")
        thin_rays.append(thin_ray_obj)
    return thin_rays
