import datetime

__all__ = [
    'BasePolicy'
]


class BasePolicy(object):
    def __init__(self, **kwargs):
        start_time = None
        end_time = None
        all_day = None

        if 'start_time' in kwargs:
            start_time = kwargs['start_time']
            if not isinstance(start_time, datetime.time):
                raise TypeError('`start_time` must be of type `datetime.time`.')
        if 'end_time' in kwargs:
            end_time = kwargs['end_time']
            if not isinstance(end_time, datetime.time):
                raise TypeError('`end_time` must be of type `datetime.time`.')
        if 'all_day' in kwargs:
            all_day = kwargs['all_day']
            if not isinstance(all_day, bool):
                raise TypeError('`all_day` must be of type `bool`.')

        if start_time is None and end_time is not None:
            raise ValueError('`start_time` and `end_time` must be given together.')
        if start_time is not None and end_time is None:
            raise ValueError('`start_time` and `end_time` must be given together.')
        if all_day and (start_time is not None and end_time is not None):
            raise ValueError('`all_day` can\'t be be `True` if `start_time` and `end_time` are given.')
        if not all_day and start_time is None and end_time is None:
            raise ValueError('Must have either `all_day` or `start_time` and `end_time` given.')

        self.start_time = start_time
        self.end_time = end_time
        self.all_day = all_day

    def allow_build_request(self, request):
        if not isinstance(request, )
