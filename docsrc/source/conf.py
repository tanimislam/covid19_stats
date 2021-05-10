# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os, sys, numpy
sys.path.append( os.path.abspath( '_sphinxextra' ) )
import utility_functions

# -- Project information -----------------------------------------------------

project = 'COVID19_STATS'
copyright = '2021, Tanim Islam'
author = 'Tanim Islam'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '1.0'

tls_verify = False

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'rstjinja',
]


#
## following instructions here (https://github.com/svenevs/exhale/tree/master/docs/_intersphinx) to fix beautifulsoup doc.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ( 'https://docs.python-requests.org/en/master', None),
    'beautifulsoup' : ( 'https://www.crummy.com/software/BeautifulSoup/bs4/doc/', '_intersphinx/bs4_objects.inv' ),
    'cartopy'  : ( 'https://scitools.org.uk/cartopy/docs/latest', None ),
    'selenium' : ( 'https://selenium-python.readthedocs.io', None ),
    'pyqt5' : ( 'https://www.riverbankcomputing.com/static/Docs/PyQt5', "_intersphinx/pyqt5_objects.inv" ),
    'requests_oauthlib' : ( 'https://requests-oauthlib.readthedocs.io/en/latest', None ),
    'google-auth-oauthlib' : ( 'https://google-auth-oauthlib.readthedocs.io/en/latest', None ),
    'google-auth' : ( 'https://google-auth.readthedocs.io/en/latest', None ),
    'PyPDF2' : ( 'https://pythonhosted.org/PyPDF2', None ),
    'Pillow' : ( 'https://pillow.readthedocs.io/en/stable', None ),
    'docutils' : ( 'https://docutils.readthedocs.io/en/sphinx-docs', None ),
    'matplotlib' : ( 'https://matplotlib.org/stable', None ),
    'mutagen'  : ( 'https://mutagen.readthedocs.io/en/latest', None ),
    'pandas'   : ( 'https://pandas.pydata.org/docs', None ),
    'nprstuff' : ( 'https://tanimislam.github.io/nprstuff', None ),
}

#
## number figures and tables
numfig = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# icon file
html_favicon = 'covid19_stats.ico'

#
## put variables into html_context dictionary
## follow advice from https://www.ericholscher.com/blog/2016/jul/25/integrating-jinja-rst-sphinx/
## beginning use case: how much data lies in the covid19 analysis dataset

##
## because current where-this-lives is being EXTRA difficult
## use the topN_json that exists right now. Not a stateless solution.
## extremely stateful, but oh hell oh well...
html_context = {
    #'dataset_size_formatted' : utility_functions.get_dataset_size_formatted(
    #    mainURL = 'https://tanimislam.sfo3.digitaloceanspaces.com', verify = False ),
    'topN_json' : utility_functions.get_topN_json(
        mainURL = 'https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_topN_LATEST.json',
        verify = False,
        topN_json = '/g/g12/islam5/ws-islam5/covid19movies/docs/covid19_topN_LATEST.json' ),
    'created_readme_template' : utility_functions.create_readme_from_template(
        verify = False,
        topN_json = '/g/g12/islam5/ws-islam5/covid19movies/docs/covid19_topN_LATEST.json' )
    }
