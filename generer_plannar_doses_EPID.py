# -*- coding: utf-8 -*-
"""
DOCUMENTATION: verifier_parametres

Genere et exporte des plannar doses qui pourront etre utilisees pour faire les QA avec l'EPID. 
Utilise le fantome 48x48x48 MAPCHECK et le point 2cm EPID.

"""

import setpath
import hmrlib.lib as lib
import qa

with lib.RSScriptWrapper(__file__):
    qa.create_ac_qa_plans(plan=None, phantom_name='48x48x48 MAPCHECK', iso_name='2cm EPID')