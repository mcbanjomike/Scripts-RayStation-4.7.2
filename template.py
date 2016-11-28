#-*- coding: utf-8 -*-
"""
Template de script pour importation dans RayStation.

Garder les scripts importés dans RS le plus simple possible en appelant des
fonctions définies dans s'autres fichiers enregistrés sous
Departements/Physiciens/TPS/RayStation/Scripts.dev (développement)
et Departements/Physiciens/TPS/RayStation/Scripts (production).
"""

import setpath

import hmrlib.lib as lib
# autres import ici
# par exemple :
# import hmrlib.roi as roi

with lib.RSScriptWrapper(__file__):
	# Les appels de fonctions vont ici
	pass