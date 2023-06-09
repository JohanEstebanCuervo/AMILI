import os
import numpy as np
import cv2
import matplotlib.pyplot as plt


def detect_spectralon(direction, imshow=False) -> np.ndarray:
    """
    Genera la mascara del spectralon

    Args:
        direction (_type_): _description_
        imshow (bool, optional): True,False or 'end'. Defaults to False.

    Raises:
        ValueError: _description_

    Returns:
        np.ndarray: _description_
    """
    image = cv2.imread(direction, cv2.IMREAD_GRAYSCALE)
    mask = np.zeros_like(image)

    if imshow is True:
        plt.imshow(image, vmin=0, vmax=255)
        plt.show()

    # _, image2 = cv2.threshold(image, 245, 255, cv2.THRESH_BINARY)
    _, image2 = cv2.threshold(image, 120, 255, cv2.THRESH_OTSU)

    if imshow is True:
        plt.imshow(image2, vmin=0, vmax=255)
        plt.show()

    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype("uint8")

    image2 = cv2.erode(image2, kernel, iterations=3)

    if imshow is True:
        plt.imshow(image2, vmin=0, vmax=255)
        plt.show()

    image2 = cv2.Canny(image2, 100, 200)

    if imshow is True:
        plt.imshow(image2, vmin=0, vmax=255)
        plt.show()

    image2 = cv2.dilate(image2, kernel, iterations=3)

    if imshow is True:
        plt.imshow(image2, vmin=0, vmax=255)
        plt.show()

    circles = cv2.HoughCircles(
        image2,
        cv2.HOUGH_GRADIENT,
        1,
        70,
        param1=50,
        param2=20,
        minRadius=0,
        maxRadius=0,
    )

    if circles is None:
        raise ValueError("No se encontraron Circulos en la imagen")

    if imshow is True:
        src = image.copy()
        for i in circles[0, :]:
            center = (int(i[0]), int(i[1]))
            # circle center
            cv2.circle(src, center, 1, (0, 0, 0), 3)
            # circle outline
            radius = int(i[2] * 0.8)
            cv2.circle(src, center, radius, (0, 0, 0), 3)

        plt.imshow(src, vmin=0, vmax=255)
        plt.show()

    circles = circles[0]
    max_radio = -1
    for cir in circles:
        if max_radio < cir[2]:
            max_radio = cir[2]
            circle = cir

    print(circle)
    mask = cv2.circle(
        mask,
        (int(circle[0]), int(circle[1])),
        int(circle[2] * 0.8),
        (255, 255, 255),
        -1,
    )

    if imshow:
        plt.imshow(mask, vmin=0, vmax=255)
        plt.show()

    return mask


def check_median(direction: str, mask: np.ndarray, ideal_value: int = 255):
    """
    Calcula la media de el circulo mayor detectado en la captura
    de una imagen
    """
    image = cv2.imread(direction, cv2.IMREAD_GRAYSCALE)
    median_value = np.mean(np.array(image[np.where(mask == 255)]).astype(float))

    if median_value < ideal_value:
        src = image + mask
        cv2.imwrite("pruebas/" + os.path.basename(direction), src)

    return median_value
