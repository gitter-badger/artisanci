from .python import detect_python
from .plat import detect_platform


__all__ = [
    'detect_all_classifiers'
]


def detect_all_classifiers(worker):
    yield from detect_platform(worker)
    yield from detect_python(worker)
