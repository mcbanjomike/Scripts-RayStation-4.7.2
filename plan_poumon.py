# -*- coding: utf-8 -*-
"""
.. rubric::
 Pré-requis:

- ROI :

  + Table:*xx* (où *xx* est le nombre de fractions, ex. : *Table:30*)

- Un ou deux PTV parmi cette liste :

  + PTV66 et CTV66 (toujours avec PTV60/CTV60)
  + PTV60 et CTV60
  + PTV55 et CTV55 (avec ou sans PTV50/CTV50)
  + PTV50 et CTV50
  + PTV40.05 et CTV40.05

- Un seul scan nommé "CT1"

- Un point ISO SCAN ou REF SCAN

- ROI facultatifs:
  + MOELLE
  + TR CEREBRAL
  + POUMON DRT
  + POUMON GCHE
  + COEUR
  + COTES
  + PL BRACHIAL


.. rubric::
 Étapes :

1. Générale

- Si un point REF SCAN existe, il est renommé ISO SCAN
- Le script auto_assign_poi_types est roulé
- Le script examine le contour Table pour déterminer le nombre de fx et remet son nom à "Table"

2. Contours

- Les rois sont assignés des types (similaire au script auto_assign_roi_types)
- Le contour BODY est renommé BODY Pinnacle
- Le contour Body+Table est supprimé
- Un nouveau contour externe est généré par RayStation avec le nom BodyRS
- BodyRS+Table est créé et désigné le contour External
- Les PTVs et leurs niveaux de doses sont identifiés
- Les contours d'optimisation sont créés:

  + PTVs avec expansions (pour aider dans la création des contours d'optimisation)
  + modPTVs, OPTPTVs, PTV-CTVs, Gradients, Rings et Tissus Sains (selon fichier Excel pour les scripts de Pinnacle)
  + prv5mmMOELLE, presMOELLE et BLOC MOELLE
  + COMBI PMNS et PMNS-PTV

- Les PTVs avec expansions sont éffacés (ainsi que les contours temp1,temp2,temp3)
- Tout override de matériel est enlevé des ROIs
- Le préfix "vide_" est ajouté devant le nom de tout ROI qui n'a pas de contour associé

3. Plan et BeamSet

- Un plan nommé "Poumon" est créé sur le scan CT 1
- Un BeamSet nommé "Trial 1" est ajouté avec les paramètres:

  + Modality: Photons
  + Technique: VMAT
  + Machine: Salle 6
  + Position: Head First Supine
  + Nb de fractions selon ce qui était écrit dans le nom du ROI Table
  + Prescription selon le PTV le plus haut
  + 100% de la dose de prescription prescrit à 98% du volume du PTV plus haut

4. Beams et parametres d'optimisation

- Le script add_beams_prostate_A1 est roulé (TEMPORAIRE)
- Le script set_optimization_parameters est roulé
- Le script set_vmat_conversion_parameters est roulé avec un temps maximum de 150s par arc

5. Objectifs et clinical goals

- Le script smart_cg_poumon est roulé
- Les *clinical goals* sont tirés du dictionnaire de critères de GJ
- Les objectifs d'optimisation sont selon le classeur Excel pour les scripts de Pinnacle

6. Dose Color Table

- Selon le prescription, la *Reference Dose* est ajustée
- Les isodoses sont créés pour les niveaux suivants :

  + 110% de la dose de prescription
  + 100% pour le PTV le plus haut
  + S'il y a deux PTVs, la dose 100% pour le 2e PTV est ajoutée
  + 75%
  + 20 Gy
  + 10 Gy

7. Gestion des points

- Les points autre que ISO, ISO SCAN et REF SCAN sont effacés

.. rubric::
 Après que le script se termine :

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
import poumon

with lib.RSScriptWrapper(__file__):
    poumon.plan_poumon()