import os
import random
import tempfile
import unittest
from artisan import ArtisanException
from artisan.yml import ArtisanYml
from artisan.yml.label_parser import parse_labels
from artisan.yml.env_parser import parse_env


class _BaseTestArtisanYmlParser(unittest.TestCase):
    def parse_artisan_yml(self, data):
        raise NotImplementedError()

    def test_single_job(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test'
            script: '.artisan/test.py'
            labels:
              python: 'cpython==2.7'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(len(yml.jobs), 1)

        job = yml.jobs[0]
        self.assertEqual(job.labels, {'python': 'cpython==2.7'})
        self.assertEqual(job.name, 'test')
        self.assertEqual(job.script, '.artisan/test.py')

    def test_multiple_jobs(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: 'script1'
            labels:
              a: '1'
          - name: 'test2'
            script: 'script2'
            labels:
              a: '2'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(len(yml.jobs), 2)

        job = yml.jobs[0]
        self.assertEqual(job.labels, {'a': '1'})
        self.assertEqual(job.name, 'test1')
        self.assertEqual(job.script, 'script1')

        job = yml.jobs[1]
        self.assertEqual(job.labels, {'a': '2'})
        self.assertEqual(job.name, 'test2')
        self.assertEqual(job.script, 'script2')

    def test_unlabeled_job(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: 'script1'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(len(yml.jobs), 1)

        job = yml.jobs[0]
        self.assertEqual(job.labels, {})
        self.assertEqual(job.name, 'test1')
        self.assertEqual(job.script, 'script1')

    def test_job_with_single_env(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: script1
            env: ARTISAN=true
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': 'true'})

    def test_job_with_list_env(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: script1
            env:
              - ARTISAN=true
              - CI=false
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': 'true', 'CI': 'false'})

    def test_job_with_dict_env(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: script1
            env:
              ARTISAN: 'true'
              CI: 'false'
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': 'true', 'CI': 'false'})

    def test_job_with_dict_env_convert_bool_to_string(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: script1
            env:
              ARTISAN: true
              CI: false
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': 'true', 'CI': 'false'})

    def test_job_with_dict_env_convert_int_to_string(self):
        yml = self.parse_artisan_yml("""
        jobs:
          - name: 'test1'
            script: script1
            env:
              ARTISAN: 1
              CI: -1
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': '1', 'CI': '-1'})


class TestArtisanYmlLabelParser(unittest.TestCase):
    def test_simple_expand_labels(self):
        labels = {'python': 'cpython==2.7'}
        self.assertEqual(parse_labels(labels), [{'python': 'cpython==2.7'}])

    def test_include_expand_labels(self):
        labels = {'include': [{'python': 'cpython==2.7'},
                              {'python': 'cpython==3.5'}]}
        self.assertEqual(parse_labels(labels), [{'python': 'cpython==2.7'},
                                                {'python': 'cpython==3.5'}])

    def test_single_key_matrix(self):
        labels = {'matrix': {'a': ['1', '2', '3']}}
        self.assertEqual(parse_labels(labels), [{'a': '1'},
                                                {'a': '2'},
                                                {'a': '3'}])

    def test_double_key_matrix(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2']}}
        labels = parse_labels(labels)

        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_with_include(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'include': [{'a': '3'}]}}
        labels = parse_labels(labels)

        self.assertEqual(len(labels), 5)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'},
                        {'a': '3'}]:
            self.assertIn(element, labels)

    def test_matrix_with_global_value(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2']},
                  'c': '3'}
        labels = parse_labels(labels)
        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1', 'c': '3'},
                        {'a': '2', 'b': '1', 'c': '3'},
                        {'a': '1', 'b': '2', 'c': '3'},
                        {'a': '2', 'b': '2', 'c': '3'}]:
            self.assertIn(element, labels)

    def test_matrix_with_exact_omit(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'omit': [{'a': '1', 'b': '1'}]}}
        labels = parse_labels(labels)
        self.assertEqual(len(labels), 3)
        for element in [{'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_with_general_omit(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'omit': [{'a': '1'}]}}
        labels = parse_labels(labels)
        self.assertEqual(len(labels), 2)
        for element in [{'a': '2', 'b': '1'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_with_multi_omit(self):
        labels = {'matrix': {'a': ['1', '2', '3'],
                             'b': ['1', '2'],
                             'omit': [{'a': '1', 'b': '2'},
                                      {'a': '3', 'b': '1'}]}}

        labels = parse_labels(labels)
        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '2', 'b': '2'},
                        {'a': '3', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_omit_key_not_in_matrix(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'omit': [{'c': '1'}]}}

        labels = parse_labels(labels)
        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_bug_parse_single_entry(self):  # See Issue #92
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'c': '3'}}

        labels = parse_labels(labels)
        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1', 'c': '3'},
                        {'a': '2', 'b': '1', 'c': '3'},
                        {'a': '1', 'b': '2', 'c': '3'},
                        {'a': '2', 'b': '2', 'c': '3'}]:
            self.assertIn(element, labels)

    def test_multiple_matrix_in_include_in_matrix(self):
        labels = {'matrix': {'include': [{'matrix': {'a': ['1', '2'],
                                                     'b': ['1', '2']}},
                                         {'c': '3'}]}}
        labels = parse_labels(labels)

        self.assertEqual(len(labels), 5)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'},
                        {'c': '3'}]:
            self.assertIn(element, labels)

    def test_omit_works_in_sub_matrix(self):
        labels = {'matrix': {'include': [{'matrix': {'a': ['1', '2'],
                                                     'b': ['1', '2']}},
                                         {'c': '3'}],
                             'omit': [{'a': '1', 'b': '2'}]}}

        labels = parse_labels(labels)

        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '2', 'b': '2'},
                        {'c': '3'}]:
            self.assertIn(element, labels)

    def test_deeply_nested_matrix_with_omit(self):
        labels = {'matrix': {'matrix': {'matrix': {'matrix': {'a': ['1', '2'],
                                                              'b': ['1', '2']}}},
                             'omit': [{'a': '1', 'b': '2'}]}}
        labels = parse_labels(labels)

        self.assertEqual(len(labels), 3)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_omit_at_global_level(self):
        labels = {'include': [{'a': '1', 'b': '2'},
                              {'a': '2', 'b': '3'}], 'omit': [{'a': '1'}]}
        labels = parse_labels(labels)

        self.assertEqual(labels, [{'a': '2', 'b': '3'}])


class TestArtisanYmlEnvParser(unittest.TestCase):
    def test_empty_environment(self):
        for env in [[], {}]:
            self.assertEqual(parse_env(env), {})

    def test_single_environment_variable(self):
        for env in ['A=1', ['A=1'], {'A': '1'}]:
            self.assertEqual(parse_env(env), {'A': '1'})

    def test_larger_environment_variables(self):
        for env in [['ARTISAN=true', 'CI=true'], {'ARTISAN': 'true', 'CI': 'true'}]:
            self.assertEqual(parse_env(env), {'ARTISAN': 'true',
                                              'CI': 'true'})

    def test_bad_types_parse_dict(self):
        for env in [{'key': (1,)}, {None: 'value'}]:
            self.assertRaises(TypeError, parse_env, env)

    def test_duplicate_keys(self):
        self.assertRaises(ArtisanException, parse_env, ['ARTISAN=1', 'ARTISAN=2'])

    def test_wrong_format(self):
        for env in ['=', '=true', 'NOEQUALSIGN', ['='], ['=true'], ['NOEQUALSIGN']]:
            self.assertRaises(ArtisanException, parse_env, env)

    def test_completely_wrong_type(self):
        for env in [None, (1,)]:
            self.assertRaises(TypeError, parse_env, env)

    def test_convert_yaml_types_to_strings(self):
        self.assertEqual(parse_env({'true': True, 'false': False, 'int': 1}),
                         {'true': 'true', 'false': 'false', 'int': '1'})


class TestArtisanYmlParserFromString(_BaseTestArtisanYmlParser):
    def parse_artisan_yml(self, data):
        return ArtisanYml.from_string(data)


class TestArtisanYmlParserFromFile(_BaseTestArtisanYmlParser):
    def parse_artisan_yml(self, data):
        path = os.path.join(tempfile.gettempdir(), '.artisan.yml')
        with open(path, 'w+') as f:
            f.truncate()
            f.write(data)
        self.addCleanup(_safe_remove, path)
        return ArtisanYml.from_path(path)


DOT = random.randint(0, 1)  # Used to alternate using `.artisan.yml` or `artisan.yml`.


class TestArtisanYmlParserFromDirectory(_BaseTestArtisanYmlParser):

    def parse_artisan_yml(self, data):
        global DOT
        path = os.path.join(tempfile.gettempdir(), ('.' if DOT else '') + 'artisan.yml')
        with open(path, 'w+') as f:
            f.truncate()
            f.write(data)
        self.addCleanup(_safe_remove, path)
        DOT = not DOT
        return ArtisanYml.from_path(tempfile.gettempdir())


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
