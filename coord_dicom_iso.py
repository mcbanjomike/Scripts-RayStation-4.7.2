# -*- coding: utf-8 -*-
"""
Ce script affiche à l'écran les coordonnées DICOM de l'isocentre.

.. rubric::
  EMPLACEMENT :

- *Scripting*
    - *General scripts*

.. rubric::
  PRÉ-REQUIS :

- Assume que l'isocentre est nommé selon les conventions habituelles :
  *PTV<niveau de dose>*.

.. seealso::
  fonctions :py:func:`hmrlib.poi.identify_isocenter_poi`, :py:func:`hmrlib.poi.show_poi_coordinates`
"""
import setpath
import hmrlib.lib as lib
import hmrlib.poi as poi

with lib.RSScriptWrapper(__file__):
    iso_name = poi.identify_isocenter_poi()
    poi.show_poi_coordinates(iso_name)
