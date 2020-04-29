def get_observations_for_objects(
        robot_point,
        sectors,
        ray_length,
        objects_for_detection):
    """
    local_origo: a Point object of the sectors origo
    angles: Sector angles
    ray_length: Length of the sectors
    objects_for_detection: List of list. Each numpy array contains object
                        coordinates for one type of objects

    Do the cast and assign the hit information for each detectable object.
        sublist[0           ] <- did hit detectableObjects[0]
        ...
        sublist[numObjects-1] <- did hit detectableObjects[numObjects-1]
        sublist[numObjects  ] <- 1 if missed else 0
        sublist[numObjects+1] <- hit fraction (or 1 if no hit)
    """
    observations = []
    for sector in sectors:
        sector_obs = [0] * (len(objects_for_detection) + 2)
        sector_obs[len(sector_obs) - 2] = 1.0

        for active_group_index, object_group in enumerate(objects_for_detection):
            for obj in object_group:
                intersects = sector.intersects(obj)
                if intersects is True:
                    new_dist = robot_point.distance(obj, sector) / ray_length
                    if (
                        new_dist < sector_obs[
                            len(sector_obs) - 1] or
                        sector_obs[len(sector_obs) - 2] > 0
                       ):
                        for i in range(len(objects_for_detection)):
                            sector_obs[i] = 0.0
                        sector_obs[active_group_index] = 1.0
                        sector_obs[len(sector_obs) - 2] = 0.0
                        sector_obs[len(sector_obs) - 1] = new_dist
        observations.extend(sector_obs)
    return observations


def print_observations(
        obs,
        angles,
        return_string=False,
        include_raw=True):
    if obs is None:
        return "No observations"

    obs_temp = obs[:]
    obs_per_sector = int(len(obs_temp) / len(angles))

    # Format float observations to int 0 or 1. The last observation
    # is distance which is shown as a float with 2 decimals
    for i in range(obs_per_sector):
        if i == (obs_per_sector - 1):
            obs_temp[i::obs_per_sector] = \
                ['%.2f' % elem for elem in obs_temp[i::obs_per_sector]]
        else:
            obs_temp[i::obs_per_sector] = \
                ['%.0f' % elem for elem in obs_temp[i::obs_per_sector]]

    obs_string = ""
    for i in range(len(angles)):
        start = i * obs_per_sector
        stop = (i + 1) * obs_per_sector
        obs_string += f'Sector {angles[i]:+>3} | {obs_temp[start:stop]}\n'

    if include_raw:
        obs_string += f'==== Raw observation\n{obs_temp}\n'

    if return_string:
        return obs_string
    else:
        print(obs_string)
        return ""
