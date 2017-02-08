#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

import artisan

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'
from datetime import datetime
import alabaster

year = datetime.now().year

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['alabaster',
              'sphinx.ext.todo',
              'sphinx.ext.intersphinx',
              'sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# Releases changelog extension
releases_release_uri = "https://github.com/artisanci/artisan/tree/%s"
releases_issue_uri = "https://github.com/artisanci/artisan/issues/%s"

# General information about the project.
project = 'Artisan'
copyright = '%d Seth Michael Larson' % year
author = 'Seth Michael Larson'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = artisan.__version__
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []
exclude_trees = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
html_theme_options = {
    'description': 'Open-Source Continuous Integration Services that work for you!',
    'github_user': 'artisanci',
    'github_repo': 'artisan',
    'github_button': False,
    'github_banner': True,
    'font_family': "'Cabin', Georgia, sans",
    'head_font_family': "'Cabin', Georgia, serif",
    'code_font_family': "'Anonymous Pro', 'Consolas', monospace",
    'page_width': '960px'
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html'
    ]
}

# Everything intersphinx's to Python.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.6', None),
}

# Autodoc settings
autodoc_default_flags = ['members', 'special-members']


def autodoc_skip_member(app, what, name, obj, skip, options):
    exclusions = {'__weakref__', '__doc__', '__module__', '__dict__'}
    exclude = name in exclusions
    return skip or exclude


def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# Suppress the warning about a non-local URI for status shields.
suppress_warnings = ['image.nonlocal_uri']

# Enable releases 'unstable prehistory' mode.
releases_unstable_prehistory = True
