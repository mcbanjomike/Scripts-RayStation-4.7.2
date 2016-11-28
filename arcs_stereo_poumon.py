#-*- coding: utf-8 -*-
"""
    Ajoute les arcs utilisés en stéréo de poumon.

    .. rubric::
      EMPLACEMENT : 

    - *Plan Design*
        - *Scripting*
            - *Module specific scripts*

    Assume qu'il n'y a qu'un seul PTV.

    Détecte s'il s'agit d'un poumon droit ou gauche si le poumon
    contralatéral n'est pas spécifié.

    Par défaut, des arcs allant de :

    - 181 à 30 degrés en CW, puis de 30 à 181 degrés en CCW pour les traitements du poumon droit;
    - 330 à 180 degrés en CW, puis de 180 à 330 degrés en CCW pour les traitements du poumon gauche;

    seront ajoutés, avec un collimateur de 5 et 355 degrés pour l'arc CW et CCW, respectivement.

    .. rubric::
      PRÉ-REQUIS :

    - Isocentre nommé *ISO SCAN* ou *ISO*.
    - ROI poumons nommés *POUMON G* et *POUMON D*.
    - ROI PTV nommé selon la convention habituelle : *PTV<niveau de dose en Gy>*.

    .. seealso::
      fonction :py:func:`beams.add_beams_lung_stereo`
"""

import setpath
import hmrlib.lib as lib
import beams

with lib.RSScriptWrapper(__file__):
    beams.add_beams_lung_stereo()
