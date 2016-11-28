# -*- coding: utf-8 -*-
"""
Ce script imprime une cpature d'écran sur l'imprimante *CutePDF Writer*.

.. rubric::
  EMPLACEMENT :

- *Scripting*
    - *General scripts*

.. seealso::
  fonction :py:func:`hmrlib.lib.print_screenshot`
"""

import setpath
import hmrlib.lib as lib

with lib.RSScriptWrapper(__file__):
    lib.print_screenshot()