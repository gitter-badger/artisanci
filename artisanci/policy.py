import datetime
import pendulum

__all__ = [
    'BasePolicy',
    'TimePolicy'
]


class BasePolicy(object):
    """ Object for describing how a farm should act """
    def allow_build_request(self, request=None):
        raise NotImplementedError()


class TimePolicy(BasePolicy):
    def __init__(self, **kwargs):
        start_time = None
        end_time = None
        all_day = None
        timezone = 'UTC'
        max_duration = 30.0

        if 'timezone' in kwargs:
            timezone = kwargs['timezone']
            if not isinstance(timezone, str):
                raise TypeError('`timezone` must be of type `str`.')
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
        if 'max_duration' in kwargs:
            max_duration = kwargs['max_duration']
            if not isinstance(max_duration, (int, float)):
                raise TypeError('`max_duration` must be of type `int` or `float`.')

        if max_duration < 3.0:
            raise ValueError('`max_duration` must be longer than 3 minutes.')
        if start_time is None and end_time is not None:
            raise ValueError('`start_time` and `end_time` must be given together.')
        if start_time is not None and end_time is None:
            raise ValueError('`start_time` and `end_time` must be given together.')
        if all_day and (start_time is not None and end_time is not None):
            raise ValueError('`all_day` can\'t be be `True` if `start_time` and `end_time` are given.')
        if not all_day and start_time is None and end_time is None:
            raise ValueError('Must have either `all_day` or `start_time` and `end_time` given.')
        if start_time > end_time:
            raise ValueError('`start_time` must be before `end_time`.')

        self.timezone = pendulum.timezone(timezone)
        self.start_time = start_time
        self.end_time = end_time
        self.all_day = all_day
        self.max_duration = max_duration

    def allow_build_request(self, request=None):
        if self.all_day:
            return True

        now = self.timezone.fromutc(pendulum.utcnow())

        # Allow a 3 minute buffer at the end of policies.
        delta = datetime.timedelta(seconds=60 * (3 + request.duration))
        return now.time() < self.start_time or (now + delta).time() > self.end_time
