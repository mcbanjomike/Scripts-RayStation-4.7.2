# -*- coding: utf-8 -*-
"""
DOCUMENTATION: finaliser_plan_foie_sbrt

===========
Pré-réquis:
===========

Un point Dose Specification Point doit être présent dans le beamset
Le contour isodose 100% devrait exister avec comme nom la dose the prescription (eg 37.5 ou 50)
La dose doit être calculé
Un contour PTVx doit exister où x est la dose de prescription (eg PTV45 ou PTV 47.5) et ne doit pas être en voxels


=======
Étapes:
=======

1. Contours renommés pour transfert Superbridge en ajoutant une étoile apres:
 - Le PTVx
 - GTV EXPI
 - FOIE INSPI et FOIE EXPI
 - MOELLE et prv5mmMOELLE
 - REINS
 - ESTOMAC, COLON, DUODENUM, GRELE, et OESOPHAGE
 - Le contour isodoses 100% est renommé ISO Presc xGy*

2. Beam set renommé "Stereo" et commentaire "VMAT" est inscrit pour transfert Superbridge

3. PT PRESC est créé et le point est placé sur un voxel qui reçoit la bonne dose par fraction (selon le prescription)

4. Le prescription est changé pour être sur le point PT PRESC

5. Le Dose Specification Point est placé sur les coordonnés du PT PRESC

6. La dose est recalculée (seulement pour que la dose au point Spec pour chaque arc s'affiche)

"""

import setpath
import hmrlib.lib as lib
import foie

with lib.RSScriptWrapper(__file__):
    foie.finaliser_plan_foie_sbrt()