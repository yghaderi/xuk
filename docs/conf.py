# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../xuk"))

project = 'xuk'
copyright = '2023, Metafid'
author = 'Yaghoub Ghaderi'
release = '0.1.14'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "autoapi.extension",
    "sphinx_copybutton",
    'sphinx-pydantic',
]

copybutton_prompt_text = ">>> "

autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]

mathjax3_config = {"chtml": {"displayAlign": "left"}}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autoapi_type = "python"
autoapi_dirs = ["../xuk"]
autoapi_ignore = ["*utils*"]

autoclass_content = "both"

autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = False

source_suffix = ".rst"
add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "show_version_warning_banner": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/yghaderi/xuk",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ]
    ,
    "external_links": [
        {
            "name": "metafid",
            "url": "https://metafid.com",
        }
    ]
}
