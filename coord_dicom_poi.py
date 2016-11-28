# -*- coding: utf-8 -*-
"""
Ce script affiche à l'écran les coordonnées DICOM de tous les POI.

.. rubric::
  EMPLACEMENT :

- *Scripting*
    - *General scripts*

.. seealso::
  fonction :py:func:`hmrlib.poi.show_all_poi_coordinates`
"""
import setpath
import hmrlib.lib as lib
import hmrlib.poi as poi

with lib.RSScriptWrapper(__file__):
    poi.show_all_poi_coordinates()
