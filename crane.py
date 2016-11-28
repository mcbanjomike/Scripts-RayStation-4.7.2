# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification crânes stéréotaxiques.

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
import message

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


def plan_crane_stereo(machine = 'BeamMod', isodose_creation = True, treatment_technique = 'VMAT', plan_name='A1'):
    """
    Voir :py:mod:`plan_poumoun_sbrt`.
    """

    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    msg = ''
   
    # Create ISO (if point doesn't already exist)
    poi.create_iso()
    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            roi.set_roi_type(name, 'Ptv', 'Target')
        elif 'CTV' in n and '-' not in n:
            roi.set_roi_type(name, 'Ctv', 'Target')
        elif 'GTV' in n and '-' not in n:
            roi.set_roi_type(name, 'Gtv', 'Target')
        elif 'ITV' in n and '-' not in n:
            roi.set_roi_type(name, 'TreatedVolume', 'Target')
        elif n == 'BODY':
            roi.set_roi_type(name, organ_type='Other')
        elif n == 'BODY+TABLE':
            roi.set_roi_type(name, organ_type='Other')
        elif n.startswith('BOLUS'):
            roi.set_roi_type(name, 'Bolus', 'Other')
        else:
            roi.set_roi_type(name, 'Organ', 'OrganAtRisk')

    # Create BodyRS, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    #roi.generate_BodyRS_plus_Table(planche_seulement=True)
    roi.generate_BodyRS_using_threshold()

    # Identify which PTV and ITV to use for creation of optimization contours
    if roi.roi_exists("PTV15"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV15"]
        presc_dose = 1500
    elif roi.roi_exists("PTV18"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV18"]
        presc_dose = 1800

    # Generate optimization contours
    # Create PTV+2mm, PTV+5mm, PTV+13mm and PTV+23mm
    patient.PatientModel.CreateRoi(Name="PTV+2mm", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2})
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="PTV+5mm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5})
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="PTV+13mm", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3})
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="PTV+23mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 2.3, 'Inferior': 2.3, 'Anterior': 2.3, 'Posterior': 2.3, 'Right': 2.3, 'Left': 2.3})
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="PTV+73mm", Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+73mm'].SetMarginExpression(SourceRoiName='PTV+23mm', MarginSettings={'Type': "Expand", 'Superior': 2.5, 'Inferior': 2.5, 'Anterior': 5, 'Posterior': 5, 'Right': 5, 'Left': 5})
    patient.PatientModel.RegionsOfInterest['PTV+73mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])    
    # Create RINGs and TISSUS SAINS
    patient.PatientModel.CreateRoi(Name="RING_0_2mm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_0_2mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+2mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_0_2mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="RING_1_3mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_1_3mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_1_3mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="RING_2_8mm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_2_8mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+13mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_2_8mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="RING_3_1cm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_3_1cm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+13mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_3_1cm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="TISSUS SAINS", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+73mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])    
    # Create CERVEAU-PTV and OPT CERVEAU-PTV
    patient.PatientModel.CreateRoi(Name="CERVEAU-PTV", Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="OPT CERVEAU-PTV", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU", "PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Erase expanded PTV contours
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+73mm'].DeleteRoi()

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="Stereo Crane", PlannedBy="", Comment="", ExaminationName="CT 1", AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    beamset = plan.AddNewBeamSet(Name="Stereo Crane", ExaminationName=exam.Name, MachineName=machine, NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=treatment_technique, PatientPosition="HeadFirstSupine", NumberOfFractions=1, CreateSetupBeams=True, Comment="VMAT")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=presc_dose, RelativePrescriptionLevel=1)

    # plan and beamset are created but not currently selected in RS
    # therefore we must retain the objects in variables and pass them on
    # to the following functions, which otherwise would assume that
    # these are currently selected by the user in RS.
    # VTL

    # Add beams
    if treatment_technique == 'VMAT':
        beams.add_beams_brain_stereo(beamset=beamset, plan_name=plan_name)
    elif treatment_technique == 'SMLC':
        beams.add_beams_brain_static(beamset=beamset, plan_name=plan_name, iso_name='ISO', exam=exam, nb_beams=13)

    # Set optimization parameters and VMAT conversion parameters
    if treatment_technique == 'VMAT':
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)
    elif treatment_technique == 'SMLC':
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40

    # Add optimization objectives
    optimization_objectives.add_opt_obj_brain_stereo(patient_plan=plan)

    # Add clinical goals
    clinical_goals.add_dictionary_cg('Crane Stereo', presc_dose/100, 1, plan=plan)
    
    # Rename PTV with standard formatting
    ptv.Name = "PTV " + plan_name + " " + str(presc_dose/100) + "Gy"
    ptv.Name = ptv.Name.replace('.0Gy','Gy')            
        
    # Generate dose color table
    if isodose_creation:
        eval.remove_all_isodose_lines()
        patient.CaseSettings.DoseColorMap.ReferenceValue = presc_dose
        if presc_dose == 1500:           
            fivegy = 33.33
            tengy = 66.67
        elif presc_dose == 1800:
            fivegy = 27.78
            tengy = 55.56
        patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
        eval.add_isodose_line_rgb(dose=tengy, r=0, g=0, b=160, alpha=255)
        eval.add_isodose_line_rgb(dose=80, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
        patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if not points.Name.upper() in ["ISO", "ISOCENTRE", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()


def finaliser_plan_crane_stereo():
    """
    #Voir :py:mod:`finaliser_plan_crane_stereo`.
    """
    patient = lib.get_current_patient()
    plan = lib.get_current_plan()

    # Rename OAR contours for SuperBridge transfer        
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["MOELLE", "TR CEREBRAL", "OEIL DRT", "OEIL GCHE"]:
            rois.Name += "*"
        
    colors = ["Red","Green","Blue","Yellow","Orange"] 
    for i, bs in enumerate(plan.BeamSets):
        ptv = patient.PatientModel.RegionsOfInterest[bs.Prescription.PrimaryDosePrescription.OnStructure.Name]
        beamset_name = ptv.Name[4:6] #ROI name must be in the format PTV A1 or PTV B1 48Gy
        nb_fx = bs.FractionationPattern.NumberOfFractions
        rx_dose = bs.Prescription.PrimaryDosePrescription.DoseValue
        
        #Use presence of isodose contour to decide whether finalisation actions are taken on a given beamset
        if roi.roi_exists("isodose "+beamset_name): #eg, isodose A1
            # Rename beamset
            bs.DicomPlanLabel = beamset_name
            
            # Rename isodose ROI and add * to it and PTV
            isodose_roi = patient.PatientModel.RegionsOfInterest["isodose " + beamset_name]         
            isodose_roi.Name = ("ISO "+ beamset_name + " " + str(rx_dose/100) + "Gy*")
            isodose_roi.Name = isodose_roi.Name.replace('.0Gy','Gy')
            ptv.Name += '*'            
            
            # Add comment for Superbridge transfer
            bs.Prescription.Description = "VMAT"
      
            # Create DSP and PT PRESC
            poi_name = 'PT PRESC ' + beamset_name
            poi.create_poi({'x': 0, 'y': 0, 'z': 0}, poi_name, color=colors[i])
            bs.CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 })
           
            # Move PT PRESC to a point that receives correct dose per fraction and prescribe
            poi.place_prescription_point(target_fraction_dose=rx_dose/nb_fx, ptv_name=ptv.Name, poi_name=poi_name, beamset=bs)
            bs.AddDosePrescriptionToPoi(PoiName=poi_name, DoseValue=rx_dose)
      
            # Move DSP to coordinates of PT PRESC and assign to all beams
            point = poi.get_poi_coordinates(poi_name)
            dsp = [x for x in bs.DoseSpecificationPoints][0]
            dsp.Name = "DSP "+beamset_name
            dsp.Coordinates = point.value

            for beam in bs.Beams:
                beam.SetDoseSpecificationPoint(Name=dsp.Name)
            bs.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point (otherwise not displayed)       
       
    
def plan_crane_3DC(site_name='A1', presc_dose=1500, nb_fx=1, isodose_creation = False, opt_collimator_angles = False):

    #WARNING: This script uses UI scripting. If the user switches focus to another piece of software during 
    #         execution, the UI commands will not be completed. The script will not give the desired results
    #         and may crash.
    
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()

    # Create ISO (if point doesn't already exist)
    poi.create_iso()
                    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi.auto_assign_roi_types_v2()
    
    # Create BodyRS, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_using_threshold()

    # Identify the PTV and prescription dose
    if roi.roi_exists("PTV15"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV15"]
        presc_dose = 1500
    elif roi.roi_exists("PTV18"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV18"]
        presc_dose = 1800
        
    # Create OPTPTV
    if not roi.roi_exists("OPTPTV"):
        patient.PatientModel.CreateRoi(Name="OPTPTV", Color="Yellow", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['OPTPTV'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.15, 'Inferior': 0.15, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['OPTPTV'].UpdateDerivedGeometry(Examination=exam)
    # Create CERVEAU-PTV
    if not roi.roi_exists("CERVEAU-PTV"):
        patient.PatientModel.CreateRoi(Name="CERVEAU-PTV", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].UpdateDerivedGeometry(Examination=exam)    
            
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)    
    
    # Create plan
    plan = patient.AddNewPlan(PlanName="3DC", PlannedBy="", Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
    
    # Create beamset
    beamset = plan.AddNewBeamSet(Name="3DC", ExaminationName=exam.Name, MachineName="BeamMod", NominalEnergy=None, Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=presc_dose, RelativePrescriptionLevel=1, AutoScaleDose=False)

    # Generate dose color table
    if isodose_creation:
        d = dict(rx_dose = presc_dose, patient = patient)
        crane_stereo_create_isodose_lines(plan_data = d)
    
    # Add beams
    beams.add_beams_brain_static(beamset=beamset, site_name=site_name, iso_name='ISO', exam=exam, nb_beams=13)    
    
    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    patient.Save()
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['3DC'].Select()  
    
    # Conform the MLCs to the OPTPTV
    ui.TabControl_Modules.TabItem['3D-CRT Beam Design'].Select()
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_PlanSettings.Click()

    # Change settings in Plan Settings window
    for row in ui.RoisUsedForPlanningView.DataGridRow:
        if row.RoiGeometry.TextBlock_Name.Text == 'OPTPTV' or row.RoiGeometry.TextBlock_Name.Text == ptv.Name:
            if not row.CheckBox.IsChecked:
                row.CheckBox.Click()    
        elif row.CheckBox.IsChecked:
            row.CheckBox.Click()

    ui.TextBox_LeafPositioningThreshold.Text = '0.25'
    ui.Button_OK.Click()
   
    # Check boxes to treat OPTPTV
    ui.Workspace.TabControl['Beams'].TabItem['Treat and Protect'].Select()
    for row in ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow:
        if not row.CheckBox[0].IsChecked:
            row.CheckBox[0].Click()   
        if row.CheckBox[1].IsChecked:
            row.CheckBox[1].Click()
            
    # Actually conform the MLCs
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformAllBeams.Click()
    
    # If requested, automatically determine collimator angles
    if opt_collimator_angles:
        optimize_collimator_angles()
    
    # Calculate dose and scale to Rx
    beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)
    beamset.NormalizeToPrescription(RoiName=ptv.Name, DoseValue=presc_dose, DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=False)
            
    # Add clinical goals
    clinical_goals.add_dictionary_cg('Crane Stereo', presc_dose/100, 1, plan = plan)            
    
    # Save plan and create copy
    patient.Save()
    plan = patient.CopyPlan(PlanName="3DC", NewPlanName="3DC optimised")
    
    # In the new plan, change optimization settings
    patient.Save() #Might not be necessary a second time, I'm not sure
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['3DC optimised'].Select()    
    
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 30
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 6
    plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True    
    
    # Uncheck Segment Shape optimization for all beams
    ui.MenuItem[3].Button_PlanOptimization.Click() #Select Plan Optimization tab
    ui.Workspace.TabControl['Objectives/Constraints'].TabItem['Beam Optimization Settings'].Select()
    if ui.Workspace.TabControl['Objectives/Constraints'].RayDataGrid.DataGridColumnHeader['Segment shapes'].CheckBox.IsChecked:
        ui.Workspace.TabControl['Objectives/Constraints'].RayDataGrid.DataGridColumnHeader['Segment shapes'].CheckBox.Click()
    
    # Add optimization objectives
    optim.add_mindose_objective(ptv.Name, presc_dose, weight=1, plan=plan)
    optim.add_dosefalloff_objective('BodyRS', presc_dose, presc_dose*0.45, 0.7, weight=10, plan=plan) 
    
    # Optimize plan twice
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()

    
def crane_3DC_erase_beams(MU_threshold=25.0):
    beamset = lib.get_current_beamset()
    num_erased = 0
    
    for beam in beamset.Beams:
        if beam.BeamMU < MU_threshold:
            beamset.DeleteBeam(BeamName=beam.Name) 
            num_erased += 1
            
    for i, beam in enumerate(beamset.Beams):
        beam.Name = beam.Name[:3]+str(i+1)
        beam.Number = i+1
        
    return num_erased
        
        
def crane_3DC_add_beams(subptv_name = 'PTV1'):

    #WARNING: This script uses UI scripting. If the user switches focus to another piece of software during 
    #         execution, the UI commands will not be completed. The script will not give the desired results
    #         and may crash.

    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    
    ptv = patient.PatientModel.RegionsOfInterest[beamset.Prescription.PrimaryDosePrescription.OnStructure.Name]
    presc_dose = beamset.Prescription.PrimaryDosePrescription.DoseValue

    # Create OPTsubPTV
    patient.PatientModel.CreateRoi(Name=("OPT"+subptv_name), Color='Skyblue', Type="Ptv", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[("OPT"+subptv_name)].SetMarginExpression(SourceRoiName=subptv_name, MarginSettings={'Type': "Expand", 'Superior': 0.15, 'Inferior': 0.15, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest[("OPT"+subptv_name)].UpdateDerivedGeometry(Examination=exam)

    #Copy all beams
    for beam in beamset.Beams:
        beamset.CopyBeam(BeamName=beam.Name)
        
    #Give every beam at least 1 MU (necessary for merging later)
    for beam in beamset.Beams:
        if beam.BeamMU == 0:
            beam.BeamMU += 1        

    #Use UI to add sub-PTV to list of optimization structures
    ui = get_current("ui")
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.TabControl_Modules.TabItem['3D-CRT Beam Design'].Select()
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_PlanSettings.Click() #Open Plan Settings window
    for row in ui.RoisUsedForPlanningView.DataGridRow:
        if row.RoiGeometry.TextBlock_Name.Text == ("OPT"+subptv_name) and not row.CheckBox.IsChecked:
            row.CheckBox.Click()
    ui.Button_OK.Click()

    #Change Treat and Protect settings for new beams
    ui.Workspace.TabControl['Beams'].TabItem['Treat and Protect'].Select()
    for row in ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow:
        if row.TextBlock_Name.Text[-2:] == '_1':
            if row.CheckBox[0].IsChecked: #OPTPTV
                row.CheckBox[0].Click()     
            if row.CheckBox[2].IsChecked: #PTV
                row.CheckBox[2].Click()                    
            if not row.CheckBox[1].IsChecked: #OPTsubPTV
                row.CheckBox[1].Click() 
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformAllBeams.Click()
    
    #Rename beams
    for i, beam in enumerate(beamset.Beams):
        beam.Name = beam.Name[:3]+str(i+1)
        
    # Calculate dose and scale to Rx
    beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)
    beamset.NormalizeToPrescription(RoiName=ptv.Name, DoseValue=presc_dose, DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=False)    

    # Uncheck Segment Shape optimization for all beams
    ui.MenuItem[3].Button_PlanOptimization.Click() #Select Plan Optimization tab
    ui.Workspace.TabControl['Objectives/Constraints'].TabItem['Beam Optimization Settings'].Select()
    if ui.Workspace.TabControl['Objectives/Constraints'].RayDataGrid.DataGridColumnHeader['Segment shapes'].CheckBox.IsChecked:
        ui.Workspace.TabControl['Objectives/Constraints'].RayDataGrid.DataGridColumnHeader['Segment shapes'].CheckBox.Click()    
        
    # Optimize plan twice
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    
    
def optimize_collimator_angles():
    """
    This script is maybe a little too slow and cumbersome to use clinically. The problem is that editing the collimator angle
    can only be done at the segment level, but doing so causes a mismatch with the beam's InitialCollimatorAngle, and that seems
    to lead to the ConformBeamMLC button not working. I can get around this by opening up the Edit dialog to change the collimator
    angle for the beam, but it takes a lot of time and it will fail catastrophically if the user does anything other than sit and watch.
    """

    ui = get_current("ui")
    beamset = lib.get_current_beamset() 
    
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.TabControl_Modules.TabItem['3D-CRT Beam Design'].Select()
    #ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformBeamMLC.Click()
    ui.Workspace.TabControl['Beams'].TabItem['Beams'].Select()

    #results = ""
    
    
    for beam in beamset.Beams:
        seg = beam.Segments[0]
        lowest_area = 10000000
        new_collimator_angle = 0
        best_angle = 0
        change_collimator_angle(beam.Number,new_collimator_angle)
        #results += "\n" + beam.Name + "\n"
        
        #Go through each collimator angle to evaluate which segment has the smallest open area
        while new_collimator_angle < 180:
            ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformBeamMLC.Click()
            if seg.LeafPositions[0][0] != seg.LeafPositions[1][0] or seg.LeafPositions[0][39] != seg.LeafPositions[1][39]: #Discount any collimator orientation that has the first/last pair of leaves open
                new_collimator_angle += 30
                change_collimator_angle(beam.Number,new_collimator_angle)            
            else: #First/last leaf pairs are closed, so evaluate this segment
                segment_area = 0
                for i in range(39):
                    segment_area += seg.LeafPositions[1][i]-seg.LeafPositions[0][i]
                #results += str(new_collimator_angle) + "                 " + str(segment_area) + "\n"                
                if segment_area < lowest_area:
                    lowest_area = segment_area
                    best_angle = new_collimator_angle
                new_collimator_angle += 30
                change_collimator_angle(beam.Number,new_collimator_angle)
      
        #Apply the best collimator angle to the beam
        change_collimator_angle(beam.Number,best_angle)
        ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformBeamMLC.Click()
        
    #message.message_window('All done!\nCollimator Angle    Segment Area\n'+results)
    
def change_collimator_angle(beam_number=1, angle=0):
    beam_number_text = str(beam_number)
    coll_angle_text = str(angle)

    ui = get_current("ui")
    ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow[beam_number_text].Select()
    ui.Workspace.TabControl['Beams'].BeamCommands.Button_Edit.Click()
    #ui = get_current("ui")
    ui.BeamDialogAngles.TextBox_CollimatorAngle.Text = coll_angle_text
    ui.Button_OK.Click()
    #ui = get_current("ui")    
    
    
    
def crane_stereo_pois(plan_data):

    # Create ISO (if point doesn't already exist)
    poi.create_iso()
    
    # Assign Point Types
    poi.auto_assign_poi_types()
    
    # Erase any points other than ISO or REF SCAN
    poi.erase_pois_not_in_list()
   
    
def crane_stereo_rois(plan_data):

    patient = plan_data['patient']
    exam = plan_data['exam']
    
    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi.auto_assign_roi_types_v2()

    # Create BodyRS, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_using_threshold()

    # Generate optimization contours
    # Create PTV+2mm, PTV+5mm, PTV+13mm and PTV+23mm
    patient.PatientModel.CreateRoi(Name="PTV+2mm", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].SetMarginExpression(SourceRoiName=plan_data['ptv'].Name, MarginSettings={'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2})
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTV+5mm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].SetMarginExpression(SourceRoiName=plan_data['ptv'].Name, MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5})
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTV+13mm", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].SetMarginExpression(SourceRoiName=plan_data['ptv'].Name, MarginSettings={'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3})
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTV+23mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].SetMarginExpression(SourceRoiName=plan_data['ptv'].Name, MarginSettings={'Type': "Expand", 'Superior': 2.3, 'Inferior': 2.3, 'Anterior': 2.3, 'Posterior': 2.3, 'Right': 2.3, 'Left': 2.3})
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].UpdateDerivedGeometry(Examination=exam)  
    # Create RINGs and TISSUS SAINS
    patient.PatientModel.CreateRoi(Name="RING_0_2mm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_0_2mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+2mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [plan_data['ptv'].Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_0_2mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_1_3mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_1_3mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_1_3mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_2_8mm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_2_8mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+13mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_2_8mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_3_1cm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_3_1cm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+13mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_3_1cm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="TISSUS SAINS", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].UpdateDerivedGeometry(Examination=exam)    
    # Create CERVEAU-PTV and OPT CERVEAU-PTV
    if not roi.roi_exists("CERVEAU-PTV"):
        patient.PatientModel.CreateRoi(Name="CERVEAU-PTV", Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [plan_data['ptv'].Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="OPT CERVEAU-PTV", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU", "PTV+23mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [plan_data['ptv'].Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].UpdateDerivedGeometry(Examination=exam)
    # Erase expanded PTV contours
    patient.PatientModel.RegionsOfInterest['PTV+2mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+5mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+13mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+23mm'].DeleteRoi()

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

        
def crane_stereo_2niveaux_rois(plan_data):

    patient = plan_data['patient']
    exam = plan_data['exam']
    
    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi.auto_assign_roi_types_v2()

    # Create BodyRS, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_using_threshold()
        
    # create modPTV
    ptvH = plan_data['ptv']
    rx_doseH = plan_data['rx_dose']
    ptvL = plan_data['ptv_low']
    rx_doseL = plan_data['rx_dose_low']
    Mod_ptvL = patient.PatientModel.CreateRoi(Name="Mod_ptvL", Color="Yellow", Type="Ptv", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Mod_ptvL'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [ptvL.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptvH.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Mod_ptvL'].UpdateDerivedGeometry(Examination=exam)
    
    

    # creer la somme des PTV
    patient.PatientModel.CreateRoi(Name="PTVs", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVs'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [ptvH.Name, ptvL.Name], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    patient.PatientModel.RegionsOfInterest['PTVs'].UpdateDerivedGeometry(Examination=exam)

    # Generate optimization contours
    # Create PTV1+3mm, PTV1+11mm, PTV1+21mm etPTV2+3mm, PTV2+11mm, PTV2+21mm
    patient.PatientModel.CreateRoi(Name="PTVH+3mm", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVH+3mm'].SetMarginExpression(SourceRoiName=ptvH.Name, MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest['PTVH+3mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVH+11mm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVH+11mm'].SetMarginExpression(SourceRoiName=ptvH.Name, MarginSettings={'Type': "Expand", 'Superior': 1.1, 'Inferior': 1.1, 'Anterior': 1.1, 'Posterior': 1.1, 'Right': 1.1, 'Left': 1.1})
    patient.PatientModel.RegionsOfInterest['PTVH+11mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVH+21mm", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVH+21mm'].SetMarginExpression(SourceRoiName=ptvH.Name, MarginSettings={'Type': "Expand", 'Superior': 2.1, 'Inferior': 2.1, 'Anterior': 2.1, 'Posterior': 2.1, 'Right': 2.1, 'Left': 2.1})
    patient.PatientModel.RegionsOfInterest['PTVH+21mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVL+3mm", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVL+3mm'].SetMarginExpression(SourceRoiName=ptvL.Name, MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest['PTVL+3mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVL+11mm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVL+11mm'].SetMarginExpression(SourceRoiName=ptvL.Name, MarginSettings={'Type': "Expand", 'Superior': 1.1, 'Inferior': 1.1, 'Anterior': 1.1, 'Posterior': 1.1, 'Right': 1.1, 'Left': 1.1})
    patient.PatientModel.RegionsOfInterest['PTVL+11mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVL+21mm", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVL+21mm'].SetMarginExpression(SourceRoiName=ptvL.Name, MarginSettings={'Type': "Expand", 'Superior': 2.1, 'Inferior': 2.1, 'Anterior': 2.1, 'Posterior': 2.1, 'Right': 2.1, 'Left': 2.1})
    patient.PatientModel.RegionsOfInterest['PTVL+21mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVs+73mm", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVs+73mm'].SetMarginExpression(SourceRoiName="PTVs", MarginSettings={'Type': "Expand", 'Superior': 7.3, 'Inferior': 7.3, 'Anterior': 7.3, 'Posterior': 7.3, 'Right': 7.3, 'Left': 7.3})
    patient.PatientModel.RegionsOfInterest['PTVs+73mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTVs+21mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTVs+21mm'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTVH+21mm", "PTVL+21mm"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    patient.PatientModel.RegionsOfInterest['PTVs+21mm'].UpdateDerivedGeometry(Examination=exam)
    # Create RINGs and TISSUS SAINS
    patient.PatientModel.CreateRoi(Name="RING_PTVH_1_3mm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVH_1_3mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVH+3mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptvH.Name, ptvL.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVH_1_3mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_PTVL_1_3mm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVL_1_3mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVL+3mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptvL.Name,"PTVH+3mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVL_1_3mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_PTVH_2_8mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVH_2_8mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVH+11mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVH+3mm","PTVL+3mm" ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVH_2_8mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_PTVL_2_8mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVL_2_8mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVL+11mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVL+3mm", "PTVH+11mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVL_2_8mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_PTVH_3_1cm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVH_3_1cm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVH+21mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVH+11mm", "PTVL+11mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVH_3_1cm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_PTVL_3_1cm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_PTVL_3_1cm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVL+21mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVL+11mm", "PTVH+21mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['RING_PTVL_3_1cm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="TISSUS SAINS", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTVs+73mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVH+21mm", "PTVL+21mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSUS SAINS'].UpdateDerivedGeometry(Examination=exam)    
    # Create CERVEAU-PTV and OPT CERVEAU-PTV
    patient.PatientModel.CreateRoi(Name="CERVEAU-PTV", Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['CERVEAU-PTV'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="OPT CERVEAU-PTV", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["CERVEAU", "PTVs+21mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTVs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT CERVEAU-PTV'].UpdateDerivedGeometry(Examination=exam)
    # efface PTV+xxmm
    patient.PatientModel.RegionsOfInterest['PTVH+3mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVH+11mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVH+21mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVL+3mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVL+11mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVL+21mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVs+21mm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTVs+73mm'].DeleteRoi()
    
    
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)    
    
    
def crane_stereo_add_plan_and_beamset(plan_data):    
    
    # Add Treatment plan
    plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy="", Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    #plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy="", Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=plan_data['beamset_name'], ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment=plan_data['treatment_technique'])
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv'].Name, DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)

    
def crane_stereo_add_beams(plan_data):
    
    beamset = plan_data['patient'].TreatmentPlans[plan_data['plan_name']].BeamSets[plan_data['beamset_name']]
    
    if plan_data['treatment_technique'] == 'VMAT':
        beams.add_beams_brain_stereo(beamset=beamset, site_name=plan_data['site_name'])
    elif plan_data['treatment_technique'] == 'SMLC':
        beams.add_beams_brain_static(beamset=beamset, site_name=plan_data['site_name'], iso_name='ISO', exam=plan_data['exam'], nb_beams=9)

        
def crane_stereo_opt_settings(plan_data):

    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]
    
    # Set optimization parameters and VMAT conversion parameters
    if plan_data['treatment_technique'] == 'VMAT':
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)
    elif plan_data['treatment_technique'] == 'SMLC':
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40

 
def crane_stereo_rename_ptv(plan_data):
 
    patient = plan_data['patient']
    
    # Rename PTV with standard formatting
    plan_data['ptv'].Name = "PTV " + plan_data['site_name'] + " " + str(plan_data['rx_dose']/100) + "Gy"
    plan_data['ptv'].Name = plan_data['ptv'].Name.replace('.0Gy','Gy')

    ''' a remettre quand v3 du launcher operationnelle
    if plan_data['ptv_low'] != None:
        plan_data['ptv_low'].Name = "PTV " + plan_data['site_name'] + " " + str(plan_data['rx_dose_low']/100) + "Gy"
        plan_data['ptv_low'].Name = plan_data['ptv_low'].Name.replace('.0Gy','Gy')
        patient.PatientModel.RegionsOfInterest['Mod_ptvL'].Name = "ModPTV " + str(plan_data['rx_dose_low']/100) + "Gy"
        patient.PatientModel.RegionsOfInterest['RING_PTVH_1_3mm'].Name = "RING_PTV" + str(plan_data['rx_dose']/100) + "_1_3mm"
        patient.PatientModel.RegionsOfInterest['RING_PTVH_2_8mm'].Name = "RING_PTV" + str(plan_data['rx_dose']/100) + "_2_8mm"
        patient.PatientModel.RegionsOfInterest['RING_PTVH_3_1cm'].Name = "RING_PTV" + str(plan_data['rx_dose']/100) + "_3_1cm"
        patient.PatientModel.RegionsOfInterest['RING_PTVL_1_3mm'].Name = "RING_PTV" + str(plan_data['rx_dose_low']/100) + "_1_3mm"
        patient.PatientModel.RegionsOfInterest['RING_PTVL_2_8mm'].Name = "RING_PTV" + str(plan_data['rx_dose_low']/100) + "_2_8mm"
        patient.PatientModel.RegionsOfInterest['RING_PTVL_3_1cm'].Name = "RING_PTV" + str(plan_data['rx_dose_low']/100) + "_3_1cm"
    '''
   
   
def crane_stereo_create_isodose_lines(plan_data):

    patient = plan_data['patient']
    rx_dose = plan_data['rx_dose']

    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=(300.0/rx_dose)*100, r=255, g=255, b=128, alpha=128)
    eval.add_isodose_line_rgb(dose=(500.0/rx_dose)*100, r=0, g=128, b=0, alpha=128)
    eval.add_isodose_line_rgb(dose=(1000.0/rx_dose)*100, r=0, g=0, b=160, alpha=255)
    eval.add_isodose_line_rgb(dose=(1200.0/rx_dose)*100, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
