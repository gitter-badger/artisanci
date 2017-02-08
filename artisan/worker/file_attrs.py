#           Copyright (c) 2017 Seth Michael Larson
# _________________________________________________________________
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

__all__ = [
    'FileAttributes',
    'stat_to_file_attrs'
]


class FileAttributes(object):
    def __init__(self):
        self.mode = None
        self.inode = None
        self.device = None
        self.nlink = None
        self.user_id = None
        self.group_id = None
        self.size = None
        self.access_time = None
        self.modify_time = None
        self.create_time = None

    def __repr__(self):
        return ('<FileAttributes mode=%s inode=%s '
                'device=%s nlink=%s user_id=%s '
                'group_id=%s size=%s atime=%s mtime=%s '
                'ctime=%s>') % (self.mode,
                                self.inode,
                                self.device,
                                self.nlink,
                                self.user_id,
                                self.group_id,
                                self.size,
                                self.access_time,
                                self.modify_time,
                                self.create_time)

    def __str__(self):
        return self.__repr__()


def stat_to_file_attrs(stat_result):
    """ Converts an object that was returned from os.stat
    into an :class:`artisan.FileAttributes` object. """
    attrs = FileAttributes()
    attrs.mode = stat_result.st_mode
    attrs.user_id = stat_result.st_uid
    attrs.group_id = stat_result.st_gid
    attrs.size = stat_result.st_size

    if hasattr(stat_result, 'st_ino'):
        attrs.inode = stat_result.st_ino
    if hasattr(stat_result, 'st_dev'):
        attrs.device = stat_result.st_dev
    if hasattr(stat_result, 'st_nlink'):
        attrs.nlink = stat_result.st_nlink

    if hasattr(stat_result, 'st_atime_ns'):
        attrs.access_time = stat_result.st_atime_ns / 1000000.0
    elif hasattr(stat_result, 'st_atime'):
        attrs.access_time = stat_result.st_atime
    if hasattr(stat_result, 'st_mtime_ns'):
        attrs.modify_time = stat_result.st_mtime_ns / 1000000.0
    elif hasattr(stat_result, 'st_mtime'):
        attrs.modify_time = stat_result.st_mtime
    if hasattr(stat_result, 'st_ctime_ns'):
        attrs.create_time = stat_result.st_ctime_ns / 1000000.0
    elif hasattr(stat_result, 'st_ctime'):
        attrs.create_time = stat_result.st_ctime

    return attrs
