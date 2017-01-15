from collections import namedtuple

__all__ = [
    'FileAttributes',
    'stat_to_file_attrs'
]


FileAttributes = namedtuple('FileAttributes', ['mode',
                                               'inode',
                                               'device',
                                               'nlink',
                                               'user_id',
                                               'group_id',
                                               'size',
                                               'access_time',
                                               'modify_time',
                                               'create_time'])


def stat_to_file_attrs(stat_result):
    """ Converts an object that was returned from os.stat
    into an :class:`artisan.FileAttributes` object. """
    attrs = FileAttributes()
    attrs.mode = stat_result.st_mode
    attrs.inode = stat_result.st_ino
    attrs.device = stat_result.st_dev
    attrs.nlink = stat_result.st_nlink
    attrs.user_id = stat_result.st_uid
    attrs.group_id = stat_result.st_gid
    attrs.size = stat_result.st_size

    if hasattr(stat_result, 'st_atime_ns'):
        attrs.access_time = stat_result.st_atime_ns / 1000000.0
    else:
        attrs.access_time = stat_result.st_atime
    if hasattr(stat_result, 'st_mtime_ns'):
        attrs.modify_time = stat_result.st_mtime_ns / 1000000.0
    else:
        attrs.modify_time = stat_result.st_mtime
    if hasattr(stat_result, 'st_ctime_ns'):
        attrs.create_time = stat_result.st_ctime_ns / 1000000.0
    else:
        attrs.create_time = stat_result.st_ctime
    return attrs
