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
    obs_temp_str = [""] * len(obs_temp)
    obs_per_sector = int(len(obs_temp) / len(angles))

    # Format float observations to int 0 or 1. The last observation
    # is distance which is shown as a float with 2 decimals
    for i in range(obs_per_sector):
        if i == (obs_per_sector - 1):
            obs_temp_str[i::obs_per_sector] = \
                ['%.3f' % elem for elem in obs_temp[i::obs_per_sector]]
        else:
            obs_temp_str[i::obs_per_sector] = \
                ['%.0f' % elem for elem in obs_temp[i::obs_per_sector]]

    obs_string = ""
    for i in range(len(angles)):
        start = i * obs_per_sector
        stop = (i + 1) * obs_per_sector
        obs_string += f'Sector {angles[i]:+>3.0f}\t|\t' \
                      f'{"    ".join(obs_temp_str[start:stop])}\n'

    if include_raw:
        obs_string += f'==== Raw observation\n{obs_temp_str}\n'

    if return_string:
        return expandTab(obs_string)
    else:
        print(obs_string)
        return ""


def expandTab(txt, tabWidth=4):
    """
    Source: https://stackoverflow.com/questions/16052862/how-to-replace-custom-tabs-with-spaces-in-a-string-depend-on-the-size-of-the-ta
    OpenCV's putText() function can't print special characters
    so tab is replaced with correct amount of spaces
    """
    out = []
    for line in txt.split('\n'):
        try:
            while True:
                i = line.index('\t')
                if (tabWidth > 0):
                    pad = " " * (tabWidth - (i % tabWidth))
                else:
                    pad = ""
                line = line.replace("\t", pad, 1)
        except:
            out.append(line)
    return "\n".join(out)


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
