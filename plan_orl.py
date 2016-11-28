# -*- coding: utf-8 -*-
"""
Ce script est destiné à la planification des cas d'ORL pour un des trois prescriptions suivants:

* 70 - 59.4 - 54 Gy en 33 fx
* 66 - 59.4 - 54 Gy en 33 fx
* 70 - 63 - 56 Gy en 35 fx

Le nombre de fractions est déterminé par la présence d'un PTV54 ou PTV56.

.. rubric::
 Pré-requis :

- PTV :

  + Trois PTVs correspondant à une des options suivantes:

    * PTV70, PTV60, PTV54
    * PTV66, PTV60, PTV54
    * PTV70, PTV63, PTV54

.. note::
 (les plans à quatre niveaux de dose ne sont pas encore supportés)

- ROI :

  + Table

- POI :

  + ISO SCAN ou REF SCAN

- 1 seul scan nommé CT1

- ROI facultatifs :

  + MOELLE
  + TR CEREBRAL
  + PARO DRT
  + PARO GCHE
  + CAVITE ORALE
  + LARYNX
  + OESOPHAGE
  + MANDIBULE
  + LEVRES
  + PL BRACHIAL DRT
  + PL BRACHIAL GCHE
  + N OPT DRT
  + N OPT GCHE
  + CHIASMA
  + CERVEAU

.. rubric::
 Étapes :

1. Générale

- Si un point REF SCAN existe, il est renommé ISO SCAN
- Le script auto_assign_poi_types est roulé

2. Contours

- Les rois sont assignés des types (similaire au script auto_assign_roi_types)
- Le contour BODY est renommé BODY Pinnacle
- Le contour Body+Table est supprimé
- Un nouveau contour externe est généré par RayStation avec le nom BodyRS
- BodyRS+Table est créé et désigné le contour External
- Les PTVs et leurs niveaux de doses sont identifiés
- Les contours d'optimisation sont créés:

  + BodyRS-5mm
  + PTVs avec expansions (pour aider dans la création des contours d'optimisation)
  + modPTVs, optPTVs, Gradients, Rings et Tissus Sains (selon fichier Excel pour les scripts de Pinnacle)
  + prv5mm pour les contours MOELLE, TR CEREBRAL, N OPT DRT, N OPT GCHE et CHIASMA
  + OPT OARs (selon fichier Excel pour les scripts de Pinnacle)
  + MAND ds PTV(haute dose) et MAND-PTVs
  + PBD/PBG ds PTV pour les deux niveaux de doses supérieures

- Les PTVs avec expansions sont éffacés (ainsi que les contours temp1,temp2,temp3)
- Tout override de matériel est enlevé des ROIs
- Le préfix "vide_" est ajouté devant le nom de tout ROI qui n'a pas de contour associé

3. Plan et BeamSet

- Un plan nommé "ORL" est créé sur le scan CT 1
- Un BeamSet nommé "Trial 1" est ajouté avec les paramètres:

  + Modality: Photons
  + Technique: VMAT
  + Machine: Salle 1
  + Position: Head First Supine
  + Nb de fractions et dose de prescription selon les PTVs
  + 100% de la dose de prescription prescrit à 95% du volume du PTV plus haut

4. Beams et parametres d'optimisation

- Le script add_beams_prostate_A1 est roulé (TEMPORAIRE)
- Le script set_optimization_parameters est roulé
- Le script set_vmat_conversion_parameters est roulé avec un temps maximum de 120s par arc

5. Objectifs et clinical goals

- Le script smart_cg_orl est roulé

6. Dose Color Table

- Selon le prescription, la *Reference Dose* est ajustée
- Les isodoses sont créés pour les niveaux suivants:

  + 105% de la dose de prescription
  + 100% pour chacun des doses des 3 PTVs
  + 45 Gy
  + 20 Gy
  + 10 Gy

7. Gestion des points

- Les points autre que ISO, ISO SCAN et REF SCAN sont effacés

.. rubric::
 Après que le script se termine:

1. Vérifiez:

- ROIs
- POIs
- prescription (salle, technique, nb de fractions, dose)
- dose grid resolution
- arcs (coordonnés de l'isocentre, angle initial et angle final, collimateur, énergie)
- objectifs d'optimisation
- clinical goals
- paramêtres d'optimisation (itérations, constrain leaf motion, temps max par arc)

2. Faites "Remove Holes (All Slices)" sur le contour BodyRS+Table
 
3. Ajoutez des overrides de matériel aux ROIs au besoin
  
"""

import setpath
import hmrlib.lib as lib
import orl

with lib.RSScriptWrapper(__file__):
    orl.plan_orl()