# -*- coding: utf-8 -*-
"""
Tente de placer automatiquement un point de prescription sur l'isodose
de prescription.

.. rubric::
  EMPLACEMENT :

- *Plan Design*
    - *Scripting*
        - *Module specific scripts*

.. rubric::
  PRÉ-REQUIS :

1.  Définition de la prescription dans l'un des onglets *Plan Design*,
    *Plan Optimization* ou *Plan Evaluation*.  On peut prescrire, par exemple,
    la dose de prescription à *Near minimum dose* au PTV.
2.  Création manuelle d'un point de spécification de dose.  Ceci n'est pas une
    action scriptable.  Le nom du point n'importe pas.  Le premier dans la liste
    sera choisi.  Aller à l'onglet *Plan Design*, faire un clic droit dans une
    des vues et choisir *Create dose specification point*.

.. warning::
  INTERVENION MANUELLE POST-EXÉCUTION REQUISE :
    -   Après exécution du script, on doit aller à l'onglet *Plan Design* -> *Plan
        Setup* puis dans l'onglet *Beam Dose Specification Points* en bas de l'écran.
    -   On doit ensuite changer le point de spécification de dose pour chacun des
        champs.

Ce script va créer le POI *PT PRESC* si celui-ci n'existe pas déjà.

Il trouvera un point situé sur le contour automatiquement identifié en tant
que PTV.  Le *PT PRESC* ira se placer sur l'isodose la plus haute s'il y a plus
d'un PTV avec plus d'un niveau de dose.

Le point sera déplacé selon le gradient local de dose jusqu'à temps de trouver
un point où la dose correspond à la dose de prescription.

Finalement, la prescription sera changée pour être prescrite au POI
*PT PRESC*.

.. note::
  On peut confirmer la valeur de dose à *PT PRESC* et au point de spécification
  de dose dans l'onglet *Plan Evaluation*, section *POI statistics*.

.. seealso::
  fonction :py:func:`hmrlib.poi.auto_place_prescription_point`
"""

import setpath
import hmrlib.lib as lib
import hmrlib.poi as poi

with lib.RSScriptWrapper(__file__):
    poi.auto_place_prescription_point()
