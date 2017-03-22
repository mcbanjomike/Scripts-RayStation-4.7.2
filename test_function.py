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

    pdb = get_current("PatientDB")
    
    input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane_test_falloff.txt'
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\falloff_output.txt'         
    statsfile = open(input_file_path)
    startpoint = 1
    endpoint = 1
    
    for i,l in enumerate(statsfile):
        #Start from the requested point in the file; reject first line of the file if it contains header information
        if i < startpoint or i > endpoint or l.split(',')[0] == 'Name':
            continue
    
        #Locate and open patient
        try:
            fullname = l.split(',')[0]
            displayname = '^' + fullname.split('^')[1] + ' ' + fullname.split('^')[0] + '$'
            patient_id = '^' + l.split(',')[1] + '$'            
            my_patient = pdb.QueryPatientInfo(Filter={'PatientID':patient_id,'DisplayName':displayname})
            
            if len(my_patient) > 0:
                pdb.LoadPatient(PatientInfo=my_patient[0])
            else:
                output = 'Patient not found: ' + displayname[1:-1] + ', No. HMR ' + patient_id[1:-1] + '\n'
                with open(output_file_path, 'a') as output_file:
                    output_file.write(output)                
                continue

        except:
            output = 'Incorrect formatting for patient ' + l.split(',')[0] + ', check source file\n' 
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue
        
        #Locate plan and beamset
        try:
            patient = lib.get_current_patient()
            plan = patient.TreatmentPlans[l.split(',')[2]]
            beamset = plan.BeamSets[l.split(',')[3]]
        except:
            output = displayname[1:-1] + ': Unable to locate plan or beamset\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue
        
        #Read prescription and ROI information
        try:
            num_ptvs = int(l.split(',')[4])
            ptv_names = [l.split(',')[5],'','','']
            rx = [int(l.split(',')[6]),0,0,0]
            technique = l.split(',')[-2]
        except:
            output = displayname[1:-1] + ': Unable to determine PTV names or prescription values\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)
            continue
        
        #Run the statistics collection script
        output = statistics.dose_falloff_v1(num_ptvs,ptv_names,rx,technique,patient,plan,beamset)   
        with open(output_file_path, 'a') as output_file:
            output_file.write(output)

    
    #launcher.crane_stats_window()
    

    
    
def test_DM():
    #launcher.verif_finale()
    temp_string = 'Mike changed this again!'
    

    
    
    
    

