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
    if obs:
        obs_temp = obs[:]
        obs_temp[::5] = ['%.0f' % elem for elem in obs_temp[::5]]
        obs_temp[1::5] = ['%.0f' % elem for elem in obs_temp[1::5]]
        obs_temp[2::5] = ['%.0f' % elem for elem in obs_temp[2::5]]
        obs_temp[3::5] = ['%.0f' % elem for elem in obs_temp[3::5]]
        obs_temp[4::5] = ['%.2f' % elem for elem in obs_temp[4::5]]
    obs_string = "==== Sector 0: {} | {}\n".format(
        obs_temp[0:5] if obs_temp else "", angles[0])
    obs_string += "==== Sector 1: {} | {}\n".format(
        obs_temp[5:10] if obs_temp else "", angles[1])
    obs_string += "==== Sector 2: {} | {}\n".format(
        obs_temp[10:15] if obs_temp else "", angles[2])
    obs_string += "==== Sector 3: {} | {}\n".format(
        obs_temp[15:20] if obs_temp else "", angles[3])
    obs_string += "==== Sector 4: {} | {}\n".format(
        obs_temp[20:25] if obs_temp else "", angles[4])
    obs_string += "==== Sector 5: {} | {}\n".format(
        obs_temp[25:30] if obs_temp else"", angles[5])
    obs_string += "==== Sector 6: {} | {}\n".format(
        obs_temp[30:35] if obs_temp else "", angles[6])

    if include_raw:
        obs_string += "==== Raw observation\n{}\n".format(obs_temp)

    if return_string:
        return obs_string
    else:
        print(obs_string)
        return ""
