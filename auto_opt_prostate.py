# -*- coding: utf-8 -*-
"""
DOCUMENTATION: auto_opt_prostate

Ce script optimise un plan deux fois. Ensuite, il regarde les objectifs MaxDVH pour le ROI RECTUM.
    - si le volume cible pour un objectif est dépassé, le volume réel obtenu est mis dans l'objectif (arrondi vers le bas)
    - si le volume cible est atteint, le volume demandé par l'objectif est baissé à 1-2% plus bas que le volume obtenu
Ensuite, le script fait un "reset" et le plan est optimisé deux fois à nouveau.

Le script devrait fonctionner pour tous les plans de prostate avec un ROI nommé "RECTUM".

"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.auto_opt_prostate()