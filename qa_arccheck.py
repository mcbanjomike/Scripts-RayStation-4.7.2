"""
Ce script ...
"""

import setpath
import hmrlib.lib as lib
import hmrlib.qa as qa

with lib.RSScriptWrapper(__file__):
    qa.process_ac_qa()
