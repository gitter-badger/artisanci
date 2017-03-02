import six
from ..exceptions import ArtisanException

__all__ = [
    'parse_farms'
]

# These are the only valid keys within a farms key-value.
_VALID_KEYS = ['sources', 'include', 'omit', 'community']


def parse_farms(farms):
    """ Parses the ``farms`` expression in ``artisan.yml`` to show
    where a project is allowed to be executed. """
    if not isinstance(farms, dict):
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly at `farms`. See the doc'
                               'umentation for more details.')

    sources, include, omit, community = [], [], [], None
    for key, value in six.iteritems(farms):
        if key not in _VALID_KEYS:
            raise ArtisanException('The key `%s` is not valid. Valid keys for '
                                   '`farms` are: `%s`. See the documentation for '
                                   'more details.' % (key, '`, `'.join(_VALID_KEYS)))
        if key == 'include' or key == 'omit' or key == 'sources':
            if not isinstance(value, (list, str)):
                raise ArtisanException('Project configuration `artisan.yml` is not '
                                       'structured properly at `farms.%s`. See the '
                                       'documentation for more details.' % key)
            if isinstance(value, str):
                value = [value]
            if key == 'include':
                include = value
            elif key == 'sources':
                sources = value
            else:
                omit = value
        elif key == 'community':
            if not isinstance(value, bool):
                raise ArtisanException('Project configuration `artisan.yml` is not '
                                       'structured properly at `farms.community`. '
                                       'See the documentation for more details.')
            community = value

    if len(include) > 0 and community:
        raise ArtisanException('Using `include` with `community: '
                               'true` are exclusive options.')

    if len(include) == 0:
        if community is False:
            raise ArtisanException('Project cannot run anywhere with current '
                                   '`farms` configuration.')
        community = True

    if len(sources) == 0:
        sources = ['https://farms.artisan.io']

    return sources, include, omit, bool(community)
