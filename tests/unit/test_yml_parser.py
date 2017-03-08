import os
import random
import tempfile
import unittest
from artisanci import ArtisanException
from artisanci.yml import ArtisanYml
from artisanci.yml.label_parser import parse_labels
from artisanci.yml.env_parser import parse_env
from artisanci.yml.farms_parser import parse_farms


class _BaseTestArtisanYmlParser(unittest.TestCase):
    def parse_artisan_yml(self, data):
        raise NotImplementedError()

    def test_single_job(self):
        yml = self.parse_artisan_yml("""
        builds:
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
        builds:
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
        builds:
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
        builds:
          - name: 'test1'
            script: script1
            env: ARTISAN=true
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': 'true'})

    def test_job_with_list_env(self):
        yml = self.parse_artisan_yml("""
        builds:
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
        builds:
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
        builds:
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
        builds:
          - name: 'test1'
            script: script1
            env:
              ARTISAN: 1
              CI: -1
        """)

        self.assertEqual(len(yml.jobs), 1)
        job = yml.jobs[0]
        self.assertEqual(job.environment, {'ARTISAN': '1', 'CI': '-1'})

    def test_project_config_no_jobs(self):
        self.assertRaises(ArtisanException, self.parse_artisan_yml, """
        farms:
          - 'gh/SethMichaelLarson'
        """)

    def test_job_has_no_name(self):
        self.assertRaises(ArtisanException, self.parse_artisan_yml, """
        builds:
          - script: script1
        """)

    def test_job_has_no_script(self):
        self.assertRaises(ArtisanException, self.parse_artisan_yml, """
        builds:
          - name: test1
        """)

    def test_farms_include(self):
        yml = self.parse_artisan_yml("""
        farms:
          include:
            - 'gh/artisan-bot'
        builds:
          - name: 'test1'
            script: 'script1'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(yml.include_farms, ['gh/artisan-bot'])
        self.assertEqual(yml.omit_farms, [])
        self.assertFalse(yml.community_farms)

    def test_farms_omit(self):
        yml = self.parse_artisan_yml("""
        farms:
          omit:
            - 'gh/artisan-bot'
        builds:
          - name: 'test1'
            script: 'script1'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(yml.include_farms, [])
        self.assertEqual(yml.omit_farms, ['gh/artisan-bot'])
        self.assertTrue(yml.community_farms)

    def test_farms_sources_default(self):
        yml = self.parse_artisan_yml("""
        builds:
          - name: 'test'
            script: '.artisan/test.py'
            labels:
              python: 'cpython==2.7'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(yml.source_farms, ['https://farms.artisan.io'])

    def test_farms_sources_given(self):
        yml = self.parse_artisan_yml("""
        farms:
          sources:
            - https://farm-a.com
            - https://farm-b.com
        builds:
          - name: 'test'
            script: '.artisan/test.py'
            labels:
              python: 'cpython==2.7'
        """)
        self.assertIsInstance(yml, ArtisanYml)
        self.assertEqual(yml.source_farms, ['https://farm-a.com', 'https://farm-b.com'])


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

    def test_wrong_types_labels(self):
        for labels in [(1,), 1, 's', []]:
            self.assertRaises(ArtisanException, parse_labels, labels)

    def test_wrong_types_include(self):
        for include in [(1,), 1, 's', {}]:
            self.assertRaises(ArtisanException, parse_labels, {'include': include})

    def test_wrong_types_matrix(self):
        for matrix in [(1,), 1, 's', []]:
            self.assertRaises(ArtisanException, parse_labels, {'matrix': matrix})


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
            self.assertRaises(ArtisanException, parse_env, env)

    def test_duplicate_keys(self):
        self.assertRaises(ArtisanException, parse_env, ['ARTISAN=1', 'ARTISAN=2'])

    def test_wrong_format(self):
        for env in ['=', '=true', 'NOEQUALSIGN', ['='], ['=true'], ['NOEQUALSIGN']]:
            self.assertRaises(ArtisanException, parse_env, env)

    def test_completely_wrong_type(self):
        for env in [None, (1,)]:
            self.assertRaises(ArtisanException, parse_env, env)

    def test_convert_yaml_types_to_strings(self):
        self.assertEqual(parse_env({'true': True, 'false': False, 'int': 1}),
                         {'true': 'true', 'false': 'false', 'int': '1'})


class TestArtisanYmlFarmsParser(unittest.TestCase):
    def test_farms_empty_community_true(self):
        self.assertEqual(parse_farms({}), (['https://farms.artisan.io'], [], [], True))

    def test_farms_with_true_community(self):
        self.assertEqual(parse_farms({'community': True}), (['https://farms.artisan.io'], [], [], True))

    def test_farms_with_false_community(self):
        self.assertRaises(ArtisanException, parse_farms, {'community': False})

    def test_farms_with_single_include(self):
        self.assertEqual(parse_farms({'include': ['gh/artisan-bot']}), (['https://farms.artisan.io'], ['gh/artisan-bot'], [], False))

    def test_farms_with_single_include_as_string(self):
        self.assertEqual(parse_farms({'include': 'gh/artisan-bot'}), (['https://farms.artisan.io'], ['gh/artisan-bot'], [], False))

    def test_farms_with_single_omit(self):
        self.assertEqual(parse_farms({'omit': ['gh/artisan-bot']}), (['https://farms.artisan.io'], [], ['gh/artisan-bot'], True))

    def test_farms_with_single_omit_as_string(self):
        self.assertEqual(parse_farms({'omit': 'gh/artisan-bot'}), (['https://farms.artisan.io'], [], ['gh/artisan-bot'], True))

    def test_farms_with_single_source(self):
        self.assertEqual(parse_farms({'sources': ['https://artisan-farm-here.com']}), (['https://artisan-farm-here.com'], [], [], True))

    def test_farms_with_single_source_as_string(self):
        self.assertEqual(parse_farms({'sources': 'https://artisan-farm-here.com'}), (['https://artisan-farm-here.com'], [], [], True))

    def test_farms_not_a_dict_exception(self):
        for entry in [None, 1, 's', [], set()]:
            self.assertRaises(ArtisanException, parse_farms, entry)

    def test_farms_bad_keys(self):
        self.assertRaises(ArtisanException, parse_farms, {'includes': ['gh/artisan-bot']})

    def test_farms_include_not_a_list_or_string(self):
        self.assertRaises(ArtisanException, parse_farms, {'include': ('gh/artisan-bot',)})

    def test_farms_community_not_a_bool(self):
        self.assertRaises(ArtisanException, parse_farms, {'community': 'false'})

    def test_farms_community_true_and_include_are_exclusive(self):
        self.assertRaises(ArtisanException, parse_farms, {'community': True, 'include': ['gh/artisan-bot']})


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

    def test_cant_find_artisan_yml(self):
        self.assertRaises(ArtisanException, ArtisanYml.from_path, '/this/path/does/not/exist')


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
