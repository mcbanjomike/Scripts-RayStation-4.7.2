# -*- coding: utf-8 -*-
"""
Ce script tente d'auto-assigner le bon type de POI pour chacun des POI
présentement définis pour le patient.

.. rubric::
  EMPLACEMENT :

- *Patient Modeling*
    - *Scripting*
        - *Module specific scripts*

Le script se fie au nom des POI.  Il ignore la casse.

Ainsi, *Iso scan* et *ISO SCAN* sont équivalents.

Le script assigne le type de *Localization Point* au point qui contient
la chaîne de caractères *SCAN*.  Si plusieurs points avec cette chaîne de
caractères sont trouvés, une erreur est lancée.

Le script assigne le type *Isocenter* au POI qui a été déterminé comme étant
le plus probable d'être l'isocentre, toujours selon son nom (sauf dans le cas
où l'isocentre est déjà le point de localisation).  Il ne lance **PAS** d'erreur
si plusieurs points avec la chaîne de caractère *ISO* sont trouvés.

Tous les autres POI sont assignés au type *Marker* par défaut.

.. rubric::
  PRÉ-REQUIS :

- Nom du point de référence au CT-Sim contient la chaîne de caractères *SCAN*.  Ex. : *ISO SCAN*, *REF SCAN*.
- Nom du point isocentre contenant la chaîne de caractère *ISO*.  Ex. : *ISO*, *ISO SCAN*.

.. seealso::
  fonction :py:func:`hmrlib.poi.auto_assign_poi_types`
"""

import setpath
import hmrlib.lib as lib
import hmrlib.poi as poi

with lib.RSScriptWrapper(__file__):
    poi.auto_assign_poi_types()
