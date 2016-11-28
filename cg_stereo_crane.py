# -*- coding: utf-8 -*-
"""
Ajoute les *clinical goals*, ou critères cliniques, de stéréotaxie de crâne.

.. rubric::
  EMPLACEMENT :

- *Plan Optimization*
    - *Scripting*
        - *Module specific scripts*

Assume un seul PTV.

.. rubric::
  PRÉ-REQUIS :

- PTV nommé avec son niveau de prescription. Ex. : *PTV18*.
- En général, ROI nommés selon les conventions habituelles établies par les scripts utilisés dans Pinnacle.

Des avertissements seront affichés à l'écran pour chacun des ROI non
trouvés par le script.

.. seealso::
  la documentation de la fonction :py:func:`clinical_goals.add_cg_brain_stereo` pour les détails.
"""

import setpath
import hmrlib.lib as lib
import clinical_goals

with lib.RSScriptWrapper(__file__):
    clinical_goals.add_cg_brain_stereo()
