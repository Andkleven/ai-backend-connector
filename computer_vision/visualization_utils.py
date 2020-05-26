import cv2

from computer_vision.game_object import GameObject
from computer_vision.observation_utils import print_observations


BLUE = (255, 0, 0)
RED = (0, 0, 255)

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2
FONT_DEFAULT_COLOR = RED


def visualize_game_arena(image, wall_objects, goal_objects):
    visualize_item(image, *wall_objects)
    visualize_item(image, *goal_objects)


def visualize_observations(lower_obs, upper_obs, angles, sectors, image):
    visualize_item(image, *sectors)

    lower_obs_str = print_observations(
        lower_obs,
        angles,
        return_string=True,
        include_raw=False)
    lower_obs_str = \
        'Lower obs\n| Ball | Goal | Wall | Nothing | Distance |\n' \
        f'{lower_obs_str}'
    visualize_item(
        image,
        lower_obs_str,
        text_pos=(50, 50),
        text_color=BLUE)

    # upper_obs_str = print_observations(
    #     upper_obs,
    #     angles,
    #     return_string=True,
    #     include_raw=False)
    # upper_obs_str = \
    #     'Upper obs\n| Ball | Goal | Wall | Nothing | Distance |\n' \
    #     f'{upper_obs_str}'
    # visualize_item(
    #     image,
    #     upper_obs_str,
    #     text_pos=(50, 350),
    #     text_color=BLUE)


def show_visualizations(image):
    cv2.imshow('Game', image)
    cv2.waitKey(1)


def visualize_item(image, *args, **kwargs):
    for item in args:
        if isinstance(item, GameObject):
            filled = False
            override_color = None
            if 'filled' in kwargs:
                filled = kwargs['filled']
            if 'override_color' in kwargs:
                override_color = kwargs['override_color']
            item.draw_object_on_image(
                image=image,
                override_color=override_color,
                filled=filled)
        elif isinstance(item, str):
            if 'text_color' in kwargs:
                text_color = kwargs['text_color']
            else:
                text_color = FONT_DEFAULT_COLOR
            for i, line in enumerate(item.split('\n')):
                x = kwargs['text_pos'][0]
                y0 = kwargs['text_pos'][1]
                dy = 25
                y = y0 + i*dy
                cv2.putText(
                    image, line, (x, y), FONT, FONT_SCALE,
                    text_color, FONT_THICKNESS)
