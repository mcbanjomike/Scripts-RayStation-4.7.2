# -*- coding: utf-8 -*-
"""
Si vous désirez faire un déplacement de l'ArcCheck pour que la dose maximum tombe sur le MicroLion
lors du QA Patient, créez un point "dose specification point" sur le point de dose max (fait-le dans
chacun des QA plans qui nécessitera un déplacement). Ce script passera à travers tous les plans QA
pour le patient; si un DSP existe dans un plan, le script fera une copie du plan QA avec un nouvel
isocentre, calculé pour que la dose max tombe maintenant sur le MicroLion. Les coordonnés sont
arrondis pour éviter des déplacements de table sous-millimétriques. La dose sera calculée pour chaque
plan QA à la fin du script.
"""

import setpath
import hmrlib.lib as lib
import hmrlib.qa as qa

with lib.RSScriptWrapper(__file__):
    qa.shift_plans_QA()
