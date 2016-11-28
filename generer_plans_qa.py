# -*- coding: utf-8 -*-
"""
Ce script créera un plan QA pour chaque BeamSet utilisant le fantôme QA VMAT ARCCHECK avec son isocentre
habituel et une grille de dose de 0.2cmx0.2cmx0.2cm. La dose total sera calculée pour chacun des plans QA.
"""

import setpath
import hmrlib.lib as lib
import hmrlib.qa as qa

with lib.RSScriptWrapper(__file__):
    qa.create_ac_qa_plans()
