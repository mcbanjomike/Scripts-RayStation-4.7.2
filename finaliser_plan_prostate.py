# -*- coding: utf-8 -*-
"""
.. note::
  LA VERSION LA PLUS À JOUR DE CE DOCUMENT SE TROUVE DANS DRUPAL: `Planification des prostates vmat`_

.. _`Planification des prostates vmat`: http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

Ce script a comme but de finaliser un plan de prostate VMAT en faisant les étapes suivantes:

1. Le script renomme les deux *beam sets* A1 et A2
2. Deux points sont générés nommés PT PRESC A1 et PT PRESC A2
3. Chaque point de prescription est placé sur un point dans son *beam set* qui reçoit 2 Gy par fraction
4. Chaque *beam set* est prescrit à son point de prescription.
5. Pour chaque *beam set*, le *Dose Specification Point* (déjà créé par l'usager avant de rouler le script)
   est placé aux mêmes coordonnés que le point PT PRESC approprié et l'arc est associé avec le Dose Specification Point.
6. Une étoile (*) est ajouté à la fin du nom pour les contours PTV A1, PTV A2, PROSTATE, RECTUM,
    VESSIE et RECTO-SIGMOIDE pour aider avec le transfert via Superbridge.
7. Les contours d'isodose 95% sont renommés, eg 51.3 devient ISO 95% 51.3Gy*, pour le transfert via Superbridge.

Le script suppose que la prescription est de 2 Gy par fraction et les doses pour chacun des *beam sets*
sont définies en regardant le nombre de fractions.

.. warning::
  IL EST FORTEMENT CONSEILLÉ DE SAUVEGARDER LE PLAN ET DE ROULER LE SCRIPT DANS UNE NOUVELLE COPIE.
  Cela vous permettra de comparer la dose auto-prescrit avec la dose du plan final pour vérifier qu'il n'y
  a pas eu de changement.

.. rubric::
  PRÉ-RÉQUIS

- Deux *beam sets* dans le plan.
- Un point de spécification de dose existant dans chacun des *beam sets*.
- Les contours PTV A1 et PTV A2.
- La dose doit être calculée dans chacun des *beam sets*.
- Les contours d'isodose 95% devrait déjà exister avec les noms suivants: 51.3 (pour plan A1), 24.7 (plan A2 en 13 fx) OU
  22.8 (plan A2 en 12 fx)
- Les points PT PRESC A1 et PT PRESC A2 ne devrait pas déjà existé. S'ils existent déjà, le script
  devrait fonctionner, mais il y aura un message d'erreur que l'usager devrait fermer pour terminer le script.

"""

import setpath
import hmrlib.lib as lib
import prostate

with lib.RSScriptWrapper(__file__):
    prostate.finaliser_plan_prostate()