# -*- coding: utf-8 -*-

import setpath
import hmrlib.hmrlib as hmrlib
import prostate

with hmrlib.RSScriptWrapper(__file__):
    prostate.test_MA()