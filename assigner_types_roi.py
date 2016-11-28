# -*- coding: utf-8 -*-
"""
Ce script tente d'auto-assigner le bon type de ROI pour chacun des ROI
présentement définis pour le patient.

.. rubric::
  EMPLACEMENT :

- *Patient Modeling*
    - *Scripting*
        - *Module specific scripts*

Le script se fie au nom des ROI.  Il est tolérant face aux espaces insérés
dans les noms.  De plus, il ne fait pas attention à la casse.

Ainsi, *Ptv 48* pourra être automatiquement identifé comme PTV et assigné au
type *Target*.

Assigne les contours contenant *PTV*, *GTV* et *ITV* dans leur nom comme étant de
type *Target*.  *Cependant, les contours dont le nom contient le caractère "-",
comme CERVEAU-PTV ne sont pas assigné au type target.*

Assigne *BODY+TABLE* comme contour externe (*external*).  Assigne *BODY* comme
*external* si et seulement si *BODY+TABLE* n'existe pas.

Assigne tout contour dont le nom commence par *BOLUS* comme étant de type
*Bolus*.

Tous les autres contours sont assignés au type *Organ at risk* par défaut.

.. rubric::
  PRÉ-REQUIS :

- ROI de PTV nommé selon les conventions habituelles, contenant la chaîne de caractères *PTV*.  Ex. : *PTV*, *PTV15*, *PTV 48*.
- GTV, CTV, ITV nommé avec des nom contenant ces chaînes de caractères.
- Contour externe nommé *BODY+TABLE* ou *BODY*.
- Nom d'un ROI bolus commençant par la chaîne de caractères *BOLUS*.

.. seealso::
  fonction :py:func:`hmrlib.roi.auto_assign_roi_types`
"""
import setpath
import hmrlib.lib as lib
import hmrlib.roi as roi

with lib.RSScriptWrapper(__file__):
    roi.auto_assign_roi_types()
