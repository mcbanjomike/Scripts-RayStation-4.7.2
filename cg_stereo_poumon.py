# -*- coding: utf-8 -*-
"""
Ajoute les clinical goals pour les cas de stéréo de poumon.

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

Ajoute automatiquement un clinical goal pour l'objectif de couverture
D100 % - 0.1 cc pour le PTV.  Celui-ci est mis en volume absolu.

Des avertissements seront affichés à l'écran pour chacun des ROI non
trouvés par le script.

.. seealso::
  la documentation de la fonction :py:func:`clinical_goals.add_cg_lung_stereo` pour les détails.
"""

import setpath
import hmrlib.lib as lib
import clinical_goals

with lib.RSScriptWrapper(__file__):
    clinical_goals.add_cg_lung_stereo()
