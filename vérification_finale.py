# -*- coding: utf-8 -*-
"""
DOCUMENTATION: verifier_parametres

Ce script demarre une vérification des paramètres pour un Beam Set dans RayStation.

"""

import setpath
import hmrlib.lib as lib
import launcher

with lib.RSScriptWrapper(__file__):
    launcher.verification_finale()