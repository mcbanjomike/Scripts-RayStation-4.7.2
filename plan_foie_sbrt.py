# -*- coding: utf-8 -*-
"""
.. rubric::
 Pré-requis :

- Un seul scan de planification nommé CT 1
- Il ne faut pas que les ROIs soient approuvés
- ROI :

  * PTV*x*:*y* où *x* est la dose de prescription en Gy et *y* et le nombre de fractions (ex. : *PTV37.5:3* ou *PTV50:5*)
  * FOIE EXPI
  * GTV
  * Table
  * ISO SCAN ou ISO PT PRESC

- ROI facultatifs :

  * MOELLE
  * COLON, GRELE, DUODENUM, ESTOMAC, OESOPHAGE
  * COTES
  * REIN DRT et REIN GCHE
  * PAROI OESO OPP

.. rubric::
 Étapes :

1. Identification des points

- Si un point ISO PT PRESC est trouvé, il est renommé ISO SCAN
- Le script auto_assign_poi_types est roulé

2. Contours

- Les rois sont assignés des types (similaire au script auto_assign_roi_types)
- Le contour BODY est renommé BODY Pinnacle
- Le contour Body+Table est supprimé
- Un nouveau contour externe est généré par RayStation avec le nom BodyRS (sauf si ce contour existe déjà)
- BodyRS+Table est créé et désigné le contour External (sauf s'il y avait déjà un contour BodyRS-Table en partant)
- Les contours d'optimisation sont créés:

  * PTV+0.2cm, PTV+0.5cm, PTV+2cm et PTV+4cm
  * Ring_1_0mm (de 0 à 2mm), Ring_2_2mm (de 2 à 5mm), Ring_3_5mm (de 5mm à 2cm) et Ring4_20mm (de 2 à 4cm)
  * TISSU SAIN A 2cm et TISSU SAIN A 4cm
  * PEAU (5mm à l'intérieure de BodyRS)
  * FOIE EXPI-GTV et PTV-GTV
  * prv5mmMOELLE (si MOELLE présent) et REINS (combinaison de REIN D et REIN G si présents)

- Tout override de matériel est enlevé des ROIs

3. Plan et BeamSet

- Un plan nommé "Stereo Foie" est créé sur le scan CT 1
- Un BeamSet nommé "Stereo" est ajouté avec les paramètres:

  * Modality: Photons
  * Technique: VMAT
  * Machine: Salle 11
  * Position: Head First Supine
  * 3 ou 5 fractions (selon le nom du ROI PTVx:y)
  * 100% de la dose de prescription prescrit à 95% du volume du PTV

4. Beams et parametres d'optimisation

- Le script add_beams_prostate_A1 est roulé (crée un seul arc)
- Le script set_optimization_parameters est roulé
- Le script set_vmat_conversion_parameters est roulé

5. Objectifs et clinical goals

- Le script smart_cg_foie_sbrt est roulé

  * Le script génère et les objectifs et les clinical goals à la fois
  * CG et objectifs dépendent sur la distance des organes à risque du PTV
  * Quand un OAR se trouve près (ou dans) du PTV, un critère de max dose 0.1cc est aussi ajouté
    sur la partie de l'organe qui est à plus de 2cm du PTV
  * Quand un OAR se trouve près (ou dans) du PTV, le script créé des contours OAR dans PTV,
    OAR hors PTV, OAR dans PTV+2cm et/ou OAR hors PTV+2cm pour aider dans l'optimisation.
    Généralement, ces contours n'auront pas d'objectifs d'optimisation d'emblé, mais le planificateur
    peut les rajouter si il ou elle juge que ça sera aidant.

6. Dose Color Table

- Selon le prescription, la Reference Dose est ajustée
- Les isodoses de 120%, 100%, 95%, 80%, 50%, 10Gy et 5Gy sont créés

7. Gestion des contours et points

- Le préfix "vide_" est ajouté a n'importe quel contour qui n'est pas dessiné
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
import foie

with lib.RSScriptWrapper(__file__):
    foie.plan_foie_sbrt()