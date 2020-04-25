'''
Module for geometric calculation functions
'''
import shapely
from shapely.geometry import LineString, Point, Polygon
from math import cos
from math import sin
from math import pi


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


def create_sectors(local_origo, angles, ray_length):
    sector_vectors = _create_sector_vectors(local_origo, angles, ray_length)
    sector_points_array = []
    sectors = []

    for i in range(len(sector_vectors) - 1):
        sector_points_array.append([
            local_origo.coords[0],
            sector_vectors[i].coords[1],
            sector_vectors[i + 1].coords[1]])

    for sector_points in sector_points_array:
        sectors.append(Polygon(sector_points))

    return sectors


def get_ray_angles(robot_rotation, angles):
    local_rotation = robot_rotation - 90
    ray_angles = angles
    for i in range(len(ray_angles)):
        ray_angles[i] = ray_angles[i] - local_rotation + 90

    return ray_angles
