import importlib
import pkgutil


for module in pkgutil.iter_modules(__path__):
    if module.name.startswith('test_'):
        importlib.import_module(f'{__name__}.{module.name}')
