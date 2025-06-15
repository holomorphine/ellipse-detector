import tkinter as tk
from defaults import CONFIGURABLE_PARAMS
from utils import validate_kernel_size


class ParameterManager:
    def __init__(self, app=None):
        self.app = app
        self.parameter_configs = CONFIGURABLE_PARAMS
        self.parameter_vars = {}
        self.init_parameter_vars()

    def init_parameter_vars(self):
        for name, config in self.parameter_configs.items():
            default = config['default']
            if config['type'] == 'boolean':
                var = tk.BooleanVar(value=default)
            elif config['type'] == 'int':
                var = tk.IntVar(value=default)
            elif config['type'] == 'double':
                var = tk.DoubleVar(value=default)
            else:
                var = tk.StringVar(value=default)

            self.parameter_vars[name] = var

    def get_value(self, name):
        var = self.parameter_vars.get(name)
        return var.get()

    def set_value(self, name, value):
        var = self.parameter_vars.get(name)
        var.set(value)

    def get_all(self):
        return {name: var.get() for name, var in self.parameter_vars.items()}

    def get_parameters_by_category(self, category):
        return [name for name, config in self.parameter_configs.items() if config['category'] == category]

    def get_parameter_var(self, name):
        return self.parameter_vars.get(name)

    def create_step_handler(self, param_name):
        config = self.parameter_configs[param_name]
        var = self.parameter_vars[param_name]
        step = config.get('step', 1.0)
        
        def handler(v):
            if 'kernel' in param_name.lower():
                value = int(float(v))
                var.set(validate_kernel_size(value))
            else:
                value = round(float(v) / step) * step
                if isinstance(var, tk.IntVar):
                    var.set(int(value))
                else:
                    var.set(value)

            self.call_update_method(param_name)

        return handler
    
    def create_change_handler(self, param_name):
        def handler():
            self.call_update_method(param_name)

        return handler
    
    def call_update_method(self, param_name):
        self.app.parameter_changed(param_name)
    
    def reset_all_parameters(self):
        if not self.app.detector:
            return

        for param_name, var in self.parameter_vars.items():
            default_value = self.parameter_configs[param_name]['default']
            var.set(default_value)
    
    def get_filter_parameters(self):
        filter_params = []
        for param_name, config in self.parameter_configs.items():
            if 'display_name' in config:
                filter_params.append((
                    config['display_name'],
                    config['min'],
                    config['max'],
                    param_name
                ))

        return filter_params

    def get_parameter_category(self, param_name):
        return self.parameter_configs[param_name].get('category')
