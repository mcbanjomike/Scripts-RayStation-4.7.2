# -*- coding: utf-8 -*-
"""
.. warning::
 Ce script ne devrait pas être utilisé pour des réirradiations, car le script suppose qu'il
 n'y a pas eu de plan précédent dans le patient RayStation. Éventuellement, le script sera mis à jour pour
 permettre les planifs sur des patients déjà irradiés.

Le script n'est pas conçu pour les cas avec 2 ptvs, mais si la dose prescrit aux deux est la même et s'ils
sont traités en même temps, il devrait marcher tant que le planificateur créé un seul ROI qui combine les PTVs
avec un nom supporté par le script (voir dans la section Pré-requis).

.. rubric::
 Pré-requis :

- Scan de planification nommé CT 1
- Il ne faut pas que les ROIs soient approuvés
- ROI :

  * PTV15 ou PTV18 ou PTV20
  * CERVEAU
  * ISO SCAN ou ISO PT PRESC

- ROI facultatifs :

  * CHIASMA
  * MOELLE
  * TRONC CEREBRAL
  * NERF OPT DRT et NERF OPT GCHE
  * OREILLE D et OREILLE G
  * COCHLEE


.. rubric::
 Étapes :

1. Identification des points

 - Le script auto_assign_poi_types est roulé

2. Contours

 - Les rois sont assignés des types (similaire au script auto_assign_roi_types)
 - Le contour BODY est renommé BODY Pinnacle
 - Le contour Body+Table est supprimé
 - Un nouveau contour externe est généré par RayStation avec le nom BodyRS
 - BodyRS+Table est créé et désigné le contour External
 - Les contours d'optimisation sont créés:

   * PTV+3mm, PTV+11mm, PTV+21mm
   * RING_1_3mm (de 0 à 3mm), RING_2_8mm (de 3mm à 1.1cm), RING_3_1cm (de 1.1cm à 2.1cm)
   * CERVEAU-PTV et OPT CERVEAU-PTV

 - Tout override de matériel est enlevé des ROIs

3. Plan et BeamSet

 - Un plan nommé "Stereo Crane" est créé sur le scan CT 1
 - Un BeamSet nommé "Stereo Crane" est ajouté avec les paramètres:

   * Modality: Photons
   * Technique: VMAT
   * Machine: Salle 11
   * Position: Head First Supine
   * 1 fraction
   * 100% de la dose de prescription prescrit à 99% du volume du PTV

4. Beams et parametres d'optimisation

 - Le script add_beams_brain_stereo est roulé
 - Le script set_optimization_parameters est roulé
 - Le script set_vmat_conversion_parameters est roulé

5. Objectifs et clinical goals

 - Le script add_opt_obj_brain_stereo est roulé
 - Le script add_cg_brain_stereo est roulé

6. Dose Color Table

 - Selon le prescription, la Reference Dose est ajustée
 - Les isodoses de 120%, 100%, 95%, 80%, 10Gy et 5Gy sont créés

7. Gestion des contours et points

 - Le préfix "vide_" est ajouté a n'importe quel contour qui n'est pas dessiné
 - Les points autre que ISO, ISO SCAN et REF SCAN sont effacés


.. rubric::
 Après que le script se termine :

1. Vérifiez :

 - ROI
 - POI
 - prescription (salle, technique, nb de fractions, dose)
 - dose grid resolution
 - arcs (coordonnés de l'isocentre, angle initial et angle final, collimateur, énergie)
 - objectifs d'optimisation
 - clinical goals
 - paramêtres d'optimisation (itérations, constrain leaf motion, temps max par arc)

2. Faites "Remove Holes (All Slices)" sur le contour BodyRS+Table

3. Ajoutez des overrides de matériel aux ROI au besoin

"""

import setpath
import hmrlib.lib as lib
import crane

with lib.RSScriptWrapper(__file__):
    crane.plan_crane_stereo()