# -*- coding: utf-8 -*-
"""
Ajoute les objectifs d'optimisation pour les cas de stéréo de poumon.

.. rubric::
  EMPLACEMENT :

- *Plan Optimization*
    - *Scripting*
        - *Module specific scripts*

Détecte s'il s'agit d'un poumon droit ou gauche automatiquement.

.. rubric::
  PRÉ-REQUIS :

- PTV nommé avec son niveau de prescription. Ex. : *PTV48*.
- ROI poumon gauche nommé *POUMON G*.
- ROI poumon droit nommé *POUMON D*.
- En général, ROI nommés selon les conventions habituelles établies par les scripts utilisés dans Pinnacle.

Assume qu'il y a un seul PTV.

.. seealso::
  la documentation de la fonction :py:func:`optimization_objectives.add_opt_obj_lung_stereo` pour les détails.
"""

import setpath
import hmrlib.lib as lib
import optimization_objectives

with lib.RSScriptWrapper(__file__):
    optimization_objectives.add_opt_obj_lung_stereo()
