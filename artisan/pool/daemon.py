import time
from service import DefaultService


class PoolDaemon(DefaultService):
    def __init__(self):
        super(PoolDaemon, self).__init__('artisan.pid')

    def run(self):
        while True:
            print('hello')
            time.sleep(2)


if __name__ == '__main__':
    s = PoolDaemon()
    s.stop()