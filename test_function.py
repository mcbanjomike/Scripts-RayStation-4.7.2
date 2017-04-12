# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification en VMAT des
prostates.

Auteur: MA
"""

import sys
import os.path
import setpath
import hmrlib.lib as lib
import hmrlib.eval as eval
import hmrlib.optim as optim
import hmrlib.poi as poi
import hmrlib.roi as roi
import hmrlib.qa as qa
import hmrlib.uis as uis
import beams
import optimization_objectives
import clinical_goals


import logging
from hmrlib.HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

# To test GUI stuff
#import clr
#import System.Array


# Temporary stuff to get rid of after testing GUI
import launcher
import poumon
import crane
import foie
import message
import verification
import statistics

import crane2ptv

# Stuff to potentially allow for UI manipulation
#from connect import *
import statetree
#import clr
#import System
#import connect
#import ScriptClient
#clr.AddReference("PresentationFramework")


base_logger = logging.getLogger("hmrlib." + os.path.basename(__file__)[:-3])
""" The basic logger object used for logging in hmrlib.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

logger = HMR_RS_LoggerAdapter(base_logger)
""" The basic logger object adapted with an HMR_RS_LoggerAdapter.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

# To allow importation of module by sphinx-python
try:
    from connect import *
    # import ScriptClient
except Exception as e:
    if 'IronPython' in sys.version:
        raise
    else:
        pass
  
    
    #Place pour tester des nouveaux fonctions
def test_MA():
    #plan = lib.get_current_plan()
    #beamset = lib.get_current_beamset()
    #exam = lib.get_current_examination()
    #patient = lib.get_current_patient()
       
    #uis.ui_statetree()
    
    #statistics.auto_collect_crane_stats(startpoint=60,endpoint=999,min_vol=3.999)
    #statistics.batch_autoplan_crane(startpoint=1,endpoint=11,min_vol=1.0)
    #statistics.single_autoplan_crane()
    #launcher.lung_stats_window()
    #statistics.auto_collect_lung_stats(startpoint=35,endpoint=35)
    statistics.auto_collect_lung_stats(startpoint=23,endpoint=33,test_plans=True,print_results=False,show_plan=False)
    
    #num_ptvs = 2
    #ptv_names = ['PTV1','PTV2','','']
    #rx = [1500,1500,0,0]
    #technique = ['IMRT']
    
    #output,header,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max = statistics.dose_falloff_crane_multi(num_ptvs,ptv_names,rx,technique,patient,plan,beamset)  

    
    
def test_DM():
    #launcher.verif_finale()
    temp_string = 'Mike changed this again!'
    

    
    
    
    

