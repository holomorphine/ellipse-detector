from ellipse_math import *
from image_preprocessing import ImagePreprocessor
from utils import load_image, find_contours


def close_contours_at_border(contours, image_shape):
    """Замыкание всех незамкнутых на границе контуров"""
    if not contours:
        return []

    return [close_contour_at_border(contour, image_shape) for contour in contours]


def calculate_ellipse_error(ellipse, error_method):
    """Вычисление ошибки аппроксимации контура эллипсом с помощью указанного метода"""
    if error_method == 'geometric':
        return calculate_error_geometric_newton(ellipse['center'],
                                                ellipse['axes'],
                                                ellipse['angle'],
                                                ellipse['x_coordinates'],
                                                ellipse['y_coordinates'])
    elif error_method == 'geometric_simple':
        return calculate_error_geometric_simple(ellipse['center'],
                                                ellipse['axes'],
                                                ellipse['angle'],
                                                ellipse['x_coordinates'],
                                                ellipse['y_coordinates'])
    else:
        return calculate_error_algebraic(ellipse['coefficients'],
                                         ellipse['x_coordinates'],
                                         ellipse['y_coordinates'])


class EllipseDetector:
    def __init__(self, image_path, param_manager):
        self.image = load_image(image_path)
        self.param_manager = param_manager
        self.preprocessor = ImagePreprocessor(self.param_manager)

        self.cached_contours = None
        self.cached_ellipses = None
        self.cached_contour_params = None
        self.cached_errors = {
            'algebraic': None,
            'geometric': None,
            'geometric_simple': None
        }

    def clear_cache(self):
        self.cached_contours = None
        self.cached_ellipses = None
        self.cached_contour_params = None
        self.cached_errors = {'algebraic': None, 'geometric': None, 'geometric_simple': None}

    def update_cache(self, param_category):
        if param_category == 'preprocessing':
            self.clear_cache()

    def get_errors(self, error_method):
        """Возвращает массив ошибок для указанного метода"""
        if not self.param_manager.get_value('show_ellipses'):
            return []

        if self.cached_errors[error_method]:
            return self.cached_errors[error_method]

        errors = []
        for ellipse in self.cached_ellipses:
            error = calculate_ellipse_error(ellipse, error_method)
            errors.append(error)
        self.cached_errors[error_method] = errors

        return errors

    def get_ellipse_from_contour(self, contour):
        """Возвращает словарь со всеми основными параметрами эллипса и контура, который он аппроксимирует,
        по заданному контуру"""
        points = contour.squeeze()
        if len(points) < 5:
            return None

        x = points[:, 0].astype(np.float64)
        y = points[:, 1].astype(np.float64)
        coefficients = get_approximation_ellipse(x, y)

        if coefficients is None:
            return None

        ellipse_params = get_ellipse_geometric_params(coefficients)
        if ellipse_params is None:
            return None

        ellipse_area = np.pi * ellipse_params['axes'][0] * ellipse_params['axes'][1]
        height, width = self.image.shape[:2]
        contour_area = calculate_contour_area(contour, (height, width))

        return {
            'int_center': (int(ellipse_params['center'][0]), int(ellipse_params['center'][1])),
            'int_axes': (int(ellipse_params['axes'][0]), int(ellipse_params['axes'][1])),
            'center': ellipse_params['center'],
            'axes': ellipse_params['axes'],
            'angle': ellipse_params['angle'],
            'ellipse_area': ellipse_area,
            'contour_area': contour_area,
            'contour': contour,
            'coefficients': coefficients,
            'x_coordinates': x,
            'y_coordinates': y,
        }

    def is_ellipse_valid(self, ellipse, error):
        """Проверка, удовлетворяет ли переданный эллипс (и контур) параметрам фильтрации эллиптических объектов"""
        error_factor = self.param_manager.get_value('error_factor')
        error_exponent = self.param_manager.get_value('error_exponent')
        max_error = error_factor / (10 ** int(error_exponent))

        if error > max_error:
            return False

        min_area = self.param_manager.get_value('min_area')
        if ellipse['ellipse_area'] < min_area:
            return False

        max_aspect_ratio = self.param_manager.get_value('max_aspect_ratio')
        if max_aspect_ratio > 0:
            a_axis, b_axis = ellipse['axes']
            if a_axis == 0 or b_axis == 0:
                return False

            ratio = max(a_axis, b_axis) / min(a_axis, b_axis)
            if ratio > max_aspect_ratio:
                return False

        area_error = self.param_manager.get_value('area_error')
        if area_error > 0:
            height, width = self.image.shape[:2]
            contour_area = ellipse['contour_area']
            ellipse_area_in_image = calculate_ellipse_area_in_bounds(
                ellipse['int_center'], ellipse['int_axes'], ellipse['angle'], (height, width))

            if contour_area == 0 or ellipse_area_in_image == 0:
                return False

            area_diff = abs(contour_area - ellipse_area_in_image) / contour_area
            if area_diff > area_error:
                return False

        return True

    def find_ellipses(self):
        """Возвращает словарь со всеми валидными эллипсами и контурами объектов, предобработанное изображение и
        изображение с границами объектов"""
        if self.image is None:
            return {
                'ellipses': [],
                'contours': [],
                'thresholded': None,
                'edges': None
            }

        thresholded, edges = self.preprocessor.preprocess_image(self.image)
        if edges is None:
            return {
                'ellipses': [],
                'contours': [],
                'thresholded': thresholded,
                'edges': edges
            }

        if self.cached_contours is None:
            contour_method = self.param_manager.get_value('contour_method')
            self.cached_contours = find_contours(edges, contour_method)

        contours = self.cached_contours

        valid_ellipses = []
        if self.param_manager.get_value('show_ellipses'):
            if self.cached_ellipses is None:
                all_ellipses = []
                for contour in contours:
                    ellipse = self.get_ellipse_from_contour(contour)
                    if ellipse:
                        all_ellipses.append(ellipse)

                self.cached_ellipses = all_ellipses
            else:
                all_ellipses = self.cached_ellipses

            error_method = self.param_manager.get_value('error_method')
            errors = self.get_errors(error_method)

            for i, ellipse in enumerate(all_ellipses):
                if i < len(errors):
                    if self.is_ellipse_valid(ellipse, errors[i]):
                        valid_ellipses.append(ellipse)

        return {
            'ellipses': valid_ellipses,
            'contours': contours,
            'thresholded': thresholded,
            'edges': edges
        }

    def draw_results(self, image, ellipses, contours):
        result_image = image.copy()

        if self.param_manager.get_value('fill_contours') and ellipses:
            valid_contours = [ellipse['contour'] for ellipse in ellipses]
            if valid_contours:
                height, width = result_image.shape[:2]
                closed_contours = close_contours_at_border(valid_contours, (height, width))
                cv2.drawContours(result_image, closed_contours, -1, FILL_COLOR, FILL_ALL_CONTOURS)

        cv2.drawContours(result_image, contours, -1, CONTOUR_COLOR, CONTOUR_THICKNESS)
        if self.param_manager.get_value('show_ellipses') and ellipses:
            for ellipse in ellipses:
                cv2.ellipse(result_image, ellipse['int_center'], ellipse['int_axes'],
                            ellipse['angle'], ELLIPSE_START_ANGLE, ELLIPSE_END_ANGLE, ELLIPSE_COLOR, ELLIPSE_THICKNESS)

        return result_image
