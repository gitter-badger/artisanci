__all__ = [
    'Classifier'
]


class Classifier(object):
    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.info = {}

    def __str__(self):
        if self.version is not None:
            return '%s-%s' % (self.name, self.version)
        return self.name

    def __repr__(self):
        return '<%s `%s`>' % (type(self).__name__, str(self))
