import unittest
from artisan.yml import ArtisanYml
from artisan.yml.parser import expand_labels


class TestArtisanYmlParser(unittest.TestCase):
    def test_simple_yml_parse(self):
        yml = ArtisanYml.from_string("""
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


class TestArtisanYmlParserExpand(unittest.TestCase):
    def test_simple_expand_labels(self):
        labels = {'python': 'cpython==2.7'}
        self.assertEqual(expand_labels(labels), [{'python': 'cpython==2.7'}])

    def test_include_expand_labels(self):
        labels = {'include': [{'python': 'cpython==2.7'},
                              {'python': 'cpython==3.5'}]}
        self.assertEqual(expand_labels(labels), [{'python': 'cpython==2.7'},
                                                 {'python': 'cpython==3.5'}])
