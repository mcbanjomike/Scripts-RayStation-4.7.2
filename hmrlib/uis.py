# -*- coding: utf-8 -*-
import sys
import os.path
import lib
import message
import statetree

# To allow importation of module by sphinx-python
try:
    from connect import *
    # import ScriptClient
except Exception as e:
    if 'IronPython' in sys.version:
        raise
    else:
        pass

def ui_statetree():
    statetree.CreateUiStateTreeWindow().ShowDialog()    
        
def show_patient_modeling():
    try:
        ui = get_current("ui")
        ui.MenuItem[1].Button_PatientModeling.Click()
    except:
        pass

def show_plan_design():
    try:
        ui = get_current("ui")
        ui.MenuItem[2].Button_PlanDesign.Click()
    except:
        pass
        
def show_plan_optimization():
    try:
        ui = get_current("ui")
        ui.MenuItem[3].Button_PlanOptimization.Click()
    except:
        pass               
        
def show_po_cg():
    try:
        ui = get_current("ui")
        ui.Workspace.TabControl[0].TabItem['Clinical Goals'].Select()
    except:
        pass
        
def show_po_bev():
    try:
        ui = get_current("ui")
        ui.Workspace.TabControl[1].TabItem['BEV'].Select()
    except:
        pass        
        
def show_po_2D():
    try:
        ui = get_current("ui")
        ui.Workspace.TabControl[1].TabItem['2D'].Select()
    except:
        pass           
        
def display_loc_point():
    try:
        beamset = lib.get_current_beamset()
        loc_point_name = beamset.PatientSetup.LocalizationPoiGeometrySource.LocalizationPoiGeometry.OfPoi.Name
        ui = get_current("ui")
        ui.MenuItem[1].Button_PatientModeling.Click()
        ui.ToolPanel.TabItem['POIs'].Select()
        ui.ToolPanel.PoiList.RayDataGrid.DataGridRow[loc_point_name].Select()
        ui.TabControl_ToolBar.TabItem['POI Tools'].Select()
        ui.TabControl_ToolBar.ToolBarGroup['CURRENT POI'].Button_LocalizePOI.Click()
    except:
        pass
        
def display_external_roi(): # WIP, do not use yet
    patient = lib.get_current_patient()
    plan = lib.get_current_plan()
    
    for roi in patient.PatientModel.StructureSets[exam.Name].RoiGeometries:
        if roi.OfRoi.Type == "External":
            external_roi = roi.OfRoi.Name
        
    try:
        ui = get_current("ui")
        ui.MenuItem[1].Button_PatientModeling.Click()       
    except:
        pass
        
def select_roi_tab():
    try:
        ui = get_current("ui")
        ui.ToolPanel.TabItem['ROIs'].Select()
    except:
        pass       