# -*- coding: utf-8 -*-
"""
Règle les paramètres d'optimisation et de conversion pour les cas de VMAT.

.. warning::
  Exécuter ce script une fois l'optimisation commencée forcera
  un **RESET** de l'optimisation en cours.

.. rubric::
  EMPLACEMENT :

- *Plan Optimization*
    - *Scripting*
        - *Module specific scripts*

Optimisation :

- Itérations en fluence = 60
- Nombre total d'itérations = 100
- Tolérance d'optimalité = 1E-9
- Calculer dose intermédiaire = Vrai
- Calculer dose finale = Vrai

Conversion :

- Restreindre le mouvement des lames = Vrai
    + Déplacement maximal des lames par degré de bras = 0.1 cm/degré
- Pour chacun des arcs définis dans le plan :
    + Espacement en degrés des points de contrôle = 4 degrés
    + Temps maximal de livraison de l'arc = 350 s

.. seealso::
  fonctions :py:func:`hmrlib.optim.set_optimization_parameters`, :py:func:`hmrlib.optim.set_vmat_conversion_parameters`
"""
import setpath
import hmrlib.lib as lib
import hmrlib.optim as optim

with lib.RSScriptWrapper(__file__):
    optim.set_optimization_parameters()
    optim.set_vmat_conversion_parameters()
