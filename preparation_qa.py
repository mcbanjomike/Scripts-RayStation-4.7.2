# -*- coding: utf-8 -*-
"""
Script pour préparer les QAs patients. Il utilise le scripting GUI, alors ne touchez pas à l'ordinateur pendant qu'il roule.
"""

import setpath
import hmrlib.lib as lib
import hmrlib.qa as qa

with lib.RSScriptWrapper(__file__):
    qa.preparation_qa()
