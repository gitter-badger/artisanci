import itertools
import six

__all__ = [
    'expand_labels',
    'expand_include',
    'expand_matrix'
]

# These are words that are used within a labels: option but
# are definitely not labels themselves. Each has a special meaning.
_LABEL_KEYWORDS = set(['matrix', 'include', 'omit'])


def expand_labels(labels):
    """ Expands a ``labels`` entry in a label expression.
    Also the starting point for the global labels option. """
    assert isinstance(labels, dict)

    groups = []
    global_labels = {}

    for label, desc in six.iteritems(labels):
        if label in _LABEL_KEYWORDS:
            if label == 'matrix':
                groups.extend(expand_matrix(desc))
            if label == 'include':
                groups.extend(expand_include(desc))
        else:
            global_labels[label] = desc

    # Now apply global level labels to each grouping.
    for group in groups:
        for label, desc in six.iteritems(global_labels):
            # Don't overwrite lower-level labels with globals.
            if label not in group:
                group[label] = desc

    return groups


def expand_include(include):
    """ Expands an ``include`` entry in a label expression. """
    assert isinstance(include, list)

    groups = []
    for entry in include:
        groups.extend(expand_labels(entry))
    return groups


def expand_matrix(matrix):
    """ Expands a ``matrix`` entry in a label expression. """
    assert isinstance(matrix, dict)

    omit = matrix.get('omit', None)
    names = [key for key in matrix.keys() if key not in _LABEL_KEYWORDS]
    groups = []
    for entry in itertools.product(*[matrix[key] for key in names]):
        omitted = False

        if omit is not None:
            entry_dict = {}
            for i, value in enumerate(entry):
                entry_dict[names[i]] = value
            for omit_dict in omit:
                for omit_key, omit_value in six.iteritems(omit_dict):
                    if omit_key not in entry_dict:
                        break
                    if entry_dict[omit_key] != omit_value:
                        break
                else:
                    omitted = True
                    break

        if not omitted:
            groups.append({})
            for i, value in enumerate(entry):
                groups[-1][names[i]] = value

    if 'include' in matrix:
        groups.extend(matrix['include'])

    return groups
