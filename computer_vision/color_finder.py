import cv2
import numpy as np


def main():
    image = cv2.imread("/home/ubuntuman/Desktop/ball.png")
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color = hsv_image[30, 30]
    color = np.reshape(color, (1, 1, 3))
    print(f'HSV color code: {color}')
    # cv2.imwrite("/home/ubuntuman/Desktop/ball_color_HSV.png", color)
    cv2.imshow("cropped", color)
    cv2.waitKey(5000)


if __name__ == "__main__":
    main()
