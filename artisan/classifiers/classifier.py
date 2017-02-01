__all__ = [
    'Classifier'
]


class Classifier(object):
    def __init__(self, name, version=None, family=None):
        self.name = name
        self.version = version
        self.family = family
        self.info = {}

    def __str__(self):
        string = self.name
        if self.family is not None:
            string = '%s-%s' % (self.family, string)
        if self.version is not None:
            string = '%s-%s' % (string, self.version)
        return string

    def __repr__(self):
        return '<%s `%s`>' % (type(self).__name__, str(self))
