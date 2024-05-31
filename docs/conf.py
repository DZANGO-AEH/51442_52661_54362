# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
import django
sys.path.insert(0, os.path.abspath('../onlyvans'))
sys.path.insert(0, os.path.abspath('.'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'onlyvans.settings'
django.setup()

project = 'OnlyVans'
copyright = '2024, Jacek Miecznikowski, Kamil Danielski, Mateusz Kalenik'
author = 'Jacek Miecznikowski, Kamil Danielski, Mateusz Kalenik'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
extensions += ["sphinxawesome_theme.highlighting"]
html_static_path = ['_static']
html_theme_options = {
    "logo_light": "../onlyvans/static/img/onlyvans-dark.svg",
    "logo_dark": "../onlyvans/static/img/onlyvans.svg",
    "show_breadcrumbs": True,
    "show_scrolltop": True,

}
html_sidebars = {
  "/about": ["sidebar_main_nav_links.html"]
}

def setup(app):
    app.add_css_file('custom.css')