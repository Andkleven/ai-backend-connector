import numpy as np
import cv2
import shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry import CAP_STYLE, JOIN_STYLE

LINE_THICKNESS = 2
LINE_COLOR = (0, 255, 255)


class GameObject():
    def __init__(self, coordinates, line_color, buffer_distance=0, name=""):
        self._coordinates = coordinates
        self._line_color = line_color
        self._buffer_distance = buffer_distance
        self._name = name

        # print(f'Name {name}\n')
        # print(f'Coords {coordinates}\n')
        if len(self._coordinates) is 0:
            raise Exception("No coordinates given to the new game object.")
        elif len(self._coordinates) is 1:
            self._geometry = Point(self._coordinates[0])
            cap_style = CAP_STYLE.round
        elif len(self._coordinates) is 2:
            self._geometry = LineString(self._coordinates)
            cap_style = CAP_STYLE.square
        else:
            self._geometry = Polygon(self._coordinates)

        if self._buffer_distance > 0:
            # Create a circle from the point by calling the buffer method
            self._geometry = self._geometry.buffer(
                self._buffer_distance,
                cap_style=cap_style)
            self._coordinates = np.array(
                [self._geometry.exterior.coords],
                np.int32)

    def draw_object_on_image(self, image):
        '''
        Draw objects boundaries to the given image. Remember to call
        "cv2.imshow" and  "cv2.waitKey"-functions after drawing all the
        objects you want.
        '''
        if isinstance(self._geometry, Point):
            # Highlight single point with a bigger point on image
            line_thickness = LINE_THICKNESS + 10
        else:
            line_thickness = LINE_THICKNESS
        pts = np.array([self._coordinates], np.int32)
        pts = pts.reshape((-1, 1, 2))
        # print(f'pts: {pts}')
        cv2.polylines(image, [pts], True, self._line_color, line_thickness)

    @property
    def geometry(self):
        return self._geometry

    @property
    def coords(self):
        return self._geometry.coords

    def distance(self, other_game_object, sector):
        hit_point = sector.geometry.intersection(other_game_object.geometry)
        return self._geometry.distance(hit_point)

    def intersects(self, other_game_object):
        return self._geometry.intersects(other_game_object.geometry)
