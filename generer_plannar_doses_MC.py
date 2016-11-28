# -*- coding: utf-8 -*-
"""
DOCUMENTATION: verifier_parametres

Genere et exporte des plannar doses qui pourront etre utilisees pour faire les QA avec le MapCheck dans l'IMF. 
Utilise le fantome 48x48x48 MAPCHECK et le point 4.8cm MAPCHECK IMF.

"""

import setpath
import hmrlib.lib as lib
import hmrlib.qa as qa

with lib.RSScriptWrapper(__file__):
    qa.create_ac_qa_plans(plan=None, phantom_name='48x48x48 FANTOME', iso_name='4.8cm MapCheck IMF')