# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification ORL IMRT et VMAT.

Auteur: original MA modif par DM
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
#import hmrlib.gui as gui
import beams
import optimization_objectives
import clinical_goals
import message

import statistics
import time
import logging
from hmrlib.HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

base_logger = logging.getLogger("hmrlib." + os.path.basename(__file__)[:-3])
# The basic logger object used for logging in hmrlib.
# It was loaded in memory by python-sphinx, which is why you see the object's address!

logger = HMR_RS_LoggerAdapter(base_logger)
# The basic logger object adapted with an HMR_RS_LoggerAdapter.
# It was loaded in memory by python-sphinx, which is why you see the object's address!

# To allow importation of module by sphinx-python
try:
    from connect import *
    # import ScriptClient
except Exception as e:
    if 'IronPython' in sys.version:
        raise
    else:
        pass

        
#Main block of scripts for IMRT/VMAT ORL plans    
def orl_pois(plan_data):

    # Create ISO (if point doesn't already exist)
    poi.create_iso()
    
    # Assign Point Types
    poi.auto_assign_poi_types()
    
    # Erase any points other than ISO or REF SCAN
    poi.erase_pois_not_in_list()
   
    
def orl_rois(plan_data):

    patient = plan_data['patient']
    exam = plan_data['exam']
    ptv = plan_data['ptv']
    rx_dose = plan_data['rx_dose']
    
    
    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    if not roi.roi_exists("BodyRS"): #If BodyRS already exists, then reassigning ROI types will remove its External status
        roi.auto_assign_roi_types_v2()

    # Create BodyRS, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table(struct=0)
    
    #dropped from orlMA
    
    # Create BodyRS-5mm, si Body-5mm existe deja il fait rien (utile pour tricker le script pour utiliser une -4mm ou -3mm)
    if not roi.roi_exists('Body-5mm'):
        patient.PatientModel.CreateRoi(Name="BodyRS-5mm", Color="Lime", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['BodyRS-5mm'].SetMarginExpression(SourceRoiName="BodyRS", MarginSettings={'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5})
        patient.PatientModel.RegionsOfInterest['BodyRS-5mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    else:
        patient.PatientModel.RegionsOfInterest['Body-5mm'].Name = 'BodyRS-5mm'
    
    # Create modPTVs
    nb_ptv = len(ptv)
    #self.Status.Text = str(ptv)
    
    #modPTV70
    patient.PatientModel.CreateRoi(Name="mod" + ptv[0], Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["mod" + ptv[0]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["mod" + ptv[0]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    
    if nb_ptv == 4:
        patient.PatientModel.CreateRoi(Name="mod" + ptv[1], Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["mod" + ptv[1]].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[1], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["mod" + ptv[1]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("mod" + ptv[2]), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[2])].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[2], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0],ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[2])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("mod" + ptv[3]), Color="Blue", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[3])].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[3], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0],ptv[1],ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[3])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif nb_ptv == 3:
        patient.PatientModel.CreateRoi(Name=("mod" + ptv[1]), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[1], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("mod" + ptv[2]), Color="Blue", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[2])].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[2], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0],ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[2])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif nb_ptv == 2:
        patient.PatientModel.CreateRoi(Name=("mod" + ptv[1]), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptv[1], "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("mod" + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    
        # Create optPTVs
    if nb_ptv == 4:
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[1]), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[2]), Color="0,255,128", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[2]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0],"mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[2]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[3]), Color="Aqua", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[3]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0],"mod" + ptv[1],"mod" + ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[3]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("PTV1et2exp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTV1et2exp")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1], "mod" + ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTV1et2exp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("PTVexp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTVexp")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV1et2exp"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTVexp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif nb_ptv == 3:
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[1]), Color="0,255,128", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[2]), Color="Aqua", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[2]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0],"mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[2]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("PTV1et2exp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTV1et2exp")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTV1et2exp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("PTVexp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTVexp")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV1et2exp"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTVexp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif nb_ptv == 2:
        patient.PatientModel.CreateRoi(Name=("OPT" + ptv[1]), Color="Aqua", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT" + ptv[1]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("PTVexp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTVexp")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["mod" + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTVexp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif nb_ptv == 1:
        patient.PatientModel.CreateRoi(Name=("PTVexp"), Color="255,128,64", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['PTVexp'].SetMarginExpression(SourceRoiName="mod" + ptv[0], MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
        patient.PatientModel.RegionsOfInterest[("PTVexp")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])

        
    # Set ROI type for all modPTVs, optPTVs and Gradients to PTV/Target
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '')
        if 'modPTV' in n:
            roi.set_roi_type(name, 'Ptv', 'Target')
        elif 'OPTPTV' in n:
            roi.set_roi_type(name, 'Ptv', 'Target')
    
    # Create RINGs
    patient.PatientModel.CreateRoi(Name="Ringtemp", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["Ringtemp"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['PTVexp'], 'MarginSettings': {'Type': "Expand", 'Superior': 3, 'Inferior': 3, 'Anterior': 3, 'Posterior': 3, 'Right': 3, 'Left': 3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['BodyRS-5mm'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["Ringtemp"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="Ring", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["Ring"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['Ringtemp'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['PTVexp'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["Ring"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    
    # Create PRVs
    list = ["MOELLE", "TR CEREBRAL", "N OPT DRT", "N OPT GCHE", "CHIASMA"]
    color = ["0, 128, 255", "Yellow", "Purple", "SkyBlue", "Red"]
    for i, name in enumerate(list):
        if roi.roi_exists(name):
            patient.PatientModel.CreateRoi(Name=("prv5mm" + name), Color=color[i], Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("prv5mm" + name)].SetWallExpression(SourceRoiName=name, OutwardDistance=0.5, InwardDistance=0)
            patient.PatientModel.RegionsOfInterest[("prv5mm" + name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    if roi.roi_exists("prv5mmTR CEREBRAL"):
        patient.PatientModel.RegionsOfInterest["prv5mmTR CEREBRAL"].Name = "prv5mm TRONC"
    if roi.roi_exists("prv5mmN OPT DRT"):
        patient.PatientModel.RegionsOfInterest["prv5mmN OPT DRT"].Name = "prv5mmNOD"
    if roi.roi_exists("prv5mmN OPT GCHE"):
        patient.PatientModel.RegionsOfInterest["prv5mmN OPT GCHE"].Name = "prv5mmNOG"
    
    # Create opt OARs
    list = ["CAVITE ORALE", "LARYNX", "LEVRES", "OESOPHAGE", "PARO DRT", "PARO GCHE"]
    color = ["Yellow", "Orange", "Tomato", "Khaki", "Green", "Purple"]
    for i, name in enumerate(list):
        if roi.roi_exists(name):
            patient.PatientModel.CreateRoi(Name=("OPT " + name), Color=color[i], Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("OPT " + name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVexp"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("OPT " + name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    
    # OPT CERVEAU, MOELLE, TRONC, et BLOC MOELLE
    if roi.roi_exists("CERVEAU"):
        patient.PatientModel.CreateRoi(Name=("OPT CERVEAU"), Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT CERVEAU"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['PTVexp'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT CERVEAU"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    
    #pas sure d'en avoir besoin
    '''
    if roi.roi_exists("MOELLE"):
        patient.PatientModel.CreateRoi(Name=("OPT MOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT MOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ALLPTVs+3mm'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT MOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT prvMOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT prvMOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mmMOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ALLPTVs+3mm'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT prvMOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    if roi.roi_exists("TR CEREBRAL"):
        patient.PatientModel.CreateRoi(Name=("OPT TRONC"), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT TRONC"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["TR CEREBRAL"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ALLPTVs+3mm'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT TRONC"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT prvTRONC"), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPT prvTRONC"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ALLPTVs+3mm'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPT prvTRONC"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    '''
    if roi.roi_exists("MOELLE"):
        patient.PatientModel.CreateRoi(Name=("temp3"), Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["temp3"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mmMOELLE", "prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 9, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['PTVexp'], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["temp3"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("BLOC MOELLE"), Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp3", "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["MOELLE", "prv5mmMOELLE", "TR CEREBRAL", "prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Contract", 'Superior': 0, 'Inferior': 0, 'Anterior': 0.2, 'Posterior': 0, 'Right': 0.1, 'Left': 0.1})
        patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # MANDIBULE
    roi.create_expanded_ptv(ptv_name = ptv[0], color="Yellow", margeptv=0.5, output_name=ptv[0])
    if roi.roi_exists("MANDIBULE"):
        patient.PatientModel.CreateRoi(Name="MAND ds " + ptv[0] + "+5mm", Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("MAND ds " + ptv[0] + "+5mm")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MANDIBULE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0] + "+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("MAND ds " + ptv[0] + "+5mm")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name="MAND-" + ptv[0] + "-5mm", Color="YellowGreen", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["MAND-" + ptv[0] + "-5mm"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MANDIBULE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0] + "+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["MAND-" + ptv[0] + "-5mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Plexus Brachiaux
    
    if roi.roi_exists("PL BRACHIAL DRT"):
        patient.PatientModel.CreateRoi(Name="PBD ds " + ptv[0], Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PBD ds " + ptv[0])].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PBD ds " + ptv[0])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        try:
            patient.PatientModel.CreateRoi(Name="tempPBD ds " + ptv[1], Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("tempPBD ds " + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("tempPBD ds " + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name="PBD ds " + ptv[1], Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBD ds " + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["tempPBD ds " + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PBD ds " + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBD ds " + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.RegionsOfInterest['tempPBD ds ' + ptv[1]].DeleteRoi()
        except:
            pass
    if roi.roi_exists("PL BRACHIAL GCHE"):
        patient.PatientModel.CreateRoi(Name="PBG ds " + ptv[0], Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["PBG ds " + ptv[0]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["PBG ds " + ptv[0]].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        try:
            patient.PatientModel.CreateRoi(Name="tempPBG ds " + ptv[1], Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("tempPBG ds " + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("tempPBG ds " + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name="PBG ds " + ptv[1], Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBG ds " + ptv[1])].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["tempPBG ds " + ptv[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PBG ds " + ptv[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBG ds " + ptv[1])].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.RegionsOfInterest['tempPBG ds ' + ptv[1]].DeleteRoi()
        except:
            pass
            
    #delete unnecessary or empty contours
    patient.PatientModel.RegionsOfInterest['temp3'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVexp'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest[ptv[0] + '+0.5cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['Ringtemp'].DeleteRoi()
    if roi.roi_exists('PTV1et2exp'):
        patient.PatientModel.RegionsOfInterest['PTV1et2exp'].DeleteRoi()
    exam_list = []
    for CT in patient.Examinations:
        exam_list.append(CT.Name)
    
    for contour in patient.PatientModel.RegionsOfInterest:
        if not roi.get_roi_approval(contour.Name,patient.Examinations["CT 1"]):
            VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
            if "CT 2" in exam_list:
                VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])
            else:
                VolCT2 = 0

            if VolCT1 == 0 and VolCT2 == 0:
                patient.PatientModel.RegionsOfInterest[contour.Name].DeleteRoi()


def orl_add_plan_and_beamset(plan_data):
    
    #plan_name = plan_data['plan_name']
    #exam = plan_data['exam']
    #beamset_name = plan_data['beamset_name']
    #site_name = plan_data['site_name']
    #machine = plan_data['machine']
    #nb_fx = plan_data['nb_fx']
    #treatment_technique = plan_data['treatment_technique']
    ptv = plan_data['ptv']
    rx_dose = plan_data['rx_dose']
    
    # Add Treatment plan
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy=planner_name, Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=plan_data['beamset_name'], ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment=plan_data['treatment_technique'])
    beamset.AddDosePrescriptionToRoi(RoiName=str(ptv[0]), DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=str(rx_dose[0]), RelativePrescriptionLevel=1)

    
def orl_add_beams(plan_data):
    
    beamset = plan_data['patient'].TreatmentPlans[plan_data['plan_name']].BeamSets[plan_data['beamset_name']]
    
    if plan_data['treatment_technique'] == 'VMAT':
        if plan_data['nb_ch'] == 1:
            iso = poi.identify_isocenter_poi()
            lib.add_arc((plan_data['site_name']+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
        elif plan_data['nb_ch'] == 2:
            iso = poi.identify_isocenter_poi()
            lib.add_arc((plan_data['site_name']+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
            lib.add_arc((plan_data['site_name']+'.2'), iso, 181, 180, 'CW', description='ARC 181-180', collimator=355, beamset=beamset)
    elif plan_data['treatment_technique'] == 'SMLC':
        iso = poi.identify_isocenter_poi()
        nb_ch = plan_data['nb_ch']
        spacing = int(360/nb_ch)
        angles = [0]
        i=1
        while i < nb_ch:
            angles.append(angles[i-1]+spacing)
            i=i+1
        desc_angles = []
        for ang in angles:
            if ang == 0:
                desc_angles.append('ANT ')
            elif ang < 90:
                desc_angles.append('OAG ')
            elif ang == 90:
                desc_angles.append('LAT G ')
            elif ang > 90 and ang < 180:
                desc_angles.append('OPG ')
            elif ang == 180:
                desc_angles.append('POST ')
            elif ang > 180 and ang < 270:
                desc_angles.append('OPD ')
            elif ang == 270:
                desc_angles.append('LAT D ')
            elif ang > 270 and ang < 360:
                desc_angles.append('OAD ')
        i=0
        while i < nb_ch:
            beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso, examination=plan_data['exam']).value, Name=plan_data['site_name']+'.'+str(i+1), Description=desc_angles[i] + str(angles[i]), GantryAngle=angles[i], CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)
            i=i+1
        
def orl_opt_settings(plan_data):

    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]
    
    # Set optimization parameters and VMAT conversion parameters
    if plan_data['treatment_technique'] == 'VMAT':
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=150, plan=plan)
    elif plan_data['treatment_technique'] == 'SMLC':
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 30
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 6        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 4
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 8
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = plan_data['nb_ch']*8

def orl_create_isodose_lines(plan_data):

    patient = plan_data['patient']
    rx_dose = plan_data['rx_dose']

    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose[0]

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=95, r=255, g=0, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=(4500*100/rx_dose[0]), r=128, g=128, b=255, alpha=255)
    try:
        eval.add_isodose_line_rgb(dose=(95*rx_dose[1]/rx_dose[0]), r=255, g=128, b=64, alpha=255)
        eval.add_isodose_line_rgb(dose=(100*rx_dose[1]/rx_dose[0]), r=128, g=64, b=0, alpha=255)
    except ValueError:
        pass
    try:
        eval.add_isodose_line_rgb(dose=(95*rx_dose[2]/rx_dose[0]), r=128, g=255, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=(100*rx_dose[2]/rx_dose[0]), r=0, g=64, b=0, alpha=255)
    except ValueError:
        pass
    try:
        eval.add_isodose_line_rgb(dose=(95*rx_dose[3]/rx_dose[0]), r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=(100*rx_dose[3]/rx_dose[0]), r=0, g=0, b=255, alpha=255)
    except ValueError:
        pass
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

