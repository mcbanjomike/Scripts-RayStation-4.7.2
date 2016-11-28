# -*- coding: utf-8 -*-
"""
.. rubric::
 Pré-requis :

- Un seul scan de planification nommé CT 1
- Il ne faut pas que les ROIs soient approuvés
- ROI :

  * PTV18
  * Table
  * ISO SCAN, REF SCAN ou ISO PT PRESC (seulement un point dans cette liste)

- ROI facultatifs :

  * MOELLE
  * QUEUE CHEVAL
  * REIN DRT et REIN GCHE
  * POUMON DRT et POUMON GCHE
  * OESOPHAGE
  * COEUR
  * PLEXUS BRACHIAL, PLEXUS SACRAL, PLEXUS LOMBAIRE
  * GROS VAISSEAUX
  * TRACHEE
  * LARYNX
  * ESTOMAC, DUODENUM, JEJUNUM, ILEON, COLON, RECTUM

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

  * PTV+0.5cm, PTV+5.5cm et PTV+10.5cm (effacés après la création des Rings et TS)
  * Ring_5mmmm (de 0 à 5mm), TS1 (de 0.5 à 5.5cm) et TS2 (de 5.5cm à 10.5cm)
  * PEAU (5mm à l'intérieure de BodyRS)
  * BODY-PTV
  * prv5mmMOELLE, MOELLE PARTIELLE et OPT PTV (si MOELLE présent)
  * REINS (combinaison de REIN DRT et REIN GCHE si présents)
  * COMBI PMNS (combinaison de POUMON DRT et POUMON GCHE si présents)

- Tout override de matériel est enlevé des ROIs

3. Plan et BeamSet

- Un plan nommé "Stereo Vertebre" est créé sur le scan CT 1
- Un BeamSet nommé "Stereo" est ajouté avec les paramètres:

  * Modality: Photons
  * Technique: VMAT
  * Machine: BeamMod
  * Position: Head First Supine
  * 1 fraction
  * 18Gy prescrit à 90% du volume du PTV

4. Beams et parametres d'optimisation

- Le script add_beams_vertebre_stereo est roulé (deux arcs totaux, un avec collimateur 90)
- Le script set_optimization_parameters est roulé
- Le script set_vmat_conversion_parameters est roulé

5. Objectifs et clinical goals

- Le script smart_cg_vertebre est roulé

  * Le script génère et les objectifs et les clinical goals à la fois
  * Les CGs sont tirés du dictionnaire commun CRITRES.txt

6. Dose Color Table

- Selon le prescription, la Reference Dose est ajustée
- Les isodoses de 120%, 100%, 95%, 80%, 50% et 5Gy sont créés

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

2. Ajoutez des overrides de matériel aux ROIs au besoin
  
"""

import setpath
import hmrlib.lib as lib
import foie

with lib.RSScriptWrapper(__file__):
    foie.plan_vertebre_sbrt()