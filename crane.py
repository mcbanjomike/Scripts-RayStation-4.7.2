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

#Scripts for 3DC plans    
def plan_crane_3DC(site_name='A1', presc_dose=1500, nb_fx=1, isodose_creation = False, opt_collimator_angles = False):

    #WARNING: This script uses UI scripting. If the user switches focus to another piece of software during 
    #         execution, the UI commands will not be completed. The script will not give the desired results
    #         and may crash.
    
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    
    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Create ISO (if point doesn't already exist)
    poi.create_iso()
                    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    if not roi.roi_exists("BodyRS"): #If BodyRS already exists, then reassigning ROI types will remove its External status
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
    elif roi.roi_exists("PTV24"):
        ptv = patient.PatientModel.RegionsOfInterest["PTV24"]
        presc_dose = 2400        
        
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
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = patient.AddNewPlan(PlanName="3DC", PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
    
    # Create beamset
    beamset = plan.AddNewBeamSet(Name="3DC", ExaminationName=exam.Name, MachineName="BeamMod", NominalEnergy=None, Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="3DC")
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
    clinical_goals.add_dictionary_cg('Crane Stereo', presc_dose/100, nb_fx, plan = plan)            
    
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
    
    
    
 
#Somewhat experimental scripts for optimizing collimator angles in 3DC cases 
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
    

    
    
#Main block of scripts for stereo IMRT/VMAT brain plans    
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
    if not roi.roi_exists("BodyRS"): #If BodyRS already exists, then reassigning ROI types will remove its External status
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
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = plan_data['patient'].AddNewPlan(PlanName=plan_data['plan_name'], PlannedBy=planner_name, Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    
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


    
    
    
    
#Script for adding a plan to an existing patient with locked contours and such
def kbp_test_phase2(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan,clinical_beamset):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Add Treatment plan
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    try:
        plan = patient.TreatmentPlans['Test KBP MA']
    except:
        plan = patient.AddNewPlan(PlanName='Test KBP MA', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    try:
        beamset = plan.BeamSets['Test KBP']
    except:
        beamset = plan.AddNewBeamSet(Name='Test KBP', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique='VMAT', PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='VMAT')
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_names[0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx[0], RelativePrescriptionLevel=1)
        
        #Add beams
        beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name='KBP1')
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)    
        
    """
    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    try:
        patient.Save()
    except Exception, err:
        message.message_window(err)
        exit(0)
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['Test KBP phase2'].Select()      
    """
    
    #Run script to determine predicted volumes for V80/70/60/50 and add optimization rings
    thing1,thing2,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max = statistics.dose_falloff_crane(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=True)
  
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[0]].GetRoiVolume()  
    result_text = ""


    #First plan: Dose falloffs (MBB), two optimizations
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)   
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += '90+30,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
       
    """
    #2. Four optimizations
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False   
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += '90+30x3,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
       

    #3. Six optimizations
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False   
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += '90+30x5,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
       
     
    #4. Eight optimizations
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False   
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += '90+30x7,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
       
     
    #5. Ten optimizations
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False   
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    optim.double_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += '90+30x9,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    """
               

    #Second plan: Dose falloffs + predicted DVHs
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()    

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += 'Falloff + DVHs,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             

    
    #Third plan: Dose falloffs + predicted DVHs (MBB style)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()    

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=200, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.0, rx[0]*0.40, 0.4, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.20, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=1, plan=plan, plan_opt=0)    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += 'Falloff + DVHs,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    
    
    #Fourth plan: Dose falloffs + RING PROX at 80%
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.8, weight=25, plan=plan, plan_opt=0)   
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += 'Falloff + RingProx80,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             

    
    #Fifth plan: Dose falloffs + extra falloff on KBP OPT CERV
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=250, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.98, rx[0]*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.60, rx[0]*0.20, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('KBP OPT CERVEAU', rx[0]*0.98, rx[0]*0.70, 0.2, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    result_text += 'Extra Falloff Cerveau,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             


    
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_phase2.txt'
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV(%),Couverture avant scaling,Max ds PTV(Gy),Indice conformité,Dose de Rx(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,99.0,rx[0]*1.5/100.0,(predicted_vol[0] + ptv_vol)/ptv_vol,rx[0]/100.0)
        #Add clinical plan here, it's going to take some effort
        ptv_coverage = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
        dose_in_brain = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,ptv_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)               
        output_file.write(header)      
        output_file.write(result_text)
    
    """
    #SAVE THE PLAN
    try:
        patient.Save()
    except Exception, err:
        print str(err)
        exit(0)
    """
    
    
#Script for adding testing multiple plans on a patient - CONTAINS OUR BEST TECHNIQUE FOR SINGLE PTV PLANNING
def kbp_test_phase3(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan,clinical_beamset,change_ct=False):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Add Treatment plan (unless it already exists)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    try:
        plan = patient.TreatmentPlans['Test KBP MA']
    except:
        plan = patient.AddNewPlan(PlanName='Test KBP MA', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset and beams (unless it/they already exists)
    try:
        beamset = plan.BeamSets['Test KBP']
    except:
        beamset = plan.AddNewBeamSet(Name='Test KBP', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique='VMAT', PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='VMAT')
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_names[0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx[0], RelativePrescriptionLevel=1)
        
        #Add beams
        beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name='KBP1')
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)


    #Run script to determine predicted volumes for V80/70/60/50 and add optimization rings
    thing1,thing2,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body = statistics.dose_falloff_crane_multi(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=True,fix_brain=True)
  
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[0]].GetRoiVolume()  
    result_text = ""

    """
    #First plan: Dose falloffs (MBB), three optimizations
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)   
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB 0.1,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
     
    #Now reoptimize with leaves at 0.2cm/deg    
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.2,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB 0.2,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
          
    """ 
     
     
     
    #Second plan: Dose falloffs + predicted DVHs
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass   

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    initial_brain_dvh1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='KBP OPT CERVEAU', DoseValues=[rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    #If obtained DVH in brain is lower than prediction, change volume to obtained-1% of ROI volume
    brain80 = min(100*predicted_vol[2]/ring_vol,100*initial_brain_dvh1[0]-1)
    brain70 = min(100*predicted_vol[3]/ring_vol,100*initial_brain_dvh1[1]-1)
    brain60 = min(100*predicted_vol[4]/ring_vol,100*initial_brain_dvh1[2]-1)
    """    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB + DVHs 0.1,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             

    #Now reoptimize with leaves at 0.2cm/deg    
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.2,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    #initial_brain_dvh2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='KBP OPT CERVEAU', DoseValues=[rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB + DVHs 0.2,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    """          
    
    
    
    
    #Third plan: Falloff + DVHs (adjusted for what was obtained in plan 2)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()    

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, brain80, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, brain70, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, brain60, weight=5, plan=plan, plan_opt=0)    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True    
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB + DVHs fit 0.1,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    """
    #Now reoptimize with leaves at 0.2cm/deg    
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.2,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'MBB + DVHs fit 0.2,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
              
        
    
    
    
    
    #Fourth plan: Dose falloffs + extra falloff on KBP OPT CERV
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=250, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.98, rx[0]*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.60, rx[0]*0.20, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('KBP OPT CERVEAU', rx[0]*0.98, rx[0]*0.70, 0.2, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Falloff Cerveau 0.1,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             

    #Now reoptimize with leaves at 0.2cm/deg    
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.2,max_arc_delivery_time=350, plan=plan)
    optim.triple_optimization(plan=plan,beamset=beamset)
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Falloff Cerveau 0.2,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    """          
        
    
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_phase3.txt'
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV(%),Couverture avant scaling,Max ds PTV(Gy),Indice conformité,Dose de Rx(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,99.0,rx[0]*1.5/100.0,(predicted_vol[0] + ptv_vol)/ptv_vol,rx[0]/100.0)
        #Add clinical plan here, it's going to take some effort
        ptv_coverage = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
        dose_in_brain = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_names[0],RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,ptv_coverage[0]*100,max_in_ptv,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)               
        output_file.write(header)      
        output_file.write(result_text)

        
#Script for adding testing multiple plans on a patient with multiple PTVs
def kbp_test_multi(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan,clinical_beamset):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Add Treatment plan (unless it already exists)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    try:
        plan = patient.TreatmentPlans['Test KBP MA']
    except:
        plan = patient.AddNewPlan(PlanName='Test KBP MA', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset and beams (unless it/they already exists)
    try:
        beamset = plan.BeamSets['Test KBP']
    except:
        beamset = plan.AddNewBeamSet(Name='Test KBP', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique='SMLC', PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='IMRT')
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_names[0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx[0], RelativePrescriptionLevel=1)
        
        #Add beams
        #beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name='KBP1')
        beams.add_beams_brain_static(beamset=beamset, site_name='KBP1', iso_name='ISO', exam=exam, nb_beams=9)
        #optim.set_optimization_parameters(plan=plan)
        #optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40    
    

    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    try:
        patient.Save()
    except Exception, err:
        message.message_window(err)
        exit(0)
    ui.MenuItem[3].Button_PlanOptimization.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['Test KBP MA'].Select()   




    

    #Run script to determine predicted volumes for V80/70/60/50 and add optimization rings
    thing1,thing2,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body = statistics.dose_falloff_crane_multi(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=True)
  
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_sum_ptvs_smooth'].GetRoiVolume()  
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume() 
    result_text = ""


    #First plan: Initial conditions
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   

    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    #Get initial coverage before scaling
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    else:
        ptv_coverage2 = [0]
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])
    else:
        ptv_coverage3 = [0]        
        
    #Increase weight of lower PTV(s)
    boost_list = []        
    for i,cov in enumerate(init_ptv_cov):
        if max(init_ptv_cov) - cov > 0.01:
            boost_list.append(ptv_names[i])
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
    if len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)        
        
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
        
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

    #Modify weights and reoptimize
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue
        if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
            objective.DoseFunctionParameters.Weight = 1.5*objective.DoseFunctionParameters.Weight
    
    #plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    #Determine initial PTV coverage
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])
        
    #Determine which PTV is least covered
    for i,cov in enumerate(init_ptv_cov):
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
        init_ptv_cov.append(0)
    elif len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)  
    
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])       
     
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial + boost,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             
     
     
     
     
    







    #Second plan: Initial conditions + predicted DVH
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    #Get initial coverage before scaling
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    else:
        ptv_coverage2 = [0]
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])
    else:
        ptv_coverage3 = [0]        
        
    #Increase weight of lower PTV(s)
    boost_list = []        
    for i,cov in enumerate(init_ptv_cov):
        if max(init_ptv_cov) - cov > 0.01:
            boost_list.append(ptv_names[i])
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
    if len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)       
        
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
        
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial + DVH,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

    #Modify weights and reoptimize
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue
        if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
            objective.DoseFunctionParameters.Weight = 1.5*objective.DoseFunctionParameters.Weight
    
    #plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    #Determine initial PTV coverage
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])
        
    #Determine initial brain DVH (for use in DVH fit plan later on)
    initial_brain_dvh = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='KBP OPT CERVEAU', DoseValues=[rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx])    
    brain80 = min(100*predicted_vol[2]/ring_vol,100*initial_brain_dvh[0]-1)
    brain70 = min(100*predicted_vol[3]/ring_vol,100*initial_brain_dvh[1]-1)
    brain60 = min(100*predicted_vol[4]/ring_vol,100*initial_brain_dvh[2]-1)    
        
    #Determine which PTV is least covered
    for i,cov in enumerate(init_ptv_cov):
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
        init_ptv_cov.append(0)
    elif len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)   
    
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])       
     
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial + DVH + boost,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             
     
    
    
    
    
    
    
    
    
    
    #Third plan: Initial conditions + DVH fit
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, brain80, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, brain70, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, brain60, weight=5, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    #Get initial coverage before scaling
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    else:
        ptv_coverage2 = [0]
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])
    else:
        ptv_coverage3 = [0]        
        
    #Increase weight of lower PTV(s)
    boost_list = []        
    for i,cov in enumerate(init_ptv_cov):
        if max(init_ptv_cov) - cov > 0.01:
            boost_list.append(ptv_names[i])
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
    if len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)     
        
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
        
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial + DVH fit,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

    #Modify weights and reoptimize
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue
        if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
            objective.DoseFunctionParameters.Weight = 1.5*objective.DoseFunctionParameters.Weight
    
    #plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    #Determine initial PTV coverage
    init_ptv_cov = []
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    init_ptv_cov.append(ptv_coverage1[0])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        init_ptv_cov.append(ptv_coverage2[0])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        init_ptv_cov.append(ptv_coverage3[0])        
        
    #Determine which PTV is least covered
    for i,cov in enumerate(init_ptv_cov):
        if cov == min(init_ptv_cov):
            prescribe_to = i
    
    #Pad init_ptv_cov out to three entries for when we print the results to file        
    if len(init_ptv_cov) == 1:
        init_ptv_cov.append(0)
        init_ptv_cov.append(0)
    elif len(init_ptv_cov) == 2:
        init_ptv_cov.append(0)
    
    #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
    if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
        if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)  
    
    #Get coverage after scaling
    ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    if num_ptvs > 1:
        ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
    if num_ptvs > 2:
        ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])       
     
    #Evaluate plan
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    result_text += 'Initial + DVH fit + boost,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             
    

    
    
    
    
    
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_multiplan_v2_fix_scaling.txt'
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV1(%),Couverture PTV2(%),Couverture PTV3(%),Couverture avant scaling PTV1,Couverture avant scaling PTV2,Couverture avant scaling PTV3,Max ds PTV(Gy),Indice conformité,Dose de Rx la plus elevée(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,99.0,99.0,99.0,99.0,99.0,rx[0]*1.5/100.0,predicted_100_body/ptv_vol,max(rx)/100.0)
        #Add clinical plan here, it's going to take some effort
        ptv_coverage1 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])  
        if num_ptvs > 1:
            ptv_coverage2 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])    
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])    
        else:
            ptv_coverage3 = [0]
        dose_in_brain = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body  = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = clinical_beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)               
        output_file.write(header)      
        output_file.write(result_text)
        
        
#Script for adding testing multiple plans on a patient with multiple PTVs - strong DVH vs weak DVH
def kbp_test_multi_v3(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan,clinical_beamset):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Add Treatment plan (unless it already exists)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    try:
        plan = patient.TreatmentPlans['Test KBP MA']
    except:
        plan = patient.AddNewPlan(PlanName='Test KBP MA', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset and beams (unless it/they already exists)
    try:
        beamset = plan.BeamSets['Test KBP']
    except:
        beamset = plan.AddNewBeamSet(Name='Test KBP', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique='SMLC', PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='IMRT')
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_names[0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx[0], RelativePrescriptionLevel=1)
        
        #Add beams
        #beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name='KBP1')
        beams.add_beams_brain_static(beamset=beamset, site_name='KBP1', iso_name='ISO', exam=exam, nb_beams=9)
        #optim.set_optimization_parameters(plan=plan)
        #optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40    
    

    """
    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    try:
        patient.Save()
    except Exception, err:
        message.message_window(err)
        exit(0)
    ui.MenuItem[3].Button_PlanOptimization.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['Test KBP MA'].Select()   
    """



    

    #Run script to determine predicted volumes for V80/70/60/50 and add optimization rings
    thing1,thing2,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body = statistics.dose_falloff_crane_multi(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=True)
  
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_sum_ptvs_smooth'].GetRoiVolume()  
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume() 
    result_text = ""


    #First plan: Falloff with strong DVH + up to 3 rounds of min dose weight adjustments
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    

    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(4):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling
        init_ptv_cov = []
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        init_ptv_cov.append(ptv_coverage1[0])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            init_ptv_cov.append(ptv_coverage2[0])
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            init_ptv_cov.append(ptv_coverage3[0])
        else:
            ptv_coverage3 = [0]        
            
        #Increase weight of lower PTV(s)
        boost_list = []        
        for i,cov in enumerate(init_ptv_cov):
            if max(init_ptv_cov) - cov > 0.01:
                boost_list.append(ptv_names[i])
            if cov == min(init_ptv_cov):
                prescribe_to = i
        
        #Pad init_ptv_cov out to three entries for when we print the results to file        
        if len(init_ptv_cov) == 1:
            init_ptv_cov.append(0)
        if len(init_ptv_cov) == 2:
            init_ptv_cov.append(0)
        
        #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
        if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)       
            
        #Get coverage after scaling
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
            
        #Evaluate plan
        dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        result_text += 'Strong DVH apres %d boosts,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (j,dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

        if j<3:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
                    objective.DoseFunctionParameters.Weight = 1.25*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
        
        
    
    
    

    #Second plan: Falloff with weak DVH + up to 3 rounds of min dose weight adjustments
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=1, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    

    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(4):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling
        init_ptv_cov = []
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        init_ptv_cov.append(ptv_coverage1[0])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            init_ptv_cov.append(ptv_coverage2[0])
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            init_ptv_cov.append(ptv_coverage3[0])
        else:
            ptv_coverage3 = [0]        
            
        #Increase weight of lower PTV(s)
        boost_list = []        
        for i,cov in enumerate(init_ptv_cov):
            if max(init_ptv_cov) - cov > 0.01:
                boost_list.append(ptv_names[i])
            if cov == min(init_ptv_cov):
                prescribe_to = i
        
        #Pad init_ptv_cov out to three entries for when we print the results to file        
        if len(init_ptv_cov) == 1:
            init_ptv_cov.append(0)
        if len(init_ptv_cov) == 2:
            init_ptv_cov.append(0)
        
        #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
        if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)       
            
        #Get coverage after scaling
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
            
        #Evaluate plan
        dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        result_text += 'Weak DVH apres %d boosts,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (j,dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

        if j<3:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
                    objective.DoseFunctionParameters.Weight = 1.25*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
        
        
    
 



 
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_multiplan_v3.txt'
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV1(%),Couverture PTV2(%),Couverture PTV3(%),Couverture avant scaling PTV1,Couverture avant scaling PTV2,Couverture avant scaling PTV3,Max ds PTV(Gy),Indice conformité,Dose de Rx la plus elevée(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,99.0,99.0,99.0,99.0,99.0,rx[0]*1.5/100.0,predicted_100_body/ptv_vol,max(rx)/100.0)
        #Add clinical plan here, it's going to take some effort
        ptv_coverage1 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])  
        if num_ptvs > 1:
            ptv_coverage2 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])    
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])    
        else:
            ptv_coverage3 = [0]
        dose_in_brain = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body  = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = clinical_beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)               
        output_file.write(header)      
        output_file.write(result_text)
                  
        
#Script for adding testing multiple plans on a patient with multiple PTVs - now with more iterations on PTV min doses
def kbp_test_multi_v4(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan,clinical_beamset):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Crâne'    

    # Add Treatment plan (unless it already exists)
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    try:
        plan = patient.TreatmentPlans['Test KBP MA']
    except:
        plan = patient.AddNewPlan(PlanName='Test KBP MA', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset and beams (unless it/they already exists)
    try:
        beamset = plan.BeamSets['Test KBP']
    except:
        beamset = plan.AddNewBeamSet(Name='Test KBP', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique='SMLC', PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='IMRT')
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_names[0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx[0], RelativePrescriptionLevel=1)
        
        #Add beams
        #beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name='KBP1')
        beams.add_beams_brain_static(beamset=beamset, site_name='KBP1', iso_name='ISO', exam=exam, nb_beams=9)
        #optim.set_optimization_parameters(plan=plan)
        #optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40    
    

    """
    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    try:
        patient.Save()
    except Exception, err:
        message.message_window(err)
        exit(0)
    ui.MenuItem[3].Button_PlanOptimization.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem['Test KBP MA'].Select()   
    """



    

    #Run script to determine predicted volumes for V80/70/60/50 and add optimization rings
    thing1,thing2,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body = statistics.dose_falloff_crane_multi(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=True)
  
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_sum_ptvs_smooth'].GetRoiVolume()  
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume() 
    result_text = ""


    #First plan: 8 rounds of min dose weight adjustments at 1.5x (BEST TECHNIQUE FOR MULTI-PTV)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    

    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(8):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling
        init_ptv_cov = []
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        init_ptv_cov.append(ptv_coverage1[0])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            init_ptv_cov.append(ptv_coverage2[0])
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            init_ptv_cov.append(ptv_coverage3[0])
        else:
            ptv_coverage3 = [0]        
            
        #Increase weight of lower PTV(s)
        boost_list = []        
        for i,cov in enumerate(init_ptv_cov):
            if max(init_ptv_cov) - cov > 0.01:
                boost_list.append(ptv_names[i])
            if cov == min(init_ptv_cov):
                prescribe_to = i
        
        #Pad init_ptv_cov out to three entries for when we print the results to file        
        if len(init_ptv_cov) == 1:
            init_ptv_cov.append(0)
        if len(init_ptv_cov) == 2:
            init_ptv_cov.append(0)
        
        #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
        if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)       
            
        #Get coverage after scaling
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
            
        #Evaluate plan
        dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        result_text += 'Weight x1.5 %d boosts,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (j,dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

        if j<7:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
                    objective.DoseFunctionParameters.Weight = 1.5*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
        
        
 
    

    #Second plan: 8 rounds of min dose weight adjustments at 1.25x (NOT BAD, BUT 1.5x IS BETTER)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 1:
        optim.add_mindose_objective(ptv_names[1], rx[1], weight=15, plan=plan, plan_opt=0)
    if num_ptvs > 2:
        optim.add_mindose_objective(ptv_names[2], rx[2], weight=15, plan=plan, plan_opt=0)        
    optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
    
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 100*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 100*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 100*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0) 
    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
    optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
    optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
    optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)    

    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(8):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling
        init_ptv_cov = []
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        init_ptv_cov.append(ptv_coverage1[0])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            init_ptv_cov.append(ptv_coverage2[0])
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            init_ptv_cov.append(ptv_coverage3[0])
        else:
            ptv_coverage3 = [0]        
            
        #Increase weight of lower PTV(s)
        boost_list = []        
        for i,cov in enumerate(init_ptv_cov):
            if max(init_ptv_cov) - cov > 0.01:
                boost_list.append(ptv_names[i])
            if cov == min(init_ptv_cov):
                prescribe_to = i
        
        #Pad init_ptv_cov out to three entries for when we print the results to file        
        if len(init_ptv_cov) == 1:
            init_ptv_cov.append(0)
        if len(init_ptv_cov) == 2:
            init_ptv_cov.append(0)
        
        #Change prescription to each PTV and scale dose (by doing this three times we guarantee that all PTVs will have adequate coverage)
        if ptv_coverage1[0] < 0.99 and ptv_names[0][:5] != 'Aucun':
            beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
            if ptv_coverage2[0] < 0.99 and ptv_names[1][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[1], DoseValue=rx[1], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])
            if ptv_coverage3[0] < 0.99 and ptv_names[2][:5] != 'Aucun':
                beamset.NormalizeToPrescription(RoiName=ptv_names[2], DoseValue=rx[2], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)       
            
        #Get coverage after scaling
        ptv_coverage1 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
        if num_ptvs > 1:
            ptv_coverage2 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])
        if num_ptvs > 2:
            ptv_coverage3 = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])   
            
        #Evaluate plan
        dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        result_text += 'Weight x1.25 apres %d boosts,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (j,dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,init_ptv_cov[2]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)             

        if j<7:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
                    objective.DoseFunctionParameters.Weight = 1.25*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_names[prescribe_to], DoseValue=rx[prescribe_to], DoseVolume=init_ptv_cov[prescribe_to]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
            
    

 
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_multiplan_v4.txt'
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV1(%),Couverture PTV2(%),Couverture PTV3(%),Couverture avant scaling PTV1,Couverture avant scaling PTV2,Couverture avant scaling PTV3,Max ds PTV(Gy),Indice conformité,Dose de Rx la plus elevée(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,99.0,99.0,99.0,99.0,99.0,rx[0]*1.5/100.0,predicted_100_body/ptv_vol,max(rx)/100.0)
        #Add clinical plan here, it's going to take some effort
        ptv_coverage1 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])  
        if num_ptvs > 1:
            ptv_coverage2 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[1], DoseValues=[rx[1]/nb_fx])    
        else:
            ptv_coverage2 = [0]
        if num_ptvs > 2:
            ptv_coverage3 = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[2], DoseValues=[rx[2]/nb_fx])    
        else:
            ptv_coverage3 = [0]
        dose_in_brain = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
        dose_in_body  = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[max(rx)/nb_fx])
        dmax = clinical_beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'stats_sum_ptvs_smooth',RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,ptv_coverage1[0]*100,ptv_coverage2[0]*100,ptv_coverage3[0]*100,max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol,max(rx)/100.0)               
        output_file.write(header)      
        output_file.write(result_text)
                
                

                
                
                
                
                
                
def crane_stereo_kbp_identify_rois(patient):
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    oar_list = []
    missing_oar = []
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
       missing_oar.append("cerveau pas trouvé")

    if "TR CEREBRAL*" in roi_names:
        tronc_name = "TR CEREBRAL*"
    elif "TR CEREBRAL" in roi_names:
        tronc_name = "TR CEREBRAL" 
    elif "TRONC CEREBRAL" in roi_names:
        tronc_name = "TRONC CEREBRAL" 
    elif "TRONC CEREBRAL*" in roi_names:
        tronc_name = "TRONC CEREBRAL*" 
    elif "TR cerebral" in roi_names:
        tronc_name = "TR cerebral" 
    elif "TRONC" in roi_names:
        tronc_name = "TRONC"         
    elif "TRONC*" in roi_names:
        tronc_name = "TRONC*"           
    else:
        missing_oar.append("tronc cérébral pas trouvé")
        
    if len(missing_oar) > 0:
        oar_list = ['ERROR']
        for oar in missing_oar:
            oar_list.append(oar)
    else:
        oar_list = [cerveau_name,tronc_name]
    
    return oar_list
    
    
def crane_stereo_kbp_predict_dose(plan_data):
            
    patient = plan_data['patient']
    ptv_names = plan_data['ptv_names']
    exam = plan_data['exam']
    site = plan_data['site_name']
    cerveau_name = plan_data['oar_list'][0]
    num_ptvs = len(ptv_names)
    
    #If predictions already exist, skip the roi creation and return only the predicted volumes
    if not roi.roi_exists("sum_ptvs_smooth_"+site):
        ptv_vol = []
        #For each PTV, create isodose prediction ROIs
        for i,ptv in enumerate(ptv_names):
            #Expand and contract PTV to smooth
            roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
            roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
            ptv_vol.append(patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume())
            
            #Calculate radii of the predicted isodoses
            marge_lat = 0.07
            marge_sup_inf = 0.02
            
            rad100 = marge_lat
            rad90 = 0.0013*ptv_vol[i] + 0.1314 + marge_lat
            rad80 = 0.0029*ptv_vol[i] + 0.2386 + marge_lat
            rad70 = 0.0048*ptv_vol[i] + 0.4109 + marge_lat
            rad60 = 0.0078*ptv_vol[i] + 0.6000 + marge_lat
            rad50 = 0.0122*ptv_vol[i] + 0.8800 + marge_lat
            rad40 = 0.0165*ptv_vol[i] + 1.4200 + marge_lat
            
            rad100_si = marge_sup_inf
            rad90_si = 0.0000*ptv_vol[i] + 0.0818 + marge_sup_inf
            rad80_si = 0.0014*ptv_vol[i] + 0.1293 + marge_sup_inf
            rad70_si = 0.0028*ptv_vol[i] + 0.1906 + marge_sup_inf
            rad60_si = 0.0048*ptv_vol[i] + 0.2351 + marge_sup_inf     
            rad50_si = 0.0058*ptv_vol[i] + 0.2931 + marge_sup_inf
            rad40_si = 0.0084*ptv_vol[i] + 0.3449 + marge_sup_inf 
            
            #Create predicted isodose ROIs starting from smoothed PTV
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Yellow", examination=exam, marge_lat=rad100, marge_sup_inf = rad100_si, output_name='predicted_r100_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Green",  examination=exam, marge_lat=rad90,  marge_sup_inf = rad90_si, output_name='predicted_r90_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Red",    examination=exam, marge_lat=rad80,  marge_sup_inf = rad80_si, output_name='predicted_r80_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Pink",   examination=exam, marge_lat=rad70,  marge_sup_inf = rad70_si, output_name='predicted_r70_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Blue",   examination=exam, marge_lat=rad60,  marge_sup_inf = rad60_si, output_name='predicted_r60_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Tomato", examination=exam, marge_lat=rad50,  marge_sup_inf = rad50_si, output_name='predicted_r50_'+str(i))
            roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Brown",  examination=exam, marge_lat=rad40,  marge_sup_inf = rad40_si, output_name='predicted_r40_'+str(i))
            
            #Erase unneeded expansion of PTV, rename smoothed volume
            patient.PatientModel.RegionsOfInterest['stats_ptv+3cm'].DeleteRoi()
            patient.PatientModel.RegionsOfInterest['stats_ptv+3cm-2.95cm'].Name = 'ptv_smooth_' + str(i)        

        #Sum the smoothed volumes for the different PTVs; also create sum of PTVs for site
        if num_ptvs == 1:
            patient.PatientModel.CreateRoi(Name="sum_ptvs_smooth_"+site, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].UpdateDerivedGeometry(Examination=exam)    
            patient.PatientModel.CreateRoi(Name="sum_ptvs_"+site, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].UpdateDerivedGeometry(Examination=exam)                
        elif num_ptvs == 2:
            patient.PatientModel.CreateRoi(Name="sum_ptvs_smooth_"+site, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.CreateRoi(Name="sum_ptvs_"+site, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].UpdateDerivedGeometry(Examination=exam)              
        elif num_ptvs == 3:
            patient.PatientModel.CreateRoi(Name="sum_ptvs_smooth_"+site, Color="128, 128, 192", Type="Ptv", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_1','ptv_smooth_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_smooth_"+site].UpdateDerivedGeometry(Examination=exam) 
            patient.PatientModel.CreateRoi(Name="sum_ptvs_"+site, Color="128, 128, 192", Type="Ptv", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1],ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site].UpdateDerivedGeometry(Examination=exam)                
        
        #Combine the expanded volumes (except if there's only one PTV, in which case we just rename the existing ones)
        if num_ptvs == 1:
            patient.PatientModel.RegionsOfInterest['predicted_r100_0'].Name = 'predicted_r100_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r90_0'].Name = 'predicted_r90_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r80_0'].Name = 'predicted_r80_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r70_0'].Name = 'predicted_r70_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r60_0'].Name = 'predicted_r60_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r50_0'].Name = 'predicted_r50_'+site
            patient.PatientModel.RegionsOfInterest['predicted_r40_0'].Name = 'predicted_r40_'+site
        else:
            patient.PatientModel.CreateRoi(Name="predicted_r100_"+site, Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r90_"+site, Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r80_"+site, Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r70_"+site, Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r60_"+site, Color="Tomato", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r50_"+site, Color="Brown", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.CreateRoi(Name="predicted_r40_"+site, Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            
            if num_ptvs == 2:
                patient.PatientModel.RegionsOfInterest['predicted_r100_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r100_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r100_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r90_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r90_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r90_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r80_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r80_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r80_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r70_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r70_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r70_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r60_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r60_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r60_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r50_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r50_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r50_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r40_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r40_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r40_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            elif num_ptvs == 3:
                patient.PatientModel.RegionsOfInterest['predicted_r100_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r100_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r100_1','predicted_r100_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r90_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r90_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r90_1','predicted_r90_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r80_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r80_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r80_1','predicted_r80_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r70_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r70_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r70_1','predicted_r70_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r60_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r60_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r60_1','predicted_r60_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r50_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r50_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r50_1','predicted_r50_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['predicted_r40_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['predicted_r40_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['predicted_r40_1','predicted_r40_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                    
            patient.PatientModel.RegionsOfInterest['predicted_r100_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r90_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r80_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r70_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r60_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r50_'+site].UpdateDerivedGeometry(Examination=exam)
            patient.PatientModel.RegionsOfInterest['predicted_r40_'+site].UpdateDerivedGeometry(Examination=exam)

        #Clean up ROIs
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            if ('ptv_smooth' in name or 'predicted_r' in name) and name[-2:] in ['_0','_1','_2']:
                patient.PatientModel.RegionsOfInterest[name].DeleteRoi()
     
    #Calculate total smoothed volume
    smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries["sum_ptvs_smooth_"+site].GetRoiVolume()    
    ptv_in_cerv_vol =  roi.get_intersecting_volume("sum_ptvs_smooth_"+site, cerveau_name, examination=exam)      
   
    # Create CERVEAU-PTV
    if not roi.roi_exists("CERVEAU-PTV_"+site):
        patient.PatientModel.CreateRoi(Name="CERVEAU-PTV_"+site, Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["CERVEAU-PTV_"+site].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['sum_ptvs_'+site], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["CERVEAU-PTV_"+site].UpdateDerivedGeometry(Examination=exam)   
   
    #Calculate predicted volumes for each isodose
    predicted_vol = [0,0,0,0,0,0,0]
    predicted_vol[0] = roi.get_intersecting_volume('predicted_r100_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[1] = roi.get_intersecting_volume('predicted_r90_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[2] = roi.get_intersecting_volume('predicted_r80_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[3] = roi.get_intersecting_volume('predicted_r70_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[4] = roi.get_intersecting_volume('predicted_r60_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[5] = roi.get_intersecting_volume('predicted_r50_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[6] = roi.get_intersecting_volume('predicted_r40_'+site, cerveau_name, examination=exam) - ptv_in_cerv_vol
    
    #Correct volumes for 70/60/50/40 according to empirical formulas that Malik devised, using average volume of PTVs
    predicted_vol[3] = predicted_vol[3] - (smoothed_vol/num_ptvs)*0.063 - 0.17
    predicted_vol[4] = predicted_vol[4] - (smoothed_vol/num_ptvs)*0.011 - 0.9
    predicted_vol[5] = predicted_vol[5] - (smoothed_vol/num_ptvs)*0.048 - 1.3
    predicted_vol[6] = predicted_vol[6] + (smoothed_vol/num_ptvs)*0.03 - 6.4      

    #Make a ring based on the estimated radius of the 40% isodose (with an added margin in sup-inf to control which leaf pairs are open), but restricted to the brain and excluding the PTV
    if not roi.roi_exists('OPT CERVEAU_'+site):
        roi.create_expanded_roi('predicted_r40_'+site, color="Brown",  examination=exam, marge_lat=0,  marge_sup_inf = 0.5, output_name='temp_r40_mod')
        patient.PatientModel.CreateRoi(Name='OPT CERVEAU_'+site, Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['OPT CERVEAU_'+site].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp_r40_mod", cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["sum_ptvs_smooth_"+site], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['OPT CERVEAU_'+site].UpdateDerivedGeometry(Examination=exam)       
        patient.PatientModel.RegionsOfInterest['temp_r40_mod'].DeleteRoi()       
    
    return predicted_vol
       
    
def crane_stereo_kbp_predict_oar_dose(plan_data):

    site = plan_data['site_name']
    exam = plan_data['exam']
    rx_dose = plan_data['rx_dose']
    tronc_name = plan_data['oar_list'][1]

    #Detailed analysis to predict dose to tronc
    tronc_est = 0 #Dose that we expect the tronc to receive (in cGy)
    ring_list = ['predicted_r40_'+site,'predicted_r50_'+site,'predicted_r60_'+site,'predicted_r70_'+site,'predicted_r80_'+site,'predicted_r90_'+site,'predicted_r100_'+site]
    for r in ring_list:
        if roi.get_intersecting_volume(tronc_name, r, examination=exam) > 0: #Tronc overlaps with this predicted dose level
            tronc_est = int(r.split('_')[1][1:])*rx_dose/100
        else:
            break
    
    if tronc_est > 800:
        tronc_max = 800
    elif tronc_est > 500 and tronc_est <= 800:
        tronc_max = tronc_est
    else:
        tronc_max = 500
        
    return tronc_max
    
   
def crane_stereo_kbp_add_VMAT_plan_and_beamset(plan_data):    
    
    name = plan_data['site_name'] + ' VMAT'
    
    # Add Treatment plan
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = plan_data['patient'].AddNewPlan(PlanName=name, PlannedBy=planner_name, Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=name, ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique='VMAT', PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment='VMAT')
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv_names'][0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)    
    
    # Add beam
    beams.add_beams_brain_stereo_kbp(beamset=beamset, site_name=plan_data['site_name'],iso_name=plan_data['iso_name'])
    
    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)
    
    return plan,beamset
    
    
def crane_stereo_kbp_add_IMRT_plan_and_beamset(plan_data):    
    
    name = plan_data['site_name'] + ' IMRT'
    if plan_data['couch']:
        name += ' Couch'    
    
    # Add Treatment plan
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = plan_data['patient'].AddNewPlan(PlanName=name, PlannedBy=planner_name, Comment="", ExaminationName=plan_data['exam'].Name, AllowDuplicateNames=False)
    
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=name, ExaminationName=plan_data['exam'].Name, MachineName=plan_data['machine'], NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique='SMLC', PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, Comment='IMRT')
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv_names'][0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1)    
    
    # Add beam
    if plan_data['couch']:    
        beams.add_beams_brain_static(beamset=beamset,site_name=plan_data['site_name'],iso_name=plan_data['iso_name'], exam=plan_data['exam'], nb_beams = 14)
    else:
        beams.add_beams_brain_static(beamset=beamset,site_name=plan_data['site_name'],iso_name=plan_data['iso_name'], exam=plan_data['exam'], nb_beams = 9)
    
    # Set optimization parameters
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
    plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
    plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40
    
    return plan,beamset
    
 
def crane_stereo_kbp_add_3DC_plan(plan_data):
    
    patient = plan_data['patient']
    site = plan_data['site_name']
    exam = plan_data['exam']
    name = site + ' ' + plan_data['technique']
    if plan_data['couch']:
        name += ' Couch'
    cerveau_name = plan_data['oar_list'][0]
    
    # Add plan
    planner_name = lib.get_user_name(os.getenv('USERNAME'))
    plan = patient.AddNewPlan(PlanName=name, PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
    
    # Add beamset
    beamset = plan.AddNewBeamSet(Name=name, ExaminationName=exam.Name, MachineName=plan_data['machine'], NominalEnergy=None, Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=plan_data['nb_fx'], CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment=plan_data['technique'])
    beamset.AddDosePrescriptionToRoi(RoiName=plan_data['ptv_names'][0], DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=plan_data['rx_dose'], RelativePrescriptionLevel=1, AutoScaleDose=False)

    # Add beams
    if plan_data['couch']:
        nb_beams = 14
    elif plan_data['technique'] == 'IMRT':
        nb_beams = 9
    elif plan_data['technique'] == '3DC':
        nb_beams = 13
    beams.add_beams_brain_static(beamset=beamset, site_name=plan_data['site_name'], iso_name=plan_data['iso_name'], exam=exam, nb_beams=nb_beams)    
    
    # Create OPTPTV
    if not roi.roi_exists("OPTPTV_"+site): #We put an underscore as the first character to guarantee that the OPTPTV shows up in the Treat and Protect list before the PTV
        patient.PatientModel.CreateRoi(Name="OPTPTV_"+site, Color="Yellow", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["OPTPTV_"+site].SetMarginExpression(SourceRoiName='sum_ptvs_'+site, MarginSettings={'Type': "Expand", 'Superior': 0.15, 'Inferior': 0.15, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["OPTPTV_"+site].UpdateDerivedGeometry(Examination=exam)
            
    # Make the new plan active through the GUI (required so we can manipulate GUI elements below)
    ui = get_current("ui")
    # We have to save before selecting the plan
    patient.Save()
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem[name].Select()  
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    
    # Conform the MLCs to the OPTPTV
    ui.TabControl_Modules.TabItem['3D-CRT Beam Design'].Select()
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_PlanSettings.Click()

    # Change settings in Plan Settings window
    for row in ui.RoisUsedForPlanningView.DataGridRow:
        if row.RoiGeometry.TextBlock_Name.Text == 'OPTPTV_'+site or row.RoiGeometry.TextBlock_Name.Text == plan_data['ptv_names'][0]:
            if not row.CheckBox.IsChecked:
                row.CheckBox.Click()    
        elif row.CheckBox.IsChecked:
            row.CheckBox.Click()

    ui.TextBox_LeafPositioningThreshold.Text = '0.25'
    ui.Button_OK.Click()
   
    # Check boxes to treat OPTPTV
    # Determine which column corresponds to the OPTPTV
    #if ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridColumnHeader['Treat'].RoiGeometry[0].TextBlock_Name.Text == 'OPTPTV_'+site:
    #    optptv_index = 0
    #else:
    #    optptv_index = 1
    # Check the boxes for the OPTPTV and uncheck the boxes for the PTV
    ui.Workspace.TabControl['Beams'].TabItem['Treat and Protect'].Select()
    for row in ui.Workspace.TabControl['Beams'].RayDataGrid.DataGridRow:
        #if optptv_index == 0:
        if not row.CheckBox[0].IsChecked:
            row.CheckBox[0].Click()   
        if not row.CheckBox[1].IsChecked:
            row.CheckBox[1].Click()
        #elif optptv_index == 1:
        #    if not row.CheckBox[1].IsChecked:
        #        row.CheckBox[1].Click()   
        #    if row.CheckBox[0].IsChecked:
        #        row.CheckBox[0].Click()                
            
    # Actually conform the MLCs
    ui.TabControl_ToolBar.ToolBarGroup['TREAT AND PROTECT'].Button_ConformAllBeams.Click()
    
    return plan,beamset

    
def crane_stereo_convert_3DC_IMRT(plan,beamset):
    ui = get_current("ui")
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    ui.TabControl_Modules.TabItem['Plan Setup'].Select()
    ui.TabControl_ToolBar.ToolBarGroup['PLAN PREPARATION'].Button_EditPlan.Click()
    ui.TabControl.TreatmentSetup.TreatmentSetup2.ComboBox_AvailableTreatmentTechniques.ToggleButton.Click()
    ui.TabControl.TreatmentSetup.TreatmentSetup2.ComboBox_AvailableTreatmentTechniques.Popup.ComboBoxItem['SMLC'].Select()
    ui.TabControl.TreatmentSetup.TreatmentSetup2.ComboBox_AvailableTreatmentTechniques.ToggleButton.Click()
    ui.Button_OK.Click()
    time.sleep(6) #The script kept crashing here, so I added a pause to let it close the Edit Plan window before proceeding
    
    # Set optimization parameters
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
    plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
    plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
    plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40
    
 
def crane_stereo_kbp_optimize_3DC_plan(plan_data,plan,beamset):

    patient = plan_data['patient']
    rx_dose = plan_data['rx_dose']
    nb_fx = plan_data['nb_fx']
    site = plan_data['site_name']

    # Calculate dose and scale to Rx
    beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)
    beamset.NormalizeToPrescription(RoiName=plan_data['ptv_names'][0], DoseValue=rx_dose, DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=False)                  
    
    # Save plan and create copy
    patient.Save()
    plan = patient.CopyPlan(PlanName=site+" 3DC", NewPlanName=site+" 3DC optimised")
    
    # In the new plan, change optimization settings
    patient.Save() #Might not be necessary a second time, I'm not sure
    ui = get_current("ui")
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.Popup.ComboBoxItem[site+' 3DC optimised'].Select()    
    ui.SelectionBar.ComboBox_TreatmentPlanCollectionView.ToggleButton.Click()
    
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
    optim.add_mindose_objective(plan_data['ptv_names'][0], rx_dose, weight=1, plan=plan)
    optim.add_dosefalloff_objective('BodyRS', rx_dose, rx_dose*0.45, 0.7, weight=10, plan=plan) 
    
    # Optimize plan twice
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    plan.PlanOptimizations[beamset.Number-1].RunOptimization()
    
    return plan,beamset
    
    
def crane_stereo_kbp_initial_optimization_objectives(plan_data,plan,predicted_vol,tronc_max):
    patient = plan_data['patient']
    ptv_names = plan_data['ptv_names']
    rx = plan_data['rx']
    site = plan_data['site_name']
    exam = plan_data['exam']
    tronc_name = plan_data['oar_list'][1]
    
    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['OPT CERVEAU_'+site].GetRoiVolume()
    
    if len(ptv_names) == 1: #Single PTV
        optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
        optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
        optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.8, round(100*predicted_vol[2]/ring_vol,2), weight=10, plan=plan, plan_opt=0)
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.7, round(100*predicted_vol[3]/ring_vol,2), weight=10, plan=plan, plan_opt=0)
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.6, round(100*predicted_vol[4]/ring_vol,2), weight=5, plan=plan, plan_opt=0)    
        optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
        
    elif len(ptv_names) > 1: #Multiple PTVs
        for i,ptv in enumerate(ptv_names):
            optim.add_mindose_objective(ptv_names[i], rx[i], weight=15, plan=plan, plan_opt=0)
            
        optim.add_dosefalloff_objective('BodyRS', max(rx)*1.00, max(rx)*0.40, 0.4, weight=10, plan=plan, plan_opt=0)
        optim.add_dosefalloff_objective('BodyRS', max(rx)*0.60, max(rx)*0.20, 1.0, weight=5, plan=plan, plan_opt=0)   
        
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.8, round(100*predicted_vol[2]/ring_vol,2), weight=10, plan=plan, plan_opt=0)
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.7, round(100*predicted_vol[3]/ring_vol,2), weight=10, plan=plan, plan_opt=0)
        optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.6, round(100*predicted_vol[4]/ring_vol,2), weight=5, plan=plan, plan_opt=0)  
        
        optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)  
        optim.add_maxdose_objective('OEIL DRT', 800, weight=1.0, plan=plan, plan_opt=0)                        
        optim.add_maxdose_objective('OEIL GCHE', 800, weight=1.0, plan=plan, plan_opt=0)      
        optim.add_maxdose_objective('CHIASMA', 800, weight=1.0, plan=plan, plan_opt=0)        
        
        
def crane_stereo_kbp_modify_plan_single_ptv(plan_data,plan,beamset,predicted_vol,tronc_max):
    patient = plan_data['patient']
    ptv_names = plan_data['ptv_names']
    rx = plan_data['rx']
    nb_fx = plan_data['nb_fx']
    tronc_name = plan_data['oar_list'][1]
    site = plan_data['site_name']
    exam = plan_data['exam']

    ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['OPT CERVEAU_'+site].GetRoiVolume()
    
    #If obtained DVH in brain is lower than prediction, change volume to obtained-1% of ROI volume
    initial_brain_dvh = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='OPT CERVEAU_'+site, DoseValues=[rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx])
    brain80 = min(100*predicted_vol[2]/ring_vol,100*initial_brain_dvh[0]-1)
    brain70 = min(100*predicted_vol[3]/ring_vol,100*initial_brain_dvh[1]-1)
    brain60 = min(100*predicted_vol[4]/ring_vol,100*initial_brain_dvh[2]-1)
    
    #Replace optimization objectives with updated values
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()    

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS', rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.8, round(brain80,2), weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.7, round(brain70,2), weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('OPT CERVEAU_'+site, rx[0]*0.6, round(brain60,2), weight=5, plan=plan, plan_opt=0)    
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
     
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    
    
def crane_stereo_kbp_modify_plan_multi_ptv(plan_data,plan,beamset):
    patient = plan_data['patient']
    ptv_names = plan_data['ptv_names']
    rx = plan_data['rx']
    nb_fx = plan_data['nb_fx']
    num_ptvs = len(ptv_names)

    #Get initial coverage before scaling
    initial_ptv_cov = []   
    for i,ptv in enumerate(ptv_names):
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        initial_ptv_cov.append(ptv_coverage[0])
    
    #Increase weight of lower PTV(s)
    boost_list = []        
    for i,cov in enumerate(initial_ptv_cov):
        if max(initial_ptv_cov) - cov > 0.01:
            boost_list.append(ptv_names[i])
        if cov == min(initial_ptv_cov):
            prescribe_to = i
    
    if len(boost_list) > 0: #If some PTVs have poor coverage, modify min dose weights and reoptimize
        #Modify weights and reoptimize
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
            try:
                f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
            except:
                continue
            if f_type == "MinDose" and objective.ForRegionOfInterest.Name in boost_list:    
                objective.DoseFunctionParameters.Weight = 1.5*objective.DoseFunctionParameters.Weight
        
        #plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
        plan.PlanOptimizations[beamset.Number-1].RunOptimization()        
        continue_optimization = True
    else: #If all PTVs are covered equally, stop here
        continue_optimization = False
        
    return continue_optimization
        
        
def crane_stereo_kbp_scale_dose(plan_data,beamset,reset_dose=False):    

    #This function verifies the initial dose to each PTV and then scales the plan to get coverage
    #For a single PTV, coverage is set to exactly 99%
    #For multiple PTVs, coverage is set to be at least 99% for all PTVs
    #If the user wishes to return the coverage to where it was initially, they can set reset_dose=True

    ptv_names = plan_data['ptv_names']
    rx = plan_data['rx']
    nb_fx = plan_data['nb_fx']
    
    #If we want to scale the dose back to its initial level, we need to determine what the initial PTV coverage was
    initial_ptv_cov = []
    for i,ptv in enumerate(ptv_names):
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        initial_ptv_cov.append(ptv_coverage[0])    
    
    #For each PTV, check coverage and scale plan if necessary
    for i,ptv in enumerate(ptv_names):
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        if len(ptv_names) == 1:
            beamset.NormalizeToPrescription(RoiName=ptv_names[i], DoseValue=rx[i], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)     
        elif len(ptv_names) > 1:
            if ptv_coverage[0] < 0.99:
                beamset.NormalizeToPrescription(RoiName=ptv_names[i], DoseValue=rx[i], DoseVolume=99, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)     
    
    #Evaluate V10,V12
    obtained_vol = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName="CERVEAU-PTV_"+plan_data['site_name'], DoseValues=[1000/nb_fx,1200/nb_fx])
    
    #Reset dose to where it was before scaling if requested
    if reset_dose:
        beamset.NormalizeToPrescription(RoiName=ptv_names[0], DoseValue=rx[0], DoseVolume=initial_ptv_cov[0]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)     
        
    return obtained_vol,initial_ptv_cov

    
def estimate_vx(predicted_vol,rx_dose,dose_level=1000):
    #predicted_vol=[v100,v90,v80,v70,v60,v50,v40] (in cc)
    #rx_dose and dose_level should be in cGy

    ratio = float(dose_level) / float(rx_dose)
    if ratio < 0.4: #Prescription is so high that 10Gy falls below the predicted dose levels
        output = 'moins que %.2fcc' % predicted_vol[6]
    elif ratio == 0.4:
        output = '%.2fcc' % predicted_vol[6]
    elif ratio > 0.4 and ratio < 0.5:
        output = 'approx %.2fcc' % ((0.5-ratio)*10*predicted_vol[6]+(ratio-0.4)*10*predicted_vol[5])
    elif ratio == 0.5:
        output = '%.2fcc' % predicted_vol[5]
    elif ratio > 0.5 and ratio < 0.6:
        output = 'approx %.2fcc' % ((0.6-ratio)*10*predicted_vol[5]+(ratio-0.5)*10*predicted_vol[4])
    elif ratio == 0.6:
        output = '%.2fcc' % predicted_vol[4]
    elif ratio > 0.6 and ratio < 0.7:
        output = 'approx %.2fcc' % ((0.7-ratio)*10*predicted_vol[4]+(ratio-0.6)*10*predicted_vol[3])
    elif ratio == 0.7:
        output = '%.2fcc' % predicted_vol[3]        
    elif ratio > 0.7 and ratio < 0.8:
        output = 'approx %.2fcc' % ((0.8-ratio)*10*predicted_vol[3]+(ratio-0.7)*10*predicted_vol[2])
    elif ratio == 0.8:
        output = '%.2fcc' % predicted_vol[2]   
    elif ratio > 0.8 and ratio < 0.9:
        output = 'approx %.2fcc' % ((0.9-ratio)*10*predicted_vol[2]+(ratio-0.8)*10*predicted_vol[1])
    elif ratio == 0.9:
        output = '%.2fcc' % predicted_vol[1]   
    elif ratio > 0.9 and ratio < 1.0:
        output = 'approx %.2fcc' % ((1.0-ratio)*10*predicted_vol[1]+(ratio-0.9)*10*predicted_vol[0])
    elif ratio == 1.0:
        output = '%.2fcc' % predicted_vol[0]           
    elif ratio > 1.0:
        output = 'au moins %.2fcc' % predicted_vol[0]
    
    return output
    
    
def crane_kbp_write_results_to_file(plan_data,plan,beamset,predicted_vol,initial_ptv_cov,obtained_vol):
    #Three elements to write to file:
    #   - demographic information (patient name, plan, beamset, PTV names, doses, technique used, nb beams, nb segments...)
    #   - predicted results
    #   - obtained results
    
    patient = plan_data['patient']
    exam = plan_data['exam']
    site = plan_data['site_name']
    rx = plan_data['rx']
    nb_fx = plan_data['nb_fx']
    ptv_names = plan_data['ptv_names']
    
    result_text = ""    
    ptv_coverage = []
    
    #Get PTV coverage
    for i,ptv in enumerate(ptv_names):
        cov = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        ptv_coverage.append(cov[0])
    
    #Pad out arrays if necessary (to prevent crashes during printing)
    if len(ptv_names) == 1:
        ptv_names.append('Aucun PTV2')
        rx.append(0)
        ptv_coverage.append(0)
        initial_ptv_cov.append(0)
    if len(ptv_names) == 2:
        ptv_names.append('Aucun PTV3')
        rx.append(0)
        ptv_coverage.append(0)
        initial_ptv_cov.append(0)        
    
    #Demographic information
    header = 'Nom du patient,No. HMR,Nom plan,Nom beamset,'
    result_text += patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ','
    header += 'Nom PTV 1,Rx PTV1 (cGy),Nom PTV 2,Rx PTV2 (cGy),Nom PTV 3,Rx PTV3 (cGy),'
    result_text += "%s,%d,%s,%d,%s,%d," % (ptv_names[0],rx[0],ptv_names[1],rx[1],ptv_names[2],rx[2])
    header += 'Technique,'
    result_text += plan_data['technique'] + ','
    
    #Predicted volumes
    header += 'Cerv-PTV V100 prédit (cc),Cerv-PTV V90 prédit (cc),Cerv-PTV V80 prédit (cc),Cerv-PTV V70 prédit (cc),Cerv-PTV V60 prédit (cc),Cerv-PTV V50 prédit (cc),Cerv-PTV V40 prédit (cc),'
    result_text += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6])
    
    #Evaluate plan
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries["sum_ptvs_smooth_"+site].GetRoiVolume() 
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries["BodyRS"].GetRoiVolume() 
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries["CERVEAU-PTV_"+site].GetRoiVolume() 
    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName="CERVEAU-PTV_"+site, DoseValues=[max(rx)/nb_fx,max(rx)*0.9/nb_fx,max(rx)*0.8/nb_fx,max(rx)*0.7/nb_fx,max(rx)*0.6/nb_fx,max(rx)*0.5/nb_fx,max(rx)*0.4/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName="BodyRS", DoseValues=[max(rx)/nb_fx])
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName="sum_ptvs_smooth_"+site,RelativeVolumes = [0.03/ptv_vol])
    max_in_ptv = dmax[0] * nb_fx / 100.0
    
    num_segments = 0
    num_beams = 0
    total_mu = 0
    for beam in beamset.Beams:
        num_beams += 1
        total_mu += beam.BeamMU
        for segment in beam.Segments:         
            num_segments += 1
    
    #CERVEAU-PTV v100/V90...V40 in cc
    header += 'Cerv-PTV V100 obtenu (cc),Cerv-PTV V90 obtenu (cc),Cerv-PTV V80 obtenu (cc),Cerv-PTV V70 obtenu (cc),Cerv-PTV V60 obtenu (cc),Cerv-PTV V50 obtenu (cc),Cerv-PTV V40 obtenu (cc),'
    result_text += '%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol)
    
    #V10 and V12 in cc
    header += 'V10 obtenu (cc),V12 obtenu (cc),'
    result_text += '%.2f,%.2f,' % (obtained_vol[0]*brain_minus_ptv_vol,obtained_vol[1]*brain_minus_ptv_vol)
    
    #PTV coverage before and after scaling
    header += 'Couverture PTV1,Couverture PTV2,Couverture PTV3,Couv PTV1 avant scaling,Couv PTV2 avant scaling,Couv PTV3 avant scaling,'
    result_text += '%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,' % (ptv_coverage[0]*100,ptv_coverage[1]*100,ptv_coverage[2]*100,initial_ptv_cov[0]*100,initial_ptv_cov[1]*100,initial_ptv_cov[2]*100)             
    
    #Max dose and conformity index
    header += 'Max dans PTV,Indice de conformité,'
    result_text += '%.2f,%.2f,' % (max_in_ptv,(dose_in_body[0]*body_vol)/ptv_vol)
    
    #Number of segments   
    header += 'Nb de faisceaux,Nb de segments,Nb de UM\n'
    result_text += '%d,%d,%.2f\n' % (num_beams,num_segments,total_mu)
    
    
    #Print
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\Crane KBP Clinique.txt'
    file_exists = os.path.exists(output_file_path)
    with open(output_file_path, 'a') as output_file:
        if not file_exists:
            output_file.write(header) #Only want to write the header if we're starting a new file
        output_file.write(result_text)