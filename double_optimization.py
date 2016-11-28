# -*- coding: utf-8 -*-
"""
.. rubric::
Script qui roule deux optimizations de suite.  
"""

import setpath
import hmrlib.lib as lib
import hmrlib.optim as optim

with lib.RSScriptWrapper(__file__):
    optim.double_optimization()