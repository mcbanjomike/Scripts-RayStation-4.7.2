# -*- coding: utf-8 -*-
"""
This module contains any functions directly related to optimization of IMRT plans (step-and-shoot + VMAT).
"""
import sys
import os.path
import lib

import beams
#import launcher

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


def _add_objective(roi_name, obj_type, is_constraint=False, plan=None, plan_opt=0):
    """
    Private function used to add an optimization objective.

    Args:
        roi_name (str): the name of the ROI for which to add the optimization objective
        obj_type (str): the type of the optimization objective
        is_constraint (bool): whether or not the objective is a constraint
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
        plan_opt (int): index of the PlanOptimization to use - allows for the addition of objectives to beamsets other than the first
                            (note that this value can be obtained by subtracting 1 from beamset.Number)

    Returns:
        the RayStation objective object
    """
    if plan is None:
        plan = lib.get_current_plan()

    try:
        with CompositeAction('Add Optimization Function'):
            retval_1 = plan.PlanOptimizations[plan_opt].AddOptimizationFunction(FunctionType=obj_type, RoiName=roi_name, IsConstraint=is_constraint,
                                                                                RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
        logger.info('Objective of type %s for ROI "%s" added.', obj_type, roi_name)
    except SystemError as e:
        if str(e).startswith('No ROI named'):
            logger.warning('Warning: no ROI named "%s".  Skip adding objective.', roi_name)
            return None
        else:
            logger.exception(e)
            raise
    return retval_1


def add_mindose_objective(roi_name, dose, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a min dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    if plan is None:
        plan = lib.get_current_plan()

    r = _add_objective(roi_name, 'MinDose', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_maxdose_objective(roi_name, dose, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a max dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'MaxDose', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_uniformdose_objective(roi_name, dose, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a uniform dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'UniformDose', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_mindvh_objective(roi_name, dose, percent_volume, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a min DVH dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        percent_volume (float): the relative volume value in %
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'MinDvh', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        r.DoseFunctionParameters.PercentVolume = percent_volume
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_maxdvh_objective(roi_name, dose, percent_volume, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a max DVH dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        percent_volume (float): the relative volume value in %
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'MaxDvh', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        r.DoseFunctionParameters.PercentVolume = percent_volume
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_dosefalloff_objective(roi_name, high_dose, low_dose, distance, weight=1.0, plan=None, plan_opt=0, adapt_dose_level=False):
    """
    Adds a dose fall-off objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        high_dose (float): the high dose value in cGy
        low_dose (float): the low dose value in cGy
        distance (float): the distance parameter in cm
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'DoseFallOff', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.HighDoseLevel = high_dose
        r.DoseFunctionParameters.LowDoseLevel = low_dose
        r.DoseFunctionParameters.LowDoseDistance = distance
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight
        if adapt_dose_level:
            r.DoseFunctionParameters.AdaptToTargetDoseLevels = True


def add_mineud_objective(roi_name, dose, param_a=1.0, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a min EUD dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        param_a (float, optional): the *a* parameter (default 1.0)
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'MinEud', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if param_a != 1.0:
            r.DoseFunctionParameters.EudParameterA = param_a
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_maxeud_objective(roi_name, dose, param_a=1.0, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a max EUD dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        param_a (float, optional): the *a* parameter (default 1.0)
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'MaxEud', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if param_a != 1.0:
            r.DoseFunctionParameters.EudParameterA = param_a
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def add_targeteud_objective(roi_name, dose, param_a=1.0, weight=1.0, plan=None, plan_opt=0):
    """
    Adds a target EUD dose objective to a ROI.

    Args:
        roi_name (str): the name of the ROI
        dose (float): the dose value in cGy
        param_a (float, optional): the *a* parameter (default 1.0)
        weight (float, optional): the weight of the objective (default 1.0)
        plan (RayStation plan object, optional): the patient plan.  If not specified, will get the currently selected one.
    """
    r = _add_objective(roi_name, 'TargetEud', plan=plan, plan_opt=plan_opt)
    if r:
        r.DoseFunctionParameters.DoseLevel = dose
        if param_a != 1.0:
            r.DoseFunctionParameters.EudParameterA = param_a
        if weight != 1.0:
            r.DoseFunctionParameters.Weight = weight


def set_optimization_parameters(fluence_iterations=60, max_iterations=100, optimality_tolerance=1E-09, compute_intermediate_dose=True, compute_final_dose=True, plan=None, beamset=None):
    """
    Sets the optimization parameters for inverse planning.

    **RESETS OPTIMIZATION IF ALREADY STARTED**

    Args:
        fluence_iterations (int, optional): the number of fluence iterations (default: 60)
        max_iterations (int, optional): the maximum number of iterations (default: 100)
        optimality_tolerance (float, optional): the tolerance of the optimizer such that it has reached an optimal solution with respect to the objective value (default: 1E-9)
        compute_intermediate_dose (bool, optional): whether of not to compute clinical dose after completing fluence iterations.  This dose is taken into account in the following optimization iterations (default: True).
        compute_final_dose (bool, optional): whether or not to compute clinical dose after optimization is done (default: True)
        plan (RS Object, optional): the RayStation plan object (if none specified, will get current)
        beamset (str or int, optional): the name of the beamset to modify.  If not used, all beamsets in the plan are affected.  An int can be provided as well (1 for first beamset, 2 for second beamset, etc.).
    """
    if plan is None:
        plan = lib.get_current_plan()

    if fluence_iterations > max_iterations:
        lib.error('Fluence iterations cannot be greater than the maximum number of iterations.')

    if beamset is None:
        logger.info('No beamset specified.  All beamsets will be modified.')
        l = 0
        for po in plan.PlanOptimizations:
            l += 1
        indices = range(l)
    elif isinstance(beamset, str):
        # figure out what index of PlanOptimizations is this beamset
        i = 0
        for po in plan.PlanOptimizations:
            for obs in po.OptimizedBeamSets:
                if beamset.startswith(obs.DicomPlanLabel):
                    break
            break
            i += 1

        indices = [i]
    elif isinstance(beamset, int):
        try:
            indices = [beamset - 1]
            test = plan.PlanOptimizations[beamset - 1]
        except IndexError as e:
            lib.error('The index provided for the beamset argument was out of range. Specify the beamset number in the plan (i.e. 1, 2, ...) or provide the beamset name as a string.')

    # TODO Ask confirmation with yes/no dialog before proceeding.
    try:
        for i in indices:
            #if not plan.PlanOptimizations[i].ProgressOfOptimization is None:
                # Reset optimization because this changes parameters that RS doesn't
                # allow changing without resetting.
                #plan.PlanOptimizations[i].ResetOptimization()
                #logger.info('Optimization was reset.')

            logger.info('PlanOptimizations[%s] selected.', i)

            op = plan.PlanOptimizations[i].OptimizationParameters
            op.DoseCalculation.IterationsInPreparationsPhase = fluence_iterations
            logger.info('Fluence iterations set to %s.', fluence_iterations)

            op.Algorithm.MaxNumberOfIterations = max_iterations
            logger.info('Max iterations set to %s.', max_iterations)

            op.Algorithm.OptimalityTolerance = optimality_tolerance
            logger.info('Optimality tolerance set to %s.', optimality_tolerance)

            op.DoseCalculation.ComputeIntermediateDose = compute_intermediate_dose
            logger.info('Compute intermediate dose set to %s.', compute_intermediate_dose)

            op.DoseCalculation.ComputeFinalDose = compute_final_dose
            logger.info('Compute final dose set to %s.', compute_final_dose)
    except Exception as e:
        logger.exception(e)
        raise


def set_imrt_conversion_parameters():
    """
    TODO: Implement.
    """
    raise NotImplementedError


def set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1, constrain_leaf_motion=True, arc_gantry_spacing=4, max_arc_delivery_time=350.0, plan=None, beamset=None):
    """
    Sets the VMAT conversion parameters.

    **RESETS OPTIMIZATION IF ALREADY STARTED**

    Args:
        max_leaf_travel_per_degree (float, optional): maximum distance a leaf can move in cm per degree of gantry movement (default: 0.1 cm/degree)
        constrain_leaf_motion (bool, optional): whether or not to impose the *max_leaf_travel_per_degree* constraint (default: True)
        arc_gantry_spacing (int, optional): the spacing in degrees between control points of the arc (default: 4 degrees)
        max_arc_delivery_time (float, optional): the maximum are delivery time in seconds (defautl 350.0 s)
        plan (RS object, optional): the RayStation plan object (if none specified, will get current)
        beamset (str or int, optional): the name of the beamset to modify.  If not used, all beamsets in the plan are affected.  An int can be provided as well (1 for first beamset, 2 for second beamset, etc.).
    """

    if plan is None:
        plan = lib.get_current_plan()

    if beamset is None:
        logger.info('No beamset specified.  All beamsets will be modified.')
        l = 0
        for po in plan.PlanOptimizations:
            l += 1
        indices = range(l)
    elif isinstance(beamset, str):
        # figure out what index of PlanOptimizations is this beamset
        i = 0
        for po in plan.PlanOptimizations:
            for obs in po.OptimizedBeamSets:
                if beamset.startswith(obs.DicomPlanLabel):
                    break
            break
            i += 1

        indices = [i]
    elif isinstance(beamset, int):
        try:
            indices = [beamset - 1]
            test = plan.PlanOptimizations[beamset - 1]
        except IndexError as e:
            lib.error('The index provided for the beamset argument was out of range. Specify the beamset number in the plan (i.e. 1, 2, ...) or provide the beamset name as a string.')

    if arc_gantry_spacing not in [2, 3, 4]:
        lib.error('The arc gantry spacing must be of 2, 3 or 4 degrees.')

    try:
        for i in indices:
            if plan.PlanOptimizations[i].ProgressOfOptimization is not None:
                # Reset optimization because this changes parameters that RS doesn't
                # allow changing without resetting.
                plan.PlanOptimizations[i].ResetOptimization()
                logger.info('Optimization reset.')

            po = plan.PlanOptimizations[i]

            logger.info('PlanOptimizations[%s] selected.', i)

            po.OptimizationParameters.SegmentConversion.ArcConversionProperties.MaxLeafTravelDistancePerDegree = max_leaf_travel_per_degree
            logger.info('Max leaf travel per degree set to %s cm/deg.', max_leaf_travel_per_degree)

            po.OptimizationParameters.SegmentConversion.ArcConversionProperties.UseMaxLeafTravelDistancePerDegree = constrain_leaf_motion
            logger.info('Constrain leaf motion set to %s.', constrain_leaf_motion)

            for ts in po.OptimizationParameters.TreatmentSetupSettings:
                for bs in ts.BeamSettings:
                    bs.ArcConversionPropertiesPerBeam.FinalArcGantrySpacing = arc_gantry_spacing
                    logger.info('Arc gantry spacing set to %s degrees for arc "%s".', arc_gantry_spacing, bs.ForBeam.Name)

                    bs.ArcConversionPropertiesPerBeam.MaxArcDeliveryTime = max_arc_delivery_time
                    logger.info('Max arc delivery time set to %s s for arc "%s".', max_arc_delivery_time, bs.ForBeam.Name)
    except Exception as e:
        logger.exception(e)
        raise


def double_optimization(plan=None, beamset=None):
    # Function which runs two consecutive optimizations.
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()

    # Beamsets are numbered starting at 1 whereas Plan Optimizations are numbered starting at 0.
    # Determine what the number of the selected beamset is, then subtract one to locate the associated Plan Optimization.
    plan.PlanOptimizations[beamset.Number - 1].RunOptimization()
    plan.PlanOptimizations[beamset.Number - 1].RunOptimization()

    
def triple_optimization(plan=None, beamset=None):
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()
       
    opt = plan.PlanOptimizations[beamset.Number - 1]
    set_optimization_parameters(plan=plan,fluence_iterations=30, max_iterations=90, compute_intermediate_dose=False)
    opt.RunOptimization()
    set_optimization_parameters(plan=plan,fluence_iterations=30, max_iterations=30, compute_intermediate_dose=False)
    opt.RunOptimization()
    opt.RunOptimization()    


def optimization_90_30(plan=None, beamset=None):
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()
       
    opt = plan.PlanOptimizations[beamset.Number - 1]
    set_optimization_parameters(plan=plan,fluence_iterations=30, max_iterations=90, compute_intermediate_dose=False)
    opt.RunOptimization()
    set_optimization_parameters(plan=plan,fluence_iterations=30, max_iterations=30, compute_intermediate_dose=False)
    opt.RunOptimization()  
    
    
def double_opt_save(plan=None, beamset=None):
    # Function which runs two consecutive optimizations and saves the plan afterwards (NB this removes the ability to undo the optimizations).
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()

    # Beamset.Number starts at 1 whereas Plan Optimizations are numbered starting at 0.
    # Determine what the number of the selected beamset is, then subtract one to locate the associated Plan Optimization.
    plan.PlanOptimizations[beamset.Number - 1].RunOptimization()
    plan.PlanOptimizations[beamset.Number - 1].RunOptimization()
    patient.Save()


def double_opt_extra():
    
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
    plan.PlanOptimizations[0].RunOptimization()
    plan.PlanOptimizations[0].RunOptimization()
    fit_objectives_orl(plan, beamset)
    plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 29
    plan.PlanOptimizations[0].RunOptimization()  
    
    
def compute_eud(dose, roi_name, parameter_a):
# Taken from RayStation 4.7.2 Scripting Guideline page 23

    # Get the dose values from the dose distribution
    dose_values = [d for d in dose.DoseValues.DoseData]
    # Get the dose grid representation of the ROI
    dgr = dose.GetDoseGridRoi(RoiName=roi_name)
    # Get indices and relative volumes
    indices = dgr.RoiVolumeDistribution.VoxelIndices
    relative_volumes = dgr.RoiVolumeDistribution.RelativeVolumes
    dose_sum = 0
    # Scale factor to prevent overflow with large parameter_a values
    scalefactor = 1 / max(dose_values)
    # Sum the dose values and scale with scalefactor and parameter_a
    for i, v in zip(indices, relative_volumes):
        d = dose_values[i] * scalefactor
        dose_sum += v * (d ** parameter_a)
    return 1 / scalefactor * dose_sum ** (1 / float(parameter_a))


def fit_objectives(plan=None, beamset=None):
    # Function which adjusts DVH and EUD values in objectives to reflect obtained values.
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()

    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue

        if f_type == "MaxDvh":
            roi_name = objective.ForRegionOfInterest.Name
            dose_level = objective.DoseFunctionParameters.DoseLevel
            target_vol = objective.DoseFunctionParameters.PercentVolume
            obtained_vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=roi_name, DoseValues=[dose_level])
            if obtained_vol[0] >= 0.02:
                objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0] * 100 - 2)

        elif f_type == "MaxEud":
            roi_name = objective.ForRegionOfInterest.Name
            dose_level = objective.DoseFunctionParameters.DoseLevel
            a = objective.DoseFunctionParameters.EudParameterA
            obtained_eud = compute_eud(plan.TreatmentCourse.TotalDose, roi_name, a)
            if obtained_eud > 200:
                objective.DoseFunctionParameters.DoseLevel = int(obtained_eud - 200)

   
def fit_objectives_orl(plan=None, beamset=None):
    # Function which adjusts DVH and EUD values in objectives to reflect obtained values.
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()
    
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
    
        try:
            f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
        except:
            continue
        
        roi_name = objective.ForRegionOfInterest.Name
        if roi_name in ['BLOC MOELLE','MOELLE','prv5mmMOELLE']:
            continue
        else:
            if f_type == "MaxDvh":
                dose_level = objective.DoseFunctionParameters.DoseLevel
                obtained_vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=roi_name, DoseValues=[dose_level])
                if obtained_vol[0] >= 0.02:
                    objective.DoseFunctionParameters.PercentVolume = int(obtained_vol[0] * 90)
                if obtained_vol[0] < 0.02:
                    objective.DoseFunctionParameters.DoseLevel = int(dose_level*0.9)

            elif f_type == "MaxEud":
                dose_level = objective.DoseFunctionParameters.DoseLevel
                a = objective.DoseFunctionParameters.EudParameterA
                obtained_eud = compute_eud(plan.TreatmentCourse.TotalDose, roi_name, a)
                if obtained_eud > 100:
                    objective.DoseFunctionParameters.DoseLevel = round(obtained_eud*0.99,-1)

            elif f_type == "MaxDose":
                dose_level = objective.DoseFunctionParameters.DoseLevel
                vol_roi=patient.PatientModel.StructureSets['CT 1'].RoiGeometries[roi_name].GetRoiVolume()
                if vol_roi >= 0.1:
                    vol_cc=0.1/vol_roi
                    max_dose_obtenue = plan.TreatmentCourse.TotalDose.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=[vol_cc])
                else:
                    max_dose_obtenue = plan.TreatmentCourse.TotalDose.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=[vol_roi])
                if max_dose_obtenue[0] < (dose_level/1.05) and max_dose_obtenue[0] > 500:
                    objective.DoseFunctionParameters.DoseLevel = int(max_dose_obtenue[0]*1.05)
                elif max_dose_obtenue[0] < (dose_level/1.05) and max_dose_obtenue[0] <= 500:
                    objective.DoseFunctionParameters.DoseLevel = 500    
    
    
def essai_autre_technique():
#pour faire un plan qui essai une autre technique (si VMAT essai IMRT et si IMRT essai VMAT)
#mais en gardant les meme objectifs d'optimisations et clinical goals
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    
    #va chercher l'info du plan original
    plan_name = plan.Name
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    ptv = beamset.Prescription.DosePrescriptions[0].OnStructure.Name
    rx_dose = beamset.Prescription.DosePrescriptions[0].DoseValue
    actual_technique = beamset.DeliveryTechnique
    patient_position = beamset.PatientPosition
    planner_name = plan.PlannedBy
    
    #crée un plan VMAT si le plan est IMRT
    if actual_technique == 'SMLC':
        new_plan = patient.AddNewPlan(PlanName= plan_name+' VMAT', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        new_plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})
        new_beamset = new_plan.AddNewBeamSet(Name='VMAT', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,Modality="Photons", TreatmentTechnique='VMAT', PatientPosition=patient_position, NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='VMAT')
        new_beamset.AddDosePrescriptionToRoi(RoiName=ptv, DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)
        new_beams = beams.add_beams_brain_stereo(beamset=new_beamset)
        set_optimization_parameters(plan=new_plan)
        set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=new_plan)
        
    #crée un plan IMRT si le plan est VMAT
    else:
        new_plan = patient.AddNewPlan(PlanName=plan_name+' IMRT', PlannedBy=planner_name, Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
        new_plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})
        new_beamset = new_plan.AddNewBeamSet(Name='IMRT', ExaminationName=exam.Name, MachineName='BeamMod', NominalEnergy=None,Modality="Photons", TreatmentTechnique='SMLC', PatientPosition=patient_position, NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment='VMAT')
        new_beamset.AddDosePrescriptionToRoi(RoiName=ptv, DoseVolume=99, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)
        new_beams = beams.add_beams_brain_static(beamset=new_beamset)
        new_plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-10
        new_plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100
        new_plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 60
        new_plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True          
        new_plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction = 20        
        new_plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinLeafEndSeparation = 1
        new_plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs = 3
        new_plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MinSegmentArea = 2
        new_plan.PlanOptimizations[0].OptimizationParameters.SegmentConversion.MaxNumberOfSegments = 40
    
    #lit les objectifs d'optimisation du plan original et en crée des pareils dans le nouveau plan
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        
        nom_roi = objective.ForRegionOfInterest.Name
        nweight = objective.DoseFunctionParameters.Weight
        
        if hasattr(objective.DoseFunctionParameters, 'FunctionType'): #les critères dose fall off n'ont pas de FunctionType, les autres en ont tous un
            type = objective.DoseFunctionParameters.FunctionType

            if type in ('MinDose','MaxDose','MinDvh','MaxDvh','UniformDose') :
                pourcent = objective.DoseFunctionParameters.PercentVolume
                dose_level = objective.DoseFunctionParameters.DoseLevel
                new_objective = new_plan.PlanOptimizations[new_beamset.Number-1].AddOptimizationFunction(FunctionType=type, RoiName=nom_roi, IsConstraint=False,RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
                new_objective.DoseFunctionParameters.DoseLevel = dose_level
                new_objective.DoseFunctionParameters.Weight = nweight
                new_objective.DoseFunctionParameters.PercentVolume = pourcent

            if type in ('MinEud','MaxEud'):
                dose_level = objective.DoseFunctionParameters.DoseLevel
                parametre_a = objective.DoseFunctionParameters.EudParameterA
                new_objective = new_plan.PlanOptimizations[new_beamset.Number-1].AddOptimizationFunction(FunctionType=type, RoiName=nom_roi, IsConstraint=False,RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
                new_objective.DoseFunctionParameters.DoseLevel = dose_level
                new_objective.DoseFunctionParameters.Weight = nweight
                new_objective.DoseFunctionParameters.EudParameterA = parametre_a
        
        else: # si pas de FunctionType on suppose que c'est un dose fall off
            high_dose_level = objective.DoseFunctionParameters.HighDoseLevel
            low_dose_level = objective.DoseFunctionParameters.LowDoseLevel
            low_dose_distance = objective.DoseFunctionParameters.LowDoseDistance
            
            new_objective = new_plan.PlanOptimizations[new_beamset.Number-1].AddOptimizationFunction(FunctionType='DoseFallOff', RoiName=nom_roi, IsConstraint=False,RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None)
            new_objective.DoseFunctionParameters.HighDoseLevel = high_dose_level
            new_objective.DoseFunctionParameters.LowDoseLevel = low_dose_level
            new_objective.DoseFunctionParameters.LowDoseDistance = low_dose_distance
            new_objective.DoseFunctionParameters.Weight = nweight


        
    for goal in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
    
        nom_roi = goal.ForRegionOfInterest.Name
        goal_criteria = goal.PlanningGoal.GoalCriteria
        goal_type = goal.PlanningGoal.Type
        acceptance_level = goal.PlanningGoal.AcceptanceLevel
        parameter_value = goal.PlanningGoal.ParameterValue
        
        new_goal = new_plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=nom_roi, GoalCriteria=goal_criteria, GoalType=goal_type, AcceptanceLevel=acceptance_level, ParameterValue=parameter_value, IsComparativeGoal=False)

    
    # Optimize plan twice
    new_plan.PlanOptimizations[new_beamset.Number-1].RunOptimization()
    new_plan.PlanOptimizations[new_beamset.Number-1].RunOptimization()
    
    #import launcher
    #launcher.debug_window('Optimisation du plan '+new_plan.Name+' terminée')   
    
    
def copy_clinical_goals(old_plan = None,new_plan = None):
    for goal in old_plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
    
        roi_name = goal.ForRegionOfInterest.Name
        goal_criteria = goal.PlanningGoal.GoalCriteria
        goal_type = goal.PlanningGoal.Type
        acceptance_level = goal.PlanningGoal.AcceptanceLevel
        parameter_value = goal.PlanningGoal.ParameterValue
        
        new_plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi_name, GoalCriteria=goal_criteria, GoalType=goal_type, AcceptanceLevel=acceptance_level, ParameterValue=parameter_value, IsComparativeGoal=False)


def erase_objectives(plan,beamset):
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass