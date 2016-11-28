# -*- coding: utf-8 -*-
"""
DOCUMENTATION: verifier_parametres

Ajoute un arc VMAT avec les angles gantry, collimateur et sens opposé au premier arc du beamset.
Devrait seulement être utilisé dans les beamsets comprenant un seul arc.
Le script suppose que le nom de l'isocentre est soit "ISOCENTRE" ou "ISO SCAN".

"""

import setpath
import hmrlib.lib as lib
import beams

with lib.RSScriptWrapper(__file__):
    beams.ajouter_arc_oppose()