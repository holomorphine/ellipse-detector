import os
import cv2
from defaults import RESIZE_WIDTH, MIN_KERNEL_SIZE


def find_contours(edges, method):
    if method == 'external':
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    else:
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    return contours


def validate_kernel_size(kernel_size):
    if kernel_size <= MIN_KERNEL_SIZE:
        return MIN_KERNEL_SIZE

    return kernel_size + 1 if kernel_size % 2 == 0 else kernel_size


def resize_image(image):
    if image.shape[1] > RESIZE_WIDTH:
        height, width = image.shape[:2]
        aspect_ratio = height / width
        new_height = int(RESIZE_WIDTH * aspect_ratio)
        return cv2.resize(image, (RESIZE_WIDTH, new_height))
    return image


def load_image(path):
    if not (os.path.exists(path) and is_valid_image_extension(path)):
        return None

    image = cv2.imread(path)
    return resize_image(image)


def is_valid_image_extension(path):
    extension = os.path.splitext(path)[1].lower()
    return extension in ['.jpg', '.jpeg', '.png', '.bmp']


def save_image(image, path):
    try:
        extension = os.path.splitext(path)[1].lower()
        success, encoded_image = cv2.imencode(extension, image)
        if success:
            encoded_image.tofile(path)
            return ''
        return 'При сохранении возникла ошибка!'
    except:
        return 'При сохранении возникла ошибка!'


def convert_bgr_to_rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def get_supported_formats():
    return [
        ('Изображения', '*.jpg *.jpeg *.png *.bmp'),
        ('JPEG', '*.jpg *.jpeg'),
        ('PNG', '*.png'),
        ('BMP', '*.bmp'),
    ]
