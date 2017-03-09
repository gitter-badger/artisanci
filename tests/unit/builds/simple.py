# Simple script that deletes a file.


def script(worker):
    worker.remove(worker.environment['DELETE_THIS'])
