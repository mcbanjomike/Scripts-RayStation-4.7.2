# -*- coding: utf-8 -*-
"""
DOCUMENTATION: smart_cg_foie_sbrt

===========
Pré-réquis:
===========

Le script utilise les contours suivants (tout les ROIs sauf le PTV sont facultatifs):
 - PTVx où x est la dose the prescription en Gy (eg PTV37.5 ou PTV45)
 - GTV
 - FOIE EXPI
 - MOELLE et prv5mmMOELLE
 - REINS (combinaison de REIN D et REIN G)
 - ESTOMAC, COLON, DUODENUM, GRELE, et OESOPHAGE
 - OESO PAROI OPP
 - PAROI
 - TISSU SAIN A 2cm
 - PEAU
 - FOIE EXP-GTV
 
 Il faut que le nombre de fractions soit 3 ou 5.
 Il faut avoir un seul scan dans le patient.


"""

import setpath
import hmrlib.lib as lib
import clinical_goals

with lib.RSScriptWrapper(__file__):
    clinical_goals.smart_cg_foie_sbrt()