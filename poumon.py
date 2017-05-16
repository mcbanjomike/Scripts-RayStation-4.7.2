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

    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    if plan_data['treatment_technique'] == 'VMAT':
        # Set VMAT conversion parameters  
        fx_dose = plan_data['rx_dose'] / plan_data['nb_fx']
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=int(fx_dose/100.0*20), plan=plan)
    elif plan_data['treatment_technique'] == 'SMLC':
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1.6
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 4
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40
    
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


        
        
        
        
        
        
        
      
#Scripts for the new KBP planning technique
def poumon_stereo_kbp_identify_rois(plan_data):
    
    patient = plan_data['patient']
    ptv_name = plan_data['ptv'].Name
    exam = plan_data['exam']
    
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    poumon_d_name = "Not found"
    poumon_g_name = "Not found"
    coeur_name = "Not found"
    bronches_name = "Not found"
    trachee_name = "Not found"
    oesophage_name = "Not found"
    moelle_name = "Not found" 
    prvmoelle_name = "Not found"
    plexus_name = "Not found"
    prvplexus_name = "Not found"
    cotes_name = "Not found"
    body_name = "Not found"
    opt_pmns_name = "Not found"
   
    #Check names for ROIs
    name_list = ['POUMON DRT','POUMON DRT*','POUMON D','POUMON D*']
    for name in name_list:
        if name in roi_names:
            poumon_d_name = name
            break
      
    name_list = ['POUMON GCHE','POUMON GCHE*','POUMON G','POUMON G*']
    for name in name_list:
        if name in roi_names:
            poumon_g_name = name
            break
            
    name_list = ['COEUR','COEUR*']
    for name in name_list:
        if name in roi_names:
            coeur_name = name
            break

    name_list = ['BR SOUCHE','BR SOUCHE*']
    for name in name_list:
        if name in roi_names:
            bronches_name = name
            break            
                        
    name_list = ['TRACHEE','TRACHEE*']
    for name in name_list:
        if name in roi_names:
            trachee_name = name
            break      

    name_list = ['OESOPHAGE','OESOPHAGE*']
    for name in name_list:
        if name in roi_names:
            oesophage_name = name
            break                

    name_list = ['COTES','COTES*']
    for name in name_list:
        if name in roi_names:
            cotes_name = name
            break              
            
    name_list = ['MOELLE','MOELLE*']
    for name in name_list:
        if name in roi_names:
            moelle_name = name
            break    

    name_list = ['PRV MOELLE','PRV MOELLE*','prvMOELLE','prvMOELLE*']
    for name in name_list:
        if name in roi_names:
            prvmoelle_name = name
            break                
            
    name_list = ['PLEXUS BRACHIAL','PLEXUS BRACHIAL*']
    for name in name_list:
        if name in roi_names:
            plexus_name = name
            break    

    name_list = ['PRV PLEXUS','PRV PLEXUS*','prvPLEXUS','prvPLEXUS*']
    for name in name_list:
        if name in roi_names:
            prvplexus_name = name
            break                
                     
    name_list = ['BodyRS','BODY']
    for name in name_list:
        if name in roi_names:
            body_name = name
            break                
            
    name_list = ['COMBI PMN-ITV-BR','COMBI PMN-ITV-BR*']
    for name in name_list:
        if name in roi_names:
            opt_pmns_name = name
            break                
    
    #Determine laterality
    if poumon_d_name == "Not found": #Patient only has left lung
        pmn_ipsi_name = poumon_g_name
        pmn_contra_name = "Not found"
        laterality = 'GCHE'
    elif poumon_g_name == "Not found": #Patient only has right lung
        pmn_ipsi_name = poumon_d_name
        pmn_contra_name = "Not found"
        laterality = 'DRT'    
    else:
        pmn_ipsi_name = roi.find_most_intersecting_roi(ptv_name,[poumon_d_name,poumon_g_name], examination=exam)
        if pmn_ipsi_name == poumon_d_name:
            laterality = 'DRT'
            pmn_contra_name = poumon_g_name
        else:
            laterality = 'GCHE'
            pmn_contra_name = poumon_d_name
          
          
    #Generate list of OAR names for later use
    oar_list = [pmn_ipsi_name,pmn_contra_name,coeur_name,bronches_name,trachee_name,oesophage_name,cotes_name,moelle_name,prvmoelle_name,plexus_name,prvplexus_name,'r50',body_name,opt_pmns_name]
    
    return oar_list,laterality
           
        
def poumon_stereo_kbp_add_plan_and_beamset(plan_data,laterality):
    
    patient = plan_data['patient']
    exam = plan_data['exam']
    
    # Add Treatment plan (unless it already exists)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    
    plan = patient.AddNewPlan(PlanName='Plan Test', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset and beams (unless it/they already exists)
    beamset = plan.AddNewBeamSet(Name=plan_data['site_name']+' test', ExaminationName=exam.Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique=plan_data['treatment_technique'], PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment='VMAT')
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv'].Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)

    #Add beams
    if plan_data['treatment_technique'] == 'SMLC':
        beams.add_beams_imrt_lung_stereo(beamset=beamset,examination=exam, ptv_name=plan_data['ptv'].Name)    
    elif plan_data['treatment_technique'] == 'VMAT':
        if plan_data['rx_dose'] >= 5600:
            two_arcs = True
        else:
            two_arcs = False            
        beams.add_beams_lung_stereo_test(laterality=laterality, beamset=beamset, examination=exam, two_arcs=two_arcs)
                  
            
def poumon_stereo_kbp_opt_settings(plan_data):

    plan = plan_data['patient'].TreatmentPlans['Plan Test']

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    if plan_data['treatment_technique'] == 'VMAT':
        # Set VMAT conversion parameters  
        fx_dose = plan_data['rx_dose'] / plan_data['nb_fx']
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=int(fx_dose/100.0*20), plan=plan)
    elif plan_data['treatment_technique'] == 'SMLC':
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1.6
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 4
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40        
        
        
def poumon_stereo_kbp_initial_plan(plan_data,oar_list):
    patient = plan_data['patient']
    exam = plan_data['exam']
    plan = patient.TreatmentPlans['Plan Test']
    beamset = plan.BeamSets[plan_data['site_name']+' test']
    rx = plan_data['rx_dose']
    
    ptv_name = plan_data['ptv'].Name
    body_name = oar_list[12]
    opt_pmns_name = oar_list[13]    

    #Set PTV contour type
    try:
        roi.set_roi_type(ptv_name, 'Ptv', 'Target')
    except:
        pass    
    
    #Collect ROI info
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()  

    #Estimate dose falloff range
    falloff_range = 1.0 + (ptv_vol - 10) * 0.0125
    if falloff_range < 1:
        falloff_range = 1
    elif falloff_range > 2:
        falloff_range = 2
        
    #Estimate what dose to ask for r50
    r50_max_dose = 40 + (ptv_vol - 8) * 0.1087
    if r50_max_dose < 40:
        r50_max_dose = 40
    elif r50_max_dose > 50:
        r50_max_dose = 50
    r50_max_dose = r50_max_dose / 100.0
    
    if ptv_vol > 40:
        r50_weight = 100
        ptv_weight = 100
    else:
        r50_weight = 25
        ptv_weight = 25      

    #Create COMBI PMN KBP (need to do this now because you can't evaluate dose on a structure that didn't exist during dose calculation)
    pmn_kbp_name = 'OPT PMNS ' + plan_data['site_name']
    roi.create_expanded_roi('r50', color="Yellow", examination=exam, marge_lat=5, marge_sup_inf = 0, output_name='temp KBP1')
    roi.create_expanded_roi('temp KBP1', color="Lightblue", examination=exam, marge_lat=5, marge_sup_inf = 0, output_name='temp KBP2')
    patient.PatientModel.CreateRoi(Name=pmn_kbp_name, Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[pmn_kbp_name].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp KBP2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [opt_pmns_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest[pmn_kbp_name].UpdateDerivedGeometry(Examination=exam)    
    patient.PatientModel.RegionsOfInterest['temp KBP1'].DeleteRoi()
    patient.PatientModel.RegionsOfInterest['temp KBP2'].DeleteRoi()          

    #Initial set of optimization objectives
    optim.add_mindose_objective(ptv_name, rx, weight=ptv_weight, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective(body_name, rx*1.00, rx*0.25, falloff_range, weight=25, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('r50', rx*r50_max_dose, weight=r50_weight, plan=plan, plan_opt=0) 
    optim.add_maxdose_objective('RING_1', rx*1.02, weight=1, plan=plan, plan_opt=0) 

    #Copy clinical goals from old-style plan
    #optim.copy_clinical_goals(old_plan = patient.TreatmentPlans[plan_data['plan_name']],new_plan = plan)
    optim.copy_clinical_goals(old_plan = patient.TreatmentPlans[0],new_plan = plan)
    
    #Run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
       
    
def poumon_stereo_kbp_modify_plan(plan_data,oar_list):    
    patient = plan_data['patient']
    exam = plan_data['exam']
    plan = patient.TreatmentPlans['Plan Test']
    beamset = plan.BeamSets[plan_data['site_name']+' test']
    rx = plan_data['rx_dose']
    nb_fx = plan_data['nb_fx']
    
    ptv_name = plan_data['ptv'].Name
    pmn_contra_name = oar_list[1]
    pmn_kbp_name = 'OPT PMNS ' + plan_data['site_name']  
    
    #Evaluate lung DVH before scaling
    dose_in_pmn_kbp = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=pmn_kbp_name, DoseValues=[2000/nb_fx,1000/nb_fx,500/nb_fx])             
    
    #Scale dose to prescription
    beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=95, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)

    #Evaluate plan
    v5_contra = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=pmn_contra_name, DoseValues=[500/nb_fx])
    oar_max_dose = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]      
    for i,oar in enumerate(oar_list):
        try:
            oar_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[oar].GetRoiVolume() 
            oar_max_dose[i] = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.1/oar_vol])[0] * nb_fx / 100.0
        except:
            oar_max_dose[i] = -999         

    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    
    #Increase weight of PTV min dose objective
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue
        if f_type == "MinDose" and objective.ForRegionOfInterest.Name == ptv_name:    
            objective.DoseFunctionParameters.Weight = 2*objective.DoseFunctionParameters.Weight    

    #Add optimization objectives for OARs
    optim.add_maxdvh_objective(pmn_kbp_name, 2000, round(dose_in_pmn_kbp[0]*80,2), weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective(pmn_kbp_name, 1000, round(dose_in_pmn_kbp[1]*80,2), weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective(pmn_kbp_name, 500,  round(dose_in_pmn_kbp[2]*80,2), weight=5, plan=plan, plan_opt=0) 
    
    if 25*v5_contra[0] > 1:
        optim.add_maxdvh_objective(pmn_contra_name, 500, round(25*v5_contra[0],2), weight=10, plan=plan, plan_opt=0) 
    else:
        optim.add_maxdose_objective(pmn_contra_name, 500, weight=10, plan=plan, plan_opt=0) 

    #We don't want to compromise on the MOELLE and PLEXUS, so they are treated separately
    if nb_fx == 8:
        moelle_tolerance_dose = 2590
        prvmoelle_tolerance_dose = 2910
        plexus_tolerance_dose = 3550
        prvplexus_tolerance_dose = 4030
    elif nb_fx == 5:
        moelle_tolerance_dose = 2620
        prvmoelle_tolerance_dose = 2930
        plexus_tolerance_dose = 2960
        prvplexus_tolerance_dose = 3340
    elif nb_fx == 3:
        moelle_tolerance_dose = 1800
        prvmoelle_tolerance_dose = 2000
        plexus_tolerance_dose = 2400
        prvplexus_tolerance_dose = 2700
    elif nb_fx == 4:
        moelle_tolerance_dose = 2020
        prvmoelle_tolerance_dose = 2240
        plexus_tolerance_dose = 2700
        prvplexus_tolerance_dose = 3050
    elif nb_fx == 15:
        moelle_tolerance_dose = 3000     
        prvmoelle_tolerance_dose = 3300 #I just made this number up
        plexus_tolerance_dose = 3800 #I just made this number up
        prvplexus_tolerance_dose = 4100 #I just made this number up

    #REMINDER: oar_list = [pmn_ipsi_name,pmn_contra_name,coeur_name,bronches_name,trachee_name,oesophage_name,cotes_name,moelle_name,prvmoelle_name,plexus_name,prvplexus_name,'r50',body_name,opt_pmns_name]        
    if moelle_tolerance_dose-200 < 100*oar_max_dose[7]: #If obtained dose is higher than tolerance-2Gy, use tolerance value-2Gy instead of obtained dose value
        optim.add_maxdose_objective(oar_list[7], moelle_tolerance_dose-200, weight=500, plan=plan, plan_opt=0) 
    else:
        if 80*oar_max_dose[7] > 1000:
            optim.add_maxdose_objective(oar_list[7], 80*oar_max_dose[7], weight=1, plan=plan, plan_opt=0) 
        elif 100*oar_max_dose[7] > 500:
            optim.add_maxdose_objective(oar_list[7], 100*oar_max_dose[7], weight=1, plan=plan, plan_opt=0) 
    
    if prvmoelle_tolerance_dose-200 < 100*oar_max_dose[8]: #If 80% of obtained dose is higher than tolerance, use tolerance value instead of obtained dose value
        optim.add_maxdose_objective(oar_list[8], prvmoelle_tolerance_dose-200, weight=500, plan=plan, plan_opt=0) 
    else:
        if 80*oar_max_dose[8] > 1000:
            optim.add_maxdose_objective(oar_list[8], 80*oar_max_dose[8], weight=1, plan=plan, plan_opt=0) 
        elif 100*oar_max_dose[8] > 500:
            optim.add_maxdose_objective(oar_list[8], 100*oar_max_dose[8], weight=1, plan=plan, plan_opt=0)             
            
    if plexus_tolerance_dose-200 < 100*oar_max_dose[9]: #If 80% of obtained dose is higher than tolerance, use tolerance value instead of obtained dose value
        optim.add_maxdose_objective(oar_list[9], plexus_tolerance_dose-200, weight=500, plan=plan, plan_opt=0) 
    else:
        if 80*oar_max_dose[9] > 1000:
            optim.add_maxdose_objective(oar_list[9], 80*oar_max_dose[9], weight=1, plan=plan, plan_opt=0) 
        elif 100*oar_max_dose[9] > 500:
            optim.add_maxdose_objective(oar_list[9], 100*oar_max_dose[9], weight=1, plan=plan, plan_opt=0) 
    
    if prvplexus_tolerance_dose-200 < 100*oar_max_dose[10]: #If 80% of obtained dose is higher than tolerance, use tolerance value instead of obtained dose value
        optim.add_maxdose_objective(oar_list[10], prvplexus_tolerance_dose-200, weight=500, plan=plan, plan_opt=0) 
    else:
        if 80*oar_max_dose[10] > 1000:
            optim.add_maxdose_objective(oar_list[10], 80*oar_max_dose[10], weight=1, plan=plan, plan_opt=0) 
        elif 100*oar_max_dose[10] > 500:
            optim.add_maxdose_objective(oar_list[10], 100*oar_max_dose[10], weight=1, plan=plan, plan_opt=0)              
    
    for i,oar in enumerate(oar_list):
        if i in [2,3,4,5,6]: #Apply to coeur, bronches, trachee, oesophage and cotes
            try: #Use a try here in case OAR is missing (which causes a crash when finding intersecting volume)
                volume_intersect = roi.get_intersecting_volume('PTV+3mm', oar, examination=exam)
                if volume_intersect == 0: #OAR far from PTV
                    if 80*oar_max_dose[i] > 1000: #Don't reduce dose value if below 10Gy
                        optim.add_maxdose_objective(oar, 80*oar_max_dose[i], weight=1, plan=plan, plan_opt=0) 
                    elif 100*oar_max_dose[i] > 500:
                        optim.add_maxdose_objective(oar, 100*oar_max_dose[i], weight=1, plan=plan, plan_opt=0)
                else: #OAR close to or inside PTV
                    newvol = roi.intersect_roi_ptv(oar, 'PTV+3mm', color="Blue", examination=exam, margeptv=0, output_name="PTV "+plan_data['site_name']+' test')
                    if 100*oar_max_dose[i] > rx:
                        optim.add_maxdose_objective(newvol.Name, rx, weight=25, plan=plan, plan_opt=0) 
                    else:
                        optim.add_maxdose_objective(newvol.Name, 90*oar_max_dose[i], weight=25, plan=plan, plan_opt=0) 
            except:
                pass        
      
         
def poumon_stereo_kbp_iterate_plan(plan_data,oar_list):
    patient = plan_data['patient']
    plan = patient.TreatmentPlans['Plan Test']
    beamset = plan.BeamSets[plan_data['site_name']+' test']
    rx = plan_data['rx_dose']
    nb_fx = plan_data['nb_fx']
    
    ptv_name = plan_data['ptv'].Name
    
    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(4):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling        
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])   
        init_ptv_cov = ptv_coverage
            
        #Modify weight of PTV min dose objective
        new_weight = 1
        if ptv_coverage[0] < 0.8:
            new_weight = 8
        elif ptv_coverage[0] < 0.90:
            new_weight = 4            
        elif ptv_coverage[0] < 0.93:
            new_weight = 2
        elif ptv_coverage[0] > 0.97:
            new_weight = 0.5        

        if new_weight == 1 or j == 3:
            #Scale dose to prescription and end script
            beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=95, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)  
            break
        elif j<3:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name == ptv_name:    
                    objective.DoseFunctionParameters.Weight = new_weight*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=init_ptv_cov[0]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)         
   
         
def poumon_stereo_kbp_evaluate_plan(plan_data,oar_list):
    patient = plan_data['patient']
    exam = plan_data['exam']
    plan = patient.TreatmentPlans['Plan Test']
    beamset = plan.BeamSets[plan_data['site_name']+' test']
    rx = plan_data['rx_dose']
    nb_fx = plan_data['nb_fx']    
    
    ptv_name = plan_data['ptv'].Name
    pmn_contra_name = oar_list[1]
    body_name = oar_list[12]
    opt_pmns_name = oar_list[13]  

    #Evaluate plan
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()  
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume() 
    opt_pmns_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[opt_pmns_name].GetRoiVolume() 
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx])        
    dose_in_opt_pmns = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=opt_pmns_name, DoseValues=[2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])        
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_name,RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    v5_contra = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=pmn_contra_name, DoseValues=[500/nb_fx])
    oar_max_dose = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]      
    for i,oar in enumerate(oar_list):
        try:
            oar_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[oar].GetRoiVolume() 
            oar_max_dose[i] = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.1/oar_vol])[0] * nb_fx / 100.0
        except:
            oar_max_dose[i] = -999         
    total_mu = 0
    num_beams = 0
    for beam in beamset.Beams:
        num_beams += 1
        total_mu += beam.BeamMU       
    
    #Add results to result_text
    result_text = 'Secret KBP 2x min dose,'
    
    for i,dose in enumerate(dose_in_body):
        result_text += "%.3f," % (dose_in_body[i]*body_vol)
    for i,dose in enumerate(dose_in_opt_pmns):
        result_text += "%.3f," % (dose_in_opt_pmns[i]*opt_pmns_vol)
    
    #REMINDER: oar_list = [pmn_ipsi_name,pmn_contra_name,coeur_name,bronches_name,trachee_name,oesophage_name,cotes_name,moelle_name,prvmoelle_name,plexus_name,prvplexus_name,'r50',body_name,opt_pmns_name]
    result_text += "%.3f," % (v5_contra[0]*100)
    result_text += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_max_dose[1],oar_max_dose[2],oar_max_dose[3],oar_max_dose[4],oar_max_dose[5],oar_max_dose[7],oar_max_dose[8],oar_max_dose[9],oar_max_dose[10],oar_max_dose[6],oar_max_dose[11])
    result_text += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%d," % (max_in_ptv,ptv_coverage[0]*100,ptv_coverage[1]*100,-999,-999,(dose_in_body[0]*body_vol)/ptv_vol,rx/100.0)        
    result_text += "%d,%.3f\n" % (num_beams,total_mu)         

    #Prepare header
    header = "Essai,Body V100 cc,Body V90 cc,Body V80 cc,Body V70 cc,"
    header += "PMN-ITV-BR V20Gy(cc),PMN-ITV-BR V15Gy(cc),PMN-ITV-BR V10Gy(cc),PMN-ITV-BR V5Gy(cc),V5Gy dans Pmn contra(%),"
    header += "D0.1cc PMN contra(Gy),D0.1cc Coeur(Gy),D0.1cc Bronches(Gy),D0.1cc Trachée(Gy),D0.1cc Oesophage(Gy),D0.1cc Moelle(Gy),D0.1cc PRV Moelle(Gy),D0.1cc Plexus(Gy),D0.1cc PRV Plexus(Gy),D0.1cc Côtes(Gy),D0.1cc à 2cm(Gy),"
    header += "Max in PTV(Gy),Couverture par 100%,Couverture par 95%,Couverture 100% avant scaling,Couverture 95% avant scaling,Indice de conformité,Prescription(Gy),"
    header += "Nb de faisceau,UM totaux\n"
    
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_poumon_secret_kbp.txt'
    with open(output_file_path, 'a') as output_file:
        output_file.write(header)      
        output_file.write(result_text)
                        
     
         
         
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

        