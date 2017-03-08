#           Copyright (c) 2017 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

""" Module for parsing the require expression
from the projects ``.artisan.yml`` file. """

import itertools
import six
from ..compat import xrange
from ..exceptions import ArtisanException

__all__ = [
    'parse_requires'
]

# These are words that are used within a requires: option but
# are definitely not requires themselves. Each has a special meaning.
_LABEL_KEYWORDS = set(['matrix', 'include', 'omit'])


def parse_requires(requires):
    """ Parses a ``requires`` entry in a require expression.
    Also the starting point for the global requires option. """
    if not isinstance(requires, dict):
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly at `jobs.*.requires`. '
                               'See the documentation for more details.')

    groups = []
    global_requires = {}

    for require, desc in six.iteritems(requires):
        if require in _LABEL_KEYWORDS:
            if require == 'matrix':
                groups.extend(expand_matrix(desc))
            if require == 'include':
                groups.extend(expand_include(desc))
        else:
            global_requires[require] = desc

    # Now apply global level requires to each grouping.
    for group in groups:
        for require, desc in six.iteritems(global_requires):
            # Don't overwrite lower-level requires with globals.
            if require not in group:
                group[require] = desc

    # If no groups were found then we only have a single entry of globals.
    if len(groups) == 0:
        groups = [global_requires]

    expand_omit(groups, requires.get('omit', []))
    return groups


def expand_include(include):
    """ Expands an ``include`` entry in a require expression. """
    if not isinstance(include, list):
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly. See the documentation '
                               'for more details.')

    groups = []
    for entry in include:
        groups.extend(parse_requires(entry))
    return groups


def expand_matrix(matrix):
    """ Expands a ``matrix`` entry in a require expression. """
    if not isinstance(matrix, dict):
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly. See the documentation '
                               'for more details.')

    omit = matrix.get('omit', [])
    names = [key for key in matrix.keys() if key not in _LABEL_KEYWORDS]
    groups = []
    if len(names):
        for entry in itertools.product(*[matrix[key] for key in names]):
            omitted = False

            if len(omit) > 0:
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
        groups.extend(expand_include(matrix['include']))
    if 'matrix' in matrix:
        groups.extend(expand_matrix(matrix['matrix']))

    expand_omit(groups, omit)
    return groups


def expand_omit(groups, omit):
    """ Applies an ``omit`` entry in a require expression. """
    if len(omit) > 0:
        for i in xrange(len(groups) - 1, -1, -1):
            group = groups[i]
            omitted = False
            for omit_dict in omit:
                for omit_key, omit_value in six.iteritems(omit_dict):
                    if omit_key not in group:
                        break
                    if group[omit_key] != omit_value:
                        break
                else:
                    omitted = True
                    break
            if omitted:
                del groups[i]
