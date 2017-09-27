# -*- coding: utf-8 -*-
"""
.. rubric::
Script qui roule deux optimizations: 90 itérations (30 fluence + 60 segments) suivi de 30 itérations (fluence seulement) 
"""

import setpath
import hmrlib.lib as lib
import hmrlib.optim as optim

with lib.RSScriptWrapper(__file__):
    optim.optimization_90_30()

