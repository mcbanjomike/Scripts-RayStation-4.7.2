# -*- coding: utf-8 -*-
"""
DOCUMENTATION: finaliser_plan_poumon_sbrt

===========
Pré-réquis:
===========

Un point Dose Specification Point doit être présent dans le beamset
Le contour isodose 100% devrait exister avec le nom 48, 54 ou 60 (selon le prescription)
La dose doit être calculé
Le scan de planification doit s'appeler CT 2
Un contour PTV48, PTV54 ou PTV60 doit exister (et ne doit pas être en voxels)


=======
Étapes:
=======

1. Contours renommés pour transfert Superbridge en ajoutant une étoile apres:
 - PTV48/PTV54/PTV60
 - ITV48/ITV54/ITV60
 - GTV expi
 - MOELLE
 - 48/54/60 (isodoses 100%) sont renommés ISO Presc 48Gy*/ISO Presc 54Gy*/ISO Presc 60Gy*

2. Beam set renommé "2arcs" et commentaire "VMAT" est inscrit pour transfert Superbridge

3. PT PRESC est créé et le point est placé sur un voxel qui reçoit la dose par fraction (selon le 
prescription)

4. Le prescription est changé pour être sur le point PT PRESC

5. Le Dose Specification Point est placé sur les coordonnés du PT PRESC et le DSP est associé avec les 2 arcs

6. La dose est recalculée (seulement pour que la dose au point Spec pour chaque arc s'affiche)

"""

import setpath
import hmrlib.lib as lib
import poumon

with lib.RSScriptWrapper(__file__):
    poumon.finaliser_plan_poumon_sbrt()