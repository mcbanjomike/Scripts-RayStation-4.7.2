# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification en VMAT des
poumons.

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

#Main block of scripts for stereo IMRT/VMAT lung cases        
def poumon_stereo_pois(plan_data):

    patient = plan_data['patient']

    # Copy CT-to-Density table to average scan from expi scan
    if plan_data['site_name'] == 'A1':
        try:
            patient.Examinations['CT 1'].EquipmentInfo.SetImagingSystemReference(ImagingSystemName=patient.Examinations['CT 2'].EquipmentInfo.ImagingSystemReference.ImagingSystemName)
        except: #For rare cases where there is only one scan
            pass
            
    #Create ISO
    poi.create_iso(exam = plan_data['exam'])
    
    # Assign Point Types
    poi.auto_assign_poi_types()
    
    # Erase any points other than ISO or REF SCAN
    if plan_data['site_name'] == "A1":
        poi.erase_pois_not_in_list(poi_list=['ISO','REF SCAN','ISO B1'])  

    
def poumon_stereo_rois(plan_data):    

    patient = plan_data['patient']
    exam = plan_data['exam']
    site_name = plan_data['site_name']
    
    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)

    if site_name == 'A1':
        roi.auto_assign_roi_types_v2()

    # Create BodyRS+Table (except for additional plans)
    if site_name == "A1":
        try:
            roi.generate_BodyRS_plus_Table(struct=1) #CT 1 (avg) is the second on the list and therefore has a structure set index of 1
        except:
            roi.generate_BodyRS_plus_Table(struct=0) #For rare cases where there's only one scan
        
    # Rename contours if this is plan B1 (unless they are approved)
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    if site_name == 'B1':
        roi_list = ['PTV48','PTV54','PTV60','ITV48','ITV54','ITV60']
        for name in roi_names:
            if name in roi_list:
                if 'PTV' in name:
                    if not roi.get_roi_approval(name, exam):
                        patient.PatientModel.RegionsOfInterest[name].Name = 'PTV A1 ' + name[-2:] + 'Gy'
                elif 'ITV' in name:
                    if not roi.get_roi_approval(name, exam):                
                        patient.PatientModel.RegionsOfInterest[name].Name = 'ITV A1 ' + name[-2:] + 'Gy'
                    
        # Rename optimization contours from A1 to avoid errors and confusion in plan B1
        roi_list = ['PTV+3mm','PTV+1.3cm','PTV+2cm','RING_1','RING_2','RING_3','r50','TISSU SAIN A 2cm','COMBI PMN-ITV-BR','OPT COMBI PMN']
        for name in roi_names:
            if name in roi_list:
                if 'PTV' in name:
                    if not roi.get_roi_approval(name, exam):
                        patient.PatientModel.RegionsOfInterest[name].Name = name.replace('PTV','PTV A1')
                else:
                    if not roi.get_roi_approval(name, exam):
                        patient.PatientModel.RegionsOfInterest[name].Name += " A1"
            elif 'dans PTV' in name:
                if not roi.get_roi_approval(name, exam):
                    patient.PatientModel.RegionsOfInterest[name].Name = name.replace('dans PTV','dans PTV A1')
            elif 'hors PTV' in name:
                if not roi.get_roi_approval(name, exam):
                    patient.PatientModel.RegionsOfInterest[name].Name = name.replace('hors PTV','hors PTV A1')
                    
    # Identify which PTV and ITV to use for creation of optimization contours, then rename them to standard format
    suffix = ' ' + str(plan_data['rx_dose']/100) + 'Gy'
    suffix = suffix.replace('.0Gy','Gy')
    if site_name == 'A1':
        ptv = plan_data['ptv']
        itv = plan_data['itv']
        ptv.Name = 'PTV ' + site_name + suffix
        itv.Name = 'ITV ' + site_name + suffix            
    elif site_name == 'B1':
        #Need to check if PTV/ITV B1 are locked. If so, must make new copies to work on.
        if roi.get_roi_approval("PTV B1", exam):
            ptv = patient.PatientModel.CreateRoi(Name=('PTV ' + site_name + suffix), Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV ' + site_name + suffix].SetMarginExpression(SourceRoiName='PTV B1', MarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['PTV ' + site_name + suffix].UpdateDerivedGeometry(Examination=exam)
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV B1"]
            ptv.Name = 'PTV ' + site_name + suffix            
        if roi.get_roi_approval("ITV B1", exam):
            itv = patient.PatientModel.CreateRoi(Name=('ITV ' + site_name + suffix), Color="Purple", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['ITV ' + site_name + suffix].SetMarginExpression(SourceRoiName='ITV B1', MarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['ITV ' + site_name + suffix].UpdateDerivedGeometry(Examination=exam)
        else:
            itv = patient.PatientModel.RegionsOfInterest["ITV B1"]       
            itv.Name = 'ITV ' + site_name + suffix               
        roi.set_roi_type(ptv.Name, 'Ptv', 'Target')
        roi.set_roi_type(itv.Name, 'TreatedVolume', 'Target')

               
    # Generate optimization contours
    # Create PTV+3mm, PTV+1.3cm and PTV+2cm
    if site_name == 'A1':
        roi_string = 'PTV'
    elif site_name == 'B1':
        roi_string = 'PTV B1'
    patient.PatientModel.CreateRoi(Name=roi_string+"+3mm", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+3mm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest[roi_string+"+3mm"].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name=roi_string+"+1.3cm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+1.3cm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3})
    patient.PatientModel.RegionsOfInterest[roi_string+"+1.3cm"].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name=roi_string+"+2cm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+2cm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2})
    patient.PatientModel.RegionsOfInterest[roi_string+"+2cm"].UpdateDerivedGeometry(Examination=exam)
    # Create RINGs
    if site_name == 'A1':
        roi_string = ''
    elif site_name == 'B1':
        roi_string = ' B1'    
    patient.PatientModel.CreateRoi(Name="RING_1"+roi_string, Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_1'+roi_string].SetWallExpression(SourceRoiName=ptv.Name, OutwardDistance=0.3, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_1'+roi_string].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_2"+roi_string, Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_2'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+3mm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_2'+roi_string].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="RING_3"+roi_string, Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_3'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+1.3cm", OutwardDistance=1.5, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_3'+roi_string].UpdateDerivedGeometry(Examination=exam)
    patient.PatientModel.CreateRoi(Name="r50"+roi_string, Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['r50'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+2cm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['r50'+roi_string].UpdateDerivedGeometry(Examination=exam)
    # Create PEAU
    if site_name == 'A1':
        patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
        patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=exam)
    # Create TISSU SAIN A 2cm and COMBI PMN-ITV-BR
    if site_name == 'A1':
        patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("PTV" + roi_string + "+2cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.CreateRoi(Name="COMBI PMN-ITV-BR", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv.Name, "BR SOUCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].UpdateDerivedGeometry(Examination=exam)
    elif site_name == 'B1':
        #Determine name of PTV and ITV for beamset A1
        for rois in patient.PatientModel.RegionsOfInterest:
            if rois.Name[:6] == "PTV A1":
                ptv_A1_name = rois.Name
                itv_A1_name = "I" + rois.Name[1:]
                break
        patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm A1+B1", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm A1+B1'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name,ptv_A1_name], 'MarginSettings': {'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm A1+B1'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.CreateRoi(Name="COMBI PMN-2ITVs-BR", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['COMBI PMN-2ITVs-BR'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv.Name,itv_A1_name,"BR SOUCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['COMBI PMN-2ITVs-BR'].UpdateDerivedGeometry(Examination=exam)
    #Creat OPT COMBI PMN
    patient.PatientModel.CreateRoi(Name="OPT COMBI PMN"+roi_string, Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'+roi_string].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'+roi_string].UpdateDerivedGeometry(Examination=exam)
    # Rename PAROI if necessary
    if site_name == 'A1':    
        if not roi.roi_exists("PAROI", exam):
            if roi.roi_exists("PAROI D", exam):
                 patient.PatientModel.RegionsOfInterest["PAROI D"].Name = "PAROI"
            elif roi.roi_exists("PAROI DRT", exam):
                 patient.PatientModel.RegionsOfInterest["PAROI DRT"].Name = "PAROI"
            elif roi.roi_exists("PAROI G", exam):
                 patient.PatientModel.RegionsOfInterest["PAROI G"].Name = "PAROI"             
            elif roi.roi_exists("PAROI GCHE", exam):
                 patient.PatientModel.RegionsOfInterest["PAROI GCHE"].Name = "PAROI"             
                        
    # Remove material override from all ROIs
    if site_name == "A1":
        for rois in patient.PatientModel.RegionsOfInterest:
            rois.SetRoiMaterial(Material=None)
    
    return(ptv.Name + ',' + itv.Name)

            
def poumon_stereo_add_plan_and_beamset(plan_data):
                           
    # Add Treatment plan (only for A1)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    if plan_data['site_name'] == "A1":
        plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy=planner_name, Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})
    elif plan_data['site_name'] == "B1": #If the existing plan is locked, create a new plan; otherwise, add beamset to current plan
        plan = lib.get_current_plan()
        try: #If the plan is not approved, then plan.Review doesn't exist and querying it will crash the script
            if plan.Review.ApprovalStatus == "Approved":
                plan = plan_data['patient'].AddNewPlan(PlanName=('B1'), PlannedBy="", Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
                plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})        
        except:
            temp7 = True

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=plan_data['beamset_name'], ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment="VMAT")
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv'].Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)
    
    return plan.Name

    
def poumon_stereo_opt_settings(plan_data):

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])

    # Set VMAT conversion parameters  
    fx_dose = plan_data['rx_dose'] / plan_data['nb_fx']
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=int(fx_dose/100.0*20), plan=plan_data['patient'].TreatmentPlans[plan_data['plan_name']])

    
def poumon_stereo_create_isodose_lines(plan_data):

    # Set Dose Color Table (only for plan A1, might crash RayStation if dose color table already exists)
    if plan_data['site_name'] == 'A1':
        eval.remove_all_isodose_lines()
        plan_data['patient'].CaseSettings.DoseColorMap.ReferenceValue = plan_data['rx_dose']
        fivegy = float(100*500/plan_data['rx_dose'])

        plan_data['patient'].CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
        eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
        eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
        plan_data['patient'].CaseSettings.DoseColorMap.PresentationType = 'Absolute'


        
        
          

#Experimental script for IMRT lung cases in RayStation (not clinical as of Dec 2016)
def plan_poumon():
    """
    Voir :py:mod:`plan_poumon`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    """
    # Rename isocenter
    # 1. If ISOCENTRE (or ISO) exists, check for REF SCAN and do not rename points. Beams will be placed on ISO and REF SCAN will act as localization point.
    # 2. Otherwise, check if ISO SCAN exists. If not, rename ISO PT PRESC or REF SCAN to ISO SCAN, which will act as isocenter and localization point.
    if not poi.poi_exists("ISOCENTRE"):
        if not poi.poi_exists("ISO"):
            if not poi.poi_exists("ISO SCAN"):
                if poi.poi_exists("ISO PT PRESC"):
                    patient.PatientModel.PointsOfInterest["ISO PT PRESC"].Name = "ISO SCAN"
                elif poi.poi_exists("REF SCAN"):
                    patient.PatientModel.PointsOfInterest["REF SCAN"].Name = "ISO SCAN"    
    """
    
    #Create ISO
    if not poi.poi_exists("ISO"):
        if poi.poi_exists("REF SCAN"):
            REF_SCAN_coords = poi.get_poi_coordinates('REF SCAN',examination)
            poi.create_poi(REF_SCAN_coords,'ISO','Blue','Isocenter',examination)    

    # Assign Point Types
    poi.auto_assign_poi_types()

    # Number of fractions should be indicated in the Table ROI (eg: Table:24)
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'TABLE:' in n:
            table_roi = patient.PatientModel.RegionsOfInterest[name]
            nb_fx = float(table_roi.Name[-2:])
            table_roi.Name = table_roi.Name[:-3]

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

    # Determine different PTV levels.
    # If one PTV exists, it is stored in the variable ptv for use in contour generation.
    # If two PTVs are found (66+60 or 55+50) then a union of the two is made and is stored as the variable ptv.
    # The individual PTVs then are stored as ptv1 (high dose) and ptv2 (low dose).
    ptvs = []
    if roi.roi_exists("PTV66"):
        ptvs.append(66)
        ptv1 = patient.PatientModel.RegionsOfInterest["PTV66"]
    if roi.roi_exists("PTV60"):
        ptvs.append(60)
        if roi.roi_exists("PTV66"):
            ptv2 = patient.PatientModel.RegionsOfInterest["PTV60"]
            patient.PatientModel.CreateRoi(Name="PTV66+60", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV66+60'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV66"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV60"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['PTV66+60'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            ptv = patient.PatientModel.RegionsOfInterest["PTV66+60"]
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV60"]
    if roi.roi_exists("PTV55"):
        ptvs.append(55)
        ptv = patient.PatientModel.RegionsOfInterest["PTV55"]
    if roi.roi_exists("PTV50"):
        ptvs.append(50)
        if roi.roi_exists("PTV55"):
            ptv1 = patient.PatientModel.RegionsOfInterest["PTV55"]
            ptv2 = patient.PatientModel.RegionsOfInterest["PTV50"]
            patient.PatientModel.CreateRoi(Name="PTV55+50", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV55+50'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV55"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV50"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['PTV55+50'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            ptv = patient.PatientModel.RegionsOfInterest["PTV55+50"]
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV50"]
    if roi.roi_exists("PTV40.05"):
        ptvs.append(40.05)
        ptv = patient.PatientModel.RegionsOfInterest["PTV40.05"]

    # DEBUG
    # tempname = ""
    # for i,dose in enumerate(ptvs):
    #     tempname += str(ptvs[i])
    # patient.PatientModel.CreateRoi(Name=tempname, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)

    # Generate optimization contours
    # Ring and TS structures are generated following the same rules for one or two PTVs, but in the case of two PTV
    # plans, both PTVs are combined into one ROI and the higher dose level is used for optimization criteria.

    # Separate CTVs from PTVs
    if len(ptvs) == 1:
        patient.PatientModel.CreateRoi(Name=("PTV" + str(ptvs[0]) + "-CTV" + str(ptvs[0])), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("PTV" + str(ptvs[0]) + "-CTV" + str(ptvs[0]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("CTV" + str(ptvs[0]))], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("PTV" + str(ptvs[0]) + "-CTV" + str(ptvs[0]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    elif len(ptvs) == 2:  # Also create mod and OPT PTVs and CTVs, as well as Gradient
        patient.PatientModel.CreateRoi(Name=("modCTV" + str(ptvs[1])), Color="Yellow", Type="Ctv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modCTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["CTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv1.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modCTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("modPTV" + str(ptvs[1])), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv2.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv1.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPTCTV" + str(ptvs[1])), Color="Yellow", Type="Ctv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("OPTCTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["CTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv1.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("OPTCTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPTPTV" + str(ptvs[1])), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("OPTPTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv2.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv1.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("OPTPTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("modPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1])), Color="YellowGreen", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["modPTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["modCTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1])), Color="SteelBlue", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["OPTPTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("modCTV" + str(ptvs[1]))], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1])), Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["modPTV" + str(ptvs[1])], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv1.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])

    # Create Rings and TS (same for one or two PTVs)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="White", margeptv=0.3, output_name=ptv.Name)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Olive", margeptv=0.6, output_name=ptv.Name)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Tomato", margeptv=1.6, output_name=ptv.Name)
    roi.create_expanded_ptv(ptv_name=ptv.Name, color="Green", margeptv=2.6, output_name=ptv.Name)
    patient.PatientModel.CreateRoi(Name=("Ring1_3mm"), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["Ring1_3mm"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(ptv.Name + "+0.6cm"), "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(ptv.Name + "+0.3cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["Ring1_3mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name=("Ring2_6mm"), Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["Ring2_6mm"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(ptv.Name + "+1.6cm"), "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(ptv.Name + "+0.6cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["Ring2_6mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name=("Ring3_16mm"), Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["Ring3_16mm"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(ptv.Name + "+2.6cm"), "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(ptv.Name + "+1.6cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["Ring3_16mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="temp1", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['temp1'].SetMarginExpression(SourceRoiName="Ring3_16mm", MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 4, 'Posterior': 4, 'Right': 4, 'Left': 4})
    patient.PatientModel.RegionsOfInterest['temp1'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name=("TS1_26mm"), Color="Teal", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["TS1_26mm"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "temp1"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(ptv.Name + "+2.6cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["TS1_26mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name="temp2", Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['temp2'].SetMarginExpression(SourceRoiName="TS1_26mm", MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 5, 'Posterior': 5, 'Right': 5, 'Left': 5})
    patient.PatientModel.RegionsOfInterest['temp2'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    patient.PatientModel.CreateRoi(Name=("TS2_66mm"), Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest["TS2_66mm"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["BodyRS", "temp2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(ptv.Name + "+2.6cm"), "TS1_26mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest["TS2_66mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])

    # Set ROI type for all modPTVs, optPTVs and Gradients to PTV/Target
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '')
        if 'modPTV' in n:
            roi.set_roi_type(name, 'Ptv', 'Target')
        if 'modCTV' in n:
            roi.set_roi_type(name, 'Ctv', 'Target')
        elif 'Gradient' in n:
            roi.set_roi_type(name, 'Ptv', 'Target')
        elif 'OPTPTV' in n:
            roi.set_roi_type(name, 'Ptv', 'Target')

    # Create prvMOELLE and presMOELLE
    if roi.roi_exists("MOELLE"):
        patient.PatientModel.CreateRoi(Name=("prv5mmMOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["prv5mmMOELLE"].SetWallExpression(SourceRoiName='MOELLE', OutwardDistance=0.5, InwardDistance=0)
        patient.PatientModel.RegionsOfInterest["prv5mmMOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("presMOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["presMOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["presMOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # PMNS-PTV et COMBI PMNS
    if roi.roi_exists("POUMON DRT"):
        if roi.roi_exists("POUMON GCHE"):
            patient.PatientModel.CreateRoi(Name=("COMBI PMNS"), Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["COMBI PMNS"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["COMBI PMNS"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("PMNS-PTV"), Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["PMNS-PTV"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["COMBI PMNS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["PMNS-PTV"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # BLOC MOELLE
    if roi.roi_exists("prv5mmMOELLE"):
        patient.PatientModel.CreateRoi(Name=("temp3"), Color="SkyBlue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["temp3"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mmMOELLE", "MOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 5, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["temp3"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("BLOC MOELLE"), Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["temp3"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Contract", 'Superior': 0, 'Inferior': 0, 'Anterior': 0.2, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])

    # Erase temporary contours
    list = [ptv.Name + "+2.6cm", ptv.Name + "+1.6cm", ptv.Name + "+0.6cm", ptv.Name + "+0.3cm", "temp1", "temp2", "temp3"]
    for name in list:
        if roi.roi_exists(name):
            patient.PatientModel.RegionsOfInterest[name].DeleteRoi()

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

    # Rename contours that have no geometry CT1 with the prefix "vide_"
    for contour in patient.PatientModel.RegionsOfInterest:
        VolCT1 = roi.get_roi_volume(contour.Name, exam=examination)
        if VolCT1 == 0:
            oldname = contour.Name
            contour.Name = ("vide_%s" % oldname)

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="Poumon", PlannedBy="", Comment="", ExaminationName="CT 1", AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset (several options depending on PTV levels)
    if len(ptvs) == 1:
        beamset = plan.AddNewBeamSet(Name="Trial 1", ExaminationName=lib.get_current_examination().Name, MachineName="Salle 6", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=True, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=98, PrescriptionType="DoseAtVolume", DoseValue=ptvs[0] * 100, RelativePrescriptionLevel=1)
    elif len(ptvs) == 2:
        beamset = plan.AddNewBeamSet(Name="Trial 1", ExaminationName=lib.get_current_examination().Name, MachineName="Salle 6", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=True, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName=ptv1.Name, DoseVolume=98, PrescriptionType="DoseAtVolume", DoseValue=ptvs[0] * 100, RelativePrescriptionLevel=1)

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
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan)

    # Add clinical goals and optimization objectives
    clinical_goals.smart_cg_poumon(plan=plan)

    # Set Dose Color Table
    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = ptvs[0] * 100

    tengy = 10.0 / float(ptvs[0]) * 100
    twentygy = 20.0 / float(ptvs[0]) * 100

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=tengy, r=255, g=128, b=64, alpha=128)
    eval.add_isodose_line_rgb(dose=twentygy, r=0, g=128, b=192, alpha=128)
    eval.add_isodose_line_rgb(dose=75, r=160, g=160, b=0, alpha=255)
    if len(ptvs) == 2:
        eval.add_isodose_line_rgb(dose=float(ptvs[1]) / float(ptvs[0]) * 100, r=0, g=160, b=0, alpha=255)  # Rx dose for low-dose PTV (green)
    #eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=110, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if points.Name.upper() not in ["ISO", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()

    msg += "Le script plan_poumon_sbrt a terminé.\n"
    msg += "Il faut faire Remove holes (on all slices) sur le contour BodyRS+Table avant d'optimiser.\n"

        