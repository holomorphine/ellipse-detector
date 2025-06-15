import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils import convert_bgr_to_rgb


def cv2_to_tkimage(cv_image):
    rgb_img = convert_bgr_to_rgb(cv_image)
    return ImageTk.PhotoImage(Image.fromarray(rgb_img))


def create_labeled_frame(parent, text):
    frame = ttk.LabelFrame(parent, text=text)
    frame.pack(fill=tk.X, pady=5)
    return frame


def create_scale_with_label(parent, text, variable, min_val, max_val,
                            callback=None, width=5, use_grid=False, row=0, col=0):
    if use_grid:
        frame = parent
        ttk.Label(frame, text=f"{text}:").grid(row=row, column=col, sticky='w', padx=(0, 5))

        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=variable)
        if callback:
            scale.configure(command=callback)
        scale.grid(row=row, column=col+1, sticky='ew', padx=5)

        ttk.Label(frame, textvariable=variable, width=width).grid(row=row, column=col+2, padx=5)
        return scale
    else:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=f"{text}:", width=15, anchor="e").pack(side=tk.LEFT, padx=5)

        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=variable)
        if callback:
            scale.configure(command=callback)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(frame, textvariable=variable, width=width).pack(side=tk.LEFT, padx=5)
        return scale


def create_radio_buttons(parent, variable, options, command=None, side=tk.LEFT):
    for text, value in options:
        btn = ttk.Radiobutton(parent, text=text, variable=variable, value=value)
        if command:
            btn.configure(command=command)
        btn.pack(side=side, padx=10)


def create_checkboxes(parent, checkboxes_config, side=tk.LEFT):
    for text, variable, command in checkboxes_config:
        checkbox = ttk.Checkbutton(parent, text=text, variable=variable)
        if command:
            checkbox.configure(command=command)
        checkbox.pack(side=side, padx=10)


def create_filter_section(parent, title, enabled_var, before_gray_var,
                          enabled_callback, before_gray_callback, params_config):
    frame = create_labeled_frame(parent, title)

    control_frame = ttk.Frame(frame)
    control_frame.pack(fill=tk.X, pady=5)

    checkboxes = [
        ('Включить фильтр', enabled_var, enabled_callback),
        ('Применять до преобразования в серый', before_gray_var, before_gray_callback)
    ]
    create_checkboxes(control_frame, checkboxes)

    if params_config:
        params_frame = ttk.Frame(frame)
        params_frame.pack(fill=tk.X, pady=5)

        for i, (text, variable, min_val, max_val, callback) in enumerate(params_config):
            create_scale_with_label(
                params_frame, text, variable, min_val, max_val,
                callback, use_grid=True, row=i, col=0
            )

        params_frame.columnconfigure(1, weight=1)
