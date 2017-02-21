__all__ = [
    'clean_label'
]


def clean_label(label):
    return label.replace(' ', '-').replace('_', '-').lower()
