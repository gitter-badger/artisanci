import psutil

__all__ = [
    'detect_machine_labels'
]


def detect_machine_labels():
    """ Gets machine specs as labels. """
    labels = [{'cpu-count': (None, str(psutil.cpu_count()))}]
    try:
        labels.append({'cpu': (None, str(int(psutil.cpu_freq().max)))})
    except Exception:
        pass
    labels.append({'disk': (None, str(int(psutil.disk_usage('/').free / (1024 * 1024))))})
    labels.append({'memory': (None, str(int(psutil.virtual_memory().total / (1024 * 1024))))})
    return labels
