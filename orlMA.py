# -*- coding: utf-8 -*-

"""
Ce module contient les fonctions nécessaires à la planification des cas d'ORL

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


def plan_orl():
    """
    Voir :py:mod:`plan_orl`.
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

    # Determine different PTV levels. If PTV56 exists, it is assumed treatment will be in 35 fractions. If PTV54 exists, 33 fx.
    # PTVs are classified as high, mid or low to simplify generation of contours later on. If PTV70 and 66 exist, the high level PTV is their union.
    ptvs = []
    if roi.roi_exists("PTV70"):
        ptvs.append(70)
        highptv = patient.PatientModel.RegionsOfInterest["PTV70"]
    if roi.roi_exists("PTV66"):
        ptvs.append(66)
        if roi.roi_exists("PTV70"):
            patient.PatientModel.CreateRoi(Name="PTV70+66", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV70+66'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV70"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV66"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['PTV70+66'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            highptv = patient.PatientModel.RegionsOfInterest["PTV70+66"]
        else:
            highptv = patient.PatientModel.RegionsOfInterest["PTV66"]
    if roi.roi_exists("PTV63"):
        ptvs.append(63)
        midptv = patient.PatientModel.RegionsOfInterest["PTV63"]
    if roi.roi_exists("PTV60"):
        ptvs.append(60)
        midptv = patient.PatientModel.RegionsOfInterest["PTV60"]
    if roi.roi_exists("PTV56"):
        ptvs.append(56)
        lowptv = patient.PatientModel.RegionsOfInterest["PTV56"]
        nb_fx = 35
    if roi.roi_exists("PTV54"):
        ptvs.append(54)
        lowptv = patient.PatientModel.RegionsOfInterest["PTV54"]
        nb_fx = 33

    # DEBUG
    # tempname = ""
    # for i,dose in enumerate(ptvs):
    #     tempname += str(ptvs[i])
    # patient.PatientModel.CreateRoi(Name=tempname, Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)

    # Generate optimization contours
    # For any plan with 3 PTVs, the algorithm is the same. For 4 PTVs, additional steps are added.
    # Create expanded PTVs
    if len(ptvs) == 3:
        # Create BodyRS-5mm
        patient.PatientModel.CreateRoi(Name="BodyRS-5mm", Color="Lime", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['BodyRS-5mm'].SetMarginExpression(SourceRoiName="BodyRS", MarginSettings={'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5})
        patient.PatientModel.RegionsOfInterest['BodyRS-5mm'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Create expanded PTVs to help with contour generation
        roi.create_expanded_ptv(ptv_name=highptv.Name, color="Tomato", margeptv=1.8, output_name=highptv.Name)
        roi.create_expanded_ptv(ptv_name=midptv.Name, color="SkyBlue", margeptv=1.8, output_name=midptv.Name)
        roi.create_expanded_ptv(ptv_name=lowptv.Name, color="Brown", margeptv=1.8, output_name=lowptv.Name)
        roi.create_expanded_ptv(ptv_name=highptv.Name, color="Magenta", margeptv=0.8, output_name=highptv.Name)
        roi.create_expanded_ptv(ptv_name=midptv.Name, color="Teal", margeptv=0.8, output_name=midptv.Name)
        roi.create_expanded_ptv(ptv_name=lowptv.Name, color="Brown", margeptv=0.8, output_name=lowptv.Name)
        roi.create_expanded_ptv(ptv_name=midptv.Name, color="Yellow", margeptv=0.5, output_name=midptv.Name)
        roi.create_expanded_ptv(ptv_name=lowptv.Name, color="Orange", margeptv=0.3, output_name=lowptv.Name)
        # Create modPTVs
        patient.PatientModel.CreateRoi(Name=("modPTV" + str(ptvs[0])), Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[0]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[0]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("modPTV" + str(ptvs[1])), Color="Green", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [midptv.Name, "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("modPTV" + str(ptvs[2])), Color="Blue", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[2]))].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [lowptv.Name, "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [midptv.Name, highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[2]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        highmod = patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[0]))]
        midmod = patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[1]))]
        lowmod = patient.PatientModel.RegionsOfInterest[("modPTV" + str(ptvs[2]))]
        # Create gradients
        # Gradient High-Mid
        patient.PatientModel.CreateRoi(Name=("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1])), Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [midmod.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Gradient High-Low
        patient.PatientModel.CreateRoi(Name=("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2])), Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2]))].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [lowmod.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Gradient Mid-Low
        patient.PatientModel.CreateRoi(Name=("Gradient" + str(ptvs[1]) + "-" + str(ptvs[2])), Color="Khaki", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[1]) + "-" + str(ptvs[2]))].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(midptv.Name + "+0.5cm"), lowmod.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2]))], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Gradient" + str(ptvs[1]) + "-" + str(ptvs[2]))].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Create optPTVs
        patient.PatientModel.CreateRoi(Name=("OPT" + midptv.Name), Color="0, 64, 0", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("OPT" + midptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [midmod.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1]))], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("OPT" + midptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("OPT" + lowptv.Name), Color="SteelBlue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("OPT" + lowptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [lowmod.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1])), ("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2]))], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("OPT" + lowptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Set ROI type for all modPTVs, optPTVs and Gradients to PTV/Target
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            n = name.replace(' ', '')
            if 'modPTV' in n:
                roi.set_roi_type(name, 'Ptv', 'Target')
            elif 'Gradient' in n:
                roi.set_roi_type(name, 'Ptv', 'Target')
            elif 'OPTPTV' in n:
                roi.set_roi_type(name, 'Ptv', 'Target')
        # Create RINGs
        patient.PatientModel.CreateRoi(Name=("Ring" + highptv.Name), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Ring" + highptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Ring" + highptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("Ring" + midptv.Name), Color="SlateBlue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Ring" + midptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(midptv.Name + "+0.8cm"), "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name, ("Ring" + highptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Ring" + midptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("Ring" + lowptv.Name), Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("Ring" + lowptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(lowptv.Name + "+0.8cm"), "BodyRS-5mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name, ("Ring" + highptv.Name), ("Ring" + midptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("Ring" + lowptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Create Tissus Sains
        patient.PatientModel.CreateRoi(Name=("TS " + highptv.Name), Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("TS " + highptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(highptv.Name + "+1.8cm"), "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), (midptv.Name + "+0.8cm"), (lowptv.Name + "+0.8cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("TS " + highptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("TS " + midptv.Name), Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("TS " + midptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [(midptv.Name + "+1.8cm"), "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), (midptv.Name + "+0.8cm"), (lowptv.Name + "+0.8cm"), ("TS " + highptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("TS " + midptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name="temp1", Color="Lime", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['temp1'].SetMarginExpression(SourceRoiName=(lowptv.Name + "+0.8cm"), MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2})
        patient.PatientModel.RegionsOfInterest['temp1'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("TS " + lowptv.Name), Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[("TS " + lowptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp1", "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), (midptv.Name + "+0.8cm"), (lowptv.Name + "+0.8cm"), ("TS " + highptv.Name), ("TS " + midptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest[("TS " + lowptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name="temp2", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['temp2'].SetMarginExpression(SourceRoiName=("TS " + lowptv.Name), MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 4, 'Posterior': 4, 'Right': 4, 'Left': 4})
        patient.PatientModel.RegionsOfInterest['temp2'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        patient.PatientModel.CreateRoi(Name=("TissusSains"), Color="Olive", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest["TissusSains"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp2", "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), (midptv.Name + "+0.8cm"), (lowptv.Name + "+0.8cm"), ("TS " + highptv.Name), ("TS " + midptv.Name), ("TS " + lowptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest["TissusSains"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
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
                patient.PatientModel.RegionsOfInterest[("OPT " + name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.8cm"), (midptv.Name + "+0.5cm"), (lowptv.Name + "+0.3cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest[("OPT " + name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # OPT CERVEAU, MOELLE, TRONC, et BLOC MOELLE
        if roi.roi_exists("CERVEAU"):
            patient.PatientModel.CreateRoi(Name=("OPT CERVEAU"), Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["OPT CERVEAU"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["OPT CERVEAU"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        if roi.roi_exists("MOELLE"):
            patient.PatientModel.CreateRoi(Name=("OPT MOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["OPT MOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["OPT MOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("OPT prvMOELLE"), Color="0, 128, 255", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["OPT prvMOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mmMOELLE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["OPT prvMOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        if roi.roi_exists("TR CEREBRAL"):
            patient.PatientModel.CreateRoi(Name=("OPT TRONC"), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["OPT TRONC"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["TR CEREBRAL"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["OPT TRONC"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("OPT prvTRONC"), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["OPT prvTRONC"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["OPT prvTRONC"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            if roi.roi_exists("MOELLE"):
                patient.PatientModel.CreateRoi(Name=("temp3"), Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
                patient.PatientModel.RegionsOfInterest["temp3"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["prv5mmMOELLE", "prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 5, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name, midptv.Name, lowptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest["temp3"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
                patient.PatientModel.CreateRoi(Name=("BLOC MOELLE"), Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
                patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp3", "BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["MOELLE", "prv5mmMOELLE", "TR CEREBRAL", "prv5mm TRONC"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Contract", 'Superior': 0, 'Inferior': 0, 'Anterior': 0.2, 'Posterior': 0, 'Right': 0.1, 'Left': 0.1})
                patient.PatientModel.RegionsOfInterest["BLOC MOELLE"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # MANDIBULE
        roi.create_expanded_ptv(ptv_name=highptv.Name, color="Yellow", margeptv=0.5, output_name=highptv.Name)
        if roi.roi_exists("MANDIBULE"):
            patient.PatientModel.CreateRoi(Name=("MAND ds " + highptv.Name + "+5mm"), Color="Maroon", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("MAND ds " + highptv.Name + "+5mm")].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MANDIBULE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.5cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("MAND ds " + highptv.Name + "+5mm")].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("MAND-PTVs"), Color="YellowGreen", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest["MAND-" + highptv.Name + "-5mm"].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["MANDIBULE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [(highptv.Name + "+0.5cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest["MAND-" + highptv.Name + "-5mm"].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        # Plexus Brachiaux
        if roi.roi_exists("PL BRACHIAL DRT"):
            patient.PatientModel.CreateRoi(Name=("PBD ds " + highptv.Name), Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBD ds " + highptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL DRT"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBD ds " + highptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("PBD ds " + midptv.Name), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBD ds " + midptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["PL BRACHIAL DRT", (midptv.Name + "+0.5cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("PBD ds " + highptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBD ds " + midptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
        if roi.roi_exists("PL BRACHIAL GCHE"):
            patient.PatientModel.CreateRoi(Name=("PBG ds " + highptv.Name), Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBG ds " + highptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PL BRACHIAL GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [highptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBG ds " + highptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
            patient.PatientModel.CreateRoi(Name=("PBG ds " + midptv.Name), Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest[("PBG ds " + midptv.Name)].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["PL BRACHIAL GCHE", (midptv.Name + "+0.5cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("PBG ds " + highptv.Name)], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest[("PBG ds " + midptv.Name)].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])

    # Erase temporary contours
    list = [highptv.Name + "+1.8cm", midptv.Name + "+1.8cm", lowptv.Name + "+1.8cm", highptv.Name + "+0.8cm", midptv.Name + "+0.8cm", lowptv.Name + "+0.8cm", highptv.Name + "+0.5cm", midptv.Name + "+0.5cm", lowptv.Name + "+0.3cm", "temp1", "temp2", "temp3"]
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
    plan = patient.AddNewPlan(PlanName="ORL", PlannedBy="", Comment="", ExaminationName="CT 1", AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset (several options depending on PTV levels)
    beamset = plan.AddNewBeamSet(Name="Trial 1", ExaminationName=lib.get_current_examination().Name, MachineName="Salle 6", NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="VMAT")
    beamset.AddDosePrescriptionToRoi(RoiName=("mod" + highptv.Name), DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=ptvs[0] * 100, RelativePrescriptionLevel=1)

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
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=120.0, plan=plan)

    # Add clinical goals and optimization objectives
    clinical_goals.smart_cg_orl(plan=plan)

    # Set Dose Color Table
    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = ptvs[0] * 100

    tengy = 10.0 / float(ptvs[0]) * 100
    twentygy = 20.0 / float(ptvs[0]) * 100
    fortyfivegy = 45.0 / float(ptvs[0]) * 100

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=tengy, r=255, g=128, b=64, alpha=128)
    eval.add_isodose_line_rgb(dose=twentygy, r=0, g=128, b=192, alpha=128)
    eval.add_isodose_line_rgb(dose=fortyfivegy, r=184, g=233, b=57, alpha=255)
    eval.add_isodose_line_rgb(dose=float(ptvs[2]) / float(ptvs[0]) * 100, r=0, g=0, b=255, alpha=255)  # Rx dose for lowest PTV level (blue)
    eval.add_isodose_line_rgb(dose=float(ptvs[1]) / float(ptvs[0]) * 100, r=0, g=160, b=0, alpha=255)  # Rx dose for mid-level PTV (green)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)  # Rx dose for highest PTV level (red)
    eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if points.Name.upper() not in ["ISO", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()

    msg += "Le script plan_poumon_sbrt a terminé.\n"
    msg += "Il faut faire Remove holes (on all slices) sur le contour BodyRS+Table avant d'optimiser.\n"
    # log_window.show_log_window(msg)

