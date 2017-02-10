import re

_LABEL_REGEX = re.compile(r'^([a-z\-]*[a-z]\-)([a-z]+)?([=><|,~\da-zA-Z\.]+)?$')


class _LabelExpr(object):
    def matches(self, labels):
        raise NotImplementedError()


class Label(_LabelExpr):
    def __init__(self, name, value=None, version=None):
        self.name = name
        self.value = value
        self.version = version


def _convert_string_to_label(string):
    match = _LABEL_REGEX.match(string)
    if match:
        name, value, version = match.groups()
        if name is None:
            name = value
            value = None
        assert name is not None
        name = name.rstrip('-')
        print(name, value, version)
        return Label(name, value, version)
