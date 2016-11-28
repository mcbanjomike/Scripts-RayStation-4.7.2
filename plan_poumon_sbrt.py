# -*- coding: utf-8 -*-
"""
.. warning::
  Ce script ne devrait pas être utilisé pour des réirradiations, car le script suppose qu'il
  n'y a pas eu de plan précédent dans le patient RayStation. Éventuellement, le script sera mis à jour pour 
  permettreles planifs sur des patients déjà irradiés.

.. rubric::
  Pré-requis:

- ROI :

  + PTV48 ou PTV54 ou PTV60
  + POUMON DRT
  + POUMON GCHE
  + Table

- POI :

  + ISO SCAN

- 2 scans nommés CT 1 (la phase expi) et CT 2 (average) - **NON NÉGOCIABLE**
- Il ne faut pas que les ROIs soient approuvés sur ni un ni l'autre des scans.
- Il faut que le scan CT 2 soit designé le *primary*.
- ROI facultatifs :

  + PEAU
  + BR SOUCHE
  + COTES
  + MOELLE
  + COEUR
  + OESOPHAGE
  + PLEXUS BRACHIAL
  + TRACHEE
  + PRV MOELLE
  + PRV PLEXUS
  + ESTOMAC
  + PAROI
  + BR SOUCHE PAROI OPP
  + OESO PAROI OPP
  + GROS VAISSEAUX

.. rubric::
  Étapes:

1. Générale

- Le Imaging System du scan CT 2 est changé pour HOST-7228
- Le script auto_assign_poi_types est roulé

2. Contours

- Les rois sont assignés des types (similaire au script auto_assign_roi_types)
- Le contour BODY est renommé BODY Pinnacle
- Le contour Body+Table est supprimé
- Un nouveau contour externe est généré par RayStation avec le nom BodyRS
- BodyRS+Table est créé et désigné le contour External
- Les contours d'optimisation sont créés:

  + PTV+3mm, PTV+1.3cm, PTV+2cm
  + RING_1 (de 0 à 3mm), RING_2 (de 3mm à 1.3cm), RING_3 (de 1.3cm à 2.8cm) et r50 (de 2 à 3cm)
  + PEAU (Inner Ring de 5mm sur BodyRS)
  + TISSU SAIN A 2cm (BodyRS - PTV+2cm)
  + COMBI PMN-ITV-BR ([POUMON D + POUMON G] - [ITV + BR SOUCHE])
  + OPT COMBI PMN ([POUMON D + POUMON G] - PTV)

- Tout override de matériel est enlevé des ROIs

3. Plan et BeamSet

- Un plan nommé "Stereo 2arcs" est créé sur le scan CT 2
- Un BeamSet nommé "2arcs" est ajouté avec les paramètres:

  + Modality: Photons
  + Technique: VMAT
  + Machine: Salle 11
  + Position: Head First Supine
  + Nb de fractions et dose de prescription selon le PTV
  + 100% de la dose de prescription prescrit à 95% du volume du PTV

4. Beams et parametres d'optimisation

- Le script add_beams_lung_stereo est roulé
- Le script set_optimization_parameters est roulé
- Le script set_vmat_conversion_parameters est roulé

5. Objectifs et clinical goals

- Le script add_opt_obj_lung_stereo est roulé
- Le script add_cg_lung_stereo est roulé

6. Dose Color Table

- Selon le prescription, la Reference Dose est ajustée
- Les isodoses de 120%, 100%, 95%, 50% et 25% sont créés, ainsi que l'isodose 5Gy

7. Gestion des contours et points

- Le préfix "vide_" est ajouté a n'importe quel contour qui n'est pas dessiné sur CT 1 et CT 2
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
    poumon.plan_poumon_sbrt()