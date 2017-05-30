# -*- coding: utf-8 -*-
"""
This module contains any functions directly related to plan evaluation.
"""
import sys
import os.path
import lib
import hmrlib.roi as roi

import logging
from HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

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


def add_clinical_goal(RoiName, GoalValue, GoalCriteria, GoalType, Volume, IsComparativeGoal=False, plan=None):
    """
    Adds a clinical goal to the current plan.

    Note that the syntax used depends on the version of RayStation running.

    Args:
        RoiName (str): the name of the ROI for which to add the goal
        GoalValue (float): the dose value of the goal in cGy
        GoalCriteria (str): one of *AtLeast* or *AtMost*
        GoalType (str): one of the clinical goal types supported by RayStation, e.g. *DoseAtAbsoluteVolume*, *AbsoluteVolumeAtDose*, *DoseAtVolume*, etc.
        Volume (float): the volume value in cc or in %, depending on the chosen goal type.

    """

    if lib.check_version(4.7):
        # Convert old-style arguments into args compatible with RayStation 4.7.2
        if GoalType == 'DoseAtVolume':
            AcceptanceLevel = GoalValue
            ParameterValue = Volume / 100.0
        elif GoalType == 'DoseAtAbsoluteVolume':
            AcceptanceLevel = GoalValue
            ParameterValue = Volume
        if GoalType == 'VolumeAtDose':
            ParameterValue = GoalValue
            AcceptanceLevel = Volume / 100.0
        elif GoalType == 'AbsoluteVolumeAtDose':
            ParameterValue = GoalValue
            AcceptanceLevel = Volume
        elif GoalType == 'AverageDose':
            ParameterValue = Volume
            AcceptanceLevel = GoalValue

        if plan is None:
            plan = lib.get_current_plan()

        if roi.roi_exists(RoiName):
            try:  # In case an identical clinical goal already exists
                plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=RoiName, GoalCriteria=GoalCriteria, GoalType=GoalType, AcceptanceLevel=AcceptanceLevel,
                                                                     ParameterValue=ParameterValue, IsComparativeGoal=IsComparativeGoal)
            except:
                logger.warning('Identical clinical goal already exists')
    else:  # RayStation 4.0
        if 'Absolute' in GoalType:
            AbsoluteGoalVolume = Volume
            GoalVolume = 0
        else:
            AbsoluteGoalVolume = 0
            GoalVolume = Volume

        if plan is None:
            plan = lib.get_current_plan()

        try:
            plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=RoiName, GoalValue=GoalValue, GoalCriteria=GoalCriteria, GoalType=GoalType,
                                                                 GoalVolume=GoalVolume, AbsoluteGoalVolume=AbsoluteGoalVolume)
            logger.info('Clinical goal of type %s (%s) added for ROI "%s" with goal value %s and volume %s', GoalType, GoalCriteria, RoiName, str(GoalValue / 100.0) + ' Gy', (str(AbsoluteGoalVolume) + ' cc' if 'Absolute' in GoalType else str(GoalVolume) + ' %'))
        except SystemError as e:
            if str(e) == 'The specified ROI does not exist':
                logger.warning('Warning: no ROI named "%s".  Skip adding clinical goal.', RoiName)
            elif str(e) == 'An identical clinical goal already exists.':
                logger.warning('Clinical goal of type %s (%s) for ROI "%s" with goal value %s and volume %s: an identical clinical goal already exists. Skipping.', GoalType, GoalCriteria, RoiName, str(GoalValue / 100.0) + ' Gy', (str(AbsoluteGoalVolume) + ' cc' if 'Absolute' in GoalType else str(GoalVolume) + ' %'))
            else:
                logger.exception(e)
                raise


def _add_isodose_line(dose, color):
    """
        Private method.

        Args:
            dose (float) : the dose level of the isodose line to add
            color (.NET System.Drawing.Color object): the color of the isodose line
    """
    patient = lib.get_current_patient()

    try:
        temp = patient.CaseSettings.DoseColorMap.ColorTable
        temp.Add(float(dose), color)
        patient.CaseSettings.DoseColorMap.ColorTable = temp
    except Exception as e:
        logger.exception(e)
        raise


def add_isodose_line_by_name(dose, color_name):
    """
        Adds an isodose line with a named color (e.g. "SlateBlue" or "Tomato" or "YellowGreen", etc.).

        Args:
            dose (float) : the dose level of the isodose line to add
            color_name (str) : the name of the color of the isodose line.  Taken from KnownColors enumeration in .NET Framework 4 (see this `URL <https://msdn.microsoft.com/en-us/library/system.drawing.knowncolor(v=vs.100).aspx>`_).
    """
    try:
        import clr
        clr.AddReference('System.Drawing')
        from System import Drawing

        # Create System.Drawing.Color instance
        color = Drawing.Color().FromName(color_name)
        _add_isodose_line(dose, color)
    except Exception as e:
        logger.exception(e)
        raise


def add_isodose_line_rgb(dose, r, g, b, alpha=255):
    """
        Adds an isodose line with (alpha) R, G, B values from 0 to 255.

        Args:
            dose (float) : the dose level of the isodose line to add
            r (int) : the 8-bit red value from 0 to 255
            g (int) : the 8-bit green value from 0 to 255
            b (int) : the 8-bit blue value from 0 to 255
            alpha (int, optinal) : the 8-bit alpha value from 0 to 255 (default 255)
    """
    try:
        import clr
        clr.AddReference('System.Drawing')
        from System import Drawing

        # Create System.Drawing.Color instance
        color = Drawing.Color().FromArgb(alpha, r, g, b)
        _add_isodose_line(dose, color)
    except Exception as e:
        logger.exception(e)
        raise


def remove_isodose_line(dose):
    """
        Removes an isodose line.

        Args:
            dose (float) : the dose level of the isodone line to remove
    """
    patient = lib.get_current_patient()

    try:
        temp = patient.CaseSettings.DoseColorMap.ColorTable
        temp.Remove(float(dose))
        patient.CaseSettings.DoseColorMap.ColorTable = temp
    except Exception as e:
        logger.exception(e)
        raise


def remove_all_isodose_lines():
    """
        Removes all isodose lines.
    """
    patient = lib.get_current_patient()

    try:
        temp = patient.CaseSettings.DoseColorMap.ColorTable
        temp.Clear()

        patient.CaseSettings.DoseColorMap.ColorTable = temp
    except Exception as e:
        logger.exception(e)
        raise


def calculate_cihi(ptv_name,isodose_name,rx_dose):
    
    patient = lib.get_current_patient()    
    beamset = lib.get_current_beamset()
    exam = lib.get_current_examination()
    
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
    isodose_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[isodose_name].GetRoiVolume()
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    cirtog = isodose_vol / ptv_vol
    
    try:
        body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['BodyRS'].GetRoiVolume()
        max_dose = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'BodyRS',RelativeVolumes = [0.1/body_vol])
        hi = max_dose[0] / (rx_dose/nb_fx*100)
    except:
        max_dose = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_name,RelativeVolumes = [0.1/ptv_vol])
        hi = max_dose[0] / (rx_dose/nb_fx*100)
        
    ptv_couvert = roi.get_intersecting_volume(ptv_name,isodose_name,exam)
    cipaddick = (ptv_couvert*ptv_couvert) / (ptv_vol*isodose_vol)
    
    return cirtog,hi,cipaddick
        
# def set_dose_color_map(map, reference_type='RelativeValue', reference_value=100, display_type='Absolute'):
#     """
#         Sets a new dose map for the diplay of isodose lines.

#         Args:
#             map (?): some way to specify the whole color map with multiple levels
#             reference_type (str, optional): either *RelativeValue* or *RelativePrescription*.
#             reference_value (str, optional): the dose reference value.
#             display_type (str, optional): either 'Absolute' or 'Relative'.

#         TODO: implementation and documentation.
#     """
#     raise NotImplementedError
