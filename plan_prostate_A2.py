# -*- coding: utf-8 -*-
"""
.. note::
  LA VERSION LA PLUS À JOUR DE CE DOCUMENT SE TROUVE DANS DRUPAL: `Planification des prostates vmat`_

.. _`Planification des prostates vmat`: http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

.. rubric::
  I. Introduction

Ce script à pour but de partir le plan A2 pour une prostate VMAT. Il est supposé que le plan A1
était fait avec le script plan_prostate_A1. Une fois que le planificateur est satisfait(e) du
1e plan, il ou elle peut démarrer ce script, qui fait les points suivants:

1. Changement du nom du 1e *beam set* à A1 et du nb. de fractions dans le plan A1 à 27
2. Ajout d'un *beam set* A2 avec un préscription de 26Gy en 13 fx et qui dépend sur la dose du *beam set* A1
3. Création d'un arc total dans le 2e *beam set*
4. Ajustement des reglages d'optimisation VMAT
5. Ajout des objectifs d'optimisation pour le plan A2
6. Ajout des clinical goals pour le plan A2
7. Ajustement du niveau de dose de référence à 26Gy pour l'affichage des isodoses

.. warning::
  IL EST FORTEMENT SUGGÉRÉ DE SAUVEGARDER LE PLAN AVANT DE ROULER CE SCRIPT. De plus, il est préférable de conserver
  le plan A1 seule jusqu'à la fin du travail, au cas où le planificateur désire d'essayer le plan A2 avec et sans split.
  Donc il est suggéré de copier le plan A1 seule et de rouler ce script dans la nouvelle copie.


.. rubric::
  II. Pré-requis

Avant de démarrer le script, le planificateur devrait être satisfait de son plan A1, fait à partir
du script plan_prostate_A1. Si le premier script d'est pas utilisé, il risque de manquer des
contours d'optimisation (surtout dans le cas d'un plan "split") et des clinical goals.

Donc, il est nécessaire d'avoir:

1. Un Plan avec un seul *beam set*
2. Un point ISO SCAN pour servir comme isocentre et point de localisation
3. Les contours suivants
    - PTV A1 (créé par le script plan_prostate_A1)
    - PTV A2 (créé par le script plan_prostate_A1)
    - BodyRS (créé par le script plan_prostate_A1)
    - RECTUM
    - VESSIE
4. Un clinical goal du type Volume at Dose sur le *PTV A1* (créé par le script plan_prostate_A1)


.. rubric::
  III. Modification/création des *beam sets*

1. Changement du nom du 1er *beam set* à *A1* et modification du nb. de fractions du 1er *beam set* à 27
2. Ajout d'un 2e *beam set* nommé *A2*
    - Machine: Salle 11
    - Modalité: photons
    - Technique: VMAT
    - Position: *Head-first supine*
    - *Create Setup Beams*: *true*
    - Nb. de fractions: 13fx
    - Le *beam set* est designé dépendant sur la dose du *set* *A1*
3. Une préscription est ajoutée au *beam set* *A1*
    - Rx au volume *PTV A2*
    - 24.7 Gy désiré à 99.5% du volume


.. rubric::
  IV. Ajout d'un arc total et réglage des paramètres d'optimisation VMAT

1. Un arc total est ajouté
    - Nom: A2.1
    - Description: Arc 181-180
    - Isocentre: *ISO* ou *ISO SCAN*
    - Angles bras: de 181 à 180
    - Rotation: *clockwise*
    - Collimateur: 5 deg

2. *Set Optimization Parameters*
    - *Fluence Iterations*: 60
    - *Total Iterations*: 100
    - *Stopping Tolerance*: 1e-9
    - *Compute Intermediate Dose* et *Compute Final Dose*: *true*

3. *Set VMAT Conversion Parameters*
    - *Max leaf travel per degree*: 0.1 cm
    - *Constrain Leaf Motion*: *true*
    - *Gantry Spacing*: 4 deg
    - *Max delivery time*: 150 s


.. rubric::
  V. Ajout des objectifs d'optimisation

=========  ===========      ================  ===========  ===================
ROI        Dépendence       Type de critère   Poids        Valeur
=========  ===========      ================  ===========  ===================
PTV A2     BeamSet          ``mindose``       100          24.7 Gy
PTV A2     BeamSet          ``maxdose``       10           27.3 Gy
RECTUM     BeamSet+Bkg      ``maxdvh``        10           75 Gy @ 15%
RECTUM     BeamSet+Bkg      ``maxdvh``        10           70 Gy @ 25%
RECTUM     BeamSet+Bkg      ``maxdvh``        10           65 Gy @ 35%
RECTUM     BeamSet+Bkg      ``maxdvh``        10           60 Gy @ 50%
RECTUM     BeamSet+Bkg      ``maxdose``       10           79.5 Gy
VESSIE     BeamSet+Bkg      ``maxdose``       1            82 Gy
Body RS    BeamSet+Bkg      ``dosefalloff``   0            76 à 40 Gy en 3 cm
=========  ===========      ================  ===========  ===================

.. rubric::
  VI. Ajout/modification des *clinical goals*

1. Modification du clinical goal de la couverture du PTV A1 - de 76 Gy à 51.3 à 99.5%
2. Ajout d'un clinical goal pour la couverture du PTV A2 - 24.7 Gy à 99.5%
3. Modification du niveau de dose de référence pour l'affichage des isodoses - de 80 Gy à 26 Gy
    
"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.create_prostate_plan_A2()