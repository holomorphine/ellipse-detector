import cv2
import numpy as np
from defaults import *
from utils import validate_kernel_size


def find_edges(image, aperture_size):
    """Поиск границ объектов методом Кэнни"""
    return cv2.Canny(image, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD, apertureSize=aperture_size)


def apply_bilateral_filter(image, kernel_size, sigma_color, sigma_space):
    """Применяет билатеральный фильтр к изображению"""
    valid_kernel_size = validate_kernel_size(kernel_size)

    return cv2.bilateralFilter(image, valid_kernel_size, sigma_color, sigma_space)


def apply_gaussian_blur(image, kernel_size, sigma_x, sigma_y):
    """Применяет размытие по Гауссу к изображению"""
    valid_kernel_size = validate_kernel_size(kernel_size)

    return cv2.GaussianBlur(image, (valid_kernel_size, valid_kernel_size), sigma_x, sigma_y)


def apply_median_blur(image, kernel_size):
    """Применяет медианный фильтр к изображению"""
    valid_kernel_size = validate_kernel_size(kernel_size)

    return cv2.medianBlur(image, valid_kernel_size)


def apply_morphological_operations(image, kernel_size, iterations, erode, dilate):
    """Применяет морфологические операции (эрозия / дилатация) к изображению"""
    valid_kernel_size = validate_kernel_size(kernel_size)

    kernel = np.ones((valid_kernel_size, valid_kernel_size), np.uint8)

    if erode:
        image = cv2.erode(image, kernel, iterations=iterations)
    if dilate:
        image = cv2.dilate(image, kernel, iterations=iterations)

    return image


def get_threshold_image(image, threshold_value):
    """Возвращает бинарное изображение после пороговой обработки"""
    _, thresholded = cv2.threshold(image, threshold_value, MAX_THRESHOLD, cv2.THRESH_BINARY)

    return thresholded


class ImagePreprocessor:
    def __init__(self, param_manager):
        self.param_manager = param_manager
        self.cached_processed_images = {}
        self.cached_params = {}

    def are_params_changed(self):
        preprocessing_params = self.param_manager.get_parameters_by_category('preprocessing')

        for param_name in preprocessing_params:
            current_value = self.param_manager.get_value(param_name)
            cached_value = self.cached_params.get(param_name)
            
            if current_value != cached_value:
                return True
        
        return False

    def apply_filters(self, image, is_before_gray):
        """Применяет к изображению фильтры, для которых флаг о порядке применения равен is_before_gray"""
        current_image = image.copy()

        if (self.param_manager.get_value('bilateral_enabled') and
                self.param_manager.get_value('bilateral_before_gray') == is_before_gray):
            current_image = apply_bilateral_filter(
                current_image,
                self.param_manager.get_value('bilateral_kernel_size'),
                self.param_manager.get_value('sigma_color'),
                self.param_manager.get_value('sigma_space')
            )

        if (self.param_manager.get_value('gaussian_blur_enabled') and
                self.param_manager.get_value('gaussian_before_gray') == is_before_gray):
            current_image = apply_gaussian_blur(
                current_image,
                self.param_manager.get_value('gaussian_kernel_size'),
                self.param_manager.get_value('gaussian_sigma_x'),
                self.param_manager.get_value('gaussian_sigma_y')
            )

        if (self.param_manager.get_value('median_blur_enabled') and
                self.param_manager.get_value('median_before_gray') == is_before_gray):
            current_image = apply_median_blur(
                current_image,
                self.param_manager.get_value('median_kernel_size')
            )

        return current_image

    def preprocess_image(self, image):
        """Основная функция предобработки изображения"""
        if not self.are_params_changed():
            return (self.cached_processed_images['thresholded'],
                    self.cached_processed_images['edges'])
        
        self.cached_processed_images.clear()
        self.cached_params = self.param_manager.get_all()
        
        current_image = image.copy()

        current_image = self.apply_filters(current_image, True)
        current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
        current_image = self.apply_filters(current_image, False)

        current_image = apply_morphological_operations(
            current_image,
            self.param_manager.get_value('morph_kernel'),
            self.param_manager.get_value('morph_iterations'),
            self.param_manager.get_value('erode'),
            self.param_manager.get_value('dilate')
        )

        thresholded = get_threshold_image(current_image, self.param_manager.get_value('threshold'))
        edges = find_edges(thresholded, self.param_manager.get_value('aperture_size'))

        self.cached_processed_images['thresholded'] = thresholded
        self.cached_processed_images['edges'] = edges

        return thresholded, edges
