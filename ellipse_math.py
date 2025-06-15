import numpy as np
import cv2
from numpy import linalg
from defaults import *


def close_contour_at_border(contour, image_shape):
    """Возвращает замкнутый на границе изображение контур"""
    height, width = image_shape
    mask = np.zeros((height, width), dtype=np.uint8)

    mask[0, :-1] = 255
    mask[-1, :] = 255
    mask[:-1, 0] = 255
    mask[:-1, -1] = 255

    cv2.drawContours(mask, [contour], FILL_ALL_CONTOURS, (255, 255, 255), FILL_ALL_CONTOURS)
    new_contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    if new_contours:
        max_contour_area = (height * width) * MAX_CONTOUR_AREA_RATIO
        filtered_contours = [c for c in new_contours if cv2.contourArea(c) < max_contour_area]
        
        if filtered_contours:
            return max(filtered_contours, key=cv2.contourArea)
    
    return contour


def calculate_ellipse_area_in_bounds(center, axes, angle, image_shape):
    """Возвращает площадь эллипса в границах изображения"""
    mask = np.zeros((image_shape[0], image_shape[1]), dtype=np.uint8)
    cv2.ellipse(mask, center, axes,
                angle, 0, 360, (255, 255, 255), -1)

    return np.count_nonzero(mask)


def calculate_contour_area(contour, image_shape):
    """Возвращает площадь контура, предварительно замкнув его на границе"""
    closed_contour = close_contour_at_border(contour, image_shape)

    return cv2.contourArea(closed_contour)


def calc_xy_sums(x, y):
    return {
        'x4': np.sum(x ** 4), 'x3': np.sum(x ** 3), 'x2': np.sum(x ** 2), 'x': np.sum(x),
        'y4': np.sum(y ** 4), 'y3': np.sum(y ** 3), 'y2': np.sum(y ** 2), 'y': np.sum(y),
        'x3y': np.sum(x ** 3 * y), 'xy3': np.sum(x * y ** 3), 'x2y2': np.sum(x ** 2 * y ** 2),
        'x2y': np.sum(x ** 2 * y), 'xy2': np.sum(x * y ** 2), 'xy': np.sum(x * y), 'n': len(x)
    }


def make_matrix_a(sums):
    return np.array([
        [sums['x4'], sums['x3y'], sums['x2y2'], sums['x3'], sums['x2y'], sums['x2']],
        [sums['x3y'], sums['x2y2'], sums['xy3'], sums['x2y'], sums['xy2'], sums['xy']],
        [sums['x2y2'], sums['xy3'], sums['y4'], sums['xy2'], sums['y3'], sums['y2']],
        [sums['x3'], sums['x2y'], sums['xy2'], sums['x2'], sums['xy'], sums['x']],
        [sums['x2y'], sums['xy2'], sums['y3'], sums['xy'], sums['y2'], sums['y']],
        [sums['x2'], sums['xy'], sums['y2'], sums['x'], sums['y'], sums['n']]
    ])


def make_matrix_b():
    return np.array([
        [0, 0, 2, 0, 0, 0],
        [0, -1, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ])


def get_approximation_ellipse(x, y):
    """Возвращает эллипсе, аппроксимирующий заданный набор точек методом наименьших квадратов"""
    sums = calc_xy_sums(x, y)
    matrix_a = make_matrix_a(sums)
    matrix_b = make_matrix_b()

    if np.abs(linalg.det(matrix_a)) < DETERMINANT_MIN_ERROR:
        return None

    try:
        result_matrix = linalg.inv(matrix_a) @ matrix_b
    except linalg.LinAlgError:
        return None

    eigenvalues, eigenvectors = linalg.eig(result_matrix)
    eigenvectors = eigenvectors.transpose()

    for i in range(len(eigenvalues)):
        eigenvalue = np.real(eigenvalues[i])
        if eigenvalue > EIGENVALUE_THRESHOLD:
            temp = eigenvectors[i] @ (matrix_a @ eigenvectors[i]) * eigenvalues[i]
            if temp < 0:
                break

            multiplier = 1 / np.sqrt(temp)

            return eigenvectors[i] * multiplier

    return None


def get_ellipse_geometric_params(coefficients):
    """Возвращает словарь с основными геометрическими параметрами эллипса по его коэффициентам"""
    a, b, c, d, e, f = np.real(coefficients)

    theta_rad = np.arctan2(-b, c - a) / 2
    if not np.isreal(theta_rad):
        return None

    theta_degrees = np.rad2deg(float(np.real(theta_rad)))

    sqr_val = (a - c) ** 2 + b ** 2
    if sqr_val < 0:
        return None

    sqrt_val = np.sqrt(sqr_val)
    common_factor = 2 * (a * e ** 2 + c * d ** 2 - b * d * e + (b ** 2 - 4 * a * c) * f)
    
    a_sqr_val = common_factor * ((a + c) + sqrt_val)
    b_sqr_val = common_factor * ((a + c) - sqrt_val)
    if a_sqr_val < 0 or b_sqr_val < 0:
        return None

    denominator = b ** 2 - 4 * a * c
    a_axis = -np.sqrt(a_sqr_val) / denominator
    b_axis = -np.sqrt(b_sqr_val) / denominator

    if not all(np.isreal([a_axis, b_axis])):
        return None

    x0 = (2 * c * d - b * e) / denominator
    y0 = (2 * a * e - b * d) / denominator

    if not all(np.isreal([x0, y0])):
        return None

    return {
        'center': (float(np.real(x0)), float(np.real(y0))),
        'axes': (float(np.real(a_axis)), float(np.real(b_axis))),
        'angle': theta_degrees
    }


def calculate_error_algebraic(coefficients, x, y):
    """Вычисляет алгебраическую ошибку аппроксимации набора точек эллипсом"""
    a, b, c, d, e, f = coefficients
    total_error = 0.0
    
    for i in range(len(x)):
        ellipse_value = a * x[i] ** 2 + b * x[i] * y[i] + c * y[i] ** 2 + d * x[i] + e * y[i]
        total_error += np.abs(ellipse_value + f) / (np.abs(ellipse_value) + np.abs(f))

    return total_error / len(x)


def get_rotated_point(x, y, center, angle):
    dx = x - center[0]
    dy = y - center[1]

    x_rotated = dx * np.cos(angle) + dy * np.sin(angle)
    y_rotated = -dx * np.sin(angle) + dy * np.cos(angle)

    return x_rotated, y_rotated


def get_distance_to_ellipse_newton(x, y, a, b):
    """Возвращает расстояние от точки до эллипса, рассчитанное методом Ньютона"""
    if x == 0 and y == 0:
        return min(a, b)

    t = np.arctan2(y, x)

    for i in range(NEWTON_MAX_ITERATIONS):
        cos_t = np.cos(t)
        sin_t = np.sin(t)

        x_ellipse = a * cos_t
        y_ellipse = b * sin_t

        dx_dt = -a * sin_t
        dy_dt = b * cos_t

        f = (x_ellipse - x) * dx_dt + (y_ellipse - y) * dy_dt

        df_dt = dx_dt ** 2 + dy_dt ** 2 + (x_ellipse - x) * (-a * cos_t) + (y_ellipse - y) * (-b * sin_t)

        if abs(f) < NEWTON_ACCURACY:
            break

        t = t - f / df_dt

    x_ellipse = a * np.cos(t)
    y_ellipse = b * np.sin(t)

    return np.sqrt((x - x_ellipse) ** 2 + (y - y_ellipse) ** 2)


def calculate_error_geometric_newton(center, axes, angle, x, y):
    """Вычисляет геометрическую ошибку аппроксимации набора точек эллипсом"""
    a, b = axes

    total_distance = 0.0
    angle_rad = np.radians(angle)
    
    for i in range(len(x)):
        x_rotated, y_rotated = get_rotated_point(x[i], y[i], center, angle_rad)
        total_distance += get_distance_to_ellipse_newton(x_rotated, y_rotated, a, b)

    return total_distance * GEOMETRIC_ERROR_SCALE_MULTIPLIER / (np.sqrt(a ** 2 + b ** 2) * len(x))


def calculate_error_geometric_simple(center, axes, angle, x, y):
    """Вычисляет упрощенную геометрическую ошибку аппроксимации набора точек эллипсом"""
    a, b = axes
    
    total_distance = 0.0
    angle_rad = np.radians(angle)
    
    for i in range(len(x)):
        x_rotated, y_rotated = get_rotated_point(x[i], y[i], center, angle_rad)
        distance = np.sqrt((x_rotated / a) ** 2 + (y_rotated / b) ** 2)
        total_distance += abs(distance - 1.0) / (distance + 1.0)

    return total_distance * GEOMETRIC_ERROR_SCALE_MULTIPLIER / len(x)
