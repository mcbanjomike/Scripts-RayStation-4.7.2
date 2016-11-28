# -*- coding: utf-8 -*-
"""
.. rubric::
Script qui roule deux optimizations de suite et qui sauvegarde par la suite.  
NB que sauvegarder vide la liste de "undo", donc il n'est par toujours souhaitable de le faire.
"""

import setpath
import hmrlib.lib as lib
import hmrlib.optim as optim

with lib.RSScriptWrapper(__file__):
    optim.double_opt_save()