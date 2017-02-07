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
    
    #statistics.stereo_brain_statistics()
    
    #a,b,c,d,e = verification.verify_beams()
    #message.message_window(a+str(b)+c+d+e)
    
    
    #qa.shift_plans_QA(print_results=True)
    #qa.create_ac_qa_plans(plan=None, phantom_name='QAVMAT ARCCHECK_2016', iso_name='ISO AC')
    
    #statetree.CreateUiStateTreeWindow().ShowDialog() 
    
    #crane.optimize_collimator_angles()
    """
    ui = get_current("ui")
    ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow['1'].Select()
    ui.Workspace.TabControl['Beams'].BeamCommands.Button_Edit.Click()
    ui = get_current("ui")
    ui.BeamDialogAngles.TextBox_CollimatorAngle.Text = '99'
    ui.Button_OK.Click()
    ui = get_current("ui")
    """
    #ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow['1'].TextBlock_BeamAnglesPO_CollimatorAngle.Text = "45.0"
    
    #ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformBeamMLC.Click()
   
    launcher.verification_finale_slim()
    #message.message_window(verification.verify_segments())
    #optim.essai_autre_technique()
    #message.message_window('essai')
    #import report
    #report.create_verif1_report()
    
    
def test_DM():
    #launcher.verif_finale()
    temp_string = 'Mike changed this again!'
    

    
    
    
    

