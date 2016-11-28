# -*- coding: utf-8 -*-
"""
Ce script est utilisé pour changer l'affichage des isodoses lors d'un planification
de prostate VMAT en deux plans. Le script change la dose de référence du *Dose Color Table*
entre deux valeurs: la dose de préscription du plan A2 et la somme des préscriptions A1+A2.
Si la dose de référence actuelle n'est ni un ni l'autre de ces valeurs, le script la change
pour être la dose de prescription du plan A2.

.. note::
  Les niveaux de dose sont basés sur le nombre de fractions dans chacun des plans.
      - A2: 2 Gy * nb de fractions dans le plan A2
      - A1+A2: 2 Gy * le nb de fractions total dans le plan A1 + le plan A2

  Donc, si le nombre de fractions change, la dose de référence suivra automatiquement.

"""
import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.toggle_reference_dose()