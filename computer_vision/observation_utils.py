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
                    new_dist = robot_point.distance(obj) / ray_length
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
        return_string=False,
        include_raw=True):
    if obs:
        obs[::5] = ['%.0f' % elem for elem in obs[::5]]
        obs[1::5] = ['%.0f' % elem for elem in obs[1::5]]
        obs[2::5] = ['%.0f' % elem for elem in obs[2::5]]
        obs[3::5] = ['%.0f' % elem for elem in obs[3::5]]
        obs[4::5] = ['%.2f' % elem for elem in obs[4::5]]
    obs_string = "==== Sector 0: {} | 90 right\n".format(
        obs[0:5] if obs else "")
    obs_string += "==== Sector 1: {} | 45 right\n".format(
        obs[5:10] if obs else "")
    obs_string += "==== Sector 2: {} | 20 right\n".format(
        obs[10:15] if obs else "")
    obs_string += "==== Sector 3: {} | forward\n".format(
        obs[15:20] if obs else "")
    obs_string += "==== Sector 4: {} | 20 left\n".format(
        obs[20:25] if obs else "")
    obs_string += "==== Sector 5: {} | 45 left\n".format(
        obs[25:30] if obs else"")
    obs_string += "==== Sector 6: {} | 90 left\n".format(
        obs[30:35] if obs else "")

    if include_raw:
        obs_string += "==== Raw observation\n{}\n".format(obs)

    if return_string:
        return obs_string
    else:
        print(obs_string)
        return ""