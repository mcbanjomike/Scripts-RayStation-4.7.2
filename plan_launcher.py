# -*- coding: utf-8 -*-
"""
DOCUMENTATION: plan_launcher

Le plan launcher est une interface graphique utilisée pour partir un plan VMAT de parmi les types suivantes:

Prostate VMAT
Crâne stéréo
SBRT Poumon
SBRT Foie
SBRT Vertebre

Le launcher vérifie que les ROIs et POIs nécessaires sont présent et confirme le prescription (dose et nombre
de fractions) avant de rouler un le script de planification approprié. Si un element important est absent,
un avertissement sera affiché pour permettre à l'utilisateur de corriger le problème.


===================
PRÉ-RÉQUIS PAR SITE
===================

Dans tous les cas, il faut que les ROIs soient désapprouvés et en format "contour".

1. PROSTATE VMAT

Pour le premier plan (A1 sauf quand un plan 3DCRT existe déjà), le PTV est construit selon l'hierarchie suivante:

PTV A1
PTV 1.5 cm + PTV VS (si présent)
PTV 1cm + PTV VS (si présent)

Pour le deuxième plan (A2 sauf quand un plan 3DCRT existe déjà), l'hierarchie est:
PTVBoostX (eg, PTVBoost8 pour un boost de 8Gy)
PTV 1cm

Si aucun de ces contours est trouvé, le script ne pourrait pas se completer.

SCAN
 - Un scan avec le nom "CT 1"
 
ROIs CRITIQUES
 - Table
 - RECTUM
 - VESSIE

ROIs FACULTATIFS
 - INTESTINS
 - TETE FEMORALE DRT et TETE FERMORALE GCHE
 - CONTRASTE
 
POI
 - Un point avec le nom ISO SCAN, REF SCAN ou ISO PT PRESC
 - S'il y a un shift d'isocentre, un point avec le nom ISO ou ISOCENTRE pour l'isocentre et un point REF SCAN
   pour le point de localisation.
 

2. CRANE STEREO

SCAN
 - Un scan avec le nom "CT 1"
 
ROIs CRITIQUES
 - PTV15 ou PTV18
 - CERVEAU

ROIs FACULTATIFS
 - CHIASMA
 - MOELLE
 - TRONC CEREBRAL
 - NERF OPT DRT et NERF OPT GCHE
 - OREILLE DRT et OREILLE GCHE
 - COCHLEE
 
POI
 - Un point avec le nom ISO SCAN, REF SCAN ou ISO PT PRESC
 - S'il y a un shift d'isocentre, un point avec le nom ISO ou ISOCENTRE pour l'isocentre et un point REF SCAN
   pour le point de localisation.
 

3. SBRT POUMON

SCAN
 - Scan de planification (average) avec le nom "CT 1"
 - Scan de transfert (expiration) avec le nom "CT 2"
 - Il faut que le scan CT 1 soit désigné le *primary*
 
ROIs CRITIQUES
 - PTV48/PTV54/PTV56/PTV60/PTV A1/PTV B1
 - ITV48/ITV54/ITV56/ITV60/ITV A1/ITV B1
 - POUMON DRT
 - POUMON GCHE
 - Table

ROIs FACULTATIFS
 - PEAU
 - BR SOUCHE
 - COTES
 - MOELLE
 - COEUR
 - OESOPHAGE
 - PLEXUS BRACHIAL
 - TRACHEE
 - PRV MOELLE
 - PRV PLEXUS
 - ESTOMAC
 - PAROI
 - BR SOUCHE PAROI OPP
 - OESO PAROI OPP
 - GROS VAISSEAUX
 
POI
 - Un point avec le nom ISO SCAN, REF SCAN ou ISO PT PRESC
 - S'il y a un shift d'isocentre, un point avec le nom ISO ou ISOCENTRE pour l'isocentre et un point REF SCAN
   pour le point de localisation.
 
 
4. SBRT FOIE

SCAN
 - Un scan avec le nom "CT 1"
 
ROIs CRITIQUES
 - PTVx où x est la dose de prescription en Gy (eg, PTV50 ou PTV37.5)
 - GTV
 - FOIE EXPI
 - Table

ROIs FACULTATIFS
 - MOELLE
 - COTES
 - COLON, GRELE, DUODENUM, ESTOMAC, OESOPHAGE
 - REIN DRT et REIN GCHE
 - PAROI OESO OPP

POI
 - Un point avec le nom ISO SCAN, REF SCAN ou ISO PT PRESC
 - S'il y a un shift d'isocentre, un point avec le nom ISO ou ISOCENTRE pour l'isocentre et un point REF SCAN
   pour le point de localisation.
 
 
5. SBRT VERTEBRE

SCAN
 - Un scan avec le nom "CT 1"
 
ROIs CRITIQUES
 - PTV18
 - Table

ROIs FACULTATIFS
 - MOELLE
 - QUEUE CHEVAL
 - ESTOMAC, DUODENUM, JEJUNUM, ILEON, COLON, RECTUM
 - REIN DRT et REIN GCHE
 - POUMON DRT et POUMON GCHE
 - OESOPHAGE
 - COEUR
 - PLEXUS BRACHIAL, PLEXUS SACRAL, PLEXUS LOMBAIRE
 - GROS VAISSEAUX
 - TRACHEE
 - LARYNX
 
POI
 - Un point avec le nom ISO SCAN, REF SCAN ou ISO PT PRESC


===========================================
FONCTIONNEMENT DES SCRIPTS DE PLANIFICATION
===========================================

Le fonctionnement des scripts de planification est détaillé dans Drupal aux endroits suivants:

1. Prostate VMAT
Planification des prostates VMAT > Description des scripts
http://drupal.radonc.hmr/content/planification-des-prostates-vmat-0

2. Crâne stéréo
Planification des crânes en stéréotaxie > Description des scripts
http://drupal.radonc.hmr/content/planification-des-cr%C3%A2nes-en-st%C3%A9r%C3%A9otaxie

3. SBRT poumon
Planification des poumons SBRT > Description des scripts
http://drupal.radonc.hmr/content/planification-des-poumons-sbrt

4. SBRT foie
 - pas encore documenté

5. SBRT vertebre
 - pas encore documenté

"""

import setpath
import hmrlib.lib as lib
import launcher

with lib.RSScriptWrapper(__file__):
    launcher.plan_launcher()