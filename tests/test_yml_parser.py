import os
import tempfile
import random
import pytest
from artisanci import ArtisanException
from artisanci.yml import ArtisanYml
from artisanci.yml.requires_parser import parse_requires
from artisanci.yml.env_parser import parse_env


def parse_from_string(data):
    return ArtisanYml.from_string(data)


def parse_from_file(data):
    path = os.path.join(tempfile.gettempdir(), '.artisan.yml')
    with open(path, 'w+') as f:
        f.truncate()
        f.write(data)
    return ArtisanYml.from_path(path)


def parse_from_dir(data):
    path = os.path.join(tempfile.gettempdir(), ('.' if random.randint(0, 1) else '') + 'artisan.yml')
    with open(path, 'w+') as f:
        f.truncate()
        f.write(data)
    return ArtisanYml.from_path(tempfile.gettempdir())


varied_parse_methods = pytest.mark.parametrize('parser', [parse_from_file, parse_from_dir, parse_from_string])


def test_file_and_dir_not_found():
    with pytest.raises(ArtisanException):
        parse_from_dir('/this/path/does/not/exist')
    with pytest.raises(ArtisanException):
        parse_from_file('/this/path/does/not/exist')


@varied_parse_methods
def test_no_build_entry(parser):
    with pytest.raises(ArtisanException):
        parser('')


@varied_parse_methods
def test_single_job(parser):
    yml = parser("""
    builds:
      - script: '.artisan/test.py'
        duration: 5
        requires:
          python: 'cpython==2.7'
    """)
    assert isinstance(yml, ArtisanYml)
    assert len(yml.jobs) == 1

    job = yml.jobs[0]

    assert job.requires == {'python': 'cpython==2.7'}
    assert job.script == '.artisan/test.py'
    assert job.duration == 5


@varied_parse_methods
def test_multiple_jobs(parser):
    yml = parser("""
    builds:
      - script: 'script1'
        duration: 5
        requires:
          a: '1'
      - script: 'script2'
        duration: 5
        requires:
          a: '2'
    """)
    assert isinstance(yml, ArtisanYml)
    assert len(yml.jobs) == 2

    job = yml.jobs[0]
    assert job.requires == {'a': '1'}
    assert job.script == 'script1'

    job = yml.jobs[1]
    assert job.requires == {'a': '2'}
    assert job.script == 'script2'


@varied_parse_methods
def test_unlabeled_job(parser):
    yml = parser("""
    builds:
      - script: 'script1'
        duration: 5
    """)
    assert len(yml.jobs) == 1

    job = yml.jobs[0]
    assert job.requires == {}
    assert job.script == 'script1'


@varied_parse_methods
def test_job_with_single_env(parser):
    yml = parser("""
    builds:
      - script: script1
        duration: 5
        env: ARTISAN=true
    """)

    assert len(yml.jobs) == 1

    job = yml.jobs[0]
    assert job.environment == {'ARTISAN': 'true'}


@varied_parse_methods
def test_job_with_list_env(parser):
    yml = parser("""
    builds:
      - script: script1
        duration: 5
        env:
          - ARTISAN=true
          - CI=false
    """)

    assert len(yml.jobs) == 1
    job = yml.jobs[0]
    assert job.environment == {'ARTISAN': 'true', 'CI': 'false'}


@varied_parse_methods
def test_job_with_dict_env(parser):
    yml = parser("""
    builds:
      - script: script1
        duration: 5
        env:
          ARTISAN: 'true'
          CI: 'false'
    """)

    assert len(yml.jobs) == 1
    job = yml.jobs[0]
    assert job.environment == {'ARTISAN': 'true', 'CI': 'false'}


@varied_parse_methods
def test_job_with_dict_env_convert_bool_to_string(parser):
    yml = parser("""
    builds:
      - script: script1
        duration: 5
        env:
          ARTISAN: true
          CI: false
    """)

    assert len(yml.jobs) == 1
    job = yml.jobs[0]
    assert job.environment == {'ARTISAN': 'true', 'CI': 'false'}


@varied_parse_methods
def test_job_with_dict_env_convert_int_to_string(parser):
    yml = parser("""
    builds:
      - script: script1
        duration: 5
        env:
          ARTISAN: 1
          CI: -1
    """)

    assert len(yml.jobs) == 1
    job = yml.jobs[0]
    assert job.environment == {'ARTISAN': '1', 'CI': '-1'}


@varied_parse_methods
def test_job_has_no_script(parser):
    with pytest.raises(ArtisanException):
        parser("""
            builds:
              - duration: 5
                requires:
                  test: a
        """)


@varied_parse_methods
def test_no_duration(parser):
    with pytest.raises(ArtisanException):
        parser("""
            builds:
              - script: '.artisan/test.py'
        """)


@varied_parse_methods
def test_too_long_script(parser):
    data = """
        builds:
          - script: 'REPLACE'
            duration: 5
            requires:
              python: 'cpython==2.7'
    """.replace('REPLACE', 'x' * 257)
    with pytest.raises(ArtisanException):
        parser(data)


@varied_parse_methods
def test_too_long_duration(parser):
    with pytest.raises(ArtisanException):
        parser("""
        builds:
          - script: '.artisan/test.py'
            duration: 61
        """)


def test_simple_expand_requires():
    requires = {'python': 'cpython==2.7'}
    assert parse_requires(requires) == [{'python': 'cpython==2.7'}]


def test_include_expand_requires():
    requires = {'include': [{'python': 'cpython==2.7'},
                            {'python': 'cpython==3.5'}]}
    assert parse_requires(requires) == [{'python': 'cpython==2.7'},
                                        {'python': 'cpython==3.5'}]


def test_single_key_matrix():
    requires = {'matrix': {'a': ['1', '2', '3']}}
    assert parse_requires(requires) == [{'a': '1'},
                                        {'a': '2'},
                                        {'a': '3'}]


def test_double_key_matrix():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2']}}
    requires = parse_requires(requires)

    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '1', 'b': '2'},
                    {'a': '2', 'b': '2'}]:
        assert element in requires


def test_matrix_with_include():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2'],
                           'include': [{'a': '3'}]}}
    requires = parse_requires(requires)

    assert len(requires) == 5
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '1', 'b': '2'},
                    {'a': '2', 'b': '2'},
                    {'a': '3'}]:
        assert element in requires


def test_matrix_with_global_value():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2']},
                'c': '3'}
    requires = parse_requires(requires)
    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1', 'c': '3'},
                    {'a': '2', 'b': '1', 'c': '3'},
                    {'a': '1', 'b': '2', 'c': '3'},
                    {'a': '2', 'b': '2', 'c': '3'}]:
        assert element in requires


def test_matrix_with_exact_omit():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2'],
                           'omit': [{'a': '1', 'b': '1'}]}}
    requires = parse_requires(requires)
    assert len(requires) == 3
    for element in [{'a': '2', 'b': '1'},
                    {'a': '1', 'b': '2'},
                    {'a': '2', 'b': '2'}]:
        assert element in requires


def test_matrix_with_general_omit():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2'],
                           'omit': [{'a': '1'}]}}
    requires = parse_requires(requires)
    assert len(requires) == 2
    for element in [{'a': '2', 'b': '1'},
                    {'a': '2', 'b': '2'}]:
        assert element in requires


def test_matrix_with_multi_omit():
    requires = {'matrix': {'a': ['1', '2', '3'],
                           'b': ['1', '2'],
                           'omit': [{'a': '1', 'b': '2'},
                                    {'a': '3', 'b': '1'}]}}

    requires = parse_requires(requires)
    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '2', 'b': '2'},
                    {'a': '3', 'b': '2'}]:
        assert element in requires


def test_matrix_omit_key_not_in_matrix():
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2'],
                           'omit': [{'c': '1'}]}}

    requires = parse_requires(requires)
    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '1', 'b': '2'},
                    {'a': '2', 'b': '2'}]:
        assert element in requires


def test_matrix_parse_single_entry_bug_issue_92():  # See Issue #92
    requires = {'matrix': {'a': ['1', '2'],
                           'b': ['1', '2'],
                           'c': '3'}}

    requires = parse_requires(requires)
    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1', 'c': '3'},
                    {'a': '2', 'b': '1', 'c': '3'},
                    {'a': '1', 'b': '2', 'c': '3'},
                    {'a': '2', 'b': '2', 'c': '3'}]:
        assert element in requires


def test_multiple_matrix_in_include_in_matrix():
    requires = {'matrix': {'include': [{'matrix': {'a': ['1', '2'],
                                                 'b': ['1', '2']}},
                                       {'c': '3'}]}}
    requires = parse_requires(requires)

    assert len(requires) == 5
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '1', 'b': '2'},
                    {'a': '2', 'b': '2'},
                    {'c': '3'}]:
        assert element in requires


def test_omit_works_in_sub_matrix():
    requires = {'matrix': {'include': [{'matrix': {'a': ['1', '2'],
                                                 'b': ['1', '2']}},
                                     {'c': '3'}],
                           'omit': [{'a': '1', 'b': '2'}]}}

    requires = parse_requires(requires)

    assert len(requires) == 4
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '2', 'b': '2'},
                    {'c': '3'}]:
        assert element in requires


def test_deeply_nested_matrix_with_omit():
    requires = {'matrix': {'matrix': {'matrix': {'matrix': {'a': ['1', '2'],
                                                          'b': ['1', '2']}}},
                           'omit': [{'a': '1', 'b': '2'}]}}
    requires = parse_requires(requires)

    assert len(requires) == 3
    for element in [{'a': '1', 'b': '1'},
                    {'a': '2', 'b': '1'},
                    {'a': '2', 'b': '2'}]:
        assert element in requires

def test_omit_at_global_level():
    requires = {'include': [{'a': '1', 'b': '2'},
                            {'a': '2', 'b': '3'}], 'omit': [{'a': '1'}]}
    requires = parse_requires(requires)

    assert requires == [{'a': '2', 'b': '3'}]


@pytest.mark.parametrize('requires', [(1,), 1, 's', []])
def test_wrong_types_requires(requires):
    with pytest.raises(ArtisanException):
        parse_requires(requires)


@pytest.mark.parametrize('include', [(1,), 1, 's'])
def test_wrong_types_include(include):
    with pytest.raises(ArtisanException):
        parse_requires({'include': include})


@pytest.mark.parametrize('matrix', [(1,), 1, 's', []])
def test_wrong_types_matrix(matrix):
    with pytest.raises(ArtisanException):
        parse_requires({'matrix': matrix})


@pytest.mark.parametrize('env', [[], {}])
def test_empty_environment(env):
    assert parse_env(env) == {}


@pytest.mark.parametrize('env', ['A=1', ['A=1'], {'A': '1'}])
def test_single_environment_variable(env):
    assert parse_env(env) == {'A': '1'}


@pytest.mark.parametrize('env', [['ARTISAN=true', 'CI=true'], {'ARTISAN': 'true', 'CI': 'true'}])
def test_larger_environment_variables(env):
    assert parse_env(env) == {'ARTISAN': 'true',
                              'CI': 'true'}


@pytest.mark.parametrize('env', [{'key': (1,)}, {None: 'value'}])
def test_bad_types_parse_dict(env):
    with pytest.raises(ArtisanException):
        parse_env(env)


def test_duplicate_keys():
    with pytest.raises(ArtisanException):
        parse_env(['ARTISAN=1', 'ARTISAN=2'])


@pytest.mark.parametrize('env', ['=', '=true', 'NOEQUALSIGN', ['='], ['=true'], ['NOEQUALSIGN']])
def test_wrong_format(env):
    with pytest.raises(ArtisanException):
        parse_env(env)


@pytest.mark.parametrize('env', [None, (1,)])
def test_completely_wrong_type(env):
    with pytest.raises(ArtisanException):
        parse_env(env)


def test_convert_yaml_types_to_strings():
    assert parse_env({'true': True, 'false': False, 'int': 1}) == {'true': 'true', 'false': 'false', 'int': '1'}
