# -*- coding: utf-8 -*-
"""
.. note::
  LA VERSION LA PLUS À JOUR DE CE DOCUMENT SE TROUVE DANS DRUPAL: `Planification des prostates vmat`_

.. _`Planification des prostates vmat`: http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

.. rubric::
  I. INTRODUCTION

Ce script à pour but de partir le plan A2 "split" (avec 2 niveaux de dose) pour une prostate VMAT.
Il est supposé que le plan A1 était fait avec le script plan_prostate_A1. Une fois que le planificateur
est satisfait(e) du 1e plan, il ou elle peut démarrer ce script, qui fait les points suivants:

1. Création des contours d'optimisation PTV A2-RECTUM et WALL RECT ds PTV A2
2. Changement du nom du 1e beam set à A1 et du nb. de fractions dans le plan A1 à 27
3. Ajout d'un Beam Set A2 avec un préscription de 26 Gy en 13 fx et qui dépend sur la dose du Beam Set A1
4. Création d'un arc total
5. Ajustement des reglages d'optimisation VMAT
6. Ajout des objectifs d'optimisation pour le plan A2 split
7. Ajout des clinical goals pour le plan A2 split
8. Ajustement du niveau de dose de référence à 26 Gy pour l'affichage des isodoses

.. warning::
  IL EST FORTEMENT SUGGÉRÉ DE SAUVEGARDER LE PLAN AVANT DE ROULER CE SCRIPT. De plus, il est mieux de conserver
  le plan A1 seule jusqu'à la fin du travail, au cas où le planificateur désire d'essayer le plan A2 avec et sans split.
  Donc il est suggéré de copier le plan A1 seule et de rouler ce script dans la nouvelle copie.


.. rubric::
  II. PRÉ-REQUIS

Avant de démarrer le script, le planificateur devrait être satisfait de son plan A1, fait à partir
du script plan_prostate_A1. Si le premier script d'est pas utilisé, il risque de manquer des
contours d'optimisation (surtout dans le cas d'un plan "split") et des clinical goals.

Donc, il est nécessaire d'avoir :

1. Un plan avec un seul Beam Set
2. Un point ISO SCAN pour servir comme isocentre et point de localisation
3. Les contours suivants
    - PTV A1 (créé par le script plan_prostate_A1)
    - PTV A2 (créé par le script plan_prostate_A1)
    - BodyRS (créé par le script plan_prostate_A1)
    - RECTUM
    - VESSIE
    - RECTUM ds PTV A2 (créé par le script plan_prostate_A1)
    - WALL RECT (créé par le script plan_prostate_A1)

4. Un clinical goal du type Volume at Dose sur le PTV A1 (créé par le script plan_prostate_A1)

.. rubric::
  III. CRÉATION DES CONTOURS D'OPTIMISATION

1. PTV A2-RECTUM est créé en excluant le contour RECTUM du PTV A2
2. WALL RECT ds PTV A2 est créé en prenant l'intersection des contours WALL RECT et PTV A2

.. note::
  Les deux contours sont de type PTV pour permettre l'usage des objectifs *min dose* dans l'optimisation

.. rubric::
  IV. MODIFICATION/CRÉATION DES BEAM SETS

1. Changement du nom du 1e beam set à *A1* et modification du nb. de fractions du 1e Beam Set à 27

2. Ajout d'un 2e Beam Set nommé A2
    - Machine: Salle 11
    - Modalité: photons
    - Technique: VMAT
    - Position: Head-first supine
    - Create Setup Beams: true
    - Nb. de fractions: 13fx
    - Le Beam Set est designé Dependent sur la dose du set A1

3. Une préscription est ajoutée au Beam Set A1
    - Rx au volume PTV A2-RECTUM
    - 24.7 Gy désiré à 99.5 % du volume


.. rubric::
  V. AJOUT D'UN ARC TOTAL ET REGLAGE DES PARAMETRES D'OPTIMISATION VMAT

1. Un arc total est ajouté
    - Nom: A2.1
    - Description: Arc 181-180
    - Isocentre: ISO ou ISO SCAN
    - Angles gantry: de 181 à 180
    - Rotation: clockwise
    - Collimateur: 5 deg

2. Set Optimization Parameters
    - Fluence Iterations: 60
    - Total Iterations: 100
    - Stopping Tolerance: 1e-9
    - Compute Intermediate Dose et Compute Final Dose: true

3. Set VMAT Conversion Parameters
    - Max leaf travel per degree: 0.1 cm
    - Constrain Leaf Motion: true
    - Gantry Spacing: 4 deg
    - Max delivery time: 150s


.. rubric::
  VI. AJOUT DES OBJECTIFS D'OPTIMISATION

=====================  =============  ================  ===========  ===================
ROI                    Dépendence     Type de critère   Poids        Valeur
=====================  =============  ================  ===========  ===================
PTV A2-RECTUM          BeamSet        ``mindose``       100          24.7 Gy
PTV A2                 BeamSet        ``maxdose``       10           27.3 Gy
RECTUM                 BeamSet+Bkg    ``maxdvh``        10           75 Gy @ 15 %
RECTUM                 BeamSet+Bkg    ``maxdvh``        10           70 Gy @ 25 %
RECTUM                 BeamSet+Bkg    ``maxdvh``        10           65 Gy @ 35 %
RECTUM                 BeamSet+Bkg    ``maxdvh``        10           60 Gy @ 50 %
RECTUM                 BeamSet+Bkg    ``maxdose``       10           79.5 Gy
VESSIE                 BeamSet+Bkg    ``maxdose``       1            82 Gy
Body RS                BeamSet+Bkg    ``dosefalloff``   0            76 à 40 Gy en 3 cm
RECTUM ds PTV A2       BeamSet        ``mindose``       10           22.8 Gy
WALL RECT ds PTV A2    BeamSet        ``maxdose``       0            24.38 Gy
=====================  =============  ================  ===========  ===================


.. rubric::
  VII. AJOUT/MODIFICATION DES CLINICAL GOALS

1. Modification du clinical goal de la couverture du PTV A1 - de 76 Gy à 51.3 à 99.5 %
2. Ajout d'un clinical goal pour la couverture du PTV A2-RECTUM - 24.7 Gy à 99.5 %
3. Ajout d'un clinical goal pour la couverture du RECTUM ds PTV A2 - 22.8 Gy à 99.5 %
4. Modification du niveau de dose de référence pour l'affichage des isodoses - de 80 Gy à 26 Gy

"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.create_prostate_plan_A2_split()
