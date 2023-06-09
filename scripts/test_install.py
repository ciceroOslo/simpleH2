"""
Test that all of our modules can be imported
Thanks https://stackoverflow.com/a/25562415/10473080
and openscm-runner
"""
import importlib
import os.path
import pkgutil

import simpleh2

def import_submodules(package_name):
    package = importlib.import_module(package_name)

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        print(full_name)
        importlib.import_module(full_name)
        if is_pkg:
            import_submodules(full_name)


import_submodules("simpleh2")

# make sure input data etc. are included
simpleh2_root = os.path.dirname(simpleh2.__file__)
print(simpleh2.__version__)
