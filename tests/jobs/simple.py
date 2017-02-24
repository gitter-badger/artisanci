# Simple script that deletes a file.


def install(worker):
    pass


def script(worker):
    worker.remove_file(worker.environment['DELETE_THIS'])
