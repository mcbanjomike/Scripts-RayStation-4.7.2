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
#import hmrlib.gui as gui
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


def create_prostate_plan_A1(nb_fx = 40, plan3D = False, machine = 'BeamMod', isodose_creation = True):
    """
    Voir :py:mod:`plan_prostate_A1`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    # Determine dose to be used for optimization of A1
    if nb_fx == 40:
        rx_dose = 8000
    elif nb_fx == 33 or nb_fx == 22:
        rx_dose = 6600
    elif nb_fx == 20:
        rx_dose = 6000
    elif nb_fx == 15: #Plans that will finish at 37.5Gy in 15fx are initially planned at 60Gy in 24fx (2.5Gy/fx)
        rx_dose = 6000
        nb_fx = 24
    """
    elif nb_fx == 15: #Plans that will finish at 37.5Gy in 15fx are initially planned at 80Gy in 32fx (2.5Gy/fx)
        rx_dose = 8000
        nb_fx = 32
    """
 
    # Create BodyRS+Table, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table()

    # Clean Contrast ROI outside of body
    if roi.roi_exists("CONTRASTE"):
        retval_1 = patient.PatientModel.CreateRoi(Name="Contraste Mod", Color="Yellow", Type="ContrastAgent", TissueName=None, RoiMaterial=None)
        retval_1.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
            "CONTRASTE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_1.UpdateDerivedGeometry(Examination=examination)

    # Create PTV A1
    # Case 1. If PTV A1 already exists, this ROI is used and no additional contours will be created.
    # Case 2. If PTV 1.5cm exists, it will be combined with PTV VS (if present) to form PTV A1.
    # Case 3. If neither PTV A1 nor PTV 1.5cm exists, the script will combine PTV 1cm and PTV VS (if present) to form PTV A1.

    # Also, if PTV A1 already exists, change ROI type to "PTV"
    if roi.roi_exists("PTV A1"):
        patient.PatientModel.RegionsOfInterest["PTV A1"].Type = "PTV"
        patient.PatientModel.RegionsOfInterest["PTV A1"].OrganData.OrganType = "Target"
        ptv = patient.PatientModel.RegionsOfInterest["PTV A1"]
    elif roi.roi_exists("PTV 1.5cm"):
        if roi.roi_exists("PTV VS"):
            ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
            ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV VS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            ptv.UpdateDerivedGeometry(Examination=examination)
        else: 
            ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV A1'].SetMarginExpression(SourceRoiName="PTV 1.5cm", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            patient.PatientModel.RegionsOfInterest['PTV A1'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'], Algorithm="Auto")
    elif roi.roi_exists("PTV 1cm"):
        if roi.roi_exists("PTV VS"):
            ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
            ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV VS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            ptv.UpdateDerivedGeometry(Examination=examination)
        else: 
            ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV A1'].SetMarginExpression(SourceRoiName="PTV 1cm", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            patient.PatientModel.RegionsOfInterest['PTV A1'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'], Algorithm="Auto")

    # Create PTV A2 (copy of PTV 1cm, except when PTVBoost exists)
    boost = 0
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        if 'PTVBOOST' in name.replace(' ', '').upper():
            boost = 1
            boost_name = name
    if boost == 1: # PTV A2 is a copy of PTVBoost
        retval_3 = patient.PatientModel.CreateRoi(Name="PTV A2", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
        retval_3.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [boost_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_3.UpdateDerivedGeometry(Examination=examination)        
    elif roi.roi_exists("PTV 1cm"): # PTV A2 is a copy of PTV 1cm
        retval_3 = patient.PatientModel.CreateRoi(Name="PTV A2", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
        retval_3.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_3.UpdateDerivedGeometry(Examination=examination)
    
    # Create RECTUM+3mm
    patient.PatientModel.CreateRoi(Name="RECTUM+3mm", Color="skyblue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RECTUM+3mm'].SetMarginExpression(SourceRoiName="RECTUM", MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest['RECTUM+3mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])   
    
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)
        
    #Override Contraste Mod with water    
    if roi.roi_exists("Contraste Mod"):
        #It is seemingly impossible to use the built-in material Water, so a copy is made called Eau
        #But first we check to see if Eau exists already, because creating a second copy crashes RayStation (even when using try)
        db = get_current("PatientDB")
        finished = False
        i=0
        #If Eau already exists, assign it to the ROI and end the function
        for material in patient.PatientModel.Materials:
            i += 1
            if material.Name == 'Eau':
                patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = material)
                finished = True
                break
        #If Eau does not exist, create it, then assign it to the ROI
        if not finished:
            patient.PatientModel.CreateMaterial(BaseOnMaterial=db.TemplateMaterials[0].Materials[25], Name = "Eau", MassDensityOverride = 1.000)
            patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = patient.PatientModel.Materials[i])        
            
    #Create ISO
    if not poi.poi_exists("ISO"):
        if poi.poi_exists("REF SCAN"):
            REF_SCAN_coords = poi.get_poi_coordinates('REF SCAN',examination)
            poi.create_poi(REF_SCAN_coords,'ISO','Blue','Isocenter',examination)
    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="A1 seul", PlannedBy="", Comment="", ExaminationName=lib.get_current_examination().Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    if patient.Examinations[0].PatientPosition == "HFS":
        position = "HeadFirstSupine"
    else:
        position = "HeadFirstProne"
        
    beamset = plan.AddNewBeamSet(Name="A1", ExaminationName=lib.get_current_examination().Name, MachineName=machine, NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique="VMAT", PatientPosition=position, NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="")
    beamset.AddDosePrescriptionToRoi(RoiName="PTV A1", DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=rx_dose*0.95, RelativePrescriptionLevel=1)

    # plan and beamset are created but not currently selected in RS
    # therefore we must retain the objects in variables and pass them on
    # to the following functions, which otherwise would assume that
    # these are currently selected by the user in RS.
    # VTL

    # Add arc
    beams.add_beams_prostate_A1(beamset=beamset)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    # Set VMAT conversion parameters
    if nb_fx == 22 or nb_fx == 20: #3 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=200.0, plan=plan)
    elif nb_fx == 24: #2.5 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=175.0, plan=plan)
    else:
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan)
    
    # Add optimization objectives
    optimization_objectives.add_opt_obj_prostate_A1(plan=plan)

    # Add clinical goals
    if nb_fx == 40:
        clinical_goals.add_dictionary_cg('Prostate', 80, 40, plan=plan)
    elif nb_fx == 33:
        clinical_goals.add_dictionary_cg('Lit Prostatique', 66, 33, plan=plan)
    elif nb_fx == 22:
        clinical_goals.add_dictionary_cg('Lit Prostatique', 66, 22, plan=plan)
    elif nb_fx == 20 or nb_fx == 24: #Includes cases of 37.5Gy-15
        clinical_goals.add_dictionary_cg('Lit Prostatique', 60, 20, plan=plan)
        
    # If 3D conformal plan exists, rename PTVs, beams and plan to A2/A3 instead of A1/A2
    if plan3D:
        patient.PatientModel.RegionsOfInterest['PTV A2'].Name = 'PTV A3'
        patient.PatientModel.RegionsOfInterest['PTV A1'].Name = 'PTV A2'
        plan.Name = "A2 seul"
        plan.BeamSets[0].DicomPlanLabel = "A2"
        for beam in plan.BeamSets[0].Beams:
            beam.Name = "A2"+beam.Name[2:]
        isodose_creation = False #Most 3D plans come with isodose lines, so always skip creating new ones to avoid crashes
            
    # Set Dose Color Table
    if isodose_creation:
        eval.remove_all_isodose_lines()
        patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose
        patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
        eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=75, r=0, g=255, b=0, alpha=255)
        #eval.add_isodose_line_rgb(dose=87.7, r=255, g=192, b=0, alpha=255)  # pour plan split
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=108.75, r=255, g=0, b=255, alpha=255)

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if not points.Name in ["ISO", "ISOCENTRE", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()        
    
    

def create_prostate_plan_PACE(nb_fx = 39, plan3D = False, machine = 'BeamMod', isodose_creation = True):
    """
    Voir :py:mod:`plan_prostate_A1`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    # Determine dose to be used for optimization of A1
    if nb_fx == 39:
        rx_dose = 7800
    elif nb_fx == 5:
        rx_dose = 3625
 
    # Create BodyRS+Table, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table()

    # Clean Contrast ROI outside of body
    if roi.roi_exists("CONTRASTE"):
        retval_1 = patient.PatientModel.CreateRoi(Name="Contraste Mod", Color="Yellow", Type="ContrastAgent", TissueName=None, RoiMaterial=None)
        retval_1.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
            "CONTRASTE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_1.UpdateDerivedGeometry(Examination=examination)

    # Identify PTV
    if roi.roi_exists("PTV_7800"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV_7800"]
    elif roi.roi_exists("PTV_3625"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV_3625"]

    # Create Rectum+3mm
    patient.PatientModel.CreateRoi(Name="Rectum+3mm", Color="skyblue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Rectum+3mm'].SetMarginExpression(SourceRoiName="Rectum", MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest['Rectum+3mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])   
    
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)
        
    #Override Contraste Mod with water    
    if roi.roi_exists("Contraste Mod"):
        #It is seemingly impossible to use the built-in material Water, so a copy is made called Eau
        #But first we check to see if Eau exists already, because creating a second copy crashes RayStation (even when using try)
        db = get_current("PatientDB")
        finished = False
        i=0
        #If Eau already exists, assign it to the ROI and end the function
        for material in patient.PatientModel.Materials:
            i += 1
            if material.Name == 'Eau':
                patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = material)
                finished = True
                break
        #If Eau does not exist, create it, then assign it to the ROI
        if not finished:
            patient.PatientModel.CreateMaterial(BaseOnMaterial=db.TemplateMaterials[0].Materials[25], Name = "Eau", MassDensityOverride = 1.000)
            patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = patient.PatientModel.Materials[i])        
            
    #Create ISO
    if not poi.poi_exists("ISO"):
        if poi.poi_exists("REF SCAN"):
            REF_SCAN_coords = poi.get_poi_coordinates('REF SCAN',examination)
            poi.create_poi(REF_SCAN_coords,'ISO','Blue','Isocenter',examination)
    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="A1 seul", PlannedBy="", Comment="", ExaminationName=lib.get_current_examination().Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    if patient.Examinations[0].PatientPosition == "HFS":
        position = "HeadFirstSupine"
    else:
        position = "HeadFirstProne"
        
    beamset = plan.AddNewBeamSet(Name="A1", ExaminationName=lib.get_current_examination().Name, MachineName=machine, NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique="VMAT", PatientPosition=position, NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=rx_dose*0.95, RelativePrescriptionLevel=1)

    # plan and beamset are created but not currently selected in RS
    # therefore we must retain the objects in variables and pass them on
    # to the following functions, which otherwise would assume that
    # these are currently selected by the user in RS.
    # VTL

    # Add arc
    beams.add_beams_prostate_A1(beamset=beamset)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    # Set VMAT conversion parameters
    if nb_fx == 5: #7.25 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=300.0, plan=plan)
    else: #2 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan)
    
    # Add optimization objectives
    optimization_objectives.add_opt_obj_prostate_A1(plan=plan)

    # Add clinical goals
    if nb_fx == 39:
        clinical_goals.add_dictionary_cg('Prostate PACE', 78, 39, plan=plan)
    elif nb_fx == 5:
        clinical_goals.add_dictionary_cg('Prostate PACE', 36.25, 5, plan=plan)
        
    #Rename PTV
    if ptv.Name == "PTV_7800":
        ptv.Name = "PTV A1 78Gy"
    elif ptv.Name == "PTV_3625":
        ptv.Name = "PTV A1 36.25Gy"
                   
    # Set Dose Color Table
    if isodose_creation:
        eval.remove_all_isodose_lines()
        patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose
        patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
        eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=75, r=0, g=255, b=0, alpha=255)
        #eval.add_isodose_line_rgb(dose=87.7, r=255, g=192, b=0, alpha=255)  # pour plan split
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=108.75, r=255, g=0, b=255, alpha=255)

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if not points.Name in ["ISO", "ISOCENTRE", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()        
    
    
    

# Script pour transformer un plan A1 de prostate en plan A1 Split. Suppose que le script plan_prostate_A1
# a été utilisé pour la creation du plan initial.
def prostate_split_A1():
    """
    Voir :py:mod:`prostate_split_A1`.
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    patient_plan = lib.get_current_plan()

    # Changer nb de fractions si pas 40
    patient_plan.BeamSets[0].FractionationPattern.NumberOfFractions = 40

    # Create PTV A1-RECTUM
    retval_4 = patient.PatientModel.CreateRoi(Name="PTV A1-RECTUM", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_4.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV A1"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  "RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_4.UpdateDerivedGeometry(Examination=examination)

    # Create WALL RECT ds PTV A1
    retval_9 = patient.PatientModel.CreateRoi(Name="WALL RECT ds PTV A1", Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_9.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["WALL RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  "PTV A1"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_9.UpdateDerivedGeometry(Examination=examination)

    # Changer objectif min dose PTV A1 à PTV A1-RECTUM
    patient_plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DeleteFunction()
    optim.add_mindose_objective('PTV A1-RECTUM', 7600, weight=100, plan=patient_plan)

    # Ajouter objectif min dose 73.2 Gy à RECTUM ds PTV A1
    optim.add_mindose_objective('RECTUM ds PTV A1', 7320, weight=10, plan=patient_plan)

    # Ajouter objectif max dose 75 Gy à WALL RECT ds PTV A1
    optim.add_maxdose_objective('WALL RECT ds PTV A1', 7500, weight=0, plan=patient_plan)

    # Ajouter un clinical goal de couverture sur le PTV A1-RECTUM (NB qu'on ne peut pas effacer le CG sur le vieux PTV car ça fait planter RayStation)
    # plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[0].DeleteFunction() # - FAIT PLANTER RAYSTATION!
    #eval.add_clinical_goal('PTV A1-RECTUM', 7600, 'AtLeast', 'VolumeAtDose', 99.5, plan=patient_plan)
    patient_plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="PTV A1-RECTUM", GoalValue=7600, GoalCriteria="AtLeast", GoalType="VolumeAtDose", GoalVolume=99.5, AbsoluteGoalVolume=0)

    # Ajouter clinical goal couverture RECTUM ds PTV
    #eval.add_clinical_goal('RECTUM ds PTV A1', 7320, 'AtLeast', 'VolumeAtDose', 99.5, plan=patient_plan)
    patient_plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="RECTUM ds PTV A1", GoalValue=7320, GoalCriteria="AtLeast", GoalType="VolumeAtDose", GoalVolume=99.5, AbsoluteGoalVolume=0)


def create_prostate_plan_A2():
    """
    Voir :py:mod:`plan_prostate_A2`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    plan = lib.get_current_plan()
    
    # Five main possibilities:
    # 1. 80 Gy-40fx > 54 Gy + 26 Gy
    # 2. 66 Gy-33fx > 44 Gy + 22 Gy
    # 3. 66 Gy-33fx > 66 Gy + Boost (NB nobody does this ever)
    # 4. 66 Gy-22fx > 42 Gy + 24 Gy
    # 5. 60 Gy-20fx > 42 Gy + 18 Gy
    # Use number of fractions to differentiate 80 Gy plans from 66 Gy ones. Use presence of PTV Boost xxGy to differentiate between cases 2 and 3.
    
    nb_fx_A1 = plan.BeamSets[0].FractionationPattern.NumberOfFractions
    # Check if 3DCRT plan exists, if so then new plan will be A3
    if roi.roi_exists("PTV A3"):
        ptv_A2 = patient.PatientModel.RegionsOfInterest["PTV A3"]
    else:
        ptv_A2 = patient.PatientModel.RegionsOfInterest["PTV A2"]
   
    # Apparently it is no longer possible to edit the number of fractions in a beamset in version 4.7.2?
    # Have to ask the planner to change the number of fractions manually, I guess.
    """
    if nb_fx_A1 == 40:
        plan.BeamSets[0].FractionationPattern.NumberOfFractions = 27
        nb_fx_A2 = 13
        rx_dose_A2 = 26
    elif nb_fx_A1 == 33: # Assume A2 will be 22Gy-11 unless PTVBOOST is found.
        plan.BeamSets[0].FractionationPattern.NumberOfFractions = 22
        nb_fx_A2 = 11
        # Check for PTVBOOST and adjust Rx and number of fractions if found.
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            if 'PTVBOOST' in name.replace(' ', '').upper():
                ptv_A2 = patient.PatientModel.RegionsOfInterest[name]
                rx_dose_A2 = float(ptv.Name[8:])
                nb_fx_A2 = rx_dose_A2 / 2
                plan.BeamSets[0].FractionationPattern.NumberOfFractions = 33
    """
                
    if nb_fx_A1 == 27: #54 + 26
        nb_fx_A2 = 13
        rx_dose_A2 = 26
        plan.BeamSets[0].Prescription.PrimaryDosePrescription.DoseValue = 5130
    elif nb_fx_A1 == 22: #44 + 22
        nb_fx_A2 = 11
        rx_dose_A2 = 22
        plan.BeamSets[0].Prescription.PrimaryDosePrescription.DoseValue = 4180
    elif nb_fx_A1 == 14: #42 + 24 or 42 + 18 (3 Gy per fraction)
        plan.BeamSets[0].Prescription.PrimaryDosePrescription.DoseValue = 3990
        try:
            total_fx = patient.TreatmentPlans["A1 seul"].BeamSets[0].FractionationPattern.NumberOfFractions          
            if total_fx == 20: #This indicates 42+18
                nb_fx_A2 = 6
                rx_dose_A2 = 18                         
            else: #42+24
                nb_fx_A2 = 8
                rx_dose_A2 = 24                  
        except:
            nb_fx_A2 = 8
            rx_dose_A2 = 24
    elif nb_fx_A1 == 33: #66 + Boost
        plan.BeamSets[0].Prescription.PrimaryDosePrescription.DoseValue = 6270
        # Check for PTVBOOST and adjust Rx and number of fractions if found.
        # Example: PTVBoost8 for 8 Gy in 4 fx, PTVBoost12 for 12 Gy in 6 fx
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            if 'PTVBOOST' in name.replace(' ', '').upper():
                #ptv_A2 = patient.PatientModel.RegionsOfInterest[name]
                rx_dose_A2 = float(name[8:])
                nb_fx_A2 = rx_dose_A2 / 2
    else:
        launcher.debug_window(input="The number of fractions in the first beamset must be 14, 22, 27 or 33.")
        #nb_fx_A2 = 11
        return
                
    # Rename first beamset A1 or A2, depending on whether 3DCRT plan exists
    if roi.roi_exists("PTV A3"):
        new_bs_name = "A3"
        old_bs_name = "A2"
    else:
        new_bs_name = "A2"
        old_bs_name = "A1"
    plan.BeamSets[0].DicomPlanLabel = old_bs_name    
        
    # Add Beam Set A2

    if patient.Examinations[0].PatientPosition == "HFS":
        beamset = plan.AddNewBeamSet(Name=new_bs_name, ExaminationName=examination.Name, MachineName="BeamMod", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx_A2, CreateSetupBeams=False, Comment="")
    else:
        beamset = plan.AddNewBeamSet(Name=new_bs_name, ExaminationName=examination.Name, MachineName="BeamMod", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstProne", NumberOfFractions=nb_fx_A2, CreateSetupBeams=False, Comment="")

    # Make A2 dependent on A1
    plan.UpdateDependency(DependentBeamSetName=new_bs_name, BackgroundBeamSetName=old_bs_name, DependencyUpdate="CreateDependency")

    # Prescribe to PTV A2
    beamset.AddDosePrescriptionToRoi(RoiName=ptv_A2.Name, DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=rx_dose_A2 * 95, RelativePrescriptionLevel=1)

    # Add arc
    beams.add_beams_prostate_A2(beamset=beamset)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan, beamset=2)

    # Set maximum delivery time
    if nb_fx_A2 == 8 or nb_fx_A2 ==6: #3Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=200.0, plan=plan, beamset=2)
    else:
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan, beamset=2)

    # Add optimization objectives
    # Type 1: 54+26
    if nb_fx_A2 == 13:
        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 2470
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 100

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 2730
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 7500
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.PercentVolume = 15
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.DoseLevel = 7000
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.PercentVolume = 25
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.DoseLevel = 6500
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.PercentVolume = 35
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.DoseLevel = 6000
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.PercentVolume = 50
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="RECTUM+3mm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.DoseLevel = 7900
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="VESSIE", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 8200

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="BodyRS", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.HighDoseLevel = 7600
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseLevel = 4000
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseDistance = 3
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.Weight = 0

    #Type 5, 42Gy + 18Gy (3Gy per fraction)
    elif nb_fx_A2 == 6:
        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 1710
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 100

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 1890
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 5700
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.PercentVolume = 15
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.DoseLevel = 5280
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.PercentVolume = 30
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.DoseLevel = 4860
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.PercentVolume = 50
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.DoseLevel = 3240
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.PercentVolume = 70
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="RECTUM+3mm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.DoseLevel = 6000
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.Weight = 10

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="VESSIE", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 6300

        plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="BodyRS", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.HighDoseLevel = 5700
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseLevel = 3000
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseDistance = 3
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.Weight = 0

        
    # Types 2, 3 and 4
    else:
        i = 0
        retval_1 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = rx_dose_A2 * 95
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 100
        i += 1

        retval_2 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=ptv_A2.Name, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=new_bs_name)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = rx_dose_A2 * 105
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
        i += 1

        if nb_fx_A2 != 11 and nb_fx_A2 != 8: # For Boost plans only
            retval_4 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = 7000
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.PercentVolume = 25
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
            i += 1

        if nb_fx_A1 == 14: #3Gy per fraction
            rect_35_dvh = 5420
            rect_50_dvh = 5000
        else: #2Gy per fraction
            rect_35_dvh = 6500
            rect_50_dvh = 6000
            
        retval_5 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = rect_35_dvh
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.PercentVolume = 35
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
        i += 1

        retval_6 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = rect_50_dvh
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.PercentVolume = 50
        plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
        i += 1

        if nb_fx_A2 == 11 or nb_fx_A2 == 8: # 44 + 22 or 42 + 24 (3 Gy per fraction)
            retval_7 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="RECTUM+3mm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = 6500
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
            i += 1

            retval_8 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="VESSIE", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = 6800
            i += 1

            retval_9 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="BodyRS", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.HighDoseLevel = 6270
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.LowDoseLevel = 3300
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.LowDoseDistance = 3
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 0

        else: # 66 + Boost
            retval_7 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="RECTUM+3mm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = (65 + rx_dose_A2) * 100
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 10
            i += 1

            retval_8 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="VESSIE", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = (68 + rx_dose_A2) * 100
            i += 1

            retval_9 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="BodyRS", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.HighDoseLevel = (66 + rx_dose_A2) * 95
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.LowDoseLevel = (66 + rx_dose_A2) * 50
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.LowDoseDistance = 3
            plan.PlanOptimizations[1].Objective.ConstituentFunctions[i].DoseFunctionParameters.Weight = 0
            
    # Modify clinical goal for coverage of PTV A1
    if old_bs_name == "A1":
        old_PTV_name = "PTV A1"
    else:
        old_PTV_name = "PTV A2"
    for cg in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
        if cg.ForRegionOfInterest.Name == old_PTV_name:
            if nb_fx_A1 == 14:
                cg.PlanningGoal.ParameterValue = nb_fx_A1 * 3 * 95 #3 Gy per fraction
            else:
                cg.PlanningGoal.ParameterValue = nb_fx_A1 * 2 * 95

    # Add clinical goal for coverage of PTV A2
    #plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=ptv_A2.Name, GoalValue=(nb_fx_A2 * 2 * 95), GoalCriteria="AtLeast", GoalType="VolumeAtDose", GoalVolume=99.5, AbsoluteGoalVolume=0)
    eval.add_clinical_goal(ptv_A2.Name, rx_dose_A2 * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)

    # Change reference value in Dose Color Table
    patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose_A2 * 100
    
    if roi.roi_exists("PTV A3"):
        for beam in plan.BeamSets[1].Beams:
            beam.Name = "A3"+beam.Name[2:]


def create_prostate_plan_A2_split():
    """
    Voir :py:mod:`plan_prostate_A2_split`.
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    # Create PTV A2-RECTUM
    retval_5 = patient.PatientModel.CreateRoi(Name="PTV A2-RECTUM", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_5.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV A2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  "RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_5.UpdateDerivedGeometry(Examination=examination)

    # Create WALL RECT ds PTV A2
    retval_10 = patient.PatientModel.CreateRoi(Name="WALL RECT ds PTV A2", Color="Aqua", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_10.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["WALL RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                   "PTV A2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_10.UpdateDerivedGeometry(Examination=examination)

    # Rename first beamset A1 and change nb fractions to 27
    plan.BeamSets[0].DicomPlanLabel = "A1"
    plan.BeamSets[0].FractionationPattern.NumberOfFractions = 27

    # Add Beam Set A2
    if patient.Examinations[0].PatientPosition == "HFS":
        beamset = plan.AddNewBeamSet(Name="A2", ExaminationName=examination.Name, MachineName="Salle 11", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=13, CreateSetupBeams=True, Comment="")
    else:
        beamset = plan.AddNewBeamSet(Name="A2", ExaminationName=examination.Name, MachineName="Salle 11", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstProne", NumberOfFractions=13, CreateSetupBeams=True, Comment="")

    # Make A2 dependent on A1
    plan.UpdateDependency(DependentBeamSetName="A2", BackgroundBeamSetName="A1", DependencyUpdate="CreateDependency")

    # Prescribe to PTV A2
    beamset.AddDosePrescriptionToRoi(RoiName="PTV A2-RECTUM", DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=2470, RelativePrescriptionLevel=1)

    # Add arc
    beams.add_beams_prostate_A2(beamset=beamset)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan, beamset=2)

    # Set maximum delivery time
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan, beamset=2)

    # Add optimization objectives
    retval_1 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName="PTV A2-RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet="A2")
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 2470
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 100

    retval_2 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="PTV A2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet="A2")
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 2730
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.Weight = 10

    retval_3 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 7500
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.PercentVolume = 15
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 10

    retval_4 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.DoseLevel = 7000
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.PercentVolume = 25
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.Weight = 10

    retval_5 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.DoseLevel = 6500
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.PercentVolume = 35
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.Weight = 10

    retval_6 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDvh", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.DoseLevel = 6000
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.PercentVolume = 50
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.Weight = 10

    retval_7 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="RECTUM", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.DoseLevel = 7950
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.PercentVolume = 50
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.Weight = 10

    retval_8 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="VESSIE", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 8200
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.PercentVolume = 50

    retval_9 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="BodyRS", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.HighDoseLevel = 7600
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseLevel = 4000
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.LowDoseDistance = 3
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[8].DoseFunctionParameters.Weight = 0

    retval_10 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName="RECTUM ds PTV A2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet="A2")
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[9].DoseFunctionParameters.DoseLevel = 2280
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[9].DoseFunctionParameters.Weight = 10

    retval_11 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName="WALL RECT ds PTV A2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet="A2")
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[10].DoseFunctionParameters.DoseLevel = 2438
    plan.PlanOptimizations[1].Objective.ConstituentFunctions[10].DoseFunctionParameters.Weight = 0

    # Modify clinical goal for coverage of PTV A1
    plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[0].PlanningGoal.GoalValue = 5130

    # Add clinical goal for coverage of PTV A2
    plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="PTV A2-RECTUM", GoalValue=2470, GoalCriteria="AtLeast", GoalType="VolumeAtDose", GoalVolume=99.5, AbsoluteGoalVolume=0)
    plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="RECTUM ds PTV A2", GoalValue=2280, GoalCriteria="AtLeast", GoalType="VolumeAtDose", GoalVolume=99.5, AbsoluteGoalVolume=0)

    # Change reference value in Dose Color Table
    patient.CaseSettings.DoseColorMap.ReferenceValue = 2600


# Toggles Dose Color Table reference dose between the dose of the currently selected beamset and the total dose for all beamsets.
# Script attempts to determine correct dose per fraction and compensate if Rx is to 95% isodose (prostate cases in progress)
def toggle_reference_dose():
    """
    Voir :py:mod:`toggle_reference_dose`.
    """
    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()

    dose_per_fx = beamset.Prescription.PrimaryDosePrescription.DoseValue / beamset.FractionationPattern.NumberOfFractions
    
    if dose_per_fx == 190: #Prostate with 2 Gy per fraction prescribed to cover with 95% isodose
        dose_per_fx = 200
    elif dose_per_fx == 237 or dose_per_fx == 238: #Prostate with 2.5 Gy per fraction prescribed to cover with 95% isodose
        dose_per_fx = 250
    elif dose_per_fx == 285: #Prostate with 3 Gy per fraction prescribed to cover with 95% isodose
        dose_per_fx = 300
    
    total_dose = 0
    for bs in plan.BeamSets:
        total_dose += bs.FractionationPattern.NumberOfFractions * dose_per_fx
    
    current_bs_dose = beamset.FractionationPattern.NumberOfFractions * dose_per_fx
        
    if patient.CaseSettings.DoseColorMap.ReferenceValue == current_bs_dose:
        patient.CaseSettings.DoseColorMap.ReferenceValue = total_dose
    else:
        patient.CaseSettings.DoseColorMap.ReferenceValue = current_bs_dose
        
    
def finaliser_plan_prostate():
    """
    Voir :py:mod:`finaliser_plan_prostate`.
    """

    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    # Rename OAR contours for SuperBridge transfer
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["RECTUM", "VESSIE", "INTESTINS", "RECTO-SIGMOIDE", "PROSTATE"]:
            rois.Name += "*"
    
    colors = ["Red","Green","Blue","Yellow","Orange"]
    
    for i, bs in enumerate(plan.BeamSets):        
        ptv = patient.PatientModel.RegionsOfInterest[bs.Prescription.PrimaryDosePrescription.OnStructure.Name]
        beamset_name = ptv.Name[4:6] #ROI name must be in the format PTV A1
        nb_fx = bs.FractionationPattern.NumberOfFractions
        if nb_fx == 15:
            rx_dose = 3750
            for cg in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
                if cg.ForRegionOfInterest.Name == ptv.Name:
                    cg.PlanningGoal.ParameterValue = 3563
        else:
            rx_dose = 200 * nb_fx
            for cg in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
                if cg.ForRegionOfInterest.Name == ptv.Name:
                    cg.PlanningGoal.ParameterValue = rx_dose * 0.95          
        
        #Use presence of isodose contour to decide whether finalisation actions are taken on a given beamset
        if roi.roi_exists("isodose "+beamset_name): #eg, isodose A1
            # Rename beamset
            bs.DicomPlanLabel = beamset_name    

            # Add * to the end of PTV name and rename 95% isodose line
            ptv.Name += '*'
            isodose_roi = patient.PatientModel.RegionsOfInterest[("isodose "+beamset_name)]
            isodose_roi.Name = ("ISO 95% "+beamset_name+" "+str(rx_dose/100.0*0.95)+"Gy*")
            isodose_roi.Name = isodose_roi.Name.replace('.0Gy','Gy')
            
            # Add comment for Superbridge transfer
            bs.Prescription.Description = "VMAT"
      
            # Create DSP and PT PRESC
            poi_name = 'PT PRESC ' + beamset_name
            poi.create_poi({'x': 0, 'y': 0, 'z': 0}, poi_name, color=colors[i])
            bs.CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 })
           
            # Move PT PRESC to a point that receives correct dose per fraction and prescribe
            poi.place_prescription_point(target_fraction_dose=rx_dose/nb_fx , ptv_name=ptv.Name, poi_name=poi_name, beamset=bs)
            bs.AddDosePrescriptionToPoi(PoiName=poi_name, DoseValue=rx_dose)
      
            # Move DSP to coordinates of PT PRESC and assign to all beams
            point = poi.get_poi_coordinates(poi_name)
            dsp = [x for x in bs.DoseSpecificationPoints][0]
            dsp.Name = "DSP "+beamset_name
            dsp.Coordinates = point.value

            for beam in bs.Beams:
                beam.SetDoseSpecificationPoint(Name=("DSP "+beamset_name))
            bs.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point (otherwise not displayed)

                
def prostate_A2_A3():
    """
    Voir :py:mod:`prostate_A2_A3`.
    """

    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()
    
    #Rename PT PRESC
    patient.PatientModel.PointsOfInterest['PT PRESC A2'].Name = 'PT PRESC A3'
    patient.PatientModel.PointsOfInterest['PT PRESC A1'].Name = 'PT PRESC A2'
    
    #Rename BeamSets
    plan.BeamSets[1].DicomPlanLabel = 'A3'
    plan.BeamSets[0].DicomPlanLabel = 'A2'
    
    #Rename Isodose contours
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        if r'ISO 95% A2' in name:
            patient.PatientModel.RegionsOfInterest[name].Name = r'ISO 95% A3' + name[10:]
        elif r'ISO 95% A1' in name:
            patient.PatientModel.RegionsOfInterest[name].Name = r'ISO 95% A2' + name[10:]
    
    #Rename Dose Specification PointsOfInterest
    plan.BeamSets[1].DoseSpecificationPoints[0].Name = 'DSP A3'
    plan.BeamSets[0].DoseSpecificationPoints[0].Name = 'DSP A2'
    
    #Rename Beams
    for beam in plan.BeamSets[1].Beams:
        beam.Name = "A3"+beam.Name[2:]
    for beam in plan.BeamSets[0].Beams:
        beam.Name = "A2"+beam.Name[2:]
    
    # Dose is recalculated to show beam dose at spec point (otherwise not displayed)    
    plan.BeamSets[0].ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  
    plan.BeamSets[1].ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)

    
def auto_opt_prostate():
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()

    
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
  
    #Get DVH values for chosen ROI
    roi_name = "RECTUM"

    #Adjust opitimization objectives to reflect obtained DVH values
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if objective.ForRegionOfInterest.Name == roi_name and objective.DoseFunctionParameters.FunctionType == 'MaxDvh':
            dose_level = objective.DoseFunctionParameters.DoseLevel
            target_vol = objective.DoseFunctionParameters.PercentVolume
            obtained_vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=roi_name, DoseValues=[dose_level])
            if obtained_vol[0]*100 > target_vol:
                objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0]*100)
            else:
                objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0]*100 - 1)

    #Reset and optimize twice
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    
def fit_obj_prostate(plan = None, beamset = None):
    
    #plan = lib.get_current_plan()
    #beamset = lib.get_current_beamset()
  
    #Get DVH values for chosen ROI
    roi_name = "RECTUM"

    #Adjust opitimization objectives to reflect obtained DVH values
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if objective.ForRegionOfInterest.Name == roi_name and objective.DoseFunctionParameters.FunctionType == 'MaxDvh':
            dose_level = objective.DoseFunctionParameters.DoseLevel
            target_vol = objective.DoseFunctionParameters.PercentVolume
            obtained_vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=roi_name, DoseValues=[dose_level])
            if obtained_vol[0]*100 > target_vol:
                objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0]*100)
            else:
                objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0]*100 - 1)
    
    
    

def prostate_A1_pois(plan_data):
        
    #Create ISO
    poi.create_iso(exam = plan_data['exam'])
    
    # Assign Point Types
    poi.auto_assign_poi_types()
    
    # Erase any points other than ISO or REF SCAN
    poi.erase_pois_not_in_list()

      
def prostate_A1_rois(plan_data):        

    patient = plan_data['patient']
    exam = plan_data['exam']
    
    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi.auto_assign_roi_types_v2()    

    # Create BodyRS+Table, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table()

    # Clean Contrast ROI outside of body
    if roi.roi_exists("CONTRASTE"):
        retval_1 = patient.PatientModel.CreateRoi(Name="Contraste Mod", Color="Yellow", Type="ContrastAgent", TissueName=None, RoiMaterial=None)
        retval_1.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
            "CONTRASTE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_1.UpdateDerivedGeometry(Examination=exam)

    # Create PTV A1 (except for PACE cases)
    if plan_data['plan_type'] != 'Prostate PACE':
        if roi.roi_exists("PTV A1"):
            patient.PatientModel.RegionsOfInterest["PTV A1"].Type = "PTV"
            patient.PatientModel.RegionsOfInterest["PTV A1"].OrganData.OrganType = "Target"
            ptv = patient.PatientModel.RegionsOfInterest["PTV A1"]
        elif roi.roi_exists("PTV 1.5cm"):
            if roi.roi_exists("PTV VS"):
                ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
                ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV VS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                ptv.UpdateDerivedGeometry(Examination=exam)
            else: 
                ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
                ptv.SetMarginExpression(SourceRoiName="PTV 1.5cm", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                ptv.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")
        elif roi.roi_exists("PTV 1cm"):
            if roi.roi_exists("PTV VS"):
                ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
                ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV VS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                ptv.UpdateDerivedGeometry(Examination=exam)
            else: 
                ptv = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
                ptv.SetMarginExpression(SourceRoiName="PTV 1cm", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                ptv.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")

        # Create PTV A2 (copy of PTV 1cm, except when PTVBoost exists) (do not perform for PACE cases)
        boost = False
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            if 'PTVBOOST' in name.replace(' ', '').upper():
                boost = True
                boost_name = name
        if boost: # PTV A2 is a copy of PTVBoost
            retval_3 = patient.PatientModel.CreateRoi(Name="PTV A2", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
            retval_3.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [boost_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            retval_3.UpdateDerivedGeometry(Examination=exam)        
        elif roi.roi_exists("PTV 1cm"): # PTV A2 is a copy of PTV 1cm
            retval_3 = patient.PatientModel.CreateRoi(Name="PTV A2", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
            retval_3.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            retval_3.UpdateDerivedGeometry(Examination=exam)
    
    if plan_data['plan_type'] == 'Prostate PACE':
        if roi.roi_exists('PTV_7800'):
            roi.set_roi_type('PTV_7800', 'Ptv', 'Target')
        if roi.roi_exists('PTV_3625'):
            roi.set_roi_type('PTV_3625', 'Ptv', 'Target')            
    
    
    # Create RECTUM+3mm
    if plan_data['plan_type'] == 'Prostate PACE':
        patient.PatientModel.CreateRoi(Name="Rectum+3mm", Color="skyblue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['Rectum+3mm'].SetMarginExpression(SourceRoiName="Rectum", MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
        patient.PatientModel.RegionsOfInterest['Rectum+3mm'].UpdateDerivedGeometry(Examination=exam)   
    else:
        patient.PatientModel.CreateRoi(Name="RECTUM+3mm", Color="skyblue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['RECTUM+3mm'].SetMarginExpression(SourceRoiName="RECTUM", MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
        patient.PatientModel.RegionsOfInterest['RECTUM+3mm'].UpdateDerivedGeometry(Examination=exam)   
    
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)
        
    #Override Contraste Mod with water    
    if roi.roi_exists("Contraste Mod"):
        #It is seemingly impossible to use the built-in material Water, so a copy is made called Eau
        #But first we check to see if Eau exists already, because creating a second copy crashes RayStation (even when using try)
        db = get_current("PatientDB")
        eau_already_exists = False
        i=0
        #If Eau already exists, assign it to the ROI and end the function
        for material in patient.PatientModel.Materials:
            i += 1
            if material.Name == 'Eau':
                patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = material)
                eau_already_exists = True
                break
        #If Eau does not exist, create it, then assign it to the ROI
        if not eau_already_exists:
            patient.PatientModel.CreateMaterial(BaseOnMaterial=db.TemplateMaterials[0].Materials[25], Name = "Eau", MassDensityOverride = 1.000)
            patient.PatientModel.RegionsOfInterest["Contraste Mod"].SetRoiMaterial(Material = patient.PatientModel.Materials[i])      
        

def prostate_A1_add_plan_and_beamset(plan_data):

    if plan_data['plan_type'] == 'Prostate PACE':
        if plan_data['rx_dose'] == 7800:
            ptv_name = 'PTV_7800'
        else:
            ptv_name = 'PTV_3625'
    else:
        ptv_name = 'PTV A1'

    # Add Treatment plan
    plan = plan_data['patient'].AddNewPlan(PlanName="A1 seul", PlannedBy="", Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    if plan_data['exam'].PatientPosition == "HFS":
        position = "HeadFirstSupine"
    else:
        position = "HeadFirstProne"
        
    beamset = plan.AddNewBeamSet(Name="A1", ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition=position, NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment="")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv_name, DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose']*0.95, RelativePrescriptionLevel=1)



def prostate_A1_opt_settings(plan_data):

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan_data['patient'].TreatmentPlans['A1 seul'])

    # Set VMAT conversion parameters
    if plan_data['nb_fx'] == 5: #7.25 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=300.0, plan=plan_data['patient'].TreatmentPlans['A1 seul'])          
    elif plan_data['nb_fx'] == 22 or plan_data['nb_fx'] == 20: #3 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=200.0, plan=plan_data['patient'].TreatmentPlans['A1 seul'])
    elif plan_data['nb_fx'] == 24: #2.5 Gy per fraction
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=175.0, plan=plan_data['patient'].TreatmentPlans['A1 seul'])  
    else:
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan_data['patient'].TreatmentPlans['A1 seul'])
    

def prostate_A1_rename(plan_data):
        
    patient = plan_data['patient']
    plan = patient.TreatmentPlans['A1 seul']
    
    patient.PatientModel.RegionsOfInterest['PTV A2'].Name = 'PTV A3'
    patient.PatientModel.RegionsOfInterest['PTV A1'].Name = 'PTV A2'
    plan.Name = "A2 seul"
    plan.BeamSets[0].DicomPlanLabel = "A2"
    for beam in plan.BeamSets[0].Beams:
        beam.Name = "A2"+beam.Name[2:]
         

def prostate_A1_create_isodose_lines(plan_data):         

    patient = plan_data['patient']

    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = plan_data['rx_dose']
    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
    eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=75, r=0, g=255, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=108.75, r=255, g=0, b=255, alpha=255)
 

    
    
    
    
    #Place pour tester des nouveaux fonctions
def test_MA():
    #plan = lib.get_current_plan()
    #beamset = lib.get_current_beamset()
    #exam = lib.get_current_examination()
    #patient = lib.get_current_patient()
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
   
    launcher.premiere_verif()
    #verification.verify_beams()
    #optim.essai_autre_technique()
    #message.message_window('essai')
    #import report
    #report.create_verif1_report()

    

    
    
    
    

