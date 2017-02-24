import os
import random
import tempfile
import unittest
from artisan.yml import ArtisanYml
from artisan.yml.parser import expand_labels


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
        

class TestArtisanYmlParserExpand(unittest.TestCase):
    def test_simple_expand_labels(self):
        labels = {'python': 'cpython==2.7'}
        self.assertEqual(expand_labels(labels), [{'python': 'cpython==2.7'}])

    def test_include_expand_labels(self):
        labels = {'include': [{'python': 'cpython==2.7'},
                              {'python': 'cpython==3.5'}]}
        self.assertEqual(expand_labels(labels), [{'python': 'cpython==2.7'},
                                                 {'python': 'cpython==3.5'}])

    def test_single_key_matrix(self):
        labels = {'matrix': {'a': ['1', '2', '3']}}
        self.assertEqual(expand_labels(labels), [{'a': '1'},
                                                 {'a': '2'},
                                                 {'a': '3'}])

    def test_double_key_matrix(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2']}}
        labels = expand_labels(labels)
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
        labels = expand_labels(labels)
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
        labels = expand_labels(labels)
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
        labels = expand_labels(labels)
        self.assertEqual(len(labels), 3)
        for element in [{'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_with_general_omit(self):
        labels = {'matrix': {'a': ['1', '2'],
                             'b': ['1', '2'],
                             'omit': [{'a': '1'}]}}
        labels = expand_labels(labels)
        self.assertEqual(len(labels), 2)
        for element in [{'a': '2', 'b': '1'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)

    def test_matrix_with_multi_omit(self):
        labels = {'matrix': {'a': ['1', '2', '3'],
                             'b': ['1', '2'],
                             'omit': [{'a': '1', 'b': '2'},
                                      {'a': '3', 'b': '1'}]}}

        labels = expand_labels(labels)
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

        labels = expand_labels(labels)
        self.assertEqual(len(labels), 4)
        for element in [{'a': '1', 'b': '1'},
                        {'a': '2', 'b': '1'},
                        {'a': '1', 'b': '2'},
                        {'a': '2', 'b': '2'}]:
            self.assertIn(element, labels)


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
