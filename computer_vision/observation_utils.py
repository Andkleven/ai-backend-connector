import shapely
from shapely.geometry import LineString, Point, Polygon


def get_observations_for_objects(
        local_origo,
        angles,
        ray_length,
        object_lines):
    """
    local_origo: a Point object of the sectors origo
    angles: Sector angles
    ray_length: Length of the sectors
    object_lines: List of list. Each numpy array contains object
                        coordinates for one type of objects
    """
    perceptions = []
    local_origo = Point(local_origo[0], local_origo[1])
    sector_vectors = _create_sector_vectors(local_origo, angles, ray_length)
    # lines_per_type = create_object_lines(object_line_coordinates)

    for sector_vector in sector_vectors:
        sector_perceptions = [0] * (len(object_lines) + 2)
        sector_perceptions[len(sector_perceptions) - 2] = 1.0

        active_group_index = 0
        for lines_of_one_type in object_lines:
            for line in lines_of_one_type:
                intersects = line.intersects(sector_vector)
                if intersects is True:
                    intersect_point = line.intersection(sector_vector)
                    new_dist = \
                        intersect_point.distance(local_origo) / ray_length
                    if (
                        new_dist < sector_perceptions[
                            len(sector_perceptions) - 1] or
                        sector_perceptions[len(sector_perceptions) - 2] > 0
                       ):
                        for i in range(len(object_lines)):
                            sector_perceptions[i] = 0.0
                        sector_perceptions[active_group_index] = 1.0
                        sector_perceptions[len(sector_perceptions) - 2] = 0.0
                        sector_perceptions[len(sector_perceptions) - 1] = \
                            new_dist
            active_group_index += 1
        perceptions.extend(sector_perceptions)
    return perceptions
