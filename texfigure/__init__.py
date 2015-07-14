# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
texfigure is a package of PythonTeX helpers for managing matplotlib plots.

Importing texfigure will set your matplotlib backend to pgf, therefore
``import texfigure`` should come before any other matplotlib imports.
"""

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

# For egg_info test builds to pass, put package imports here.
if not _ASTROPY_SETUP_:
    from setup_mpl import configure_latex_plots, figsize # This sets pgf backend
    from texfigure import *

import sys

def repr_latex_formatter(obj):
    if hasattr(obj, '_repr_latex_'):
        return obj._repr_latex_()
    else:
        if sys.version_info[0] == 2:
            return unicode(obj)
        else:
            return str(obj)
