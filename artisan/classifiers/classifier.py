from collections import namedtuple

__all__ = [
    'Classifier',
    'classifier_to_string'
]


Classifier = namedtuple('Classifier', ['family', 'name', 'version'])


def classifier_to_string(classifier):
    """
    Convert a ``Classifier`` instance into a string.

    :param Classifier classifier: Classifier instance.
    :return: String of the classifier.
    """
    assert isinstance(classifier, Classifier)
    string = classifier.name
    if classifier.family:
        string = classifier.family + '-' + string
    if classifier.version:
        string = string + '-' + classifier.version
    return string
