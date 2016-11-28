# -*- coding: utf-8 -*-
"""
    Ajoute les arcs utilisés pour la stéréo de crâne.

    .. rubric::
      EMPLACEMENT :
    
    - *Plan Design*
        - *Scripting*
            - *Module specific scripts*

    Assume qu'il y a un seul PTV.

    Par défaut, ajoute des arcs allant de :

    - 181 à 180 degrés en CW avec collimateur de 5 degrés
    - 180 à 181 degrés en CCW avec collimateur de 355 degrés

    .. rubric::
      PRÉ-REQUIS :

    - Isocentre nommé *ISO SCAN* ou *ISO*.

    .. seealso::
      fonction :py:func:`beams.add_beams_brain_stereo`
"""

import setpath
import hmrlib.lib as lib
import beams

with lib.RSScriptWrapper(__file__):
    beams.add_beams_brain_stereo()
