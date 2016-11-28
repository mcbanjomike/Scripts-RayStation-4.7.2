# -*- coding: utf-8 -*-
"""
DOCUMENTATION: changer technique VMAT-IMRT

Crée un nouveau plan avec les memes objectifs d'optimisation et les memes clinical goals que celui sélectionné (ne pas oublier de sélectionner un plan)
mais en changant la technique de traitement pour passer de VMAT à IMRT ou d'IMRT à VMAT. Optimise 2 fois le nouveau plan.

"""

import setpath
import hmrlib.lib as lib
import hmrlib.optim as optim

with lib.RSScriptWrapper(__file__):
    optim.essai_autre_technique()