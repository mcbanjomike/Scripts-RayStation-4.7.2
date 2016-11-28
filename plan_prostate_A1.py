# -*- coding: utf-8 -*-
"""
.. note::
  LA VERSION LA PLUS À JOUR DE CE DOCUMENT SE TROUVE DANS DRUPAL: `Planification des prostates vmat`_

.. _`Planification des prostates vmat`: http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

.. rubric::
  I. Introduction

Ce script à pour but de partir un plan de prostate VMAT en faisant les étapes suivantes:

1. Création d'un nouveau contour externe et d'un contour de contraste modifié
2. Création de contours pour l'optimisation en RayStation
3. Ajout d'un Treatment Plan et d'un Beam Set avec préscription de 80Gy en 40fx
4. Création d'un arc total
5. Ajustement des reglages d'optimisation VMAT
6. Ajout des objectifs d'optimisation pour le plan A1
7. Ajout des clinical goals pour le plan A1
8. Attribution des types de POIs
9. Création du Dose Color Table

.. note::
 IMPORTANT : Le script ne peut pas changer le matériel dans le contour Contraste Mod (voir section II),
 alors ça doit être fait à la main. Il faut aussi faire "Remove holes (on all slices)" sur le contour
 BodyRS+Table avant de démarrer l'optimisation.


.. rubric::
  II. Pré-requis

Avant de démarrer le script, il faut s'assurer que le patient dans RayStation comprend:
    1. Un scan de planification
    2. Un point nommé ISO PT PRESC pour servir comme isocentre et point de localization
    3. Les ROIs de base pour les volumes à traiter:
        - PTV 1cm (prostate + marge de 1cm sauf en post [7mm])
        - PTV VS (vésiclues + marge)
    4. Les ROIs pour les organes à risques:
        - RECTUM
        - VESSIE
        - INTESTINS (facultatif)
        - TETE FEMORALE DRT et TETE FEMORALE GCHE (facultatifs)
        - CONTRASTE (facultatif)
    5. Le ROI Table (créé au scan)
        

.. rubric::
  III. Modification des contours

1. Suppression du contour Body+Table et modification du nom du contour BODY
    Le contour Body+Table de Pinnacle est effacé, si présent. Le contour BODY est renommé BODY Pinnacle pour le distinguer du nouveau contour
    BodyRS créé dans la prochaine étape.  
  
2. Création d'un nouveau contour External
    Pour éviter des problèmes de calcul dans RayStation (causés par des boucles dans le contour externe), un contour BodyRS est créé avec les outils
    de RayStation. Ensuite, le contour BodyRS+Table est créé en prenant la somme de BodyRS et la table importé de Pinnacle. Ce contour est ensuite
    désigné le contour externe, mais avant de lancer une optimisation is faut utiliser le fonction "Remove holes (on all slices)" sur le ROI.
    
3. Modification du contour CONTRASTE (seulement si le contour existe)
    * RayStation refuse de calculer la dose si il y a un contour avec un override de matériel qui sort du contour External.  Pour éviter ce problème, le script:
        - Crée un contour Contraste Mod de type "ContrastAgent" qui est l'intersection des contours BodyRS et CONTRASTE
        - Enlève l'override de materiel sur l'ancien contour CONTRASTE
        - Il est important de faire un override de materiel sur le contour Contraste Mod avec de l'eau, mais comme ça ne peut pas être scripté, le planificateur
          doit le faire à la main.

4. Création des PTVs A1 et A2
    - PTV A1 est créé de l'union des ROIs PTV 1cm et PTV VS (NB que si un contour PTV A1 existe déjà, cette étape est sautée)
    - PTV A2 est une copie de PTV VS

5. Créations des contours d'optimisation
    - RECTUM ds PTV A1
    - RECTUM ds PTV A2
    - WALL RECTUM (un ring qui s'étend 2mm vers l'intérieur et 2mm vers l'extérieur du contour RECTUM)
    
6. Changement du nom du POI "ISO PR PRESC" à "ISO SCAN" (pour faciliter l'assignation du point de localization plus bas)

.. rubric::
  IV. Ajout du plan et du *beam set*

1. Un plan nommé A1 seul est créé

2. Un Beam Set nommé A1 est créé dans le plan A1 seul
    - Machine: Salle 11
    - Modalité: photons
    - Technique: VMAT
    - Position: Head-first supine
    - Create Setup Beams: true
    - Nb. de fractions: 40fx
    
3. Une préscription est ajoutée au Beam Set A1
    - Rx au volume PTV A1
    - 76 Gy désiré à 99.5% du volume


.. rubric:: 
  V. Ajout d'un arc total et réglage des paramètres d'optimisation VMAT

1. Un arc total est ajouté
    - Nom: A1.1
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
  VI. Ajout des objectifs d'optimisation

===================  ================  ===========  ======================
ROI                  Type de critère   Poids        Valeur
===================  ================  ===========  ======================
PTV A1               ``mindose``       100          76 Gy
PTV A1               ``maxdose``       10           83 Gy
RECTUM               ``maxdvh``        10           75 Gy @ 15%
RECTUM               ``maxdvh``        10           70 Gy @ 25%
RECTUM               ``maxdvh``        10           65 Gy @ 35%
RECTUM               ``maxdvh``        10           60 Gy @ 50%
RECTUM               ``maxdose``       10           79.5 Gy
VESSIE               ``maxdose``       1            82 Gy
Body RS              ``dosefalloff``   0            76 à 40 Gy en 3 cm
===================  ================  ===========  ======================


.. rubric::
  VII. Ajout des *clinical goals*

===================  ===================  ============================
ROI                  Type de critère      Valeur
===================  ===================  ============================
PTV A1               ``Volume at Dose``   au moins 99.5% à 76 Gy
PTV A1               ``Dose at Volume``   maximum de 88 Gy à 0.1cc
INTESTINS            ``Volume at Dose``   maximum de 65cc à 45 Gy
INTESTINS            ``Volume at Dose``   maximum de 100cc à 40 Gy
INTESTINS            ``Volume at Dose``   maximum de 180cc à 35 Gy
INTESTINS            ``Dose at Volume``   maximum de 50Gy à 0.1cc
RECTUM               ``Volume at Dose``   maximum de 15% à 75 Gy
RECTUM               ``Volume at Dose``   maximum de 25% à 70 Gy
RECTUM               ``Volume at Dose``   maximum de 35% à 65 Gy
RECTUM               ``Volume at Dose``   maximum de 50% à 60 Gy
RECTUM               ``Dose at Volume``   maximum de 75 Gy à 15%
RECTUM               ``Dose at Volume``   maximum de 80 Gy à 0.1cc
TETE FEMORALE GCHE   ``Volume at Dose``   maximum de 10% à 52 Gy
TETE FEMORALE GCHE   ``Dose at Volume``   maximum de 60 Gy à 0.1cc
TETE FEMORALE DRT    ``Volume at Dose``   maximum de 10% à 52 Gy
TETE FEMORALE DRT    ``Dose at Volume``   maximum de 60 Gy à 0.1cc
VESSIE               ``Volume at Dose``   maximum de 15% à 80 Gy
VESSIE               ``Volume at Dose``   maximum de 25% à 75 Gy
VESSIE               ``Volume at Dose``   maximum de 35% à 70 Gy
VESSIE               ``Volume at Dose``   maximum de 50% à 65 Gy
===================  ===================  ============================


.. rubric::
  VIII. Attribution des types de POI

Fait avec le script :py:func:`hmrlib.poi.auto_assign_poi_types` de VTL
    - Cherche un point avec SCAN dans son nom et le désigne comme point de localization
    - Si aucun point ne contient SCAN dans son nom, l'isocentre est choisi comme point de localization  


.. rubric::
  IX. Création du *dose color table*

Le dose color table est généré. Comme ça fait planter RayStation quand on demande de créé un isodose qui existe déjà dans le dose color table,
j'ai décidé d'inclure dès le départ l'isodose de 87.7%, utilisé dans les plans A2 Split. Le planificateur peut l'effacer s'il ou elle juge que
ce n'est pas nécessaire pour leur plan.

"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.create_prostate_plan_A1()