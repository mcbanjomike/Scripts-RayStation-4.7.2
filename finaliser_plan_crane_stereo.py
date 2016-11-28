# -*- coding: utf-8 -*-
"""
DOCUMENTATION: finaliser_plan_crane_stereo

===========
Pré-réquis:
===========

Un point Dose Specification Point doit être présent dans le beamset
Le contour isodose 100% devrait exister avec le nom 15, 18 ou 20 (selon le prescription)
La dose doit être calculé
Un contour PTV15, PTV18 ou PTV20 doit exister


=======
Étapes:
=======

1. Contours renommés pour transfert Superbridge en ajoutant une étoile apres:
 - PTV15/PTV18/PTV20
 - TRONC CEREBRAL
 - MOELLE
 - OEIL DRT et OEIL GCHE
 - Les contours 15/18/20 (isodoses 100%) sont renommés ISO Presc 15Gy*/ISO Presc 18Gy*/ISO Presc 20Gy*

2. Beam set renommé "Stereo Crane" et commentaire "VMAT" est inscrit pour transfert Superbridge

3. PT PRESC est créé et le point est placé sur un voxel qui reçoit la dose par fraction (selon le 

prescription)

4. Le prescription est changé pour être sur le point PT PRESC

5. Le Dose Specification Point est placé sur les coordonnés du PT PRESC

6. La dose est recalculée (seulement pour que la dose au point Spec pour chaque arc s'affiche)

"""

import setpath
import hmrlib.lib as lib
import crane

with lib.RSScriptWrapper(__file__):
    crane.finaliser_plan_crane_stereo()