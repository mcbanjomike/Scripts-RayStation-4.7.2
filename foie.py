# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification des foies stéréotaxiques.

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


def plan_foie_sbrt(nb_fx = 1, machine = 'BeamMod', isodose_creation = True):
    """
    Voir :py:mod:`plan_poumoun_sbrt`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    #Create ISO
    if not poi.poi_exists("ISO"):
        if poi.poi_exists("REF SCAN"):
            REF_SCAN_coords = poi.get_poi_coordinates('REF SCAN',examination)
            poi.create_poi(REF_SCAN_coords,'ISO','Blue','Isocenter',examination)    
    
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

    # Create BodyRS+Table, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table()

    # Determine PTV name, prescription dose and number of fractions
    # Format: PTVx:y where x is the dose in Gy and y is the number of fractions (eg: PTV37.5:3 or PTV50:5)
    # nb_fx copies last character in string, then :y is stripped from PTV name so that the prescription dose can be determined
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            try:
                presc_dose = float(name[3:])
            except:
                continue
            ptv = patient.PatientModel.RegionsOfInterest[name]
            break
            
    # Rename PTV to standard format (eg, PTV A1 37.5Gy)
    ptv.Name = 'PTV A1 ' + str(presc_dose) + 'Gy'
    ptv.Name = ptv.Name.replace('.0Gy','Gy')

    # Generate optimization contours
    # Create PTV+2mm, PTV+5mm, PTV+20mm and PTV+40mm
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Magenta", margeptv=0.2)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Yellow", margeptv=0.5)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Orange", margeptv=2)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Green", margeptv=4)
    # Create RINGs
    patient.PatientModel.CreateRoi(Name="Ring_1_0mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_1_0mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+0.2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_1_0mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="Ring_2_2mm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_2_2mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+0.2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_2_2mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="Ring_3_5mm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_3_5mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_3_5mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="Ring_4_20mm", Color="Tomato", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_4_20mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+4cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_4_20mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create TS contours
    patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="TISSU SAIN A 4cm", Color="Purple", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 4cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+4cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 4cm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create PEAU
    patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
    patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create FOIE EXPI-GTV
    patient.PatientModel.CreateRoi(Name="FOIE EXPI-GTV", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['FOIE EXPI-GTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["FOIE EXPI"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["GTV"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['FOIE EXPI-GTV'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create OPT FOIE EXPI
    patient.PatientModel.CreateRoi(Name="OPT FOIE EXPI", Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT FOIE EXPI'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["FOIE EXPI"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT FOIE EXPI'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create PTV-GTV
    patient.PatientModel.CreateRoi(Name="PTV-GTV", Color="128, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV-GTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["GTV"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['PTV-GTV'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create prv5mmMOELLE
    if roi.roi_exists("MOELLE"):
        patient.PatientModel.CreateRoi(Name="prv5mmMOELLE", Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['prv5mmMOELLE'].SetWallExpression(SourceRoiName="MOELLE", OutwardDistance=0.5, InwardDistance=0)
        patient.PatientModel.RegionsOfInterest['prv5mmMOELLE'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Create REINS
    if roi.roi_exists("REIN DRT"):
        if roi.roi_exists("REIN GCHE"):
            patient.PatientModel.CreateRoi(Name="REINS", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['REINS'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["REIN DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["REIN GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['REINS'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Erase expanded PTV contours
    patient.PatientModel.RegionsOfInterest['PTV+0.2cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+0.5cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+2cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+4cm'].DeleteRoi()

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="Stereo Foie", PlannedBy="", Comment="", ExaminationName="CT 1", AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset (assumes 5 fractions)
    beamset = plan.AddNewBeamSet(Name="Stereo", ExaminationName=lib.get_current_examination().Name, MachineName=machine, NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=True, Comment="VMAT")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=presc_dose * 100, RelativePrescriptionLevel=1)

    # plan and beamset are created but not currently selected in RS
    # therefore we must retain the objects in variables and pass them on
    # to the following functions, which otherwise would assume that
    # these are currently selected by the user in RS.
    # VTL

    # Add arcs - borrowed from prostate
    beams.add_beams_prostate_A1(beamset=beamset)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    # Set VMAT conversion parameters
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)

    # Add clinical goals and optimization objectives
    clinical_goals.smart_cg_foie_sbrt(plan=plan, ptv=ptv, Rx_dose=presc_dose)

    # Set Dose Color Table
    if isodose_creation:
        eval.remove_all_isodose_lines()
        patient.CaseSettings.DoseColorMap.ReferenceValue = presc_dose * 100
        fivegy = 5 / presc_dose * 100
        tengy = 10 / presc_dose * 100

        patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
        eval.add_isodose_line_rgb(dose=tengy, r=0, g=0, b=160, alpha=128)
        eval.add_isodose_line_rgb(dose=50, r=128, g=0, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=80, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
        patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if not points.Name in ["ISO", "ISOCENTRE", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()


def finaliser_plan_foie_sbrt():
    """
    #Voir :py:mod:`finaliser_plan_foie_stereo`.
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    plan = lib.get_current_plan() 
    
    # Rename OAR contours for SuperBridge transfer        
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["GTV EXPI", "FOIE INSPI", "FOIE EXPI", "MOELLE", "REINS", "OESOPHAGE", "ESTOMAC", "DUODENUM", "COLON", "GRELE"]:
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
   
    
def calculer_NTCP_foie(rx_dose=None, nb_fx=None):
    #Code to calculate differential DVH
    #Taken from RayStation 4.5 Scripting Guideline
    #Note that all dose values are converted from cGy to Gy to be consistent with Excel spreadsheet
    import math
    
    plan = lib.get_current_plan()
    patient = lib.get_current_patient()
    examination = lib.get_current_examination() 
    beamset = lib.get_current_beamset()
    
    #Get demographic information
    patient_ID = patient.PatientID
    patient_name = patient.PatientName.replace("^", " ")
    #Get plan information
    if rx_dose is None:
        rx_dose = float(beamset.Prescription.PrimaryDosePrescription.DoseValue)/100.0
    if nb_fx is None:
        nb_fx = float(beamset.FractionationPattern.NumberOfFractions)
    volume=roi.get_roi_volume("FOIE EXPI-GTV", exam=examination)
    
    #Set bin size (Gy)
    bin_size = 0.01 #keep as float
    file_path = r'\\radonc.hmr\Departements\Dosimétristes\STEREO FOIE\Calculs NTCP'
    structure_set = plan.GetStructureSet()

    #Make sure all ROI voxel volumes are computed
    plan.ComputeRoiVoxelVolumes()
    #Get plan dose
    plan_dose = [d/100.0 for d in plan.TreatmentCourse.TotalDose.DoseValues.DoseData]
    plan_max_dose = math.ceil(max(plan_dose)*100)/100.0
    #Compute differential DVH
    #Get dose grid ROI representation
    dgr = plan.TreatmentCourse.TotalDose.GetDoseGridRoi(RoiName="FOIE EXPI-GTV")
    roi_dose = [plan_dose[vi] for vi in dgr.RoiVolumeDistribution.VoxelIndices]
    roi_max_dose = math.ceil(max(roi_dose)*100)/100.0
    #Set number of bins
    num_of_bins = int(math.ceil(max(roi_dose)/bin_size))
    
    #Build and populate the differential DVH
    differential_dvh = [0.0] * num_of_bins
    relative_volumes = dgr.RoiVolumeDistribution.RelativeVolumes
    for i,rd in enumerate(roi_dose):
        bin_number = int(rd / bin_size) #bin number is floor value of int division
        differential_dvh[bin_number] += relative_volumes[i] #I am pretty sure this points to the same voxel as the dose being evaluated. Pretty sure.
  
    #Write to file where filename is 'file+path\' + ROI name + '.txt'
    with open(file_path + '\\Calcul NTCP ' + patient_name + ' ' + patient_ID + ".txt",'w') as dvh_file:
        dvh_file.write('Patient:                    ' + patient_name + '\n')
        dvh_file.write('No. HMR:                    ' + patient_ID + '\n')
        dvh_file.write('Dose de prescription:       %.2fGy\n' % rx_dose)
        dvh_file.write('Dose max globale:           %.2fGy\n' % plan_max_dose)
        dvh_file.write('Dose max au FOIE EXPI-GTV:  %.2fGy\n' % roi_max_dose)
        dvh_file.write('Volume du FOIE EXPI-GTV:    %.2fcc\n\n' % volume)

        #Calculate Veff
        sum_max = 0.0
        sum_presc = 0.0
        sum_max_BED = 0.0
        sum_presc_BED = 0.0
        total_volume = 0.0
        n = 0.97 #used for calculation of Veff
        alpha_beta = 2.5 #used for biological dose calculations (in cGy)
        ref_dose_fx = 1.5 #reference dose per fraction, assumed to be 1.5Gy
        max_norm = plan_max_dose * ((1+(plan_max_dose/nb_fx)/alpha_beta)/(1+ref_dose_fx/alpha_beta)) #for Veff biologique
        rx_norm = rx_dose * ((1+(rx_dose/nb_fx)/alpha_beta)/(1+ref_dose_fx/alpha_beta)) #for Veff biologique

        for i,dd in enumerate(differential_dvh):
            #Bin i corresponds to the range of dose i*bin_size to (i+1)*bin_size
            #Assuming 1 cGy bins, bin 57 covers range from 57 to 58 cGy
            diff_volume = dd #New method, since dd is already a fractional volume
            #di = (i*bin_size + (i+1)*bin_size)/2 #finds average dose of each bin
            di = i*bin_size #finds floor dose of each bin
            di_BED = di * (1+(di/nb_fx)/alpha_beta)/(1+(ref_dose_fx/alpha_beta)) #bin dose normalized to 1.5Gy/fx
            sum_max += diff_volume*(di/plan_max_dose)**(1/n) #normaled to max dose in plan
            sum_presc += diff_volume*(di/rx_dose)**(1/n) #normalized to prescription dose
            sum_max_BED += diff_volume*(di_BED/max_norm)**(1/n) #using max dose normalized to 1.5Gy/fx
            sum_presc_BED += diff_volume*(di_BED/rx_norm)**(1/n) #using prescription normalized to 1.5Gy/fx
            total_volume += diff_volume
            
        #Calculate NTCP
        TD50_1 = 45.8
        m = 0.12
        t = (rx_norm - TD50_1*sum_presc_BED**(-n))/(m*TD50_1*sum_presc_BED**(-n))
        
        #Code taken from http://www.codeproject.com/Articles/34030/Computing-Normal-Probabilities-in-IronPython
        def phi(x):
            # constants
            a1 =  0.254829592
            a2 = -0.284496736
            a3 =  1.421413741
            a4 = -1.453152027
            a5 =  1.061405429
            p  =  0.3275911

            # Save the sign of x
            sign = 1
            if x < 0:
                sign = -1
            x = abs(x)/math.sqrt(2.0)

            # A&S formula 7.1.26
            t = 1.0/(1.0 + p*x)
            y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*math.exp(-x*x)

            return 0.5*(1.0 + sign*y)
        
        NTCP = phi(t)

        """
        #Fractional results, no longer shown
        #Write results to file
        dvh_file.write('\nVolume check (should be 1): %.4f\n' % total_volume)
        dvh_file.write('Dose max normalized to 1.5Gy/fx: %.2fGy\n' % max_norm)
        dvh_file.write('Dose Rx normalized to 1.5Gy/fx : %.2fGy\n' % rx_norm)
        dvh_file.write('t (debug - used for NTCP calc) : %.6f\n\n' % t)
        
        dvh_file.write('Veff normalized to global Dmax: %.4f\n' % sum_max)
        dvh_file.write('Veff normalized to Presc: %.4f\n' % sum_presc)
        dvh_file.write('Veff Biologique normalized to global Dmax: %.4f\n\n' % sum_max_BED)
        
        dvh_file.write('RESULTS:\n')
        dvh_file.write('Veff Biologique normalized to Presc: %.4f\n' % sum_presc_BED)
        dvh_file.write('NTCP (NON-VALIDÉ): %.4f\n\n\n' % NTCP)
        """
       
        #Convert Veff and NTCP from fractions to percent values
        sum_max *= 100.0
        sum_presc *= 100.0
        sum_max_BED *= 100.0
        sum_presc_BED *= 100.0
        NTCP *= 100.0
        
        #dvh_file.write('\nVolume check (should be 1): %.4f\n' % total_volume)
        dvh_file.write('Dose max normalized to 1.5Gy/fx: %.2fGy\n' % max_norm)
        dvh_file.write('Dose Rx normalized to 1.5Gy/fx : %.2fGy\n' % rx_norm)
        #dvh_file.write('t (debug - used for NTCP calc) : %.6f\n\n' % t)
        
        dvh_file.write('Veff normalized to global Dmax(pourcent): %.2f\n' % sum_max)
        dvh_file.write('Veff normalized to Presc (pourcent): %.2f\n' % sum_presc)
        dvh_file.write('Veff Biologique normalized to global Dmax (pourcent): %.2f\n\n' % sum_max_BED)
        
        dvh_file.write('RESULTS:\n')
        dvh_file.write('Veff Biologique normalized to Presc (pourcent): %.2f\n' % sum_presc_BED)
        dvh_file.write('NTCP (pourcent): %.2f\n\n\n' % NTCP)

        #Write differential DVH to file
        dvh_file.write('Dose (Gy)     Fractional volume         Normalized dose (Gy)   Fractional volume\n')        
        for i,dd in enumerate(differential_dvh):
            #Bin i corresponds to the range of dose i*bin_size to (i+1)*bin_size
            #Assuming 0.01 Gy bins, bin 57 covers range from 0.57 to 0.58 cGy
            diff_dose = i*bin_size #Gives floor dose for bin i
            di_BED = diff_dose * (1+(diff_dose/nb_fx)/alpha_beta)/(1+(ref_dose_fx/alpha_beta))
            diff_volume = dd
            dvh_file.write('%6.2f          %1.10f            %10.2f               %1.10f\n' % (diff_dose, dd, di_BED, dd))


            
                
            

def foie_stereo_rois(plan_data):

    ptv = plan_data['ptv']
    exam = plan_data['exam']
    patient = plan_data['patient']
            
    # Rename PTV to standard format (eg, PTV A1 37.5Gy)
    ptv.Name = 'PTV ' + plan_data['site_name'] + ' ' +  str(float(plan_data['rx_dose'])/100.0) + 'Gy'
    ptv.Name = ptv.Name.replace('.0Gy','Gy')

    # Generate optimization contours
    # Create PTV+2mm, PTV+5mm, PTV+20mm and PTV+40mm
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Magenta", margeptv=0.2)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Yellow", margeptv=0.5)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Orange", margeptv=2)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Green", margeptv=4)
    # Create RINGs
    patient.PatientModel.CreateRoi(Name="Ring_1_0mm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_1_0mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+0.2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_1_0mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="Ring_2_2mm", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_2_2mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+0.2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_2_2mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="Ring_3_5mm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_3_5mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_3_5mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="Ring_4_20mm", Color="Tomato", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_4_20mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS+Table", "PTV+4cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_4_20mm'].UpdateDerivedGeometry(Examination=exam)
    # Create TS contours
    patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="TISSU SAIN A 4cm", Color="Purple", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 4cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+4cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 4cm'].UpdateDerivedGeometry(Examination=exam)
    # Create PEAU
    patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
    patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=exam)
    # Create FOIE EXPI-GTV
    patient.PatientModel.CreateRoi(Name="FOIE EXPI-GTV", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['FOIE EXPI-GTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["FOIE EXPI"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["GTV"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['FOIE EXPI-GTV'].UpdateDerivedGeometry(Examination=exam)
    # Create OPT FOIE EXPI
    patient.PatientModel.CreateRoi(Name="OPT FOIE EXPI", Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT FOIE EXPI'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["FOIE EXPI"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT FOIE EXPI'].UpdateDerivedGeometry(Examination=exam)
    # Create PTV-GTV
    patient.PatientModel.CreateRoi(Name="PTV-GTV", Color="128, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV-GTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["GTV"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['PTV-GTV'].UpdateDerivedGeometry(Examination=exam)
    # Create prv5mmMOELLE
    if roi.roi_exists("MOELLE"):
        patient.PatientModel.CreateRoi(Name="prv5mmMOELLE", Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['prv5mmMOELLE'].SetWallExpression(SourceRoiName="MOELLE", OutwardDistance=0.5, InwardDistance=0)
        patient.PatientModel.RegionsOfInterest['prv5mmMOELLE'].UpdateDerivedGeometry(Examination=exam)
    # Create REINS
    if roi.roi_exists("REIN DRT"):
        if roi.roi_exists("REIN GCHE"):
            patient.PatientModel.CreateRoi(Name="REINS", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['REINS'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["REIN DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["REIN GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['REINS'].UpdateDerivedGeometry(Examination=exam)
    # Erase expanded PTV contours
    patient.PatientModel.RegionsOfInterest['PTV+0.2cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+0.5cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+2cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+4cm'].DeleteRoi()

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

        
        
def foie_stereo_add_plan_and_beamset(plan_data):        
        
    # Add Treatment plan
    plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy="", Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset (assumes 5 fractions)
    beamset = plan.AddNewBeamSet(Name=plan_data['beamset_name'], ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment=plan_data['treatment_technique'])
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv'].Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)

    
def foie_stereo_opt_settings(plan_data):

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])

    # Set conversion parameters
    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]
    
    if plan_data['treatment_technique'] == 'VMAT':
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])
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
    
def foie_stereo_create_isodose_lines(plan_data):

    patient = plan_data['patient']

    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = plan_data['rx_dose']
    fivegy = 500 / plan_data['rx_dose'] * 100
    tengy = 1000 / plan_data['rx_dose'] * 100

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
    eval.add_isodose_line_rgb(dose=tengy, r=0, g=0, b=160, alpha=128)
    eval.add_isodose_line_rgb(dose=50, r=128, g=0, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=80, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
    
    
    

def vertebre_stereo_rois(plan_data):

    ptv = plan_data['ptv']
    exam = plan_data['exam']
    patient = plan_data['patient']

    # Generate optimization contours
    # Create PTV+5mm, PTV+5.5cm and PTV+10.5cm
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Magenta", margeptv=0.5)
    patient.PatientModel.CreateRoi(Name="PTV+5.5cm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+5.5cm'].SetMarginExpression(SourceRoiName="PTV+0.5cm", MarginSettings={'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 5, 'Posterior': 5, 'Right': 5, 'Left': 5})
    patient.PatientModel.RegionsOfInterest['PTV+5.5cm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="PTV+10.5cm", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+10.5cm'].SetMarginExpression(SourceRoiName="PTV+5.5cm", MarginSettings={'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 5, 'Posterior': 5, 'Right': 5, 'Left': 5})
    patient.PatientModel.RegionsOfInterest['PTV+10.5cm'].UpdateDerivedGeometry(Examination=exam)
    # Create Ring and TS contours
    patient.PatientModel.CreateRoi(Name="Ring_5mm", Color="Khaki", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['Ring_5mm'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['Ring_5mm'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="TS1", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TS1'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+5.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+0.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TS1'].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="TS2", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TS2'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "PTV+10.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+5.5cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TS2'].UpdateDerivedGeometry(Examination=exam)
    # Create Peau
    patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
    patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=exam)
    # Create BODY-PTV
    patient.PatientModel.CreateRoi(Name="BODY-PTV", Color="255, 128, 0", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['BODY-PTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['BODY-PTV'].UpdateDerivedGeometry(Examination=exam)
    
    list_opt = []
    #Contours derived from QUEUE CHEVAL
    if roi.roi_exists("QUEUE CHEVAL"):
        # Create prv1mmQUEUE
        patient.PatientModel.CreateRoi(Name="prv1mmQUEUE", Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['prv1mmQUEUE'].SetWallExpression(SourceRoiName="QUEUE CHEVAL", OutwardDistance=0.1, InwardDistance=0)
        patient.PatientModel.RegionsOfInterest['prv1mmQUEUE'].UpdateDerivedGeometry(Examination=exam)
        list_opt.append("QUEUE CHEVAL")
        list_opt.append("prv1mmQUEUE")
    #Contours derived from MOELLE
    if roi.roi_exists("MOELLE"):
        # Create prv2mmMOELLE
        patient.PatientModel.CreateRoi(Name="prv2mmMOELLE", Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['prv2mmMOELLE'].SetWallExpression(SourceRoiName="MOELLE", OutwardDistance=0.2, InwardDistance=0)
        patient.PatientModel.RegionsOfInterest['prv2mmMOELLE'].UpdateDerivedGeometry(Examination=exam)
        # Create MOELLE PARTIELLE
        patient.PatientModel.CreateRoi(Name="MOELLE PARTIELLE", Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['MOELLE PARTIELLE'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 3, 'Posterior': 3, 'Right': 3, 'Left': 3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["MOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['MOELLE PARTIELLE'].UpdateDerivedGeometry(Examination=exam)
        list_opt.append("MOELLE")
        list_opt.append("prv2mmMOELLE")    
    if len(list_opt)==2:
        # Create OPT PTV
        patient.PatientModel.CreateRoi(Name="OPTPTV", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['OPTPTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [list_opt[0],list_opt[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['OPTPTV'].UpdateDerivedGeometry(Examination=exam)
    elif len(list_opt)==4:
        # Create OPT PTV
        patient.PatientModel.CreateRoi(Name="OPTPTV", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['OPTPTV'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [list_opt[0],list_opt[1],list_opt[2],list_opt[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['OPTPTV'].UpdateDerivedGeometry(Examination=exam)
    # Create REINS
    if roi.roi_exists("REIN DRT"):
        if roi.roi_exists("REIN GCHE"):
            patient.PatientModel.CreateRoi(Name="REINS", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['REINS'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["REIN DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["REIN GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['REINS'].UpdateDerivedGeometry(Examination=exam)
    # Create COMBI PMNS
    if roi.roi_exists("POUMON DRT"):
        if roi.roi_exists("POUMON GCHE"):
            patient.PatientModel.CreateRoi(Name="COMBI PMNS", Color="lightblue", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['COMBI PMNS'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['COMBI PMNS'].UpdateDerivedGeometry(Examination=exam) 

    # Erase expanded PTV contours
    patient.PatientModel.RegionsOfInterest['PTV+0.5cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+5.5cm'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['PTV+10.5cm'].DeleteRoi()
    
    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)


        
        
def vertebre_stereo_opt_settings(plan_data):

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])

    # Set VMAT conversion parameters
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.2, max_arc_delivery_time=350.0, plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])

    
def vertebre_stereo_create_isodose_lines(plan_data):    

    patient = plan_data['patient']

    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = 1800
    fivegy = 5 / 18.0 * 100
    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
    eval.add_isodose_line_rgb(dose=50, r=128, g=0, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=80, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'