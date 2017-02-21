from .platform import detect_platform_labels
from .python import detect_python_labels
from .machine import detect_machine_labels
from .label import Label

__all__ = [
    'detect_labels'
]


def detect_labels():
    detects = []
    detects.extend(detect_platform_labels())
    detects.extend(detect_python_labels())
    detects.extend(detect_machine_labels())
    labels = []
    for kw in detects:
        for name, (type, version) in kw.items():
            labels.append(Label(name, type, version))
    return labels
