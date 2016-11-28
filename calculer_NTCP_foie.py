# -*- coding: utf-8 -*-
"""
DOCUMENTATION: calculer_NTCP_foie

Ce script a comme but de calculer le Veff et le NTCP pour les cas de stéréotaxie de foie.
Les resultats seront enregistrés dans N:\Dosimétristes\STEREO FOIE\Calculs NTCP

Pré-réquis:
Un contour "FOIE EXPI-GTV"
La dose doit être calculée
Il faut avoir une prescription
  
"""

import setpath
import hmrlib.lib as lib
import foie

with lib.RSScriptWrapper(__file__):
    foie.calculer_NTCP_foie()