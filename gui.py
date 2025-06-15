import os
from tkinter import filedialog, messagebox
from ttkthemes import ThemedStyle
from ellipse_detector import EllipseDetector
from defaults import *
from utils import get_supported_formats, save_image
from parameter_manager import ParameterManager
from gui_helper import *


class EllipseDetectorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Ellipse Detector - Настройки')
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.maxsize(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT)

        self.detector = None
        self.image_windows = {}
        self.current_result_image = None

        self.param_manager = ParameterManager(self)

        self.setup_ui()
        self.status_bar.config(text='Загрузите изображение')

    def create_threshold_section(self, parent):
        frame = create_labeled_frame(parent, 'Пороговая обработка')
        var = self.param_manager.get_parameter_var('threshold')
        callback = self.param_manager.create_step_handler('threshold')

        create_scale_with_label(frame, 'Порог', var,
                                0, MAX_THRESHOLD, callback, width=4)

    def create_canny_section(self, parent):
        frame = create_labeled_frame(parent, 'Детектор границ Canny')
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text='Размер окна:').pack(side=tk.LEFT, padx=(5, 10))

        aperture_options = [('3×3 (детально)', 3), ('5×5 (средне)', 5), ('7×7 (гладко)', 7)]
        aperture_var = self.param_manager.get_parameter_var('aperture_size')
        create_radio_buttons(control_frame, aperture_var,
                             aperture_options, self.param_manager.create_change_handler('aperture_size'))

    def create_morphology_section(self, parent):
        frame = create_labeled_frame(parent, 'Морфологические операции')

        checkboxes_frame = ttk.Frame(frame)
        checkboxes_frame.pack(fill=tk.X, pady=5)

        morph_checkboxes = [
            ('Эрозия', self.param_manager.get_parameter_var('erode'),
             self.param_manager.create_change_handler('erode')),
            ('Дилатация', self.param_manager.get_parameter_var('dilate'),
             self.param_manager.create_change_handler('dilate'))
        ]
        create_checkboxes(checkboxes_frame, morph_checkboxes, side=tk.LEFT)

        kernel_var = self.param_manager.get_parameter_var('morph_kernel')
        kernel_callback = self.param_manager.create_step_handler('morph_kernel')
        iterations_var = self.param_manager.get_parameter_var('morph_iterations')
        iterations_callback = self.param_manager.create_step_handler('morph_iterations')

        create_scale_with_label(frame, 'Размер ядра', kernel_var,
                                1, 21, kernel_callback, width=3)
        create_scale_with_label(frame, 'Итерации', iterations_var,
                                1, 10, iterations_callback, width=3)

    def create_filter_sections(self, parent):
        bilateral_params = [
            ('Размер ядра', self.param_manager.get_parameter_var('bilateral_kernel_size'), 1, 21,
             self.param_manager.create_step_handler('bilateral_kernel_size')),
            ('Sigma Color', self.param_manager.get_parameter_var('sigma_color'), 1, 300,
             self.param_manager.create_step_handler('sigma_color')),
            ('Sigma Space', self.param_manager.get_parameter_var('sigma_space'), 1, 300,
             self.param_manager.create_step_handler('sigma_space'))
        ]

        create_filter_section(
            parent, 'Билатеральный фильтр',
            self.param_manager.get_parameter_var('bilateral_enabled'),
            self.param_manager.get_parameter_var('bilateral_before_gray'),
            self.param_manager.create_change_handler('bilateral_enabled'),
            self.param_manager.create_change_handler('bilateral_before_gray'),
            bilateral_params
        )

        gaussian_params = [
            ('Размер ядра', self.param_manager.get_parameter_var('gaussian_kernel_size'), 1, 21,
             self.param_manager.create_step_handler('gaussian_kernel_size')),
            ('Sigma X', self.param_manager.get_parameter_var('gaussian_sigma_x'), 0.1, 10.0,
             self.param_manager.create_step_handler('gaussian_sigma_x')),
            ('Sigma Y', self.param_manager.get_parameter_var('gaussian_sigma_y'), 0.1, 10.0,
             self.param_manager.create_step_handler('gaussian_sigma_y'))
        ]

        create_filter_section(
            parent, 'Гауссово размытие',
            self.param_manager.get_parameter_var('gaussian_blur_enabled'),
            self.param_manager.get_parameter_var('gaussian_before_gray'),
            self.param_manager.create_change_handler('gaussian_blur_enabled'),
            self.param_manager.create_change_handler('gaussian_before_gray'),
            gaussian_params
        )

        median_params = [
            ('Размер ядра', self.param_manager.get_parameter_var('median_kernel_size'), 1, 21,
             self.param_manager.create_step_handler('median_kernel_size'))
        ]

        create_filter_section(
            parent, 'Медианный фильтр',
            self.param_manager.get_parameter_var('median_blur_enabled'),
            self.param_manager.get_parameter_var('median_before_gray'),
            self.param_manager.create_change_handler('median_blur_enabled'),
            self.param_manager.create_change_handler('median_before_gray'),
            median_params
        )

    def create_filter_parameters(self, parent):
        validation_params = self.param_manager.get_filter_parameters()

        for display_name, min_val, max_val, param_name in validation_params:
            var = self.param_manager.get_parameter_var(param_name)
            callback = self.param_manager.create_step_handler(param_name)

            create_scale_with_label(parent, display_name, var, min_val, max_val, callback)

    def setup_filter_tab(self, parent):
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        error_frame = create_labeled_frame(params_frame, 'Метод подсчета ошибки')
        error_options = [
            ('Алгебраический', 'algebraic'),
            ('Геометрический (метод Ньютона)', 'geometric'),
            ('Геометрический (упрощенный)', 'geometric_simple')
        ]
        error_var = self.param_manager.get_parameter_var('error_method')
        create_radio_buttons(error_frame, error_var,
                             error_options, self.param_manager.create_change_handler('error_method'))

        display_frame = create_labeled_frame(params_frame, 'Опции отображения')
        display_checkboxes = [
            ('Закрасить эллиптические контуры', self.param_manager.get_parameter_var('fill_contours'),
             self.param_manager.create_change_handler('fill_contours')),
            ('Отображать эллипсы', self.param_manager.get_parameter_var('show_ellipses'),
             self.param_manager.create_change_handler('show_ellipses'))
        ]
        create_checkboxes(display_frame, display_checkboxes)

        contour_frame = create_labeled_frame(params_frame, 'Метод выделения контуров')
        contour_options = [('Внешние контуры', 'external'), ('Все контуры', 'list')]
        contour_var = self.param_manager.get_parameter_var('contour_method')
        create_radio_buttons(contour_frame, contour_var,
                             contour_options, self.param_manager.create_change_handler('contour_method'))

        self.create_filter_parameters(params_frame)

    def setup_preprocessing_tab(self, parent):
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=canvas.winfo_width()))

        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.create_threshold_section(scrollable_frame)
        self.create_canny_section(scrollable_frame)
        self.create_morphology_section(scrollable_frame)
        self.create_filter_sections(scrollable_frame)

    def close_image_windows(self):
        for win in list(self.image_windows.values()):
            try:
                if win['window'].winfo_exists():
                    win['window'].destroy()
            except tk.TclError:
                pass
        self.image_windows = {}

    def reset_app_state(self):
        self.close_image_windows()

        self.detector = None
        self.current_result_image = None

        self.ellipse_count_label.config(text='Найдено эллипсов: 0')
        self.status_bar.config(text='Готово к работе')

    def create_window(self, title, width, height, x, y):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry(f"{width + 12}x{height + 12}+{x}+{y}")
        window.resizable(False, False)

        def on_window_close():
            if title == 'Итоговое изображение':
                self.reset_app_state()
            else:
                for name, win_data in list(self.image_windows.items()):
                    if win_data['window'] == window:
                        del self.image_windows[name]
                        break
                window.destroy()

        window.protocol('WM_DELETE_WINDOW', on_window_close)
        label = ttk.Label(window)
        label.pack()
        return {'window': window, 'label': label}

    def create_image_windows(self):
        self.close_image_windows()

        height, width = self.detector.image.shape[:2]
        main_x, main_y, main_width = self.winfo_x(), self.winfo_y(), self.winfo_width()

        windows_config = [
            ('Итоговое изображение', main_x + main_width + 10, main_y, False),
            ('Обработанное изображение', main_x + main_width + 10, main_y, True),
            ('Границы объектов', main_x + main_width + 10, main_y, True)
        ]

        self.image_windows = {}
        for title, x, y, minimize in windows_config:
            window_data = self.create_window(title, width, height, x, y)
            if minimize:
                window_data['window'].iconify()

            key = title.split()[0]
            key_map = {'Итоговое': 'Result', 'Обработанное': 'Processed', 'Границы': 'Edges'}
            self.image_windows[key_map.get(key)] = window_data

    def update_image_window(self, name, cv_img):
        try:
            window_data = self.image_windows.get(name)
            if window_data and window_data['window'].winfo_exists():
                img = cv2_to_tkimage(cv_img)
                window_data['label'].config(image=img)
                window_data['label'].image = img
        except tk.TclError:
            if name in self.image_windows:
                del self.image_windows[name]

    def update_images(self):
        if not self.detector or self.detector.image is None:
            return

        try:
            results = self.detector.find_ellipses()
            ellipses = results['ellipses']
            contours = results['contours']
            thresholded = results['thresholded']
            edges = results['edges']

            self.ellipse_count_label.config(text=f"Найдено эллипсов: {len(ellipses)}")

            self.current_result_image = self.detector.draw_results(
                self.detector.image.copy(), ellipses, contours
            )

            images = {'Result': self.current_result_image, 'Processed': thresholded, 'Edges': edges}
            for name, img in images.items():
                self.update_image_window(name, img)

        except Exception as e:
            messagebox.showerror('Ошибка', f"Ошибка обработки изображения:\n{str(e)}")

    def create_detector(self, image_path):
        try:
            self.detector = EllipseDetector(image_path, self.param_manager)
            self.param_manager.reset_all_parameters()
            self.create_image_windows()
            self.update_images()
            self.status_bar.config(text=f"Загружено изображение: {os.path.basename(image_path)}")
        except Exception as e:
            messagebox.showerror('Ошибка', f"Не удалось загрузить изображение! \n{str(e)}")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=get_supported_formats(), title='Выберите изображение'
        )
        if file_path:
            try:
                self.create_detector(os.path.normpath(file_path))
            except Exception as e:
                self.status_bar.config(text='Ошибка загрузки изображения')
                messagebox.showerror('Ошибка', f"Не удалось загрузить изображение! \n{str(e)}")

    def save_result(self):
        if self.current_result_image is None:
            messagebox.showwarning('Предупреждение', 'Загрузите изображение!')

            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.png', filetypes=get_supported_formats(), title='Сохранить изображение'
        )

        if file_path:
            error_message = save_image(self.current_result_image, file_path)

            if error_message:
                messagebox.showerror('Ошибка', error_message)
            else:
                messagebox.showinfo('Сохранение', 'Файл сохранён!')

    def reset_to_defaults(self):
        if not self.detector:
            messagebox.showwarning('Предупреждение', 'Загрузите изображение!')
            return

        for param_name, config in self.param_manager.parameter_configs.items():
            self.param_manager.set_value(param_name, config['default'])

        self.detector.clear_cache()

        self.update_images()
        self.status_bar.config(text='Параметры сброшены к значениям по умолчанию')

    def setup_common_controls(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)

        buttons = [
            ('Загрузить изображение', self.load_image),
            ('Сохранить изображение', self.save_result),
            ('Сбросить параметры', self.reset_to_defaults)
        ]

        for text, command in buttons:
            ttk.Button(buttons_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

        self.status_bar = ttk.Label(parent, text='Готово к работе', relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_ui(self):
        style = ThemedStyle()
        style.set_theme('scidpurple')

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tab_control = ttk.Notebook(main_frame)
        basic_tab = ttk.Frame(tab_control)
        preprocess_tab = ttk.Frame(tab_control)

        tab_control.add(basic_tab, text='Фильтрация объектов')
        tab_control.add(preprocess_tab, text='Предобработка изображения')
        tab_control.pack(expand=1, fill='both')

        self.ellipse_count_label = ttk.Label(
            main_frame, text='Найдено эллипсов: 0', font=('Helvetica', 10, 'bold')
        )
        self.ellipse_count_label.pack(pady=5)

        self.setup_filter_tab(basic_tab)
        self.setup_preprocessing_tab(preprocess_tab)
        self.setup_common_controls(main_frame)

        ttk.Style().configure('TLabel', padding=5)
        ttk.Style().configure('TScale', padding=5)

    def on_close(self):
        self.close_image_windows()
        self.destroy()

    def parameter_changed(self, param_name):
        if self.detector:
            category = self.param_manager.get_parameter_category(param_name)
            self.detector.update_cache(category)
            self.update_images()


def run_app():
    app = EllipseDetectorApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()


if __name__ == '__main__':
    run_app()
