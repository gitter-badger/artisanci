class Label(object):
    def __init__(self, name, type=None, version=None):
        self.name = name
        self.type = type
        self.version = version

    def __eq__(self, other):
        if isinstance(other, Label):
            return (self.name == other.name and
                    self.type == other.type and
                    self.version == other.version)
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Label):
            return (self.name != other.name or
                    self.type != other.type or
                    self.version != other.version)
        else:
            return NotImplemented

    def __str__(self):
        string = self.name
        if self.type:
            string += ':' + self.type
        if self.version:
            string += '==' + self.version
        return string

    def __repr__(self):
        return self.__str__()
