from ruamel.yaml import YAML


def parse_options(path_to_options_file):
    with open(path_to_options_file, 'r') as f:
        yaml = YAML()
        options = yaml.load(f)
    return options


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
        obs_string += f'Sector {angles[i]:+>3.0f} | {obs_temp[start:stop]}\n'

    if include_raw:
        obs_string += f'==== Raw observation\n{obs_temp}\n'

    if return_string:
        return obs_string
    else:
        print(obs_string)
        return ""


def get_ray_angles(max_angle_per_side, number_of_rays_per_side):
    """
    Creates angles for all observation rays.

    max_angle_per_side : float
        maximum angle to each side for the observation rays

    number_of_rays_per_side : int
        Number of rays on each side. Total amount of rays is
        2 x number_of_rays_per_side + 1
        The +1 ray is the ray directly forward

    return : list(float)
        list of angles from left (positive angles) to
        right (negative angles)
    """
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
