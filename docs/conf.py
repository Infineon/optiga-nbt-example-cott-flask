# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT
from sphinx_pyproject import SphinxConfig

from cott.version import __version__ as cott_version
config = SphinxConfig("../pyproject.toml", globalns=globals(), config_overrides={"version": cott_version})
extensions = ["sphinx.ext.autodoc"]
html_theme = "classic"
master_doc = "index"
