# -*- coding: utf-8 -*-
"""
.. note::
  LA VERSION LA PLUS À JOUR DE CE DOCUMENT SE TROUVE DANS DRUPAL: `Planification des prostates vmat`_

.. _`Planification des prostates vmat`: http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

Ce script à comme but de convertir un plan A1 de prostate VMAT standard en plan "split", c'est à dire
avec deux niveaux de dose dans le PTV A1. Le script prend pour acquis que le premier plan était
fait avec le script plan_prostate_A1 et que le contour WALL RECTUM existe toujours. Normalement,
le script devrait préserver les objectifs DVHs rectum tel quel, pour permettre de rapidement redémarrer
le plan en version split sans perdre les pourcentages ni les poids utilisés dans les optimisations à date.

.. warning::
  IL EST FORTEMENT RECOMMANDÉ DE SAUVEGARDER VOTRE PLAN ET DE ROULER CE SCRIPT DANS UNE NOUVELLE COPIE.

.. rubric::
  Étapes du script

Avant de rouler le script, il faut vérifier que les ROIs PTV A1, RECTUM, WALL RECT et RECTUM ds PTV A1 existent.
  
1. Remet le nombre de fractions du plan A1 à 40
2. Crée les contours PTV A1-RECTUM et WALL RECT ds PTV A1
3. Remplace l'objectif de min dose sur le PTV A1 avec un min dose sur le PTV A1-RECTUM (76 Gy à 99.5%, poids 100)
4. Ajoute un objectif min dose 73.2 Gy à RECTUM ds PTV A1 (poids 10)
5. Ajoute un objectif max dose 75 Gy à WALL RECT ds PTV A1 (poids 10)
6. Ajoute un clinical goal pour la couverture du PTV A1-RECTUM (76 Gy à 99.5%)
7. Ajoute un clinical goal pour la couverture du RECTUM ds PTV A1 (73.2 Gy à 99.5%)

.. note::
  BUG CONNU: le script ne peut pas effacer le clinical goal pour la couverture du PTV A1 qui reste du plan A1 initial,
  il faut l'enlever à la main.
  
"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.prostate_split_A1()