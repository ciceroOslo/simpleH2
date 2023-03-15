"""
Init
"""
from . import _version
from .simpleh2 import SIMPLEH2  # noqa: F401

__version__ = _version.get_versions()["version"]
