# Цвета
ELLIPSE_COLOR = (0, 0, 255)
CONTOUR_COLOR = (0, 255, 0)
FILL_COLOR = (0, 255, 0)

# Толщина отображения эллипсов и контуров
ELLIPSE_THICKNESS = 2
CONTOUR_THICKNESS = 1

# Математические параметры
NEWTON_ACCURACY = 1e-5
NEWTON_MAX_ITERATIONS = 20
EIGENVALUE_THRESHOLD = 1e-10
DETERMINANT_MIN_ERROR = 1e-3
GEOMETRIC_ERROR_SCALE_MULTIPLIER = 0.01

# Размер изображений
RESIZE_WIDTH = 600

# Размеры окна настроек
MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 700
MAX_WINDOW_WIDTH = 1000
MAX_WINDOW_HEIGHT = 1200

# Параметры предобработки изображения
CANNY_LOW_THRESHOLD = 50
CANNY_HIGH_THRESHOLD = 150
MAX_THRESHOLD = 255
MAX_CONTOUR_AREA_RATIO = 0.8
MIN_KERNEL_SIZE = 1

# Углы для отрисовки эллипсов
ELLIPSE_START_ANGLE = 0
ELLIPSE_END_ANGLE = 360

# Для заливки контуров
FILL_ALL_CONTOURS = -1

# Настраиваемые параметры
CONFIGURABLE_PARAMS = {
    # Фильтрация эллипсов
    'error_exponent': {
        'default': 4.0,
        'type': 'double',
        'min': 1.0,
        'max': 20.0,
        'step': 1.0,
        'display_name': 'Error Exponent',
        'category': 'filter'
    },
    'error_factor': {
        'default': 1.0,
        'type': 'double',
        'min': 1.0,
        'max': 9.0,
        'step': 0.1,
        'display_name': 'Error Factor',
        'category': 'filter'
    },
    # Минимальная площадь эллипса
    'min_area': {
        'default': 50.0,
        'type': 'double',
        'min': 0.0,
        'max': 20000.0,
        'step': 10.0,
        'display_name': 'Min Area',
        'category': 'filter'
    },
    # Максимальное отношение большей полуоси к меньшей
    'max_aspect_ratio': {
        'default': 2.0,
        'type': 'double',
        'min': 0.0,
        'max': 20.0,
        'step': 0.1,
        'display_name': 'Max Aspect Ratio',
        'category': 'filter'
    },
    # Относительная ошибка площади эллипса и площади контура
    'area_error': {
        'default': 0.0,
        'type': 'double',
        'min': 0.0,
        'max': 5.0,
        'step': 0.01,
        'display_name': 'Area Error',
        'category': 'filter'
    },
    'error_method': {
        'default': 'algebraic',
        'type': 'string',
        'options': ['algebraic', 'geometric', 'geometric_simple'],
        'category': 'filter'
    },
    # Отображение
    'fill_contours': {
        'default': False,
        'type': 'boolean',
        'category': 'display'
    },
    'show_ellipses': {
        'default': True,
        'type': 'boolean',
        'category': 'display'
    },
    'contour_method': {
        'default': 'external',
        'type': 'string',
        'options': ['external', 'list'],
        'category': 'preprocessing'
    },
    # Предобработка изображения
    'threshold': {
        'default': 50,
        'type': 'int',
        'min': 0,
        'max': 255,
        'step': 1.0,
        'category': 'preprocessing'
    },
    'erode': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'dilate': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'morph_kernel': {
        'default': 3,
        'type': 'int',
        'min': 1,
        'max': 21,
        'step': 2.0,
        'category': 'preprocessing'
    },
    'morph_iterations': {
        'default': 1,
        'type': 'int',
        'min': 1,
        'max': 10,
        'step': 1.0,
        'category': 'preprocessing'
    },
    'aperture_size': {
        'default': 3,
        'type': 'int',
        'options': [3, 5, 7],
        'category': 'preprocessing'
    },
    'bilateral_enabled': {
        'default': True,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'bilateral_before_gray': {
        'default': True,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'bilateral_kernel_size': {
        'default': 5,
        'type': 'int',
        'min': 1,
        'max': 21,
        'step': 2.0,
        'category': 'preprocessing'
    },
    'sigma_color': {
        'default': 175,
        'type': 'int',
        'min': 1,
        'max': 300,
        'step': 1.0,
        'category': 'preprocessing'
    },
    'sigma_space': {
        'default': 175,
        'type': 'int',
        'min': 1,
        'max': 300,
        'step': 1.0,
        'category': 'preprocessing'
    },
    'gaussian_blur_enabled': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'gaussian_before_gray': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'gaussian_kernel_size': {
        'default': 5,
        'type': 'int',
        'min': 1,
        'max': 21,
        'step': 2.0,
        'category': 'preprocessing'
    },
    'gaussian_sigma_x': {
        'default': 1.0,
        'type': 'double',
        'min': 0.1,
        'max': 10.0,
        'step': 0.1,
        'category': 'preprocessing'
    },
    'gaussian_sigma_y': {
        'default': 1.0,
        'type': 'double',
        'min': 0.1,
        'max': 10.0,
        'step': 0.1,
        'category': 'preprocessing'
    },
    'median_blur_enabled': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'median_before_gray': {
        'default': False,
        'type': 'boolean',
        'category': 'preprocessing'
    },
    'median_kernel_size': {
        'default': 5,
        'type': 'int',
        'min': 1,
        'max': 21,
        'step': 2.0,
        'category': 'preprocessing'
    }
}
