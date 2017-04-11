
def create_prostate_plan_A1_old():
    """
    Voir :py:mod:`plan_prostate_A1`.
    """
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    # Create BodyRS+Table, erase Body+table from Pinnacle, rename BODY to BODY Pinnacle
    roi.generate_BodyRS_plus_Table()

    # Clean Contrast ROI outside of body
    if roi.roi_exists("CONTRASTE"):
        retval_1 = patient.PatientModel.CreateRoi(Name="Contraste Mod", Color="Yellow", Type="ContrastAgent", TissueName=None, RoiMaterial=None)
        retval_1.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
            "CONTRASTE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_1.UpdateDerivedGeometry(Examination=examination)

    # Remove material override from ROI CONTRASTE
    if roi.roi_exists("CONTRASTE"):
        patient.PatientModel.RegionsOfInterest['CONTRASTE'].SetRoiMaterial(Material=None)

    # Create PTV A1
    # Case 1. Is PTV 37.5 exists, create a copy called PTV A1
    # Case 2. If PTV A1 exists already, it will be used
    # Case 3. If neither PTV 37.5 nor PTV A1 exists, the script will combine PTV 1cm and PTV VS into a new contour called PTV A1
    if roi.roi_exists("PTV 37.5"):
        patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['PTV A1'].SetMarginExpression(SourceRoiName="PTV 37.5", MarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['PTV A1'].UpdateDerivedGeometry(Examination=patient.Examinations['CT 1'])
    # Also, if PTV A1 already exists, change ROI type to "PTV"
    if roi.roi_exists("PTV A1"):
        patient.PatientModel.RegionsOfInterest["PTV A1"].Type = "PTV"
        patient.PatientModel.RegionsOfInterest["PTV A1"].OrganData.OrganType = "Target"
    if not roi.roi_exists("PTV A1"):
        if roi.roi_exists("PTV 1cm"):
            retval_2 = patient.PatientModel.CreateRoi(Name="PTV A1", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
            retval_2.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                "PTV VS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            retval_2.UpdateDerivedGeometry(Examination=examination)
        else:
            logger.warning('Neither PTV A1 nor PTV 1cm was found. Unable to create PTV A1.')

    # Create PTV A2 (copy of PTV 1cm)
    if roi.roi_exists("PTV 1cm"):
        retval_3 = patient.PatientModel.CreateRoi(Name="PTV A2", Color="Lime", Type="Ptv", TissueName=None, RoiMaterial=None)
        retval_3.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV 1cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        retval_3.UpdateDerivedGeometry(Examination=examination)
    else:
        logger.warning('PTV 1cm not found. Unable to create PTV A2.')

    # Create RECTUM ds PTV A1
    retval_6 = patient.PatientModel.CreateRoi(Name="RECTUM ds PTV A1", Color="Blue", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_6.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV A1"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  "RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_6.UpdateDerivedGeometry(Examination=examination)

    # Create RECTUM ds PTV A2
    retval_7 = patient.PatientModel.CreateRoi(Name="RECTUM ds PTV A2", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
    retval_7.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["PTV A2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  "RECTUM"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_7.UpdateDerivedGeometry(Examination=examination)

    # Create WALL RECTUM
    retval_8 = patient.PatientModel.CreateRoi(Name="WALL RECTUM", Color="Tomato", Type="Organ", TissueName=None, RoiMaterial=None)
    retval_8.SetWallExpression(SourceRoiName="RECTUM", OutwardDistance=0.2, InwardDistance=0.2)
    retval_8.UpdateDerivedGeometry(Examination=examination)

    # Rename isocenter
    if poi.poi_exists("REF SCAN"):
        patient.PatientModel.PointsOfInterest["REF SCAN"].Name = "ISO SCAN"
    elif poi.poi_exists("ISO PT PRESC"):
        patient.PatientModel.PointsOfInterest["ISO PT PRESC"].Name = "ISO SCAN"
    else:
        logger.warning('REF SCAN and ISO PT PRESC not found. Verify the coordinates of the beam isocenter and the localization point.')

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="A1 seul", PlannedBy="", Comment="", ExaminationName=lib.get_current_examination().Name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    if patient.Examinations[0].PatientPosition == "HFS":
        beamset = plan.AddNewBeamSet(Name="A1", ExaminationName=lib.get_current_examination().Name, MachineName="Salle 11", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=40, CreateSetupBeams=True, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName="PTV A1", DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=7600, RelativePrescriptionLevel=1)
    else:
        beamset = plan.AddNewBeamSet(Name="A1", ExaminationName=lib.get_current_examination().Name, MachineName="Salle 11", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstProne", NumberOfFractions=40, CreateSetupBeams=True, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName="PTV A1", DoseVolume=99.5, PrescriptionType="DoseAtVolume", DoseValue=7600, RelativePrescriptionLevel=1)

    # If PTV 37.5 exists, change number of fractions to have 2.5 Gy/fx
    if roi.roi_exists("PTV 37.5"):
        plan.BeamSets[0].FractionationPattern.NumberOfFractions = 32
        logger.warning('PTV 37.5 found, changing dose to 2.5Gy per fraction.')

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
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=150.0, plan=plan)

    # Add optimization objectives
    optimization_objectives.add_opt_obj_prostate_A1(patient_plan=plan)

    # Add clinical goals
    clinical_goals.add_cg_prostate_A1(patient_plan=plan)

    # Assign Point Types
    poi.auto_assign_poi_types()

    # Set Dose Color Table
    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = 8000
    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
    eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=75, r=0, g=255, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=87.7, r=255, g=192, b=0, alpha=255)  # pour plan split
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=105, r=255, g=255, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=108.75, r=255, g=0, b=255, alpha=255)

    logger.warning("Le script plan_prostate_A1 a terminé.\n")
    logger.warning("N'oubliez pas d'ajoutez un override de matériel sur le contour Contraste Mod au besoin.\n")
    logger.warning("Il faut faire Remove holes (on all slices) sur le contour BodyRS+Table avant d'optimiser.\n")
    """
    

def finaliser_plan_prostate_old():
    """
    Voir :py:mod:`finaliser_plan_prostate`.
    """
    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    #patient.TreatmentPlans['A1 seul'].BeamSets['A1'].CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 1, 'y': -3, 'z': 2 })
    
    
    
    # Scale clinical goals for plans at 66, 44 or 37.5 Gy
    scaledose = 80
    if roi.roi_exists("62.7"):  # Pour les plans 66Gy/33fx
        scaledose = 66
    if roi.roi_exists("41.8"):  # Pour les plans 44Gy/22fx
        scaledose = 44
    if roi.roi_exists("35.63"):  # Pour les plans 37.5Gy/15fx
        scaledose = 37.5

    if not scaledose == 80:
        for cg in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
            old_goal = cg.PlanningGoal.GoalValue
            cg.PlanningGoal.GoalValue = old_goal * scaledose / 80

    # Append * to ROI names for SuperBridge transfer
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["PTV A1", "PTV A2", "RECTUM", "VESSIE", "INTESTINS", "RECTO-SIGMOIDE", "PROSTATE"]:
            rois.Name += "*"
        elif rois.Name in ["51.3", "24.7", "22.8", "62.7", "41.8", "35.63", "20.9"]:
            patient.PatientModel.RegionsOfInterest[rois.Name].Name = ("ISO 95%% %sGy*" % rois.Name)

    # All operations are completed for Beam Set A1 first, to prevent problems in the event that A2 does not exist
    # rename Beam Set A1
    plan.BeamSets[0].DicomPlanLabel = "A1"

    # Ajouter commentaire pour transfert SuperBridge
    plan.BeamSets[0].Prescription.Description = "VMAT"

    # create PT PRESC A1
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC A1', color="Red")

    # move prescription point to 2Gy/fraction, except for 37.5Gy/15 plans
    if roi.roi_exists("ISO 95% 35.63Gy*"):
        poi.place_prescription_point(target_fraction_dose=250, ptv_name="PTV A1*", poi_name="PT PRESC A1", beamset=plan.BeamSets[0])
    else:
        poi.place_prescription_point(target_fraction_dose=200, ptv_name="PTV A1*", poi_name="PT PRESC A1", beamset=plan.BeamSets[0])

    # prescribe to point
    if roi.roi_exists("ISO 95% 35.63Gy*"):
        presc_dose = 250 * plan.BeamSets[0].FractionationPattern.NumberOfFractions  # Set Rx dose to 2.5Gy * nb of fractions
    else:
        presc_dose = 200 * plan.BeamSets[0].FractionationPattern.NumberOfFractions  # Set Rx dose to 2Gy * nb of fractions
    try:
        plan.BeamSets[0].AddDosePrescriptionToPoi(PoiName='PT PRESC A1', DoseValue=presc_dose)
    except Exception as e:
        logger.exception(e)
        raise

    # Move dose specification point to prescription point and set DSP for arc A1.1
    point = poi.get_poi_coordinates("PT PRESC A1")
    try:
        dsp = [x for x in plan.BeamSets[0].DoseSpecificationPoints][0]
        dsp.Name = "DSP A1"
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise
    plan.BeamSets[0].Beams[0].SetDoseSpecificationPoint(Name="DSP A1")
    plan.BeamSets[0].ComputeDose(DoseAlgorithm="CCDose")  # Dose is recalculated to show beam dose at spec point in RayStation (otherwise not displayed)

    # Check to see if A2 exists before continuing, otherwise exit script
    try:
        b = plan.BeamSets[1]
    except:
        return

    # rename Beam Set A2
    plan.BeamSets[1].DicomPlanLabel = "A2"

    # Ajouter commentaire pour transfert SuperBridge
    plan.BeamSets[1].Prescription.Description = "VMAT"

    # create PT PRESC A2
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC A2', color="Blue")

    # move prescription point to 2Gy/fraction
    poi.place_prescription_point(target_fraction_dose=200, ptv_name="PTV A2*", poi_name="PT PRESC A2", beamset=plan.BeamSets[1])

    # prescribe to point
    presc_dose = 200 * plan.BeamSets[1].FractionationPattern.NumberOfFractions
    try:
        plan.BeamSets[1].AddDosePrescriptionToPoi(PoiName='PT PRESC A2', DoseValue=presc_dose)
    except Exception as e:
        logger.exception(e)
        raise

    # Move dose specification point to prescription point and set DSP for arc A2.1
    point = poi.get_poi_coordinates("PT PRESC A2")
    try:
        dsp = [x for x in plan.BeamSets[1].DoseSpecificationPoints][0]
        dsp.Name = "DSP A2"
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise
    plan.BeamSets[1].Beams[0].SetDoseSpecificationPoint(Name="DSP A2")
    plan.BeamSets[1].ComputeDose(DoseAlgorithm="CCDose")  # Dose is recalculated to show beam dose at spec point in RayStation (otherwise not displayed)
    

def finaliser_plan_crane_stereo_old():
    """
    #Voir :py:mod:`finaliser_plan_crane_stereo`.
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    # Create DSP - only works in 4.7
    if lib.check_version(4.7):
        plan.BeamSets[0].CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 }) 
    
    # Append * to ROI names for SuperBridge transfer
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["PTV15", "PTV18", "PTV20", "MOELLE", "TR CEREBRAL", "OEIL DRT", "OEIL GCHE"]:
            rois.Name += "*"
        elif rois.Name in ["15", "18", "20"]:
            patient.PatientModel.RegionsOfInterest[rois.Name].Name = ("ISO Presc %sGy*" % rois.Name)

    # rename Beam Set A1
    plan.BeamSets[0].DicomPlanLabel = "Stereo Crane"

    # Ajouter commentaire pour transfert SuperBridge
    plan.BeamSets[0].Prescription.Description = "VMAT"

    # create PT PRESC
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC', color="Red", examination=examination)

    # move prescription point to receive correct dose per fraction
    if roi.roi_exists("ISO Presc 15Gy*"):
        poi.place_prescription_point(target_fraction_dose=1500, ptv_name="PTV15*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=examination)
        presc_dose = 1500
    elif roi.roi_exists("ISO Presc 18Gy*"):
        poi.place_prescription_point(target_fraction_dose=1800, ptv_name="PTV18*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=examination)
        presc_dose = 1800
    #elif roi.roi_exists("ISO Presc 20Gy*"):
    #    poi.place_prescription_point(target_fraction_dose=2000, ptv_name="PTV20*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=examination)
    #    presc_dose = 2000

    # prescribe to point
    try:
        plan.BeamSets[0].AddDosePrescriptionToPoi(PoiName='PT PRESC', DoseValue=presc_dose)
    except Exception as e:
        logger.exception(e)
        raise

    # Move dose specification point to prescription point and set DSP for all arcs
    point = poi.get_poi_coordinates("PT PRESC", examination=examination)
    try:
        dsp = [x for x in plan.BeamSets[0].DoseSpecificationPoints][0]
        dsp.Name = "DSP A1"
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise

    for beam in plan.BeamSets[0].Beams:
        beam.SetDoseSpecificationPoint(Name="DSP A1")
    plan.BeamSets[0].ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point in RayStation (otherwise not displayed)

 
def plan_poumon_sbrt_old(nb_fx = 1):
    """
    Voir :py:mod:`plan_poumoun_sbrt`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    if lib.check_version(4.7):
        scan_index = 1 #Apparently the index is the same even though the names are swapped?
        scan_name = "CT 1"
        patient.Examinations[scan_index].EquipmentInfo.SetImagingSystemReference(ImagingSystemName="HOST-7228")
    else:
        scan_index = 1
        scan_name = "CT 2"
        # Change Imaging System for 2nd scan
        patient.Examinations[scan_index].SetImagingSystem(ImagingSystemName="HOST-7228")

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

    # Create BodyRS+Table
    roi.generate_BodyRS_plus_Table(struct=scan_index)
                    
    # Identify which PTV and ITV to use for creation of optimization contours
    if roi.roi_exists("PTV48", patient.Examinations[scan_name]):
        ptv = patient.PatientModel.RegionsOfInterest["PTV48"]
        itv = patient.PatientModel.RegionsOfInterest["ITV48"]
        rx_dose = 4800
    elif roi.roi_exists("PTV54", patient.Examinations[scan_name]):
        ptv = patient.PatientModel.RegionsOfInterest["PTV54"]
        itv = patient.PatientModel.RegionsOfInterest["ITV54"]
        rx_dose = 5400
    elif roi.roi_exists("PTV60", patient.Examinations[scan_name]):
        ptv = patient.PatientModel.RegionsOfInterest["PTV60"]
        itv = patient.PatientModel.RegionsOfInterest["ITV60"]
        rx_dose = 6000

    # Generate optimization contours
    # Create PTV+3mm, PTV+1.3cm and PTV+2cm
    patient.PatientModel.CreateRoi(Name="PTV+3mm", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+3mm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest['PTV+3mm'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="PTV+1.3cm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+1.3cm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3})
    patient.PatientModel.RegionsOfInterest['PTV+1.3cm'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="PTV+2cm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PTV+2cm'].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2})
    patient.PatientModel.RegionsOfInterest['PTV+2cm'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create RINGs
    patient.PatientModel.CreateRoi(Name="RING_1", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_1'].SetWallExpression(SourceRoiName=ptv.Name, OutwardDistance=0.3, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_1'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="RING_2", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_2'].SetWallExpression(SourceRoiName="PTV+3mm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_2'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="RING_3", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_3'].SetWallExpression(SourceRoiName="PTV+1.3cm", OutwardDistance=1.5, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_3'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="r50", Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['r50'].SetWallExpression(SourceRoiName="PTV+2cm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['r50'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create PEAU
    patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
    patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create TISSU SAIN A 2cm, COMBI PMN-ITV-BR and OPT COMBI PMN
    patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PTV+2cm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="COMBI PMN-ITV-BR", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv.Name, "BR SOUCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="OPT COMBI PMN", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])

    # Remove material override from all ROIs
    for rois in patient.PatientModel.RegionsOfInterest:
        rois.SetRoiMaterial(Material=None)

    # Add Treatment plan
    plan = patient.AddNewPlan(PlanName="Stereo 2arcs", PlannedBy="", Comment="", ExaminationName=scan_name, AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})

    # Add beamset
    if roi.roi_exists("PTV48", patient.Examinations[scan_name]):
        beamset = plan.AddNewBeamSet(Name="2arcs", ExaminationName=lib.get_current_examination().Name, MachineName="BeamMod", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)
    elif roi.roi_exists("PTV54", patient.Examinations[scan_name]):
        beamset = plan.AddNewBeamSet(Name="2arcs", ExaminationName=lib.get_current_examination().Name, MachineName="BeamMod", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)
    elif roi.roi_exists("PTV60", patient.Examinations[scan_name]):
        beamset = plan.AddNewBeamSet(Name="2arcs", ExaminationName=lib.get_current_examination().Name, MachineName="BeamMod", NominalEnergy=None,
                                          Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="VMAT")
        beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)

    # plan and beamset are created but not currently selected in RS
    # therefore we must retain the objects in variables and pass them on
    # to the following functions, which otherwise would assume that
    # these are currently selected by the user in RS.
    # VTL

    # Add arcs
    beams.add_beams_lung_stereo(beamset=beamset, examination=patient.Examinations[scan_name])

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    # Set VMAT conversion parameters
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=350.0, plan=plan)

    # Add optimization objectives
    optimization_objectives.add_opt_obj_lung_stereo(patient_plan=plan)

    # Add clinical goals
    clinical_goals.smart_cg_lung_stereo(plan=plan, examination=patient.Examinations[scan_name])

    # Set Dose Color Table
    eval.remove_all_isodose_lines()
    patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose
    fivegy = float(100*500/rx_dose)

    patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
    eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
    eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
    eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
    eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
    eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
    eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
    patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Rename contours that have no geometry on either CT set with the prefix vide_
    for contour in patient.PatientModel.RegionsOfInterest:
        VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
        VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])

        if VolCT1 == 0:
            if VolCT2 == 0:
                oldname = contour.Name
                contour.Name = ("vide_%s" % oldname)

    # Erase any points other than ISO, ISO SCAN or REF SCAN
    for points in patient.PatientModel.PointsOfInterest:
        if not points.Name.upper() in ["ISO", "ISO SCAN", "REF SCAN"]:
            points.DeleteRoi()

    msg += "Le script plan_poumon_sbrt a terminé.\n"
    msg += "Il faut faire Remove holes (on all slices) sur le contour BodyRS+Table avant d'optimiser.\n"
    # log_window.show_log_window(msg)


def finaliser_plan_poumon_sbrt_old():
    """
    Voir :py:mod:`finaliser_plan_poumon_sbrt`.
    """

    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    if lib.check_version(4.7):
        scan_name = "CT 1"
        expi_scan = "CT 2"
        plan.BeamSets[0].CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 }) # Create DSP - only works in 4.7
    else:
        scan_name = "CT 2"
        expi_scan = "CT 1"

    # Append * to ROI names for SuperBridge transfer
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["PTV48", "PTV54", "PTV56", "PTV60", "ITV48", "ITV54", "ITV56", "ITV60", "GTV expi", "MOELLE"]:
            rois.Name += "*"
            patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=rois.Name)
        elif rois.Name in ["48", "54", "56", "60"]:
            patient.PatientModel.RegionsOfInterest[rois.Name].Name = ("ISO Presc %sGy*" % rois.Name)
            patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=rois.Name)

    # rename Beam Set A1
    plan.BeamSets[0].DicomPlanLabel = "Stereo"

    # Ajouter commentaire pour transfert SuperBridge
    plan.BeamSets[0].Prescription.Description = "VMAT"

    # create PT PRESC
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC', color="Red", examination=patient.Examinations[scan_name])

    # move prescription point to receive correct dose per fraction
    if roi.roi_exists("ISO Presc 48Gy*", patient.Examinations[scan_name]):
        poi.place_prescription_point(target_fraction_dose=1200, ptv_name="PTV48*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=patient.Examinations[scan_name])
    elif roi.roi_exists("ISO Presc 54Gy*", patient.Examinations[scan_name]):
        poi.place_prescription_point(target_fraction_dose=1800, ptv_name="PTV54*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=patient.Examinations[scan_name])
    elif roi.roi_exists("ISO Presc 56Gy*", patient.Examinations[scan_name]):
        poi.place_prescription_point(target_fraction_dose=1400, ptv_name="PTV56*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=patient.Examinations[scan_name])
    elif roi.roi_exists("ISO Presc 60Gy*", patient.Examinations[scan_name]):
        if plan.BeamSets[0].FractionationPattern.NumberOfFractions == 5:  # 60 Gy en 5 fx
            poi.place_prescription_point(target_fraction_dose=1200, ptv_name="PTV60*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=patient.Examinations[scan_name])
        elif plan.BeamSets[0].FractionationPattern.NumberOfFractions == 8:  # 60 Gy en 8 fx
            poi.place_prescription_point(target_fraction_dose=750, ptv_name="PTV60*", poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=patient.Examinations[scan_name])

    # prescribe to point
    if roi.roi_exists("ISO Presc 48Gy*", patient.Examinations[scan_name]):
        presc_dose = 4800  # Set Rx dose to 48Gy
    elif roi.roi_exists("ISO Presc 54Gy*", patient.Examinations[scan_name]):
        presc_dose = 5400  # Set Rx dose to 54Gy
    elif roi.roi_exists("ISO Presc 56Gy*", patient.Examinations[scan_name]):
        presc_dose = 5600  # Set Rx dose to 54Gy        
    elif roi.roi_exists("ISO Presc 60Gy*", patient.Examinations[scan_name]):
        presc_dose = 6000  # Set Rx dose to 60Gy
    try:
        plan.BeamSets[0].AddDosePrescriptionToPoi(PoiName='PT PRESC', DoseValue=presc_dose)
    except Exception as e:
        logger.exception(e)
        raise

    # Move dose specification point to prescription point and set DSP for all arcs
    point = poi.get_poi_coordinates("PT PRESC", patient.Examinations[scan_name])
    try:
        dsp = [x for x in plan.BeamSets[0].DoseSpecificationPoints][0]
        dsp.Name = "DSP A1"
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script if you are using RayStation 4.0.3.4.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise

    for beam in plan.BeamSets[0].Beams:
        beam.SetDoseSpecificationPoint(Name="DSP A1")
    plan.BeamSets[0].ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point in RayStation (otherwise not displayed)


def finaliser_plan_foie_sbrt_old():
    """
    #Voir :py:mod:`finaliser_plan_crane_stereo`.
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    # Create DSP - only works in 4.7
    if lib.check_version(4.7):
        plan.BeamSets[0].CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 }) 
    
    # Determine PTV name, prescription dose and number of fractions
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            try:
                presc_dose = float(name[3:])
            except:
                continue
            ptv = patient.PatientModel.RegionsOfInterest[name]
            dose_roi_name = ptv.Name[3:]
            break

    nb_fx = plan.BeamSets[0].FractionationPattern.NumberOfFractions

    # Append * to ROI names for SuperBridge transfer
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["GTV EXPI", "FOIE INSPI", "FOIE EXPI", "MOELLE", "REINS", "OESOPHAGE", "ESTOMAC", "DUODENUM", "COLON", "GRELE", ptv.Name]:
            rois.Name += "*"
        elif rois.Name == dose_roi_name:
            patient.PatientModel.RegionsOfInterest[dose_roi_name].Name = ("ISO PRESC %sGy*" % dose_roi_name)

    # rename Beam Set A1
    plan.BeamSets[0].DicomPlanLabel = "Stereo"

    # Ajouter commentaire pour transfert SuperBridge
    plan.BeamSets[0].Prescription.Description = "VMAT"

    # create PT PRESC
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC', color="Red", examination=examination)

    # move prescription point to receive correct dose per fraction
    poi.place_prescription_point(target_fraction_dose=presc_dose * 100 / nb_fx, ptv_name=ptv.Name, poi_name="PT PRESC", beamset=plan.BeamSets[0], exam=examination)

    # prescribe to point
    try:
        plan.BeamSets[0].AddDosePrescriptionToPoi(PoiName='PT PRESC', DoseValue=presc_dose * 100)
    except Exception as e:
        logger.exception(e)
        raise

    # Move dose specification point to prescription point and set DSP for all arcs
    point = poi.get_poi_coordinates("PT PRESC", examination=examination)
    try:
        dsp = [x for x in plan.BeamSets[0].DoseSpecificationPoints][0]
        dsp.Name = "DSP A1"
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise

    for beam in plan.BeamSets[0].Beams:
        beam.SetDoseSpecificationPoint(Name="DSP A1")
    plan.BeamSets[0].ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point in RayStation (otherwise not displayed)


def add_beams_lung_stereo_old(contralateral_lung=None, beamset=None, examination=None):
    """
        Ajoute les arcs utilisés en stéréo de poumon.

        Détecte s'il s'agit d'un poumon droit ou gauche si le poumon
        contralatéral n'est pas spécifié.

        Par défaut, des arcs allant de :

        - 181 à 30 degrés en CW, puis de 30 à 181 degrés en CCW pour les traitements du poumon droit;
        - 330 à 180 degrés en CW, puis de 180 à 330 degrés en CCW pour les traitements du poumon gauche;

        seront ajoutés, avec un collimateur de 5 et 355 degrés pour l'arc CW et CCW, respectivement.

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.
        - ROI poumons nommés *POUMON G* et *POUMON D*
        - ROI PTV nommé selon la convention habituelle *PTV<niveau de dose en Gy>*

        Args:
            contralateral_lung (str, optional): le nom du ROI du poumon contralatéral : *POUMON G* ou *POUMON D*.
            beamset: objet beamset de RayStation
            examination: object examination de RayStation

        .. seealso::
          fonctions :py:func:`hmrlib.lib.add_arc`, :py:func:`hmrlib.roi.identify_ptvs2`, :py:func:`hmrlib.roi.find_most_intersecting_roi`
    """

    iso = poi.identify_isocenter_poi()
    
    #Ajouté par MA pour permettre le fonctionnement du méga-script poumons
    if beamset is None:
        beamset = lib.get_current_beamset()
    if examination is None:
        examination = lib.get_current_examination()

    if contralateral_lung is None:
        ptvs = roi.identify_ptvs2()
        if roi.find_most_intersecting_roi(ptvs[0], ['POUMON DRT', 'POUMON GCHE'], examination=examination) == 'POUMON DRT':
            contralateral_lung = 'POUMON GCHE'
        else:
            contralateral_lung = 'POUMON DRT'

    if contralateral_lung == 'POUMON GCHE':
        # Poumon D treated
        lib.add_arc('A1.1', iso, 181, 30, 'CW', description='ARC 181-30', collimator=5, beamset=beamset, exam=examination)
        lib.add_arc('A1.2', iso, 30, 181, 'CCW', description='ARC 30-181', collimator=355, beamset=beamset, exam=examination)
    elif contralateral_lung == 'POUMON DRT':
        # Poumon G treated
        lib.add_arc('A1.1', iso, 330, 180, 'CW', description='ARC 330-180', collimator=5, beamset=beamset, exam=examination)
        lib.add_arc('A1.2', iso, 180, 330, 'CCW', description='ARC 180-330', collimator=355, beamset=beamset, exam=examination)
    else:
        lib.error('Contralateral lung ROI name not recognized.')


# Function modified to work with new syntax in RayStation 4.7.2
# Obsolete now that add_clinical_goal checks which version is running and adjusts accordingly.
def add_clinical_goal_472(RoiName, GoalValue, GoalCriteria, GoalType, Volume, IsComparativeGoal=False, plan=None):
    """
    Adds a clinical goal to the current plan.

    Args:
        RoiName (str): the name of the ROI for which to add the goal
        GoalValue (float): the dose value of the goal in cGy
        GoalCriteria (str): one of *AtLeast* or *AtMost*
        GoalType (str): one of the clinical goal types supported by RayStation, e.g. *DoseAtAbsoluteVolume*, *AbsoluteVolumeAtDose*, *DoseAtVolume*, etc.
        Volume (float): the volume value in cc or in %, depending on the chosen goal type.
    """
    # Convert old-style arguments into args compatible with RayStation 4.7.2
    if GoalType=='DoseAtVolume':
        AcceptanceLevel = GoalValue
        ParameterValue = Volume/100.0
    elif GoalType=='DoseAtAbsoluteVolume':
        AcceptanceLevel = GoalValue
        ParameterValue = Volume
    if GoalType=='VolumeAtDose':
        ParameterValue = GoalValue
        AcceptanceLevel = Volume/100.0
    elif GoalType=='AbsoluteVolumeAtDose':
        ParameterValue = GoalValue
        AcceptanceLevel = Volume
        
    if plan is None:
        plan = lib.get_current_plan()

    if roi.roi_exists(RoiName):
        plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=RoiName, GoalCriteria=GoalCriteria, GoalType=GoalType, AcceptanceLevel=AcceptanceLevel,
                                                             ParameterValue=ParameterValue, IsComparativeGoal=IsComparativeGoal)


def smart_cg_lung_stereo_old(plan=None, examination=None):
    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()

    # Set PTV name and prescription type
    if roi.roi_exists("PTV54", examination):
        ptv = patient.PatientModel.RegionsOfInterest["PTV54"]
        Rx = 0
    elif roi.roi_exists("PTV48", examination):
        ptv = patient.PatientModel.RegionsOfInterest["PTV48"]
        Rx = 1
    elif roi.roi_exists("PTV60", examination):
        ptv = patient.PatientModel.RegionsOfInterest["PTV60"]
        if plan.BeamSets[0].FractionationPattern.NumberOfFractions == 8:
            Rx = 2
        elif plan.BeamSets[0].FractionationPattern.NumberOfFractions == 5:
            Rx = 3

    # Objectifs de couverture
    dose_level1 = [5130, 4560, 5700, 5700]  # Isodose 95%
    dose_level2 = [5400, 4800, 6000, 6000]  # Isodose de prescription
    dose_level3 = [8100, 7200, 9000, 9000]  # Isodose 150%

    # Compute what is 0.1 cc in percentage of the volume
    ptone_cc_percentage = roi.convert_absolute_volume_to_percentage(ptv.Name, volume_cc=0.1, examination=examination)
    # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
    eval.add_clinical_goal(ptv.Name, dose_level1[Rx], 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=plan)
    eval.add_clinical_goal(ptv.Name, dose_level2[Rx], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(ptv.Name, dose_level3[Rx], "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)

    # BR SOUCHE
    if roi.roi_exists("BR SOUCHE", examination):
        roi_name = "BR SOUCHE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # Paroi trachée/bronches opposées
    if roi.roi_exists("BR SOUCHE PAROI OPP", examination):
        roi_name = "BR SOUCHE PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 2110, 1800]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 4, plan=plan)

    # COEUR
    if roi.roi_exists("COEUR", examination):
        roi_name = "COEUR"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3850, 3200]  # 15cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)

    # COTES
    if roi.roi_exists("COTES", examination):
        roi_name = "COTES"
        dose_level1 = [3700, 4200, 5640, 4630]  # 0.1cc hors PTV
        dose_level2 = [3530, 4000, 5360, 4400]  # 0.3cc hors PTV
        dose_level3 = [2660, 3000, 3960, 3290]  # 1.4cc hors PTV
        dose_level4 = [1790, 2000, 2570, 2180]  # 3.6cc hors PTV
        dose_level5 = [910, 1000, 1220, 1070]  # 5cc hors PTV
        dose_level6 = [5400, 4800, 6000, 6000]  # 0.1cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level6[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # ESTOMAC
    if roi.roi_exists("ESTOMAC", examination):
        roi_name = "ESTOMAC"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 15cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)

    # GROS VAISSEAUX
    if roi.roi_exists("GROS VAISSEAUX", examination):
        roi_name = "GROS VAISSEAUX"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 4860, 4010]  # 10cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)

    # INTESTINS
    if roi.roi_exists("INTESTINS", examination):
        roi_name = "INTESTINS"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 10cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)

    # MOELLE
    if roi.roi_exists("MOELLE", examination):
        roi_name = "MOELLE"
        dose_level1 = [1800, 2020, 2590, 2620]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # PRV MOELLE
    if roi.roi_exists("PRV MOELLE", examination):
        roi_name = "PRV MOELLE"
        dose_level1 = [2000, 2240, 2910, 2930]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # OESOPHAGE
    # If ROI intersects PTV, add appropriate clinical goal and leave OESOPHAGE ds PTV contour for optimization
    # If ROI within 2cm of PTV, add appropriate clinical goal and leave OESOPHAGE ds PTV+2cm contour for optimization
    # If ROI >2cm from PTV, add appropriate clinical goal without leaving any additional contours
    if roi.roi_exists("OESOPHAGE", examination):
        roi_name = "OESOPHAGE"
        dose_level1 = [1000, 1100, 1350, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3050, 4030, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()
            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # Paroi oesophagienne opposée
    if roi.roi_exists("OESO PAROI OPP", examination):
        roi_name = "OESO PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 3290, 2750]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)

    # PAROI
    if roi.roi_exists("PAROI", examination):
        roi_name = "PAROI"
        dose_level1 = [6000, 6850, 9380, 7590]  # 3cc hors PTV
        dose_level2 = [3000, 3390, 4510, 3730]  # 30cc dans PTV
        dose_level3 = [4000, 4550, 6130, 5010]  # 0.2% dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            eval.add_clinical_goal(hors.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)

    # PEAU
    if roi.roi_exists("PEAU", examination):
        roi_name = "PEAU"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # PLEXUS BRACHIAL
    if roi.roi_exists("PLEXUS BRACHIAL", examination):
        roi_name = "PLEXUS BRACHIAL"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # PRV PLEXUS
    if roi.roi_exists("PRV PLEXUS", examination):
        roi_name = "PRV PLEXUS"
        dose_level1 = [2700, 3050, 4030, 3340]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # COMBI PMN-ITV-BR
    if roi.roi_exists("COMBI PMN-ITV-BR", examination):
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'VolumeAtDose', 20, plan=plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1000, 'AtMost', 'VolumeAtDose', 15, plan=plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1500, 'AtMost', 'VolumeAtDose', 10, plan=plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 2000, 'AtMost', 'VolumeAtDose', 5, plan=plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'AverageDose', 0, plan=plan)

    # CONTRALATERAL LUNG - Does this function need me to send it examination??
    if roi.find_most_intersecting_roi(ptv.Name, ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
        contralateral_lung = 'POUMON DRT'
    else:
        contralateral_lung = 'POUMON GCHE'

    eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=plan)

    # TRACHEE
    if roi.roi_exists("TRACHEE", examination):
        roi_name = "TRACHEE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)

    # TISSU SAIN A 2cm
    if roi.roi_exists("TISSU SAIN A 2cm", examination):
        roi_name = "TISSU SAIN A 2cm"
        dose_level1 = [2700, 2400, 3000, 3000]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)    
    

def smart_cg_foie_sbrt_old(plan=None, examination=None):
    # This script adds both clinical goals and optimization objectives for cases of liver SBRT.
    # For OAR, proximity to the PTV is evaluated and used to choose which goals and objectives to add.
    # In all cases, the number of fractions determines which set of target doses are used.

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()

    # Determine Rx type via number of fractions
    if plan.BeamSets[0].FractionationPattern.NumberOfFractions == 3:
        Rx = 0
    elif plan.BeamSets[0].FractionationPattern.NumberOfFractions == 5:
        Rx = 1

    # Determine PTV name and prescription dose
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            ptv = patient.PatientModel.RegionsOfInterest[name]
            Rx_dose = float(ptv.Name[3:])
            break

    # Compute what is 0.1 cc in percentage of the volume
    ptone_cc_percentage = roi.convert_absolute_volume_to_percentage(ptv.Name, volume_cc=0.1, examination=examination)
    # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
    eval.add_clinical_goal(ptv.Name, Rx_dose * 95, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=plan)
    eval.add_clinical_goal(ptv.Name, Rx_dose * 100, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(ptv.Name, Rx_dose * 150, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)

    # Add optimization objectives for PTV, PTV-GTV and Rings
    optim.add_mindose_objective(ptv.Name, Rx_dose * 100, weight=10, plan=plan)
    optim.add_maxdose_objective(ptv.Name, Rx_dose * 133.33, plan=plan)

    optim.add_maxdose_objective("PTV-GTV", Rx_dose * 124.44, plan=plan)

    optim.add_maxdose_objective('Ring_1_0mm', Rx_dose * 101, plan=plan)
    optim.add_maxdose_objective('Ring_2_2mm', Rx_dose * 86.67, plan=plan)
    optim.add_maxeud_objective('Ring_3_5mm', Rx_dose * 101, 1, 1, plan=plan)
    optim.add_maxdose_objective('Ring_4_20mm', Rx_dose * 42.22, plan=plan)

    optim.add_dosefalloff_objective('BodyRS', Rx_dose * 101, Rx_dose * 100 / 2, 2, weight=1, plan=plan)

    # MOELLE
    if roi.roi_exists("MOELLE", examination):
        roi_name = "MOELLE"
        dose_level1 = [1800, 2620]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # prv5mmMOELLE
    if roi.roi_exists("prv5mmMOELLE", examination):
        roi_name = "prv5mmMOELLE"
        dose_level1 = [2000, 2930]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # COEUR
    if roi.roi_exists("COEUR", examination):
        roi_name = "COEUR"
        dose_level1 = [3000, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level3 = [0, 3200]  # 15cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx == 1:  # Only for prescriptions in 5 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 15, 1, plan=plan)

    # OESOPHAGE, ESTOMAC, DUODENUM, GRELE and COLON all use the same logic:
        # If ROI intersects PTV, add clinical goals for ROI dans PTV as well as max 0.1cc > 2cm from PTV. Leave ROI dans PTV and ROI hors PTV+2cm contours for optimization.
            #(max 0.1cc < 2cm is not added because it is unattainable)
        # If ROI within 2cm of PTV, add clinical goal for max 0.1cc < 2cm and max 0.1cc > 2cm. Leave ROI dans PTV+2cm and ROI hors PTV+2cm contours for optimization.
        # If ROI >2cm from PTV, add clinical goal for max 0.1cc > 2cm without leaving any additional contours.

    # OESOPHAGE
    if roi.roi_exists("OESOPHAGE", examination):
        roi_name = "OESOPHAGE"
        dose_level1 = [1000, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # ESTOMAC - Same logic as OESOPHAGE, but with different dose values
    if roi.roi_exists("ESTOMAC", examination):
        roi_name = "ESTOMAC"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # DUODENUM - Exactly the same as OESOPHAGE
    if roi.roi_exists("DUODENUM", examination):
        roi_name = "DUODENUM"
        dose_level1 = [1000, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # GRELE - Exactly the same as ESTOMAC
    if roi.roi_exists("GRELE", examination):
        roi_name = "GRELE"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # COLON - Exactly the same as ESTOMAC
    if roi.roi_exists("COLON", examination):
        roi_name = "COLON"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # PEAU
    if roi.roi_exists("PEAU", examination):
        roi_name = "PEAU"
        dose_level1 = [2400, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # COTES
    if roi.roi_exists("COTES", examination):
        roi_name = "COTES"
        dose_level1 = [3700, 4630]  # 0.1cc hors PTV
        dose_level2 = [3530, 4400]  # 0.3cc hors PTV
        dose_level3 = [2660, 3290]  # 1.4cc hors PTV
        dose_level4 = [1790, 2180]  # 3.6cc hors PTV
        dose_level5 = [910, 1070]  # 5cc hors PTV
        dose_level6 = [5400, Rx_dose * 100]  # 0.1cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination, margeptv=0.2)
        dans.Name += "+2mm"
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level6[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level6[Rx], plan=plan)
            optim.add_maxeud_objective(hors.Name, dose_level1[Rx] * 0.66, 1, 1, plan=plan)

    # PAROI
    if roi.roi_exists("PAROI", examination):
        roi_name = "PAROI"
        dose_level1 = [6000, 7590]  # 3cc hors PTV
        dose_level2 = [3000, 3730]  # 30cc dans PTV
        dose_level3 = [4000, 5010]  # 0.2% dans PTV

        if not roi.roi_exists("PAROI hors PTV", examination):
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination)

        eval.add_clinical_goal(hors.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
        eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
        eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        optim.add_maxdose_objective(hors.Name, Rx_dose * 100 - 200, plan=plan)

    # Paroi oesophagienne opposée
    if roi.roi_exists("OESO PAROI OPP", examination):
        roi_name = "OESO PAROI OPP"
        if Rx == 1:  # Only for prescriptions in 5 fx
            dose_level1 = [0, Rx_dose * 105]  # 0.1cc
            dose_level2 = [0, 2750]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # FOIE EXPI
    if roi.roi_exists("FOIE EXPI", examination):
        roi_name = "FOIE EXPI"
        dose_level1 = [1500, 1810]  # dose moyenne
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)

    # FOIE EXPI-GTV
    if roi.roi_exists("FOIE EXPI-GTV", examination):
        roi_name = "FOIE EXPI-GTV"
        dose_level1 = [1500, 1810]  # dose moyenne
        dose_level2 = [1700, 2700]  # 700cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)
        eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 700, plan=plan)

    # OPT FOIE EXPI
    if roi.roi_exists("OPT FOIE EXPI", examination):
        roi_name = "OPT FOIE EXPI"
        dose_level1 = [1500, 1810]  # dose moyenne
        optim.add_maxeud_objective(roi_name, dose_level1[Rx] - 100, 1, 1, plan=plan)

    # REINS
    if roi.roi_exists("REINS", examination):
        roi_name = "REINS"
        dose_level1 = [1020, 1200]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)
        optim.add_maxeud_objective('REIN DRT', dose_level1[Rx] - 200, 1, 1, plan=plan)
        optim.add_maxeud_objective('REIN GCHE', dose_level1[Rx] - 200, 1, 1, plan=plan)

    # TISSU SAIN A 2cm
    if roi.roi_exists("TISSU SAIN A 2cm", examination):
        roi_name = "TISSU SAIN A 2cm"
        eval.add_clinical_goal(roi_name, Rx_dose * 50, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
    

def plan_launcher_old():
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()



    class ScriptLauncher(Form):
        def __init__(self):
            self.Text = "Planning Script Launcher"

            self.Width = 750
            self.Height = 400

            self.setupPlanningScriptLauncher()
            self.setupOKButtons()

            self.Controls.Add(self.LauncherPanel)
            self.Controls.Add(self.OKbuttonPanel)
            
        def newPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 300
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def setupPlanningScriptLauncher(self):
            self.LauncherPanel = self.newPanel(0, 0)

            self.Label1 = Label()
            self.Label1.Text = "Choissisez le site à planifier:                       Patient: " + patient.PatientName.replace('^', ', ')
            self.Label1.Location = Point(25, 25)
            self.Label1.Font = Font("Arial", 10, FontStyle.Bold)
            self.Label1.AutoSize = True

            self.SiteButton1 = RadioButton()
            self.SiteButton1.Text = "Prostate"
            self.SiteButton1.Location = Point(25, 50)
            #self.SiteButton1.Checked = True
            self.SiteButton1.CheckedChanged += self.checkedChanged
            
            self.SiteButton2 = RadioButton()
            self.SiteButton2.Text = "Crâne Stéréo"
            self.SiteButton2.Location = Point(25, 80)
            self.SiteButton2.CheckedChanged += self.checkedChanged

            self.SiteButton3 = RadioButton()
            self.SiteButton3.Text = "SBRT Poumon"
            self.SiteButton3.Location = Point(25, 110)
            self.SiteButton3.CheckedChanged += self.checkedChanged
            
            self.SiteButton4 = RadioButton()
            self.SiteButton4.Text = "SBRT Foie"
            self.SiteButton4.Location = Point(25, 140)
            self.SiteButton4.CheckedChanged += self.checkedChanged
    
            self.Label2 = Label()
            self.Label2.Text = ""
            self.Label2.Location = Point(300, 50)
            self.Label2.AutoSize = True
            self.Label2.Font = Font("Arial", 10)
            self.Label2.ForeColor = Color.Black
            
            self.Label3 = Label()
            self.Label3.Text = ""
            self.Label3.Location = Point(300, 70)
            self.Label3.AutoSize = True
            self.Label3.Font = Font("Arial", 10)
            self.Label3.ForeColor = Color.Black
            
            self.Label4 = Label()
            self.Label4.Text = ""
            self.Label4.Location = Point(300, 90)
            self.Label4.AutoSize = True
            self.Label4.Font = Font("Arial", 10)
            self.Label4.ForeColor = Color.Black
            
            self.Label5 = Label()
            self.Label5.Text = ""
            self.Label5.Location = Point(300, 110)
            self.Label5.AutoSize = True
            self.Label5.Font = Font("Arial", 10)
            self.Label5.ForeColor = Color.Black
            
            self.Label6 = Label()
            self.Label6.Text = ""
            self.Label6.Location = Point(300, 250)
            self.Label6.AutoSize = True
            self.Label6.Font = Font("Arial", 12, FontStyle.Bold)
            self.Label6.ForeColor = Color.Black
            
            self.comboBoxRx = ComboBox()
            self.comboBoxRx.Parent = self
            self.comboBoxRx.Size = Size(200,40)
            self.comboBoxRx.Location = Point(25,190)
            
            self.check1 = CheckBox()
            self.check1.Text = "Double optimization initiale?"
            self.check1.Location = Point(50, 230)
            self.check1.Width = 300
            self.check1.Checked = False
            
            self.check2 = CheckBox()
            self.check2.Text = ""
            self.check2.Location = Point(50, 260)
            self.check2.Width = 300            
            
            self.LauncherPanel.Controls.Add(self.Label1)
            self.LauncherPanel.Controls.Add(self.Label2)
            self.LauncherPanel.Controls.Add(self.Label3)
            self.LauncherPanel.Controls.Add(self.Label4)
            self.LauncherPanel.Controls.Add(self.Label5)
            self.LauncherPanel.Controls.Add(self.Label6)
            self.LauncherPanel.Controls.Add(self.SiteButton1)
            self.LauncherPanel.Controls.Add(self.SiteButton2)
            self.LauncherPanel.Controls.Add(self.SiteButton3)
            self.LauncherPanel.Controls.Add(self.SiteButton4)
            self.LauncherPanel.Controls.Add(self.check1)
            self.LauncherPanel.Controls.Add(self.check2)
            #self.LauncherPanel.Controls.Add(self.comboBoxProstate)

            exam_list = []
            for CT in patient.Examinations:
                exam_list.append(CT.Name)
            
            for contour in patient.PatientModel.RegionsOfInterest:
                VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
                if "CT 2" in exam_list:
                    VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])
                else:
                    VolCT2 = 0

                if VolCT1 == 0:
                    if VolCT2 == 0:
                        oldname = contour.Name
                        contour.Name = ("vide_%s" % oldname)
            
        def checkedChanged(self, sender, args):
            if not sender.Checked:
                return

            # Erase error messages and clear prescription selection menu
            self.Label2.Text = " "
            self.Label3.Text = " "
            self.Label4.Text = " "
            self.Label5.Text = " "
            self.Label6.Text = " "
            self.Label2.ForeColor = Color.Black
            self.Label3.ForeColor = Color.Black
            self.Label4.ForeColor = Color.Black
            self.Label5.ForeColor = Color.Black
            self.Label6.ForeColor = Color.Black
            self.check1.Checked = False            
            self.check2.Text = ""
            self.comboBoxRx.Items.Clear()
            
            roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                        
            if sender.Text == "Prostate":      
                # set selection
                self.comboBoxRx.Text = "Choisissez la prescription"
                self.comboBoxRx.SelectedValueChanged += self.comboBox_SelectedValueChangedHandler
                # add items
                self.comboBoxRx.Items.Add("80Gy-40")
                self.comboBoxRx.Items.Add("66Gy-33")
                self.comboBoxRx.Items.Add("37.5Gy-15")
                
                self.check2.Text = "Est-ce qu'il y a un plan 3D conforme?"
            
                boost = False
                for name in roi_names:
                    if 'PTVBOOST' in name.replace(' ', '').upper():
                        boost = True
                        boost_name = name

                #Find ROI(s) that will be used to create PTV A1
                if 'PTV A1' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV A1 déjà existent"
                elif 'PTV 1.5cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm"          
                elif 'PTV 1cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm"
                else:
                    self.Label2.Text = "Attention: Aucun ROI source trouvé pour le PTV A1!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Find ROI that will be used to create PTV A2
                if boost:
                    self.Label3.Text = "Source pour PTV A2: " + boost_name
                elif 'PTV 1cm' in roi_names:
                    self.Label3.Text = "Source pour PTV A2: PTV 1cm"
                else:
                    self.Label3.Text = "Attention: Aucun ROI source trouvé pour le PTV A2!"     
                    self.Label3.ForeColor = Color.Orange                       
                
                #Verify presence of essential contours
                essential_list = ["Table","RECTUM","VESSIE"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label4.Text = "ROIs Table, RECTUM et VESSIE trouvés"

                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISOCENTRE"):
                    if poi.poi_exists("ISO"):
                        self.Label5.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO"
                        self.Label5.ForeColor = Color.Red  
                    elif poi.poi_exists("ISO SCAN"):
                        self.Label5.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO SCAN"
                        self.Label5.ForeColor = Color.Red                     
                    else:
                        self.Label5.Text = "Point ISOCENTRE sera utilisé comme isocentre"
                elif poi.poi_exists("ISO"):
                    if poi.poi_exists("ISO SCAN"):
                        self.Label5.Text = "Deux potentiels isocentres trouvés: ISO et ISO SCAN"
                        self.Label5.ForeColor = Color.Red  
                    else:
                        self.Label5.Text = "Point ISO sera utilisé comme isocentre"                    
                elif poi.poi_exists("ISO SCAN"):
                    self.Label5.Text = "Point ISO SCAN sera utilisé comme isocentre"
                elif poi.poi_exists("ISO PT PRESC"):
                    self.Label5.Text = "Point ISO PT PRESC sera renommé ISO SCAN et sera utilisé comme isocentre"
                elif poi.poi_exists("REF SCAN"):
                    self.Label5.Text = "Point REF SCAN sera renommé ISO SCAN et sera utilisé comme isocentre"                    
                else:
                    self.Label5.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label5.ForeColor = Color.Red                  
 

            elif sender.Text == "Crâne Stéréo":      
                self.check1.Checked = True  #Double optimization
                #Identify the PTV
                if 'PTV15' in roi_names:
                    self.Label2.Text = "PTV15 trouvé"
                    self.comboBoxRx.Items.Add("15Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("15Gy-1")
                elif 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                if 'CERVEAU' not in roi_names:
                    self.Label3.Text = "ROI CERVEAU pas trouvé!"
                    self.Label3.ForeColor = Color.Red          
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("REF SCAN"):
                    self.Label4.Text = "Point REF SCAN sera utilisé comme isocentre"
                elif poi.poi_exists("ISO PT PRESC"):
                    self.Label4.Text = "Point ISO PT PRESC sera utilisé comme isocentre"
                elif poi.poi_exists("ISO SCAN"):
                    self.Label4.Text = "Point ISO SCAN sera utilisé comme isocentre"
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red    
                    
                    
            elif sender.Text == "SBRT Poumon":      
                self.check1.Checked = True  #Double optimization
                #Identify the PTV
                if 'PTV48' in roi_names:
                    if 'ITV48' in roi_names:
                        self.Label2.Text = "PTV48 et ITV 48 trouvés"
                        self.comboBoxRx.Items.Add("48Gy-4")
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("48Gy-4")
                        #nb_fx = 4
                    else: 
                        self.Label2.Text = "Attention: PTV48 trouveé, mais ITV48 absent!"     
                        self.Label2.ForeColor = Color.Red   
                elif 'PTV54' in roi_names:
                    if 'ITV54' in roi_names:
                        self.Label2.Text = "PTV54 et ITV54 trouvés"
                        self.comboBoxRx.Items.Add("54Gy-3")
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("54Gy-3")
                        #nb_fx = 3
                    else:
                        self.Label2.Text = "Attention: PTV54 trouveé, mais ITV54 absent!"     
                        self.Label2.ForeColor = Color.Red                           
                elif 'PTV60' in roi_names:
                    if 'ITV60' in roi_names:
                        self.Label2.Text = "PTV60 et ITV60 trouvés"
                        self.comboBoxRx.Items.Add("60Gy-5")
                        self.comboBoxRx.Items.Add("60Gy-8")
                        self.comboBoxRx.Text = "Choisissez la prescription"
                    else:
                        self.Label2.Text = "Attention: PTV60 trouveé, mais ITV60 absent!"     
                        self.Label2.ForeColor = Color.Red      
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Verify presence of essential contours
                essential_list = ["Table","POUMON DRT","POUMON GCHE","BR SOUCHE"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, BR SOUCHE et POUMONs trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISOCENTRE"):
                    if poi.poi_exists("ISO"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO"
                        self.Label4.ForeColor = Color.Red  
                    elif poi.poi_exists("ISO SCAN"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO SCAN"
                        self.Label4.ForeColor = Color.Red                     
                    else:
                        self.Label4.Text = "Point ISOCENTRE sera utilisé comme isocentre"
                elif poi.poi_exists("ISO"):
                    if poi.poi_exists("ISO SCAN"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISO et ISO SCAN"
                        self.Label4.ForeColor = Color.Red  
                    else:
                        self.Label4.Text = "Point ISO sera utilisé comme isocentre"                    
                elif poi.poi_exists("ISO SCAN"):
                    self.Label4.Text = "Point ISO SCAN sera utilisé comme isocentre"
                elif poi.poi_exists("ISO PT PRESC"):
                    self.Label4.Text = "Point ISO PT PRESC sera renommé ISO SCAN et sera utilisé comme isocentre"
                elif poi.poi_exists("REF SCAN"):
                    self.Label4.Text = "Point REF SCAN sera renommé ISO SCAN et sera utilisé comme isocentre"                    
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red      


            elif sender.Text == "SBRT Foie":      
                self.check1.Checked = True  #Double optimization
                #Identify the PTV
                ptv_name = "NoValue"
                #roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                for name in roi_names:
                    n = name.replace(' ', '').upper()
                    if 'PTV' in n and '-' not in n:
                        try:
                           presc_dose = float(name[3:])
                        except:
                            continue
                        ptv_name = name
                        break  
                if ptv_name != "NoValue":
                    self.Label2.Text = name + " trouvé"
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-3")
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-5")
                    self.comboBoxRx.Text = "Choisissez la prescription"
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Verify presence of essential contours
                essential_list = ["Table","FOIE EXPI","GTV"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, FOIE EXPI et GTV trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISOCENTRE"):
                    if poi.poi_exists("ISO"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO"
                        self.Label4.ForeColor = Color.Red  
                    elif poi.poi_exists("ISO SCAN"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISOCENTRE et ISO SCAN"
                        self.Label4.ForeColor = Color.Red                     
                    else:
                        self.Label4.Text = "Point ISOCENTRE sera utilisé comme isocentre"
                elif poi.poi_exists("ISO"):
                    if poi.poi_exists("ISO SCAN"):
                        self.Label4.Text = "Deux potentiels isocentres trouvés: ISO et ISO SCAN"
                        self.Label4.ForeColor = Color.Red  
                    else:
                        self.Label4.Text = "Point ISO sera utilisé comme isocentre"                    
                elif poi.poi_exists("ISO SCAN"):
                    self.Label4.Text = "Point ISO SCAN sera utilisé comme isocentre"
                elif poi.poi_exists("ISO PT PRESC"):
                    self.Label4.Text = "Point ISO PT PRESC sera renommé ISO SCAN et sera utilisé comme isocentre"
                elif poi.poi_exists("REF SCAN"):
                    self.Label4.Text = "Point REF SCAN sera renommé ISO SCAN et sera utilisé comme isocentre"                    
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     
                 
                    
        def okClicked(self, sender, args):
            if self.SiteButton1.Checked: #Prostate
                Rx_type = self.comboBoxRx.SelectedItem
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red  
                else:
                    if Rx_type == "80Gy-40":
                        nb_fx = 40
                    elif Rx_type == "66Gy-33":
                        nb_fx = 33
                    elif Rx_type == "37.5Gy-15":
                        nb_fx = 15
                        
                    # Check whether 3DCRT plan exists    
                    if self.check2.Checked:
                        self.Label6.ForeColor = Color.Black
                        self.Label6.Text = "Création du plan en cours"
                        prostate.create_prostate_plan_A1(nb_fx = nb_fx, plan3D = True)
                    else:
                        self.Label6.ForeColor = Color.Black
                        self.Label6.Text = "Création du plan en cours"
                        prostate.create_prostate_plan_A1(nb_fx = nb_fx, plan3D = False)
                        
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        if self.check2.Checked:
                            self.Label6.Text = "Première optimization en cours"
                            patient.TreatmentPlans["A2 seul"].PlanOptimizations[0].RunOptimization()
                            self.Label6.Text = "Deuxième optimization en cours"
                            patient.TreatmentPlans["A2 seul"].PlanOptimizations[0].RunOptimization()
                        else:
                            self.Label6.Text = "Première optimization en cours"
                            patient.TreatmentPlans["A1 seul"].PlanOptimizations[0].RunOptimization()
                            self.Label6.Text = "Deuxième optimization en cours"
                            patient.TreatmentPlans["A1 seul"].PlanOptimizations[0].RunOptimization()                        
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green      
                
 
            elif self.SiteButton2.Checked: #Crâne stéréo
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    crane.plan_crane_stereo()
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Crane"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Crane"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   

                    
            elif self.SiteButton3.Checked: #SBRT Poumon
                Rx_type = self.comboBoxRx.SelectedItem
                if Rx_type == "60Gy-5":
                    nb_fx = 5
                    rx_dose = 6000
                elif Rx_type == "60Gy-8":
                    nb_fx = 8
                    rx_dose = 6000
                elif Rx_type == "54Gy-3":
                    nb_fx = 3          
                    rx_dose = 5400
                elif Rx_type == "48Gy-4":
                    nb_fx = 4           
                    rx_dose = 4800
                elif Rx_type == "56Gy-4":
                    nb_fx = 4           
                    rx_dose = 5600
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    plan_name = 'A1'
                    # Check if the user wants to add plan B1 to an existing plan
                    if self.check2.Checked:
                        plan_name = 'B1'
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    poumon.plan_poumon_sbrt(nb_fx,rx_dose,plan_name)
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo 2arcs"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo 2arcs"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   
                
            elif self.SiteButton4.Checked: #SBRT Foie
                Rx_type = self.comboBoxRx.SelectedItem
                if Rx_type[-1] == "3":
                    nb_fx = 3
                elif Rx_type[-1] == "5":
                    nb_fx = 5
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    foie.plan_foie_sbrt(nb_fx)
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Foie"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Foie"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   

            else:
                self.Label6.Text = "Le site n'a pas été sélectionné!"                
                self.Label6.ForeColor = Color.Red

        def cancelClicked(self, sender, args):
            self.Close()
             
        def setupOKButtons(self):
            self.OKbuttonPanel = self.newPanel(0, 275)

            okButton = Button()
            okButton.Text = "OK"
            okButton.Location = Point(25, 50)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(okButton.Left + okButton.Width + 10, okButton.Top)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked

            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            
        # eventhandler
        def comboBox_SelectedValueChangedHandler(self, sender, args):
            Rx_type = self.comboBoxRx.Text


    form = ScriptLauncher()
    Application.Run(form)   
               
    
def plan_launcher():

    class ScriptLauncher(Form):
        def __init__(self):
            self.Text = "Planning Script Launcher"

            self.Width = 750
            self.Height = 550

            self.setupPlanningScriptLauncher()
            self.setupOKButtons()
            self.setupMachineSelectPanel()

            self.Controls.Add(self.LauncherPanel)
            self.Controls.Add(self.OKbuttonPanel)
            self.Controls.Add(self.MachineSelectPanel)
            
        def newPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 300
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 150
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel            
            
            
        def setupPlanningScriptLauncher(self):
            self.LauncherPanel = self.newPanel(0, 0)

            self.Label1 = Label()
            self.Label1.Text = "Choissisez le site à planifier:                       Patient: " + patient.PatientName.replace('^', ', ')
            self.Label1.Location = Point(25, 25)
            self.Label1.Font = Font("Arial", 10, FontStyle.Bold)
            self.Label1.AutoSize = True

            self.SiteButton1 = RadioButton()
            self.SiteButton1.Text = "Prostate"
            self.SiteButton1.Location = Point(40, 50)
            #self.SiteButton1.Checked = True
            self.SiteButton1.CheckedChanged += self.checkedChanged
            
            self.SiteButton2 = RadioButton()
            self.SiteButton2.Text = "Crâne Stéréo"
            self.SiteButton2.Location = Point(40, 75)
            self.SiteButton2.CheckedChanged += self.checkedChanged

            self.SiteButton3 = RadioButton()
            self.SiteButton3.Text = "SBRT Poumon"
            self.SiteButton3.Location = Point(40, 100)
            self.SiteButton3.CheckedChanged += self.checkedChanged
            
            self.SiteButton4 = RadioButton()
            self.SiteButton4.Text = "SBRT Foie"
            self.SiteButton4.Location = Point(40, 125)
            self.SiteButton4.CheckedChanged += self.checkedChanged
            
            self.SiteButton5 = RadioButton()
            self.SiteButton5.Text = "Vertebre"
            self.SiteButton5.Location = Point(40, 150)
            self.SiteButton5.CheckedChanged += self.checkedChanged            
    
            self.Label2 = Label()
            self.Label2.Text = ""
            self.Label2.Location = Point(300, 50)
            self.Label2.AutoSize = True
            self.Label2.Font = Font("Arial", 10)
            self.Label2.ForeColor = Color.Black
            
            self.Label3 = Label()
            self.Label3.Text = ""
            self.Label3.Location = Point(300, 70)
            self.Label3.AutoSize = True
            self.Label3.Font = Font("Arial", 10)
            self.Label3.ForeColor = Color.Black
            
            self.Label4 = Label()
            self.Label4.Text = ""
            self.Label4.Location = Point(300, 90)
            self.Label4.AutoSize = True
            self.Label4.Font = Font("Arial", 10)
            self.Label4.ForeColor = Color.Black
            
            self.Label5 = Label()
            self.Label5.Text = ""
            self.Label5.Location = Point(300, 110)
            self.Label5.AutoSize = True
            self.Label5.Font = Font("Arial", 10)
            self.Label5.ForeColor = Color.Black
            
            self.Label6 = Label()
            self.Label6.Text = ""
            self.Label6.Location = Point(300, 190)
            self.Label6.AutoSize = True
            self.Label6.Font = Font("Arial", 12, FontStyle.Bold)
            self.Label6.ForeColor = Color.Black

            self.Label7 = Label()
            self.Label7.Text = ""
            self.Label7.Location = Point(300, 220)
            self.Label7.AutoSize = True
            self.Label7.Font = Font("Arial", 11, FontStyle.Italic)
            self.Label7.ForeColor = Color.Black
            
            self.comboBoxRx = ComboBox()
            self.comboBoxRx.Parent = self
            self.comboBoxRx.Size = Size(200,40)
            self.comboBoxRx.Location = Point(25,190)
            
            self.check1 = CheckBox()
            self.check1.Text = "Double optimization initiale?"
            self.check1.Location = Point(40, 230)
            self.check1.Width = 300
            self.check1.Checked = False
            
            self.check2 = CheckBox()
            self.check2.Text = ""
            self.check2.Location = Point(40, 255)
            self.check2.Width = 300            

            self.check3 = CheckBox()
            self.check3.Text = ""
            self.check3.Location = Point(40, 280)
            self.check3.Width = 300            
            
            self.LauncherPanel.Controls.Add(self.Label1)
            self.LauncherPanel.Controls.Add(self.Label2)
            self.LauncherPanel.Controls.Add(self.Label3)
            self.LauncherPanel.Controls.Add(self.Label4)
            self.LauncherPanel.Controls.Add(self.Label5)
            self.LauncherPanel.Controls.Add(self.Label6)
            self.LauncherPanel.Controls.Add(self.Label7)            
            self.LauncherPanel.Controls.Add(self.SiteButton1)
            self.LauncherPanel.Controls.Add(self.SiteButton2)
            self.LauncherPanel.Controls.Add(self.SiteButton3)
            self.LauncherPanel.Controls.Add(self.SiteButton4)
            self.LauncherPanel.Controls.Add(self.SiteButton5)
            self.LauncherPanel.Controls.Add(self.check1)
            self.LauncherPanel.Controls.Add(self.check2)
            self.LauncherPanel.Controls.Add(self.check3)            
            #self.LauncherPanel.Controls.Add(self.comboBoxProstate)

            exam_list = []
            for CT in patient.Examinations:
                exam_list.append(CT.Name)
            
            for contour in patient.PatientModel.RegionsOfInterest:
                if not roi.get_roi_approval(contour.Name,patient.Examinations["CT 1"]):
                    VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
                    if "CT 2" in exam_list:
                        VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])
                    else:
                        VolCT2 = 0

                    if VolCT1 == 0:
                        if VolCT2 == 0:
                            oldname = contour.Name
                            contour.Name = ("vide_%s" % oldname)
            
        def checkedChanged(self, sender, args):
            if not sender.Checked:
                return

            # Erase error messages and clear prescription selection menu
            self.Label2.Text = " "
            self.Label3.Text = " "
            self.Label4.Text = " "
            self.Label5.Text = " "
            self.Label6.Text = " "
            self.Label7.Text = " "            
            self.Label2.ForeColor = Color.Black
            self.Label3.ForeColor = Color.Black
            self.Label4.ForeColor = Color.Black
            self.Label5.ForeColor = Color.Black
            self.Label6.ForeColor = Color.Black
            self.Label7.ForeColor = Color.Black    
            self.check1.Text = "Double optimization initiale?"            
            self.check1.Checked = False            
            self.check2.Text = ""
            self.check2.Checked = False
            self.check3.Text = ""
            self.check3.Checked = False
            self.comboBoxRx.Items.Clear()
            PACE = False
            
            roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                        
            if sender.Text == "Prostate":      
                # set selection
                self.comboBoxRx.Text = "Choisissez la prescription"
                self.comboBoxRx.SelectedValueChanged += self.comboBox_SelectedValueChangedHandler
                # add items
                self.comboBoxRx.Items.Add("80Gy-40")
                self.comboBoxRx.Items.Add("66Gy-33")
                self.comboBoxRx.Items.Add("66Gy-22")
                self.comboBoxRx.Items.Add("60Gy-20")
                self.comboBoxRx.Items.Add("37.5Gy-15")
                self.comboBoxRx.Items.Add("PACE 78Gy-39")
                self.comboBoxRx.Items.Add("PACE 36.25Gy-5")
                
                self.check1.Text = "Auto-optimisation initial"
                self.check1.Checked = True
                self.check2.Text = "Est-ce qu'il y a un plan 3D conforme?"
                self.check3.Text = "Sauter la création des lignes d'isodoses"    
            
                boost = False
                for name in roi_names:
                    if 'PTVBOOST' in name.replace(' ', '').upper():
                        boost = True
                        boost_name = name

                #Find ROI(s) that will be used to create PTV A1
                if 'PTV A1' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV A1 déjà existent"
                elif 'PTV 1.5cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm"          
                elif 'PTV 1cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm"
                elif 'PTV_7800' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_7800"
                    self.comboBoxRx.Text = "PACE 78Gy-39"
                    PACE = True
                elif 'PTV_3625' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_3625"            
                    self.comboBoxRx.Text = "PACE 36.25Gy-5"
                    PACE = True
                else:
                    self.Label2.Text = "Attention: Aucun ROI source trouvé pour le PTV A1!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Find ROI that will be used to create PTV A2
                if boost:
                    self.Label3.Text = "Source pour PTV A2: " + boost_name
                elif 'PTV 1cm' in roi_names:
                    self.Label3.Text = "Source pour PTV A2: PTV 1cm"
                else:
                    self.Label3.Text = "Attention: Aucun ROI source trouvé pour le PTV A2!"     
                    self.Label3.ForeColor = Color.Orange                       
                
                #Verify presence of essential contours
                if not PACE:
                    essential_list = ["Table","RECTUM","VESSIE"]
                else:
                    essential_list = ["Table","Rectum","Bladder"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    if not PACE:
                        self.Label4.Text = "ROIs Table, RECTUM et VESSIE trouvés"
                    else:
                        self.Label4.Text = "ROIs Table, Rectum et Bladder trouvés"

                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                 
 

            elif sender.Text == "Crâne Stéréo":     
                self.check1.Checked = True  #Double optimization       
                self.check3.Text = "Sauter la création des lignes d'isodoses"    
                #Identify the PTV
                if 'PTV15' in roi_names:
                    self.Label2.Text = "PTV15 trouvé"
                    self.comboBoxRx.Items.Add("15Gy-1 VMAT")
                    self.comboBoxRx.Items.Add("15Gy-1 IMRT")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("15Gy-1 VMAT")
                elif 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1 VMAT")
                    self.comboBoxRx.Items.Add("18Gy-1 IMRT")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1 VMAT")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                if 'CERVEAU' not in roi_names:
                    self.Label3.Text = "ROI CERVEAU pas trouvé!"
                    self.Label3.ForeColor = Color.Red          
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red    
                    
                    
            elif sender.Text == "SBRT Poumon":   
                self.check1.Checked = True  #Double optimization 
                self.check2.Text = "Ajouter deuxième arc? (plans difficiles)"            
                #Identify the PTV
                self.comboBoxRx.Items.Add("48Gy-4")
                self.comboBoxRx.Items.Add("54Gy-3")
                self.comboBoxRx.Items.Add("56Gy-4")
                self.comboBoxRx.Items.Add("60Gy-5")
                self.comboBoxRx.Items.Add("60Gy-8")
                if 'PTV48' in roi_names:
                    if 'ITV48' in roi_names:
                        self.Label2.Text = "PTV48 et ITV 48 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("48Gy-4")
                    else: 
                        self.Label2.Text = "Attention: PTV48 trouveé, mais ITV48 absent!"     
                        self.Label2.ForeColor = Color.Red   
                elif 'PTV54' in roi_names:
                    if 'ITV54' in roi_names:
                        self.Label2.Text = "PTV54 et ITV54 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("54Gy-3")
                    else:
                        self.Label2.Text = "Attention: PTV54 trouveé, mais ITV54 absent!"     
                        self.Label2.ForeColor = Color.Red       
                elif 'PTV56' in roi_names:
                    if 'ITV56' in roi_names:
                        self.Label2.Text = "PTV56 et ITV56 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("56Gy-4")
                    else:
                        self.Label2.Text = "Attention: PTV56 trouveé, mais ITV56 absent!"     
                        self.Label2.ForeColor = Color.Red                           
                elif 'PTV60' in roi_names:
                    if 'ITV60' in roi_names:
                        self.Label2.Text = "PTV60 et ITV60 trouvés"
                        self.comboBoxRx.Text = "Choisissez la prescription"
                        self.check2.Checked = True
                    else:
                        self.Label2.Text = "Attention: PTV60 trouveé, mais ITV60 absent!"     
                        self.Label2.ForeColor = Color.Red      
                elif 'PTV A1' in roi_names:
                    if 'ITV A1' in roi_names:
                        self.Label2.Text = "PTV A1 et ITV A1 trouvés"
                        self.comboBoxRx.Text = "Choisissez la prescription"
                    else:
                        self.Label2.Text = "Attention: PTV A1 trouveé, mais ITV A1 absent!"     
                        self.Label2.ForeColor = Color.Red    
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé pour plan A1!"     
                    self.Label2.ForeColor = Color.Red     
                if 'PTV B1' in roi_names:
                    if 'ITV B1' in roi_names:
                        if poi.poi_exists("ISO B1"):
                            self.Label5.Text = "PTV B1, ITV B1 et ISO B1 trouvés, possible d'ajouter un plan B1"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"
                        else:
                            self.Label5.Text = "PTV B1 et ITV B1 trouvés, mais ISO B1 absent"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"            
                            self.Label7.Text = "RAPPEL: Pour la création d'un plan B1, il est possible\nd'utiliser un nouvel isocentre avec le nom ISO B1."
                    else:
                        self.Label5.Text = "Attention: PTV B1 trouvé, mais ITV B1 absent!"     
                        self.Label5.ForeColor = Color.Red  
                    
                #Verify presence of essential contours
                essential_list = ["Table","POUMON DRT","POUMON GCHE","BR SOUCHE"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, BR SOUCHE et POUMONs trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO", patient.Examinations['CT 1']):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN", patient.Examinations['CT 1']):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     


            elif sender.Text == "SBRT Foie":     
                self.check1.Checked = True  #Double optimization        
                self.check3.Text = "Sauter la création des lignes d'isodoses"             
                #Identify the PTV
                ptv_name = "NoValue"
                #roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                for name in roi_names:
                    n = name.replace(' ', '').upper()
                    if 'PTV' in n and '-' not in n:
                        try:
                           presc_dose = float(name[3:])
                        except:
                            continue
                        ptv_name = name
                        break  
                if ptv_name != "NoValue":
                    self.Label2.Text = name + " trouvé"
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-3")
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-5")
                    self.comboBoxRx.Text = "Choisissez la prescription"
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Verify presence of essential contours
                essential_list = ["Table","FOIE EXPI","GTV"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, FOIE EXPI et GTV trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     
                 
                 
            elif sender.Text == "Vertebre":     
                self.check1.Checked = True  #Double optimization       
                self.check3.Text = "Sauter la création des lignes d'isodoses"    
                #Identify the PTV
                if 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red                         
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                     
                 
                    
        def okClicked(self, sender, args):
            #Check to see which machine is selected for treatment
            if self.BeamModButton.Checked:
                machine = 'BeamMod'
            elif self.InfinityButton.Checked:
                machine = 'Infinity'
            else:
                self.Label6.Text = "Il faut choisir un appareil avant de continuer"
                self.Label6.ForeColor = Color.Red            
                return
                
            #Prevent users from creating a new plan twice in a row
            if self.Label6.Text == "Script terminé! Cliquez sur Cancel pour sortir.":
                return
                
            #Check to see which site is treated (and therefore which script to launch)
            if self.SiteButton1.Checked: #Prostate
                Rx_type = self.comboBoxRx.SelectedItem
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red  
                else:
                    if Rx_type == "80Gy-40":
                        nb_fx = 40
                    elif Rx_type == "66Gy-33":
                        nb_fx = 33
                    elif Rx_type == "66Gy-22":
                        nb_fx = 22                        
                    elif Rx_type == "60Gy-20":
                        nb_fx = 20   
                    elif Rx_type == "37.5Gy-15":
                        nb_fx = 15
                    elif Rx_type == "PACE 78Gy-39":
                        nb_fx = 39
                    elif Rx_type == "PACE 36.25Gy-5":
                        nb_fx = 5                       
                        
                    if self.check3.Checked:
                        isodose_creation = False
                    else:
                        isodose_creation = True                        
                        
                    # Check whether 3DCRT plan exists    
                    if self.check2.Checked:
                        self.Label6.ForeColor = Color.Black
                        self.Label6.Text = "Création du plan en cours"
                        prostate.create_prostate_plan_A1(nb_fx = nb_fx, plan3D = True, machine = machine, isodose_creation = isodose_creation)
                    else:
                        self.Label6.ForeColor = Color.Black
                        self.Label6.Text = "Création du plan en cours"
                        if nb_fx == 39 or nb_fx ==5: #PACE protocol
                            prostate.create_prostate_plan_PACE(nb_fx = nb_fx, plan3D = False, machine = machine, isodose_creation = isodose_creation)
                        else:
                            prostate.create_prostate_plan_A1(nb_fx = nb_fx, plan3D = False, machine = machine, isodose_creation = isodose_creation)
                        
                    # Auto optimization if requested by user    
                    if self.check1.Checked:
                        if self.check2.Checked: #If A1 grand bassin already exists
                            opt_plan = patient.TreatmentPlans["A2 seul"]  
                        else:
                            opt_plan = patient.TreatmentPlans["A1 seul"]                       
                        self.Label6.Text = "Auto-optimization en cours (1er opt avant fit)"
                        opt_plan.PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Auto-optimization en cours (2er opt avant fit)"
                        opt_plan.PlanOptimizations[0].RunOptimization()                     
                        self.Label6.Text = "Auto-optimization en cours (Ajustement des objectifs)"                        
                        prostate.fit_obj_prostate(plan=opt_plan, beamset = opt_plan.BeamSets[0])
                        opt_plan.PlanOptimizations[0].AutoScaleToPrescription = False
                        opt_plan.PlanOptimizations[0].ResetOptimization()
                        self.Label6.Text = "Auto-optimization en cours (1er opt après fit)"
                        opt_plan.PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Auto-optimization en cours (2er opt après fit)"
                        opt_plan.PlanOptimizations[0].RunOptimization()                           
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green      
                
 
            elif self.SiteButton2.Checked: #Crâne stéréo
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    if self.comboBoxRx.Text[-4:] == "VMAT":
                        treatment_technique = 'VMAT'
                    else:
                        treatment_technique = 'SMLC'
                        
                    if self.check3.Checked:
                        isodose_creation = False
                    else:
                        isodose_creation = True     
                        
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    crane.plan_crane_stereo(machine = machine, isodose_creation = isodose_creation, treatment_technique = treatment_technique)
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Crane"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Crane"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   

                    
            elif self.SiteButton3.Checked: #SBRT Poumon
                Rx_type = self.comboBoxRx.SelectedItem
                if Rx_type == "60Gy-5":
                    nb_fx = 5
                    rx_dose = 6000
                elif Rx_type == "60Gy-8":
                    nb_fx = 8
                    rx_dose = 6000
                elif Rx_type == "54Gy-3":
                    nb_fx = 3          
                    rx_dose = 5400
                elif Rx_type == "48Gy-4":
                    nb_fx = 4           
                    rx_dose = 4800
                elif Rx_type == "56Gy-4":
                    nb_fx = 4           
                    rx_dose = 5600
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    plan_name = 'A1'
                    plan_opt = 0
                    # Check if the user wants to add plan B1 to an existing plan
                    if self.check3.Checked:
                        plan_name = 'B1'
                        plan_opt = 1
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    if self.check2.Checked: # Request for a second arc
                        two_arcs = True
                    else:
                        two_arcs = False
                    poumon.plan_poumon_sbrt(nb_fx,rx_dose,plan_name,two_arcs,machine)
                    # Double optimization if requested by user                 
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Poumon"].PlanOptimizations[plan_opt].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Poumon"].PlanOptimizations[plan_opt].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   
                
            elif self.SiteButton4.Checked: #SBRT Foie
                Rx_type = self.comboBoxRx.SelectedItem
                if Rx_type[-1] == "3":
                    nb_fx = 3
                elif Rx_type[-1] == "5":
                    nb_fx = 5
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    if self.check3.Checked:
                        isodose_creation = False
                    else:
                        isodose_creation = True
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    foie.plan_foie_sbrt(nb_fx,machine,isodose_creation)
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Foie"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Foie"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   

            elif self.SiteButton5.Checked: #Vertebre
                if self.comboBoxRx.SelectedIndex == -1:
                    self.Label6.Text = "Il faut choisir une prescription avant de continuer"
                    self.Label6.ForeColor = Color.Red
                else:
                    if self.check3.Checked:
                        isodose_creation = False
                    else:
                        isodose_creation = True     
                        
                    self.Label6.ForeColor = Color.Black
                    self.Label6.Text = "Création du plan en cours"
                    foie.plan_vertebre_sbrt(machine = machine, isodose_creation = isodose_creation)
                    # Double optimization if requested by user    
                    if self.check1.Checked:
                        self.Label6.Text = "Première optimization en cours"
                        patient.TreatmentPlans["Stereo Vertebre"].PlanOptimizations[0].RunOptimization()
                        self.Label6.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans["Stereo Vertebre"].PlanOptimizations[0].RunOptimization()
                    self.Label6.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                    self.Label6.ForeColor = Color.Green   
                    
                    
                    
            else:
                self.Label6.Text = "Le site n'a pas été sélectionné!"                
                self.Label6.ForeColor = Color.Red

        def cancelClicked(self, sender, args):
            self.Close()

        def setupMachineSelectPanel(self):
            self.MachineSelectPanel = self.miniPanel(0, 300)
            
            self.MachineLabel = Label()
            self.MachineLabel.Text = "Appareil de traitement:"
            self.MachineLabel.Location = Point(25, 30)
            self.MachineLabel.Font = Font("Arial", 10)
            self.MachineLabel.AutoSize = True

            self.BeamModButton = RadioButton()
            self.BeamModButton.Text = "BeamMod (salles 11-12)"
            self.BeamModButton.Location = Point(40, 55)
            self.BeamModButton.Checked = True
            self.BeamModButton.AutoSize = True
            
            self.InfinityButton = RadioButton()
            self.InfinityButton.Text = "Infinity (salles 1-2-6)"
            self.InfinityButton.Location = Point(40, 80)
            self.InfinityButton.Checked = False 
            self.InfinityButton.AutoSize = True            

            self.MachineSelectPanel.Controls.Add(self.MachineLabel)
            self.MachineSelectPanel.Controls.Add(self.BeamModButton)
            self.MachineSelectPanel.Controls.Add(self.InfinityButton)            
            
            
        def setupOKButtons(self):
            self.OKbuttonPanel = self.newPanel(0, 425)

            okButton = Button()
            okButton.Text = "OK"
            okButton.Location = Point(25, 50)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(okButton.Left + okButton.Width + 10, okButton.Top)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked

            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            
        # eventhandler
        def comboBox_SelectedValueChangedHandler(self, sender, args):
            Rx_type = self.comboBoxRx.Text

    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return                 
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
        
    form = ScriptLauncher()
    Application.Run(form)     

   
def plan_launcher_v2():

    class ScriptLauncher(Form):
        def __init__(self):
            self.Text = "Planning Script Launcher v2"

            self.Width = 750
            self.Height = 580

            self.setupPlanningScriptLauncher()
            self.setupOKButtons()
            self.setupMachineSelectPanel()

            self.Controls.Add(self.LauncherPanel)
            self.Controls.Add(self.OKbuttonPanel)
            self.Controls.Add(self.MachineSelectPanel)
            
        def newPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 350
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 130
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel            
            
            
        def setupPlanningScriptLauncher(self):
            self.LauncherPanel = self.newPanel(0, 0)

            self.PatientLabel = Label()
            self.PatientLabel.Text = "Choissisez le site à planifier:                       Patient: " + patient.PatientName.replace('^', ', ')
            self.PatientLabel.Location = Point(25, 25)
            self.PatientLabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.PatientLabel.AutoSize = True

            self.sitecombo = ComboBox()
            self.sitecombo.Parent = self
            self.sitecombo.Size = Size(200,40)
            self.sitecombo.Location = Point(25, 50)
            self.sitecombo.Items.Add("Prostate")
            self.sitecombo.Items.Add("Poumon")     
            self.sitecombo.Items.Add("Crâne")
            self.sitecombo.Items.Add("Foie")                 
            self.sitecombo.Items.Add("Vertebre")              
            self.sitecombo.Text = "Choisissez site"
            self.sitecombo.TextChanged += self.siteselectionChanged           
    
            self.Label2 = Label()
            self.Label2.Text = ""
            self.Label2.Location = Point(300, 50)
            self.Label2.AutoSize = True
            self.Label2.Font = Font("Arial", 10)
            self.Label2.ForeColor = Color.Black
            
            self.Label3 = Label()
            self.Label3.Text = ""
            self.Label3.Location = Point(300, 70)
            self.Label3.AutoSize = True
            self.Label3.Font = Font("Arial", 10)
            self.Label3.ForeColor = Color.Black
            
            self.Label4 = Label()
            self.Label4.Text = ""
            self.Label4.Location = Point(300, 90)
            self.Label4.AutoSize = True
            self.Label4.Font = Font("Arial", 10)
            self.Label4.ForeColor = Color.Black
            
            self.Label5 = Label()
            self.Label5.Text = ""
            self.Label5.Location = Point(300, 110)
            self.Label5.AutoSize = True
            self.Label5.Font = Font("Arial", 10)
            self.Label5.ForeColor = Color.Black
            
            #self.Status = Label()
            #self.Status.Text = ""
            #self.Status.Location = Point(300, 190)
            #self.Status.AutoSize = True
            #self.Status.Font = Font("Arial", 12, FontStyle.Bold)
            #self.Status.ForeColor = Color.Black

            self.Reminder = Label()
            self.Reminder.Text = ""
            self.Reminder.Location = Point(300, 220)
            self.Reminder.AutoSize = True
            self.Reminder.Font = Font("Arial", 11, FontStyle.Italic)
            self.Reminder.ForeColor = Color.Black
            
            self.RxLabel = Label()
            self.RxLabel.Text = "Prescription:"
            self.RxLabel.Location = Point(25, 90)
            self.RxLabel.Font = Font("Arial", 10)
            self.RxLabel.AutoSize = True  
            
            self.comboBoxRx = ComboBox()
            self.comboBoxRx.Parent = self
            self.comboBoxRx.Size = Size(90,40)
            self.comboBoxRx.Location = Point(135,90)            
            
            #self.DoseLabel = Label()
            #self.DoseLabel.Text = "Dose (Gy):"
            #self.DoseLabel.Location = Point(25, 90)
            #self.DoseLabel.Font = Font("Arial", 10)
            #self.DoseLabel.AutoSize = True               

            #self.dosebox = TextBox()
            #self.dosebox.Text = "----"
            #self.dosebox.Location = Point(135, 90)
            #self.dosebox.Width = 40
              
            #self.FxLabel = Label()
            #self.FxLabel.Text = "Nb de fx:"
            #self.FxLabel.Location = Point(25, 120)
            #self.FxLabel.Font = Font("Arial", 10)
            #self.FxLabel.AutoSize = True               

            #self.Fxbox = TextBox()
            #self.Fxbox.Text = "----"
            #self.Fxbox.Location = Point(135, 120)
            #self.Fxbox.Width = 40                        
                        
            self.techniqueLabel = Label()
            self.techniqueLabel.Text = "Technique:"
            self.techniqueLabel.Location = Point(25, 120)
            self.techniqueLabel.Font = Font("Arial", 10)
            self.techniqueLabel.AutoSize = True                
            
            self.techniquecombo = ComboBox()
            self.techniquecombo.Parent = self
            self.techniquecombo.Size = Size(55,40)
            self.techniquecombo.Location = Point(135, 120)                          
            
            self.isodoseLabel = Label()
            self.isodoseLabel.Text = "Créér isodoses?"
            self.isodoseLabel.Location = Point(25, 150)
            self.isodoseLabel.Font = Font("Arial", 10)
            self.isodoseLabel.AutoSize = True               
            
            self.isodosecombo = ComboBox()
            self.isodosecombo.Parent = self
            self.isodosecombo.Size = Size(55,40)
            self.isodosecombo.Location = Point(135, 150)   
            self.isodosecombo.Items.Add("Oui")     
            self.isodosecombo.Items.Add("Non")                 
            self.isodosecombo.Text = 'Oui'                   

            self.SiteLabel = Label()
            self.SiteLabel.Text = "Nom du site:"
            self.SiteLabel.Location = Point(25, 180)
            self.SiteLabel.Font = Font("Arial", 10)
            self.SiteLabel.AutoSize = True               

            self.SiteBox = TextBox()
            self.SiteBox.Text = "A1"
            self.SiteBox.Location = Point(135, 180)
            self.SiteBox.Width = 40                 
   
            self.scanLabel = Label()
            self.scanLabel.Text = "Scan de planif"
            self.scanLabel.Location = Point(25, 210)
            self.scanLabel.Font = Font("Arial", 10)
            self.scanLabel.AutoSize = True               
            
            self.scancombo = ComboBox()
            self.scancombo.Parent = self
            self.scancombo.Size = Size(55,40)
            self.scancombo.Location = Point(135, 210)              
            self.isodosecombo.Text = 'Choissisez'            

            
            self.OptionsLabel = Label()
            self.OptionsLabel.Text = "Options:"
            self.OptionsLabel.Location = Point(25, 250)
            self.OptionsLabel.Font = Font("Arial", 10)
            self.OptionsLabel.AutoSize = True            
                      
            self.check1 = CheckBox()
            self.check1.Text = "Double optimization initiale?"
            self.check1.Location = Point(40, 270)
            self.check1.Width = 300
            self.check1.Checked = False
            
            self.check2 = CheckBox()
            self.check2.Text = ""
            self.check2.Location = Point(40, 295)
            self.check2.Width = 300            

            self.check3 = CheckBox()
            self.check3.Text = ""
            self.check3.Location = Point(40, 320)
            self.check3.Width = 300    
            
            
            
            self.LauncherPanel.Controls.Add(self.PatientLabel)
            self.LauncherPanel.Controls.Add(self.Label2)
            self.LauncherPanel.Controls.Add(self.Label3)
            self.LauncherPanel.Controls.Add(self.Label4)
            self.LauncherPanel.Controls.Add(self.Label5)
            #self.LauncherPanel.Controls.Add(self.Status)
            self.LauncherPanel.Controls.Add(self.Reminder)    
            self.LauncherPanel.Controls.Add(self.RxLabel) 
            #self.LauncherPanel.Controls.Add(self.DoseLabel)
            #self.LauncherPanel.Controls.Add(self.dosebox)  
            #self.LauncherPanel.Controls.Add(self.FxLabel)
            #self.LauncherPanel.Controls.Add(self.Fxbox)
            self.LauncherPanel.Controls.Add(self.isodoseLabel)
            self.LauncherPanel.Controls.Add(self.scanLabel)
            self.LauncherPanel.Controls.Add(self.techniqueLabel)         
            self.LauncherPanel.Controls.Add(self.SiteLabel)
            self.LauncherPanel.Controls.Add(self.SiteBox)      
            self.LauncherPanel.Controls.Add(self.OptionsLabel)            
            self.LauncherPanel.Controls.Add(self.check1)
            self.LauncherPanel.Controls.Add(self.check2)
            self.LauncherPanel.Controls.Add(self.check3)            


            exam_list = []
            for CT in patient.Examinations:
                exam_list.append(CT.Name)
            
            for contour in patient.PatientModel.RegionsOfInterest:
                if not roi.get_roi_approval(contour.Name,patient.Examinations["CT 1"]):
                    VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
                    if "CT 2" in exam_list:
                        VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])
                    else:
                        VolCT2 = 0

                    if VolCT1 == 0 and VolCT2 == 0:
                        contour.Name = ("vide_" + contour.Name)
            
        def siteselectionChanged(self, sender, args):

            # Erase error messages and clear prescription selection menu
            self.Label2.Text = ""
            self.Label3.Text = ""
            self.Label4.Text = ""
            self.Label5.Text = ""
            self.Status.Text = ""
            self.Reminder.Text = ""            
            self.Label2.ForeColor = Color.Black
            self.Label3.ForeColor = Color.Black
            self.Label4.ForeColor = Color.Black
            self.Label5.ForeColor = Color.Black
            self.Status.ForeColor = Color.Black
            self.Reminder.ForeColor = Color.Black    
            self.check1.Text = "Double optimization initiale?"            
            self.check1.Checked = False            
            self.check2.Text = ""
            self.check2.Checked = False
            self.check3.Text = ""
            self.check3.Checked = False
            self.comboBoxRx.Items.Clear()
            self.comboBoxRx.Text = "-----"
            self.techniquecombo.Items.Clear()
            self.techniquecombo.Items.Add("VMAT")                 
            self.techniquecombo.Text = 'VMAT'    
            PACE = False
            
            roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                        
            if self.sitecombo.Text == "Prostate":      
                # add items
                self.comboBoxRx.Items.Add("80Gy-40")
                self.comboBoxRx.Items.Add("66Gy-33")
                self.comboBoxRx.Items.Add("66Gy-22")
                self.comboBoxRx.Items.Add("60Gy-20")
                self.comboBoxRx.Items.Add("37.5Gy-15")
                self.comboBoxRx.Items.Add("PACE 78Gy-39")
                self.comboBoxRx.Items.Add("PACE 36.25Gy-5")
                self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("80Gy-40")
                self.Reminder.Text = "Pour les plans de prostate, le nom du site est\nchoisi de façon automatique (donc la boîte\nNom du site sera ignorée.)"
                self.check1.Text = "Auto-optimisation initial"
                self.check1.Checked = True
                self.check2.Text = "Est-ce qu'il y a un plan 3D conforme?"
            
                boost = False
                for name in roi_names:
                    if 'PTVBOOST' in name.replace(' ', '').upper():
                        boost = True
                        boost_name = name

                #Find ROI(s) that will be used to create PTV A1
                if 'PTV A1' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV A1 déjà existent"
                elif 'PTV 1.5cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm"
                elif 'PTV 1cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm"
                elif 'PTV_7800' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_7800"
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("PACE 78Gy-39")
                    PACE = True
                elif 'PTV_3625' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_3625"  
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("PACE 36.25Gy-5")
                    PACE = True
                else:
                    self.Label2.Text = "Attention: Aucun ROI source trouvé pour le PTV A1!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Find ROI that will be used to create PTV A2
                if boost:
                    self.Label3.Text = "Source pour PTV A2: " + boost_name
                elif 'PTV 1cm' in roi_names:
                    self.Label3.Text = "Source pour PTV A2: PTV 1cm"
                elif not PACE:
                    self.Label3.Text = "Attention: Aucun ROI source trouvé pour le PTV A2!"     
                    self.Label3.ForeColor = Color.Orange                       
                
                #Verify presence of essential contours
                if not PACE:
                    essential_list = ["Table","RECTUM","VESSIE"]
                else:
                    essential_list = ["Table","Rectum","Bladder"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    if not PACE:
                        self.Label4.Text = "ROIs Table, RECTUM et VESSIE trouvés"
                    else:
                        self.Label4.Text = "ROIs Table, Rectum et Bladder trouvés"

                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                 
 

            elif self.sitecombo.Text == "Crâne":     
                self.check1.Checked = True  #Double optimization
                #Identify the PTV
                if 'PTV15' in roi_names:
                    self.Label2.Text = "PTV15 trouvé"
                    self.comboBoxRx.Items.Add("15Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("15Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "15"
                    #self.Fxbox.Text = "1"
                elif 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "18"
                    #self.Fxbox.Text = "1"
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                if 'CERVEAU' not in roi_names:
                    self.Label3.Text = "ROI CERVEAU pas trouvé!"
                    self.Label3.ForeColor = Color.Red          
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red    
                    
                    
            elif self.sitecombo.Text == "Poumon":   
                self.Reminder.Text = "Pour les plans de poumon, le nom du site est\nchoisi de façon automatique (donc la boîte\nNom du site sera ignorée.)"
                self.check1.Checked = True  #Double optimization 
                self.check2.Text = "Ajouter deuxième arc? (plans difficiles)"            
                self.comboBoxRx.Items.Add("48Gy-4")
                self.comboBoxRx.Items.Add("54Gy-3")
                self.comboBoxRx.Items.Add("56Gy-4")
                self.comboBoxRx.Items.Add("60Gy-5")
                self.comboBoxRx.Items.Add("60Gy-8")
                
                #Identify the PTV
                if 'PTV48' in roi_names:
                    if 'ITV48' in roi_names:
                        self.Label2.Text = "PTV48 et ITV48 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("48Gy-4")
                    else: 
                        self.Label2.Text = "Attention: PTV48 trouveé, mais ITV48 absent!"     
                        self.Label2.ForeColor = Color.Red   
                elif 'PTV54' in roi_names:
                    if 'ITV54' in roi_names:
                        self.Label2.Text = "PTV54 et ITV54 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("54Gy-3")
                    else:
                        self.Label2.Text = "Attention: PTV54 trouveé, mais ITV54 absent!"     
                        self.Label2.ForeColor = Color.Red       
                elif 'PTV56' in roi_names:
                    if 'ITV56' in roi_names:
                        self.Label2.Text = "PTV56 et ITV56 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("56Gy-4")
                    else:
                        self.Label2.Text = "Attention: PTV56 trouveé, mais ITV56 absent!"     
                        self.Label2.ForeColor = Color.Red                           
                elif 'PTV60' in roi_names:
                    if 'ITV60' in roi_names:
                        self.Label2.Text = "PTV60 et ITV60 trouvés"
                        self.comboBoxRx.Text = "-----"
                        self.check2.Checked = True
                    else:
                        self.Label2.Text = "Attention: PTV60 trouveé, mais ITV60 absent!"     
                        self.Label2.ForeColor = Color.Red      
                elif 'PTV A1' in roi_names:
                    if 'ITV A1' in roi_names:
                        self.Label2.Text = "PTV A1 et ITV A1 trouvés"
                        self.comboBoxRx.Text = "-----"
                    else:
                        self.Label2.Text = "Attention: PTV A1 trouveé, mais ITV A1 absent!"     
                        self.Label2.ForeColor = Color.Red    
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé pour plan A1!"     
                    self.Label2.ForeColor = Color.Red     
                if 'PTV B1' in roi_names:
                    if 'ITV B1' in roi_names:
                        if poi.poi_exists("ISO B1"):
                            self.Label5.Text = "PTV B1, ITV B1 et ISO B1 trouvés, possible d'ajouter un plan B1"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"
                        else:
                            self.Label5.Text = "PTV B1 et ITV B1 trouvés, mais ISO B1 absent"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"            
                            self.Reminder.Text = "RAPPEL: Pour la création d'un plan B1, il est possible\nd'utiliser un nouvel isocentre avec le nom ISO B1."
                    else:
                        self.Label5.Text = "Attention: PTV B1 trouvé, mais ITV B1 absent!"     
                        self.Label5.ForeColor = Color.Red  
                    
                #Verify presence of essential contours
                essential_list = ["Table","POUMON DRT","POUMON GCHE","BR SOUCHE"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, BR SOUCHE et POUMONs trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO", patient.Examinations['CT 1']):           
                    self.Label4.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN", patient.Examinations['CT 1']):           
                    self.Label4.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     


            elif self.sitecombo.Text == "Foie":     
                self.check1.Checked = True  #Double optimization       
                #Identify the PTV
                ptv_name = "NoValue"
                #roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                for name in roi_names:
                    n = name.replace(' ', '').upper()
                    if 'PTV' in n and '-' not in n:
                        try:
                           presc_dose = float(name[3:])
                        except:
                            continue
                        ptv_name = name
                        break  
                if ptv_name != "NoValue":
                    self.Label2.Text = ptv_name + " trouvé"
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-3")
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-5")
                    self.comboBoxRx.Text = "Choisissez"
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Verify presence of essential contours
                essential_list = ["Table","FOIE EXPI","GTV"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, FOIE EXPI et GTV trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     
                 
                 
            elif self.sitecombo.Text == "Vertebre":     
                self.check1.Checked = True  #Double optimization        
                #Identify the PTV
                if 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red                         
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                     
                 
                    
        def okClicked(self, sender, args):
            #Prevent users from creating a new plan twice in a row
            if self.Status.Text == "Script terminé! Cliquez sur Cancel pour sortir.":
                return
                
            #Check to see which machine is selected for treatment
            if self.BeamModButton.Checked:
                machine = 'BeamMod'
            elif self.InfinityButton.Checked:
                machine = 'Infinity'
            else:
                self.Status.Text = "Il faut choisir un appareil avant de continuer"
                self.Status.ForeColor = Color.Red            
                return               
                
            #Check whether to create isodose lines
            if self.isodosecombo.Text == 'Oui':
                isodose_creation = True
            else:
                isodose_creation = False
                
            #Check treatment techniqueLabel
            if self.techniquecombo.Text == 'IMRT':
                treatment_technique = 'SMLC'
            else:
                treatment_technique = 'VMAT'
                
            #Ensure that a prescription has been selected
            if self.comboBoxRx.Text == '-----' or self.comboBoxRx.SelectedIndex == -1:
                self.Status.Text = "Il faut choisir une prescription avant de continuer"
                self.Status.ForeColor = Color.Red              
                return
            
            #Determine prescription dose (in cGy) and number of fractions
            pace = False
            temp_string = self.comboBoxRx.Text
            if temp_string[:5] == 'PACE ':
                temp_string = temp_string[5:]
                pace = True
            try:
                rx_dose = int(float(temp_string.split('Gy-')[0]) * 100)
                nb_fx = int(temp_string.split('Gy-')[1])
            except:
                self.Status.Text = "Impossible de lire dose de prescription ou nombre de fractions"
                self.Status.ForeColor = Color.Red              
                return
                

            #Check to see which site is treated (and therefore which script to launch)
            if self.sitecombo.Text == 'Prostate':
            
                if nb_fx == 15: #37.5Gy-15 plans are initially planned as 60Gy-24 using clinical goals for a 60Gy-20 prescription
                    nb_fx = 24
                    rx_dose = 6000
                    
                #Set the plan type (used for adding clinical goals later)
                if pace:
                    plan_type = 'Prostate PACE'
                elif nb_fx == 40:
                    plan_type = 'Prostate'
                else:
                    plan_type = 'Lit Prostatique'

                d = dict(patient = patient,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         treatment_technique = treatment_technique,
                         plan_type = plan_type)        

                self.Status.ForeColor = Color.Black
                
                self.Status.Text = "En cours: Gestion des POIs"
                prostate.prostate_A1_pois(plan_data = d)
                
                self.Status.Text = "En cours: Création des ROIs (peut prendre un peu de temps)"
                prostate.prostate_A1_rois(plan_data = d)
                
                self.Status.Text = "En cours: Ajout du plan et beamset"
                prostate.prostate_A1_add_plan_and_beamset(plan_data = d)           

                self.Status.Text = "En cours: Ajout des faisceaux"
                beams.add_beams_prostate_A1(beamset=patient.TreatmentPlans['A1 seul'].BeamSets['A1'])          

                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                prostate.prostate_A1_opt_settings(plan_data = d)                
            
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation"
                optimization_objectives.add_opt_obj_prostate_A1(plan=patient.TreatmentPlans['A1 seul'])
                
                self.Status.Text = "En cours: Ajout des clinical goals"
                if nb_fx == 24: #37.5Gy-15 plans are initially planned as 60Gy-24 using clinical goals for a 60Gy-20 prescription
                    clinical_goals.add_dictionary_cg(plan_type, rx_dose/100, 20, plan=patient.TreatmentPlans['A1 seul'])
                else:
                    clinical_goals.add_dictionary_cg(plan_type, rx_dose/100, nb_fx, plan=patient.TreatmentPlans['A1 seul'])
                
                if self.check2.Checked and plan_type != 'Prostate PACE': #If 3DCRT grand bassin plan exists
                    self.Status.Text = "En cours: Changement de noms pour A2-A3"
                    prostate.prostate_A1_rename(plan_data = d)
                    isodose_creation = False
            
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    prostate.prostate_A1_create_isodose_lines(plan_data = d)
            
                if plan_type == 'Prostate PACE':
                    self.Status.Text = "En cours: Changement du nom du PTV"
                    if roi.roi_exists("PTV_7800"):
                        patient.PatientModel.RegionsOfInterest["PTV_7800"].Name = "PTV A1 78Gy"
                    if roi.roi_exists("PTV_3625"):
                        patient.PatientModel.RegionsOfInterest["PTV_3625"].Name = "PTV A1 36.25Gy"                        
                    
                # Auto optimization if requested by user    
                if self.check1.Checked:
                    if self.check2.Checked and plan_type != 'Prostate PACE': #If A1 grand bassin already exists
                        opt_plan = patient.TreatmentPlans["A2 seul"]  
                    else:
                        opt_plan = patient.TreatmentPlans["A1 seul"]                       
                    self.Status.Text = "Auto-optimization en cours (1er opt avant fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Auto-optimization en cours (2er opt avant fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()                     
                    self.Status.Text = "Auto-optimization en cours (Ajustement des objectifs)"                        
                    prostate.fit_obj_prostate(plan=opt_plan, beamset = opt_plan.BeamSets[0])
                    opt_plan.PlanOptimizations[0].AutoScaleToPrescription = False
                    opt_plan.PlanOptimizations[0].ResetOptimization()
                    self.Status.Text = "Auto-optimization en cours (1er opt après fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Auto-optimization en cours (2er opt après fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()                   
                    
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green      
                
 
            elif self.sitecombo.Text == 'Crâne':
                if rx_dose == 1500:
                    ptv = patient.PatientModel.RegionsOfInterest["PTV15"]
                elif rx_dose == 1800:  
                    ptv = patient.PatientModel.RegionsOfInterest["PTV18"]                        
            
                #Create the plan data dictionary to send to the component scripts                        
                #d = {'plan_name':'A1'}
                d = dict(patient = patient,
                         plan_name = 'Stereo Crane',
                         beamset_name = 'Stereo Crane',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = ptv,
                         treatment_technique = treatment_technique)                        
                    
                self.Status.ForeColor = Color.Black
                
                self.Status.Text = "En cours: Gestion des POIs"
                crane.crane_stereo_pois(plan_data = d)
                
                self.Status.Text = "En cours: Création des ROIs (peut prendre un peu de temps)"
                crane.crane_stereo_rois(plan_data = d)
                
                self.Status.Text = "En cours: Ajout du plan et beamset"
                crane.crane_stereo_add_plan_and_beamset(plan_data = d)           

                self.Status.Text = "En cours: Ajout des faisceaux"
                crane.crane_stereo_add_beams(plan_data = d)    

                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                crane.crane_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation"
                optimization_objectives.add_opt_obj_brain_stereo(patient_plan = patient.TreatmentPlans[d['plan_name']])

                self.Status.Text = "En cours: Ajout des clinical goals"
                clinical_goals.add_dictionary_cg('Crane Stereo', rx_dose/100, 1, plan = patient.TreatmentPlans[d['plan_name']])
                
                self.Status.Text = "En cours: Changement du nom du PTV"
                crane.crane_stereo_rename_ptv(plan_data = d)

                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    crane.crane_stereo_create_isodose_lines(plan_data = d)                    
                
                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "En cours: Première optimization"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "En cours: Deuxième optimization"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   

                    
            elif self.sitecombo.Text == 'Poumon':            
                # Check if the user wants to add plan B1 to an existing plan
                if self.check3.Checked:
                    site_name = 'B1'
                    plan_opt = 1 #Assume for now that B1 will be added as a second beamset in the original plan
                    self.SiteBox.Text = 'B1'
                    ptv_name = 'PTV B1'
                    itv_name = 'ITV B1'
                else:
                    site_name = 'A1' #It's too complicated to accept arbitrary site names for lung cases, sorry
                    plan_opt = 0
                    #Determine PTV and ITV names (based on message displayed in Label2 - does not work for B1 plans because message is changed!)
                    ptv_name = self.Label2.Text
                    ptv_name = ptv_name[0:6] #Include 6 characters in case PTV A1 is used
                    if ptv_name[-1] == ' ':
                        ptv_name = ptv_name[0:5] #Drop blank space at the end if applicable
                    itv_name = 'I' + ptv_name[1:]

                # See if second arc was requested
                if self.check2.Checked: 
                    two_arcs = True
                else:
                    two_arcs = False
            
                #Create the plan data dictionary to send to the component scripts                        
                d = dict(patient = patient,
                         plan_name = 'Stereo Poumon',
                         beamset_name = site_name,
                         site_name = site_name,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest[ptv_name],
                         itv = patient.PatientModel.RegionsOfInterest[itv_name],
                         treatment_technique = treatment_technique,
                         two_arcs = two_arcs)                            
                    
                self.Status.ForeColor = Color.Black
                
                self.Status.Text = "En cours: Gestion des POIs"
                poumon.poumon_stereo_pois(plan_data = d)
                
                self.Status.Text = "En cours: Création des ROIs"
                new_names = poumon.poumon_stereo_rois(plan_data = d)

                self.Status.Text = "En cours: Ajout du plan et beamset"
                new_plan_name = poumon.poumon_stereo_add_plan_and_beamset(plan_data = d)
                d['plan_name'] = new_plan_name #Update plan name because B1 plan will either be added to existing Stereo Poumon or else will be called B1

                self.Status.Text = "En cours: Ajout des faisceaux"
                beams.add_beams_lung_stereo(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], examination=d['exam'], ptv_name=d['ptv'].Name, two_arcs=d['two_arcs'])                    
                
                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                poumon.poumon_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                clinical_goals.smart_cg_lung_stereo(plan=patient.TreatmentPlans[d['plan_name']], examination=d['exam'], nb_fx=nb_fx, rx_dose=rx_dose, ptv=d['ptv'], beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']])              
                
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    poumon.poumon_stereo_create_isodose_lines(plan_data=d)
                
                # Double optimization if requested by user                 
                if self.check1.Checked:
                    if new_plan_name == 'B1': #This indicates a new plan was made (because old one was locked) which only has one beamset, so we need to set plan_opt to 0
                        plan_opt = 0
                    self.Status.Text = "Première optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[plan_opt].RunOptimization()
                    self.Status.Text = "Deuxième optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[plan_opt].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   
                
                
            elif self.sitecombo.Text == 'Foie':
            
                d = dict(patient = patient,
                         plan_name = 'Stereo Foie',
                         beamset_name = 'Stereo',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest[self.Label2.Text.split()[0]],
                         treatment_technique = treatment_technique)     
                         
                         
                self.Status.ForeColor = Color.Black
                self.Status.Text = "En cours: Gestion des POIs"
                poi.create_iso(exam = d['exam'])
                poi.auto_assign_poi_types()
                poi.erase_pois_not_in_list()
                
                self.Status.Text = "En cours: Création des ROIs"
                roi.auto_assign_roi_types_v2()
                roi.generate_BodyRS_plus_Table()
                foie.foie_stereo_rois(plan_data = d)

                self.Status.Text = "En cours: Ajout du plan et beamset"
                foie.foie_stereo_add_plan_and_beamset(plan_data = d)

                self.Status.Text = "En cours: Ajout des faisceaux"     
                beams.add_beams_prostate_A1(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], site_name=d['site_name'])
                
                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                foie.foie_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                clinical_goals.smart_cg_foie_sbrt(plan=patient.TreatmentPlans[d['plan_name']], ptv=d['ptv'], Rx_dose=d['rx_dose']/100.0)
              
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    foie.foie_stereo_create_isodose_lines(plan_data = d)

                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "Première optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Deuxième optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   

                
            elif self.sitecombo.Text == 'Vertebre':
                
                d = dict(patient = patient,
                         plan_name = 'Stereo Vertebre',
                         beamset_name = 'Stereo',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest['PTV18'],
                         treatment_technique = treatment_technique)     
                         
                         
                self.Status.ForeColor = Color.Black
                self.Status.Text = "En cours: Gestion des POIs"
                poi.create_iso(exam = d['exam'])
                poi.auto_assign_poi_types()
                poi.erase_pois_not_in_list()
                
                self.Status.Text = "En cours: Création des ROIs"
                roi.auto_assign_roi_types_v2()
                roi.generate_BodyRS_plus_Table()
                foie.vertebre_stereo_rois(plan_data = d)

                self.Status.Text = "En cours: Ajout du plan et beamset"
                foie.foie_stereo_add_plan_and_beamset(plan_data = d) #OK to use same function as for liver cases

                self.Status.Text = "En cours: Ajout des faisceaux"     
                beams.add_beams_vertebre_stereo(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], site_name=d['site_name'])
                
                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                foie.vertebre_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                clinical_goals.smart_cg_vertebre(plan=patient.TreatmentPlans[d['plan_name']])
              
                self.Status.Text = "En cours: Changement du nom du PTV"
                crane.crane_stereo_rename_ptv(plan_data = d) #OK to borrow from crâne
              
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    foie.vertebre_stereo_create_isodose_lines(plan_data = d)

                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "Première optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Deuxième optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   
                    
                    
                    
            else:
                self.Status.Text = "Le site n'a pas été sélectionné!"                
                self.Status.ForeColor = Color.Red

        def cancelClicked(self, sender, args):
            self.Close()

        def setupMachineSelectPanel(self):
            self.MachineSelectPanel = self.miniPanel(0, 350)
            
            self.MachineLabel = Label()
            self.MachineLabel.Text = "Appareil de traitement:"
            self.MachineLabel.Location = Point(25, 30)
            self.MachineLabel.Font = Font("Arial", 10)
            self.MachineLabel.AutoSize = True

            self.BeamModButton = RadioButton()
            self.BeamModButton.Text = "BeamMod (salles 11-12)"
            self.BeamModButton.Location = Point(40, 55)
            self.BeamModButton.Checked = True
            self.BeamModButton.AutoSize = True
            
            self.InfinityButton = RadioButton()
            self.InfinityButton.Text = "Infinity (salles 1-2-6)"
            self.InfinityButton.Location = Point(40, 80)
            self.InfinityButton.Checked = False 
            self.InfinityButton.AutoSize = True            

            self.MachineSelectPanel.Controls.Add(self.MachineLabel)
            self.MachineSelectPanel.Controls.Add(self.BeamModButton)
            self.MachineSelectPanel.Controls.Add(self.InfinityButton)            
            
            
        def setupOKButtons(self):
            self.OKbuttonPanel = self.newPanel(0, 455)

            okButton = Button()
            okButton.Text = "OK"
            okButton.Location = Point(25, 50)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(okButton.Left + okButton.Width + 10, okButton.Top)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.Status = Label()
            self.Status.Text = ""
            self.Status.Location = Point(200, 50)
            self.Status.AutoSize = True
            self.Status.Font = Font("Arial", 12, FontStyle.Bold)
            self.Status.ForeColor = Color.Black

            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.Status)
            
            if roi.roi_exists('CERVEAU'):
                self.sitecombo.Text = 'Crâne'
            elif roi.roi_exists('PROSTATE'):
                self.sitecombo.Text = 'Prostate'   
            elif roi.roi_exists('ITV48') or roi.roi_exists('ITV54') or roi.roi_exists('ITV56') or roi.roi_exists('ITV60'):
                self.sitecombo.Text = 'Poumon'
            elif roi.roi_exists('FOIE EXPI'):
                self.sitecombo.Text = 'Foie'                   

            for CT in patient.Examinations:
                self.scancombo.Items.Add(CT.Name)
            try:
                self.scancombo.SelectedIndex = self.scancombo.FindStringExact("CT 1")
            except:
                self.scancombo.SelectedIndex = 0
                
    #Check for common errors while importing patient and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return      
        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
        
    form = ScriptLauncher()
    Application.Run(form)     

  
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
          
                    
def plan_poumon_sbrt(nb_fx = None, rx_dose = None, plan_name = 'A1', two_arcs = False, machine = 'BeamMod'):
    """
    Voir :py:mod:`plan_poumoun_sbrt`.
    """

    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    msg = ''

    if lib.check_version(4.7):
        scan_index = 1 #Apparently the index is the same even though the names are swapped?
        scan_name = "CT 1"
        if plan_name == 'A1':
            patient.Examinations[scan_index].EquipmentInfo.SetImagingSystemReference(ImagingSystemName=patient.Examinations[0].EquipmentInfo.ImagingSystemReference.ImagingSystemName)
    else:
        scan_index = 1
        scan_name = "CT 2"
        # Change Imaging System for 2nd scan
        patient.Examinations[scan_index].SetImagingSystem(ImagingSystemName="HOST-7228")

    #Create ISO
    if not poi.poi_exists("ISO", patient.Examinations[scan_name]):
        if poi.poi_exists("REF SCAN", patient.Examinations[scan_name]):
            REF_SCAN_coords = poi.get_poi_coordinates('REF SCAN',patient.Examinations[scan_name])
            poi.create_poi(REF_SCAN_coords,'ISO','Blue','Isocenter',patient.Examinations[scan_name])
    
    # Assign Point Types
    poi.auto_assign_poi_types()

    # Assign ROI Types (excerpted from roi.auto_assign_roi_types)
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    if plan_name == 'A1':
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

    # Create BodyRS+Table (except for additional plans)
    if plan_name == "A1":
        roi.generate_BodyRS_plus_Table(struct=scan_index)
        
    # Rename contours if this is plan B1 (unless they are approved)
    if plan_name == 'B1':
        roi_list = ['PTV48','PTV54','PTV60','ITV48','ITV54','ITV60']
        for name in roi_names:
            if name in roi_list:
                if 'PTV' in name:
                    if not roi.get_roi_approval(name, patient.Examinations[scan_name]):
                        patient.PatientModel.RegionsOfInterest[name].Name = 'PTV A1 ' + name[-2:] + 'Gy'
                elif 'ITV' in name:
                    if not roi.get_roi_approval(name, patient.Examinations[scan_name]):                
                        patient.PatientModel.RegionsOfInterest[name].Name = 'ITV A1 ' + name[-2:] + 'Gy'
                    
        # Rename optimization contours from A1 to avoid errors and confusion in plan B1
        roi_list = ['PTV+3mm','PTV+1.3cm','PTV+2cm','RING_1','RING_2','RING_3','r50','TISSU SAIN A 2cm','COMBI PMN-ITV-BR','OPT COMBI PMN']
        for name in roi_names:
            if name in roi_list:
                if 'PTV' in name:
                    if not roi.get_roi_approval(name, patient.Examinations[scan_name]):
                        patient.PatientModel.RegionsOfInterest[name].Name = name.replace('PTV','PTV A1')
                else:
                    if not roi.get_roi_approval(name, patient.Examinations[scan_name]):
                        patient.PatientModel.RegionsOfInterest[name].Name += " A1"
            elif 'dans PTV' in name:
                if not roi.get_roi_approval(name, patient.Examinations[scan_name]):
                    patient.PatientModel.RegionsOfInterest[name].Name = name.replace('dans PTV','dans PTV A1')
            elif 'hors PTV' in name:
                if not roi.get_roi_approval(name, patient.Examinations[scan_name]):
                    patient.PatientModel.RegionsOfInterest[name].Name = name.replace('hors PTV','hors PTV A1')
                    
    # Identify which PTV and ITV to use for creation of optimization contours, then rename them to standard format
    suffix = ' ' + str(rx_dose/100)
    suffix = suffix + 'Gy'
    suffix = suffix.replace('.0Gy','Gy')
    if plan_name == 'A1':
        if roi.roi_exists("PTV48", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.RegionsOfInterest["PTV48"]
            itv = patient.PatientModel.RegionsOfInterest["ITV48"]
        elif roi.roi_exists("PTV54", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.RegionsOfInterest["PTV54"]
            itv = patient.PatientModel.RegionsOfInterest["ITV54"]
        elif roi.roi_exists("PTV56", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.RegionsOfInterest["PTV56"]
            itv = patient.PatientModel.RegionsOfInterest["ITV56"]                  
        elif roi.roi_exists("PTV60", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.RegionsOfInterest["PTV60"]
            itv = patient.PatientModel.RegionsOfInterest["ITV60"]
        elif roi.roi_exists("PTV A1", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.RegionsOfInterest["PTV A1"]
            itv = patient.PatientModel.RegionsOfInterest["ITV A1"]       
        ptv.Name = 'PTV ' + plan_name + suffix
        itv.Name = 'ITV ' + plan_name + suffix            
    elif plan_name == 'B1':
        #Need to check if PTV/ITV B1 are locked. If so, must make new copies to work on.
        if roi.get_roi_approval("PTV B1", patient.Examinations[scan_name]):
            ptv = patient.PatientModel.CreateRoi(Name=('PTV ' + plan_name + suffix), Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['PTV ' + plan_name + suffix].SetMarginExpression(SourceRoiName='PTV B1', MarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['PTV ' + plan_name + suffix].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV B1"]
            ptv.Name = 'PTV ' + plan_name + suffix            
        if roi.get_roi_approval("ITV B1", patient.Examinations[scan_name]):
            itv = patient.PatientModel.CreateRoi(Name=('ITV ' + plan_name + suffix), Color="Purple", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['ITV ' + plan_name + suffix].SetMarginExpression(SourceRoiName='ITV B1', MarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['ITV ' + plan_name + suffix].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
        else:
            itv = patient.PatientModel.RegionsOfInterest["ITV B1"]       
            itv.Name = 'ITV ' + plan_name + suffix               
        roi.set_roi_type(ptv.Name, 'Ptv', 'Target')
        roi.set_roi_type(itv.Name, 'TreatedVolume', 'Target')

               
    # Generate optimization contours
    # Create PTV+3mm, PTV+1.3cm and PTV+2cm
    if plan_name == 'A1':
        roi_string = 'PTV'
    elif plan_name == 'B1':
        roi_string = 'PTV B1'
    patient.PatientModel.CreateRoi(Name=roi_string+"+3mm", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+3mm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3})
    patient.PatientModel.RegionsOfInterest[roi_string+"+3mm"].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name=roi_string+"+1.3cm", Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+1.3cm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3})
    patient.PatientModel.RegionsOfInterest[roi_string+"+1.3cm"].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name=roi_string+"+2cm", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[roi_string+"+2cm"].SetMarginExpression(SourceRoiName=ptv.Name, MarginSettings={'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2})
    patient.PatientModel.RegionsOfInterest[roi_string+"+2cm"].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create RINGs
    if plan_name == 'A1':
        roi_string = ''
    elif plan_name == 'B1':
        roi_string = ' B1'    
    patient.PatientModel.CreateRoi(Name="RING_1"+roi_string, Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_1'+roi_string].SetWallExpression(SourceRoiName=ptv.Name, OutwardDistance=0.3, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_1'+roi_string].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="RING_2"+roi_string, Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_2'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+3mm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_2'+roi_string].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="RING_3"+roi_string, Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['RING_3'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+1.3cm", OutwardDistance=1.5, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['RING_3'+roi_string].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    patient.PatientModel.CreateRoi(Name="r50"+roi_string, Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['r50'+roi_string].SetWallExpression(SourceRoiName="PTV" + roi_string + "+2cm", OutwardDistance=1, InwardDistance=0)
    patient.PatientModel.RegionsOfInterest['r50'+roi_string].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create PEAU
    if plan_name == 'A1':
        patient.PatientModel.CreateRoi(Name="PEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['PEAU'].SetWallExpression(SourceRoiName="BodyRS", OutwardDistance=0, InwardDistance=0.5)
        patient.PatientModel.RegionsOfInterest['PEAU'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Create TISSU SAIN A 2cm and COMBI PMN-ITV-BR
    if plan_name == 'A1':
        patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [("PTV" + roi_string + "+2cm")], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
        patient.PatientModel.CreateRoi(Name="COMBI PMN-ITV-BR", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv.Name, "BR SOUCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['COMBI PMN-ITV-BR'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    elif plan_name == 'B1':
        #Determine name of PTV and ITV for beamset A1
        for rois in patient.PatientModel.RegionsOfInterest:
            if rois.Name[:6] == "PTV A1":
                ptv_A1_name = rois.Name
                itv_A1_name = "I" + rois.Name[1:]
                break
        patient.PatientModel.CreateRoi(Name="TISSU SAIN A 2cm A1+B1", Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm A1+B1'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name,ptv_A1_name], 'MarginSettings': {'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['TISSU SAIN A 2cm A1+B1'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
        patient.PatientModel.CreateRoi(Name="COMBI PMN-2ITVs-BR", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['COMBI PMN-2ITVs-BR'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv.Name,itv_A1_name,"BR SOUCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['COMBI PMN-2ITVs-BR'].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    #Creat OPT COMBI PMN
    patient.PatientModel.CreateRoi(Name="OPT COMBI PMN"+roi_string, Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'+roi_string].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["POUMON DRT", "POUMON GCHE"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv.Name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['OPT COMBI PMN'+roi_string].UpdateDerivedGeometry(Examination=patient.Examinations[scan_name])
    # Rename PAROI if necessary
    if plan_name == 'A1':    
        if not roi.roi_exists("PAROI", patient.Examinations[scan_name]):
            if roi.roi_exists("PAROI D", patient.Examinations[scan_name]):
                 patient.PatientModel.RegionsOfInterest["PAROI D"].Name = "PAROI"
            elif roi.roi_exists("PAROI DRT", patient.Examinations[scan_name]):
                 patient.PatientModel.RegionsOfInterest["PAROI DRT"].Name = "PAROI"
            elif roi.roi_exists("PAROI G", patient.Examinations[scan_name]):
                 patient.PatientModel.RegionsOfInterest["PAROI G"].Name = "PAROI"             
            elif roi.roi_exists("PAROI GCHE", patient.Examinations[scan_name]):
                 patient.PatientModel.RegionsOfInterest["PAROI GCHE"].Name = "PAROI"             
                        
    # Remove material override from all ROIs
    if plan_name == "A1":
        for rois in patient.PatientModel.RegionsOfInterest:
            rois.SetRoiMaterial(Material=None)

    # Add Treatment plan (only for A1)
    if plan_name == "A1":
        plan = patient.AddNewPlan(PlanName=("Stereo Poumon"), PlannedBy="", Comment="", ExaminationName=scan_name, AllowDuplicateNames=False)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})
    elif plan_name == "B1":
        plan = lib.get_current_plan()
        try: #If the plan is not approved, then plan.Review doesn't exist and querying it will crash the script
            if plan.Review.ApprovalStatus == "Approved": #Add new plan, since we can't add a beamset to a locked plan. Otherwise, add B1 beamset to existing plan.
                plan = patient.AddNewPlan(PlanName=("Poumon B1"), PlannedBy="", Comment="", ExaminationName=scan_name, AllowDuplicateNames=False)
                plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2, 'y': 0.2, 'z': 0.2})        
        except: #If the plan is not approved, then we don't need to do anything
            pass

    # Add beamset
    beamset = plan.AddNewBeamSet(Name=plan_name, ExaminationName=scan_name, MachineName=machine, NominalEnergy=None,
                                      Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=nb_fx, CreateSetupBeams=False, Comment="VMAT")
    beamset.AddDosePrescriptionToRoi(RoiName=ptv.Name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=rx_dose, RelativePrescriptionLevel=1)

    # Add arcs
    beams.add_beams_lung_stereo(beamset=beamset, examination=patient.Examinations[scan_name], ptv_name=ptv.Name, two_arcs=two_arcs)

    # Set optimization parameters
    optim.set_optimization_parameters(plan=plan)

    # Set VMAT conversion parameters  
    fx_dose = rx_dose / nb_fx    
    optim.set_vmat_conversion_parameters(max_arc_delivery_time=int(fx_dose/100.0*20), plan=plan)

    # Add clinical goals and optimization objectives
    clinical_goals.smart_cg_lung_stereo(plan=plan, examination=patient.Examinations[scan_name], nb_fx=nb_fx, rx_dose=rx_dose, ptv=ptv, beamset=plan.BeamSets[plan_name])

    # Set Dose Color Table (only for plan A1, might crash RayStation if dose color table already exists)
    if plan_name == "A1":
        eval.remove_all_isodose_lines()
        patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose
        fivegy = float(100*500/rx_dose)

        patient.CaseSettings.DoseColorMap.ColorMapReferenceType = "ReferenceValue"
        eval.add_isodose_line_rgb(dose=0, r=0, g=0, b=0, alpha=0)
        eval.add_isodose_line_rgb(dose=fivegy, r=0, g=128, b=0, alpha=128)
        eval.add_isodose_line_rgb(dose=25, r=0, g=0, b=160, alpha=128)
        eval.add_isodose_line_rgb(dose=50, r=128, g=128, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=95, r=0, g=255, b=255, alpha=255)
        eval.add_isodose_line_rgb(dose=100, r=255, g=0, b=0, alpha=255)
        eval.add_isodose_line_rgb(dose=120, r=255, g=255, b=0, alpha=255)
        patient.CaseSettings.DoseColorMap.PresentationType = 'Absolute'

    # Erase any points other than ISO, ISOCENTRE, ISO SCAN or REF SCAN
    if plan_name == "A1":
        for points in patient.PatientModel.PointsOfInterest:
            if not points.Name.upper() in ["ISO", "ISOCENTRE", "ISO SCAN", "REF SCAN", "ISO B1"]:
                points.DeleteRoi()

    # For B1 plans, rename optimization contours to avoid confusion
    # WAIT STOP this now has to be done in smart_cg_poumon, since the A1 optimization contours may be approved and will still have their original names. Ugh.
    """
    if plan_name == "B1":
        roi_list = ['PTV+3mm','PTV+1.3cm','PTV+2cm','RING_1','RING_2','RING_3','r50','TISSU SAIN A 2cm','COMBI PMN-ITV-BR','OPT COMBI PMN']
        for name in roi_names:
            if name in roi_list:
                if 'PTV' in name:
                    patient.PatientModel.RegionsOfInterest[name].Name = name.replace('PTV','PTV B1')
                else:
                    patient.PatientModel.RegionsOfInterest[name].Name += " B1"
            elif 'dans PTV' in name and 'A1' not in name:
                patient.PatientModel.RegionsOfInterest[name].Name = name.replace('dans PTV','dans PTV B1')
            elif 'hors PTV' in name:
                patient.PatientModel.RegionsOfInterest[name].Name = name.replace('hors PTV','hors PTV B1')
    """
     
    
def finaliser_plan_poumon_sbrt():
    """
    Voir :py:mod:`finaliser_plan_poumon_sbrt`.
    """

    patient = lib.get_current_patient()
    # examination = lib.get_current_examination()
    plan = lib.get_current_plan()

    if lib.check_version(4.7):
        scan_name = "CT 1"
        expi_scan = "CT 2"
    else:
        scan_name = "CT 2"
        expi_scan = "CT 1"

    # Rename OAR contours for SuperBridge transfer        
    for rois in patient.PatientModel.RegionsOfInterest:
        if rois.Name in ["GTV expi", "MOELLE","ITV48","ITV54","ITV56","ITV60"]:
            rois.Name += "*"
            patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=rois.Name)        
        
    colors = ["Red","Green","Blue","Yellow","Orange"]
    
    for i, bs in enumerate(plan.BeamSets):
        ptv = patient.PatientModel.RegionsOfInterest[bs.Prescription.PrimaryDosePrescription.OnStructure.Name]
        beamset_name = ptv.Name[4:6] #ROI name must be in the format PTV A1 or PTV B1 48Gy
        nb_fx = bs.FractionationPattern.NumberOfFractions
        rx_dose = bs.Prescription.PrimaryDosePrescription.DoseValue
        
        #Use presence of isodose contour to decide whether finalisation actions are taken on a given beamset
        if roi.roi_exists("isodose "+beamset_name, examination=patient.Examinations[scan_name]): #eg, isodose A1
            # Rename beamset
            bs.DicomPlanLabel = beamset_name
            
            # Rename isodose ROI and add * to it and PTV
            isodose_roi = patient.PatientModel.RegionsOfInterest["isodose " + beamset_name]         
            isodose_roi.Name = ("ISO "+ beamset_name + " " + str(rx_dose/100) + "Gy*")
            isodose_roi.Name = isodose_roi.Name.replace('.0Gy','Gy')
            ptv.Name += '*'     
            if roi.roi_exists("ITV "+beamset_name, examination=patient.Examinations[scan_name]): #eg, ITV B1
                patient.PatientModel.RegionsOfInterest["ITV " + beamset_name].Name += '*'
            
            # Copy PTV and isodose ROIs to second beamset for patient positioning at treatment room
            patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=ptv.Name)    
            patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=isodose_roi.Name)    
            
            # Add comment for Superbridge transfer
            bs.Prescription.Description = "VMAT"
      
            # Create DSP and PT PRESC
            poi_name = 'PT PRESC ' + beamset_name
            poi.create_poi({'x': 0, 'y': 0, 'z': 0}, poi_name, color=colors[i], examination=patient.Examinations[scan_name])
            bs.CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 })
           
            # Move PT PRESC to a point that receives correct dose per fraction and prescribe
            poi.place_prescription_point(target_fraction_dose=rx_dose/nb_fx, ptv_name=ptv.Name, poi_name=poi_name, beamset=bs, exam=patient.Examinations[scan_name])
            bs.AddDosePrescriptionToPoi(PoiName=poi_name, DoseValue=rx_dose)
      
            # Move DSP to coordinates of PT PRESC and assign to all beams
            point = poi.get_poi_coordinates(poi_name)
            dsp = [x for x in bs.DoseSpecificationPoints][0]
            dsp.Name = "DSP "+beamset_name
            dsp.Coordinates = point.value

            for beam in bs.Beams:
                beam.SetDoseSpecificationPoint(Name=dsp.Name)
            bs.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point (otherwise not displayed)        


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
    
    
    
    
 
def verification_finale_old():

    class Verif1Window(Form):
        def __init__(self):
            self.Text = "Vérification finale"

            self.Width = 535
            self.Height = 1000

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
            #Create the dictionary that will be used to pass the verification info to the print function
            self.d = dict(patient_name = patient.PatientName.replace('^', ', '),
                     plan_name = plan.Name,
                     beamset_name = beamset.DicomPlanLabel,
                     patient_number = patient.PatientID,
                     #planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
                     planned_by_name = plan.PlannedBy,
                     verified_by_name = lib.get_user_name(os.getenv('USERNAME')),
                     ext_text = "Script pas roulé",
                     grid_text = "Script pas roulé",
                     DSP_text = "Script pas roulé",
                     iso_text = "Script pas roulé",
                     beam_text = "Script pas roulé",
                     presc_text = "Script pas roulé",
                     segments_text = "Script pas roulé",
                     check_scanOK = "Pas vérifié",
                     check_ext = "Pas vérifié",
                     check_isoOK = "Pas vérifié",
                     check_grid = "Pas vérifié",                     
                     check_beams_Rx = "Pas vérifié",
                     check_segments = "Pas vérifié",
                     check_distribution_dose = "Pas vérifié",
                     check_DSP = "Pas vérifié")
            
            #Create dictionaries for window/level switching
            self.lung_dict = dict(x=-600,y=1600)
            self.lw_dict = dict(x=-exam.Series[0].LevelWindow.x,y=exam.Series[0].LevelWindow.y)            
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 800
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') #+ "                  Plan: " + plan.Name + "                  Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 35
            offset = 20   

            
            self.label_scanOK = Label()
            self.label_scanOK.Text = "Scan OK (étendu du scan)"
            self.label_scanOK.Location = Point(25, offset)
            self.label_scanOK.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_scanOK.AutoSize = True              
            
            self.check_scanOK = CheckBox()
            self.check_scanOK.Location = Point(480, offset)
            self.check_scanOK.Width = 30
            self.check_scanOK.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External' et overrides"
            button_ext.Font = Font("Arial", 11, FontStyle.Bold)
            button_ext.Location = Point(25, offset + vert_spacer)
            button_ext.Width = 410 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(480, offset + vert_spacer)
            self.check_ext.Width = 30
            self.check_ext.Checked = False   
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre et point de localisation"
            button_isoOK.Font = Font("Arial", 11, FontStyle.Bold)
            button_isoOK.Location = Point(25, offset + vert_spacer*2)
            button_isoOK.Width = 410 
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(480, offset + vert_spacer*2)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False              
           

           
            button_grid = Button()
            button_grid.Text = "La grille de dose est correcte"
            button_grid.Font = Font("Arial", 11, FontStyle.Bold)
            button_grid.Location = Point(25, offset + vert_spacer*3)
            button_grid.Width = 410 
            button_grid.Click += self.button_grid_Clicked              
                    
            self.check_grid = CheckBox()
            self.check_grid.Location = Point(480, offset + vert_spacer*3)
            self.check_grid.Width = 30
            self.check_grid.Checked = False              

            
           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 11, FontStyle.Bold)
            button_beams_Rx.Location = Point(25, offset + vert_spacer*4)
            button_beams_Rx.Width = 410 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(480, offset + vert_spacer*4)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              
         
         
         
            button_segments = Button()
            button_segments.Text = "Les segments sont corrects/flashé au besoin"
            button_segments.Font = Font("Arial", 11, FontStyle.Bold)
            button_segments.Location = Point(25, offset + vert_spacer*5)
            button_segments.Width = 410 
            button_segments.Click += self.button_segments_Clicked                        
            
            self.check_segments = CheckBox()
            self.check_segments.Location = Point(480, offset + vert_spacer*5)
            self.check_segments.Width = 30
            self.check_segments.Checked = False                      


            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(25, offset + vert_spacer*6)
            self.label_distribution_dose.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(480, offset + vert_spacer*6)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         

            
            
            self.label_DSP = Label()
            self.label_DSP.Text = "Notez le HT et les DSP"
            self.label_DSP.Location = Point(25, offset + vert_spacer*7)
            self.label_DSP.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_DSP.AutoSize = True              
            
            self.check_DSP = CheckBox()
            self.check_DSP.Location = Point(480, offset + vert_spacer*7)
            self.check_DSP.Width = 30
            self.check_DSP.Checked = False        
            
            
            
            self.label_results_header = Label()
            self.label_results_header.Text = ""
            self.label_results_header.Location = Point(25, offset + vert_spacer*9)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = ""
            self.label_results.Location = Point(25, offset + vert_spacer*10)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = ""
            self.label_reminder.Location = Point(25, offset + vert_spacer*11)
            self.label_reminder.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_reminder.ForeColor = Color.Red
            self.label_reminder.AutoSize = True                 
            
            
           
            self.MainWindow.Controls.Add(self.label_scanOK)
            self.MainWindow.Controls.Add(self.check_scanOK)  
            
            self.MainWindow.Controls.Add(button_ext)  
            self.MainWindow.Controls.Add(self.check_ext)            
            
            self.MainWindow.Controls.Add(button_isoOK)   
            self.MainWindow.Controls.Add(self.check_isoOK)     
            
            self.MainWindow.Controls.Add(button_grid)
            self.MainWindow.Controls.Add(self.check_grid)              
            
            self.MainWindow.Controls.Add(button_beams_Rx)            
            self.MainWindow.Controls.Add(self.check_beams_Rx)
                      
            self.MainWindow.Controls.Add(button_segments)
            self.MainWindow.Controls.Add(self.check_segments)               
            
            self.MainWindow.Controls.Add(self.label_distribution_dose)
            self.MainWindow.Controls.Add(self.check_distribution_dose)            

            self.MainWindow.Controls.Add(self.label_DSP)
            self.MainWindow.Controls.Add(self.check_DSP)               
            
            self.MainWindow.Controls.Add(self.label_results_header)
            self.MainWindow.Controls.Add(self.label_results)
            self.MainWindow.Controls.Add(self.label_reminder)            
                        
            
        def button_ext_Clicked(self, sender, args):  
            self.message.ForeColor = Color.Black        
            self.message.Text = "Vérification du contour External en cours"
            self.d['ext_text'] = verification.verify_external_and_overrides()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['ext_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
            self.label_reminder.Text = "Rappel:\nVérifiez que la table (ou la planche ORL) est comprise dans\nle contour External avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_grid_Clicked(self, sender, args):       
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de la grille de dose en cours"
            self.d['grid_text'] = verification.verify_dose_grid_resolution()
            self.d['DSP_text'] = verification.verify_dose_specification_points()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['grid_text']
            self.label_results.Text += "\n" + self.d['DSP_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
            self.label_reminder.Text = ""
            self.message.Text = ""            
            
        def button_isoOK_Clicked(self, sender, args):
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 110)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
            self.label_reminder.Text = ""
            self.label_results.Text = ""
            self.label_results_header.Text = "Résultats"
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de la prescription en cours"
            self.d['presc_text'] = verification.verify_prescription()
            self.label_results.Text = self.d['presc_text']
            self.message.Text = "Vérification des faisceaux en cours"
            a,b,c,d,e = verification.verify_beams()
            self.d['beam_text'] = a + "\n\n" + d + "\n" + e + "\n\n" + c  
            self.label_results.Text += "\n\nFaisceaux:\n" + self.d['beam_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 170 + 15*b)
            self.label_reminder.Text = "Rappel:\nS'il y a un prothèse, un pacemaker ou un membre qui dépasse le\nFOV du scan, vérifiez que les angles de gantry sont bien choisis"
            self.message.Text = ""
            
        def button_segments_Clicked(self, sender, args):   
            self.message.ForeColor = Color.Black        
            self.label_reminder.Text = ""
            self.label_results.Text = ""        
            self.message.Text = "Vérification des segments en cours"
            self.d['segments_text'] = verification.verify_segments()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['segments_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 90)
            self.label_reminder.Text = "Rappel:\nVérifiez les segments en mode BEV avant de procéder"
            self.message.Text = ""            
            
        #def cancelClicked(self, sender, args):
        #    self.Close()          
            
        def levelwindowClicked(self, sender, args):
            if exam.Series[0].LevelWindow.x == -600 and exam.Series[0].LevelWindow.y == 1600:
                exam.Series[0].LevelWindow = self.lw_dict
            else:
                exam.Series[0].LevelWindow = self.lung_dict                   
            
        def referencedoseClicked(self, sender, args):
            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"       
            prostate.toggle_reference_dose_verif2()              
            self.message.Text = ""    
            
        def printClicked(self, sender, args):     

            #Verify that all boxes have been checked
            warning = False
            if self.check_scanOK.Checked:
                self.d['check_scanOK'] = 'OK'
            else:
                warning = True
            if self.check_ext.Checked:
                self.d['check_ext'] = 'OK'
            else:
                warning = True
            if self.check_isoOK.Checked:
                self.d['check_isoOK'] = 'OK'
            else:
                warning = True
            if self.check_grid.Checked:
                self.d['check_grid'] = 'OK'
            else:
                warning = True
            if self.check_beams_Rx.Checked:
                self.d['check_beams_Rx'] = 'OK'
            else:
                warning = True
            if self.check_segments.Checked:
                self.d['check_segments'] = 'OK'
            else:
                warning = True
            if self.check_distribution_dose.Checked:
                self.d['check_distribution_dose'] = 'OK'                
            else:
                warning = True
            if self.check_DSP.Checked:
                self.d['check_DSP'] = 'OK'
            else:
                warning = True                
                

            self.message.ForeColor = Color.Black
            self.message.Text = "Impression en cours"
            report.create_verif2_report(data=self.d)
            
            if warning:
                self.message.ForeColor = Color.Red
                self.message.Text = "Impression terminé - vérification incomplète"
            else:
                self.message.ForeColor = Color.Green
                self.message.Text = "Impression terminé"
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 900)
            
            printButton = Button()
            printButton.Text = "Imprimer"
            printButton.Location = Point(25, 28)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            #cancelButton = Button()
            #cancelButton.Text = "Annuler"
            #cancelButton.Location = Point(110,10)
            #self.CancelButton = cancelButton
            #cancelButton.Click += self.cancelClicked

            levelwindowButton = Button()
            levelwindowButton.Text = "Level/Window"
            levelwindowButton.Location = Point(108,28)
            levelwindowButton.Width = 85
            levelwindowButton.Click += self.levelwindowClicked            
            
            referencedoseButton = Button()
            referencedoseButton.Text = "Toggle Reference Dose"
            referencedoseButton.Location = Point(200,28)
            referencedoseButton.Width = 140
            referencedoseButton.Click += self.referencedoseClicked                
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(30, 0)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(printButton)
            self.OKbuttonPanel.Controls.Add(levelwindowButton)
            self.OKbuttonPanel.Controls.Add(referencedoseButton)
            self.OKbuttonPanel.Controls.Add(self.message)
               
                
                
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
    try:
        temp = patient.ModificationInfo.UserName
    except:
        debug_window('ATTENTION: Le plan a été modifié depuis la dernière sauvegarde.\n\nFermez cette fenêtre pour poursuivre avec la vérification.')
        #return
        
    form = Verif1Window()
    Application.Run(form)   



   
def verification_initiale_old():

    class Verif1Window(Form):
        def __init__(self):
            self.Text = "Première vérification"

            self.Width = 535
            self.Height = 1000

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
            #Create the dictionary that will be used to pass the verification info to the print function
            self.d = dict(patient_name = patient.PatientName.replace('^', ', '),
                     plan_name = plan.Name,
                     beamset_name = beamset.DicomPlanLabel,
                     patient_number = patient.PatientID,
                     #planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
                     planned_by_name = plan.PlannedBy,
                     verified_by_name = lib.get_user_name(os.getenv('USERNAME')),
                     ext_text = "Script pas roulé",
                     iso_text = "Script pas roulé",
                     beam_text = "Script pas roulé",
                     presc_text = "Script pas roulé",
                     opt_text = "Script pas roulé",
                     check_bonscan = "Pas vérifié",
                     check_scanOK = "Pas vérifié",
                     check_ext = "Pas vérifié",
                     check_isoOK = "Pas vérifié",
                     check_beams_Rx = "Pas vérifié",
                     check_contours = "Pas vérifié",
                     check_optimisation = "Pas vérifié",
                     check_distribution_dose = "Pas vérifié")
            
            #Create dictionaries for window/level switching
            self.lung_dict = dict(x=-600,y=1600)
            self.lw_dict = dict(x=-exam.Series[0].LevelWindow.x,y=exam.Series[0].LevelWindow.y)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 800
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') #+ "                  Plan: " + plan.Name + "                  Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 35
            offset = 20   
            
            self.label_bonscan = Label()
            self.label_bonscan.Text = "Le bon scan est utilisé pour la planification"
            self.label_bonscan.Location = Point(25, offset)
            self.label_bonscan.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_bonscan.AutoSize = True              
            
            self.check_bonscan = CheckBox()
            self.check_bonscan.Location = Point(480, offset)
            self.check_bonscan.Width = 30
            self.check_bonscan.Checked = False        

            
       
            self.label_scanOK = Label()
            self.label_scanOK.Text = "Scan OK (artéfactes, étendu du scan, objets sur la table)"
            self.label_scanOK.Location = Point(25, offset + vert_spacer)
            self.label_scanOK.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_scanOK.AutoSize = True              
            
            self.check_scanOK = CheckBox()
            self.check_scanOK.Location = Point(480, offset + vert_spacer)
            self.check_scanOK.Width = 30
            self.check_scanOK.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External' + overrides"
            button_ext.Font = Font("Arial", 11, FontStyle.Bold)
            button_ext.Location = Point(25, offset + vert_spacer*2)
            button_ext.Width = 410 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(480, offset + vert_spacer*2)
            self.check_ext.Width = 30
            self.check_ext.Checked = False   
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre"
            button_isoOK.Font = Font("Arial", 11, FontStyle.Bold)
            button_isoOK.Location = Point(25, offset + vert_spacer*3)
            button_isoOK.Width = 410 
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(480, offset + vert_spacer*3)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False              
           

           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 11, FontStyle.Bold)
            button_beams_Rx.Location = Point(25, offset + vert_spacer*4)
            button_beams_Rx.Width = 410 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(480, offset + vert_spacer*4)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              
         
         
         
            self.label_contours = Label()
            self.label_contours.Text = "Les contours d'optimisation sont corrects"
            self.label_contours.Location = Point(25, offset + vert_spacer*5)
            self.label_contours.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_contours.AutoSize = True              
            
            self.check_contours = CheckBox()
            self.check_contours.Location = Point(480, offset + vert_spacer*5)
            self.check_contours.Width = 30
            self.check_contours.Checked = False              

            
            
            button_optimisation = Button()
            button_optimisation.Text = "Objectifs et paramètres d'optimisation"
            button_optimisation.Font = Font("Arial", 11, FontStyle.Bold)
            #button_optimisation.TextAlign = HorizontalAlignment.Center
            button_optimisation.Location = Point(25, offset + vert_spacer*6)
            button_optimisation.Width = 410 
            button_optimisation.Click += self.button_opt_Clicked          
            
            self.check_optimisation = CheckBox()
            self.check_optimisation.Location = Point(480, offset + vert_spacer*6)
            self.check_optimisation.Width = 30
            self.check_optimisation.Checked = False                  


            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(25, offset + vert_spacer*7)
            self.label_distribution_dose.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(480, offset + vert_spacer*7)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         


            self.label_results_header = Label()
            self.label_results_header.Text = ""
            self.label_results_header.Location = Point(25, offset + vert_spacer*9)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = ""
            self.label_results.Location = Point(25, offset + vert_spacer*10)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = ""
            self.label_reminder.Location = Point(25, offset + vert_spacer*11)
            self.label_reminder.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_reminder.ForeColor = Color.Red
            self.label_reminder.AutoSize = True                 
            
            
            
            self.MainWindow.Controls.Add(self.label_bonscan)
            self.MainWindow.Controls.Add(self.check_bonscan)
            
            self.MainWindow.Controls.Add(self.label_scanOK)
            self.MainWindow.Controls.Add(self.check_scanOK)  
            
            self.MainWindow.Controls.Add(button_ext)  
            self.MainWindow.Controls.Add(self.check_ext)            
            
            self.MainWindow.Controls.Add(button_isoOK)   
            self.MainWindow.Controls.Add(self.check_isoOK)                 
            
            self.MainWindow.Controls.Add(button_beams_Rx)            
            self.MainWindow.Controls.Add(self.check_beams_Rx)
                      
            self.MainWindow.Controls.Add(self.label_contours)
            self.MainWindow.Controls.Add(self.check_contours)               

            self.MainWindow.Controls.Add(button_optimisation)            
            self.MainWindow.Controls.Add(self.check_optimisation)
            
            self.MainWindow.Controls.Add(self.label_distribution_dose)
            self.MainWindow.Controls.Add(self.check_distribution_dose)            

            self.MainWindow.Controls.Add(self.label_results_header)
            self.MainWindow.Controls.Add(self.label_results)
            self.MainWindow.Controls.Add(self.label_reminder)            

            
        def button_ext_Clicked(self, sender, args):       
            self.message.Text = "Vérification du contour External en cours"
            self.d['ext_text'] = verification.verify_external_and_overrides()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['ext_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
            self.label_reminder.Text = "Rappel:\nVérifiez que la table (ou la planche ORL) est comprise dans\nle contour External avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_isoOK_Clicked(self, sender, args):
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            #self.label_results.Text = d['presc_text']
            #d['iso_text'] = a #+ "\n" + b + "\n" + c + "\n\n" + d
            #self.label_results.Text = d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 110)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
            self.label_reminder.Text = ""
            self.label_results.Text = ""
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification de la prescription en cours"
            self.d['presc_text'] = verification.verify_prescription()
            self.label_results.Text = self.d['presc_text']
            self.message.Text = "Vérification des faisceaux en cours"
            a,b,c,d,e = verification.verify_beams()   #d and e are not needed for a first verification (machine type and energy)
            self.d['beam_text'] = a + "\n\n" + e  + "\n\n" + c
            self.label_results.Text += "\n\nFaisceaux:\n" + self.d['beam_text']
            #self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 80 + 15*b)
            self.message.Text = ""

        def button_opt_Clicked(self, sender, args):       
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification des paramètres d'optimisation"              
            a,b,c,d = verification.verify_opt_parameters()
            self.d['opt_text']  = a + "\n" + b + "\n" + d + "\n" + c   
            self.label_results.Text = self.d['opt_text']
            #d['opt_text'] = a + "\n" + b + "\n" + d + "\n" + c
            #self.label_results.Text = d['opt_text'] 
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 90)
            self.label_reminder.Text = "Rappel:\nVérifier tout les objectifs d'optimisation avant de\nprocéder à la prochaine étape"
            self.message.Text = ""            
            
        #def cancelClicked(self, sender, args):
        #    self.Close()    

        def levelwindowClicked(self, sender, args):
            if exam.Series[0].LevelWindow.x == -600 and exam.Series[0].LevelWindow.y == 1600:
                exam.Series[0].LevelWindow = self.lw_dict
            else:
                exam.Series[0].LevelWindow = self.lung_dict            

        def referencedoseClicked(self, sender, args):
            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"       
            prostate.toggle_reference_dose()              
            self.message.Text = ""    
                
        def printClicked(self, sender, args):     

            #Verify that all boxes have been checked
            warning = False
            if self.check_bonscan.Checked:
                self.d['check_bonscan'] = 'OK'
            else:
                warning = True
            if self.check_scanOK.Checked:
                self.d['check_scanOK'] = 'OK'
            else:
                warning = True                
            if self.check_ext.Checked:
                self.d['check_ext'] = 'OK'
            else:
                warning = True                
            if self.check_isoOK.Checked:
                self.d['check_isoOK'] = 'OK'
            else:
                warning = True                
            if self.check_beams_Rx.Checked:
                self.d['check_beams_Rx'] = 'OK'
            else:
                warning = True                
            if self.check_contours.Checked:
                self.d['check_contours'] = 'OK'
            else:
                warning = True                
            if self.check_optimisation.Checked:
                self.d['check_optimisation'] = 'OK'
            else:
                warning = True                
            if self.check_distribution_dose.Checked:
                self.d['check_distribution_dose'] = 'OK'                
            else:
                warning = True                
                

            self.message.ForeColor = Color.Black
            self.message.Text = "Impression en cours"
            report.create_verif1_report(data=self.d)
            
            if warning:
                self.message.ForeColor = Color.Red
                self.message.Text = "Impression terminé - vérification incomplète"
            else:
                self.message.ForeColor = Color.Green
                self.message.Text = "Impression terminé"
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 900)
            
            printButton = Button()
            printButton.Text = "Imprimer"
            printButton.Location = Point(25, 28)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            #cancelButton = Button()
            #cancelButton.Text = "Annuler"
            #cancelButton.Location = Point(110,10)
            #self.CancelButton = cancelButton
            #cancelButton.Click += self.cancelClicked

            levelwindowButton = Button()
            levelwindowButton.Text = "Level/Window"
            levelwindowButton.Location = Point(108,28)
            levelwindowButton.Width = 85
            levelwindowButton.Click += self.levelwindowClicked            
            
            referencedoseButton = Button()
            referencedoseButton.Text = "Toggle Reference Dose"
            referencedoseButton.Location = Point(200,28)
            referencedoseButton.Width = 140
            referencedoseButton.Click += self.referencedoseClicked                
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(30, 0)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(printButton)
            self.OKbuttonPanel.Controls.Add(levelwindowButton)
            self.OKbuttonPanel.Controls.Add(referencedoseButton)
            self.OKbuttonPanel.Controls.Add(self.message)
               
               
                
                
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
    try:
        temp = patient.ModificationInfo.UserName
    except:
        message.message_window('ATTENTION: Le plan a été modifié depuis la dernière sauvegarde.\n\nFermez cette fenêtre pour poursuivre avec la vérification.')
        #return        
              
    form = Verif1Window()
    Application.Run(form)   
     
 




#Modified version of the script that can handle multiple PTVs and locked plans
def stereo_brain_statistics_v2(num_ptvs, ptv_names, rx, technique):
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()    
   
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
        return "ROI pour cerveau pas trouvé"
        
    if "BodyRS" in roi_names:
        body_name = "BodyRS"
    elif "BODY" in roi_names:
        body_name = "BODY"    
    else:
        return "ROI pour body pas trouvé"
        
    if "CERVEAU-PTV" in roi_names:
        cerv_ptv_name = "CERVEAU-PTV"
    elif "CERV-PTV" in roi_names:
        cerv_ptv_name = "CERV-PTV"
    elif "CERVEAU-PTVs" in roi_names:
        cerv_ptv_name = "CERVEAU-PTVs"
    else:
        return "CERVEAU-PTV pas trouvé"

    if "MOELLE*" in roi_names:
        moelle_name = "MOELLE*"
    else:
        moelle_name = "MOELLE"
        
    if "TR CEREBRAL*" in roi_names:
        tronc_name = "TR CEREBRAL*"
    elif "TR CEREBRAL" in roi_names:
        tronc_name = "TR CEREBRAL" 
    elif "TRONC CEREBRAL" in roi_names:
        tronc_name = "TRONC CEREBRAL" 
    elif "TRONC CEREBRAL*" in roi_names:
        tronc_name = "TRONC CEREBRAL*" 
    else:
        return "ROI pour tronc cérébral pas trouvé"
                
    if "OEIL DRT*" in roi_names:
        oeild_name = "OEIL DRT*"
    else:
        oeild_name = "OEIL DRT"           

    if "OEIL GCHE*" in roi_names:
        oeilg_name = "OEIL GCHE*"
    else:
        oeilg_name = "OEIL GCHE"               
               
    #Get prescription information
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    #Get brain volume and radius
    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerveau_name].GetRoiVolume()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerv_ptv_name].GetRoiVolume()
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    
    #PTV stats
    ptv_output = ""
    ptv_header = ""
    ptv_vol = [0,0,0,0]
    ptv_rad = [0,0,0,0]
    ptv_tronc_overlap = [0,0,0,0]
    sum_big_small = 0
    for i,ptv in enumerate(ptv_names):
        ring_vol = [0,0,0,0,0,0]
        ring_int_vol = [0,0,0,0,0,0]
        
        #PTV Header
        ptv_header += "Nom du PTV" + str(i+1) + ",Dose Rx (cGy),Couverture par 100%,Vol PTV(cc),Rayon estimé(cm),Vol smoothé(cc),"
        ptv_header += "Ring90 vol(cc),Ring90dsCERV vol(cc),Ring80 vol(cc),Ring80dsCERV vol(cc),Ring70 vol(cc),Ring70dsCERV vol(cc),Ring60 vol(cc),Ring60dsCERV vol(cc),Ring50 vol(cc),Ring50dsCERV vol(cc),Ring40 vol(cc),Ring40dsCERV vol(cc),Fraction PTV ds tronc,"        
        
        if ptv_names[i] == "":
            ptv_output += "Aucun PTV" + str(i+1) + ","
            ptv_output += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," #repeat a whole bunch for each empty field
            continue
            
        ptv_vol[i] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume()
        ptv_rad[i] = math.pow(3*ptv_vol[i]/(4*math.pi),1.0/3)
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        
        #Create rings
        roi.create_expanded_ptv(ptv_names[i], color="Yellow", examination=exam, margeptv=0.25, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Pink", examination=exam, margeptv=0.4, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Blue", examination=exam, margeptv=0.6, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Tomato", examination=exam, margeptv=0.8, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="YellowGreen", examination=exam, margeptv=1.1, output_name='stats_ptv')
        
        roi.create_ring(ptv_names[i], r2=0.25, r1=0, new_name='ring90')
        roi.create_ring('stats_ptv+0.25cm', r2=0.15, r1=0, new_name='ring80')
        roi.create_ring('stats_ptv+0.4cm', r2=0.2, r1=0, new_name='ring70')
        roi.create_ring('stats_ptv+0.6cm', r2=0.2, r1=0, new_name='ring60')
        roi.create_ring('stats_ptv+0.8cm', r2=0.3, r1=0, new_name='ring50')
        roi.create_ring('stats_ptv+1.1cm', r2=0.4, r1=0, new_name='ring40')
        
        #Check volume of each ring
        ring_vol[0] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring90'].GetRoiVolume()
        ring_vol[1] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring80'].GetRoiVolume()
        ring_vol[2] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring70'].GetRoiVolume()
        ring_vol[3] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring60'].GetRoiVolume()
        ring_vol[4] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring50'].GetRoiVolume()
        ring_vol[5] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring40'].GetRoiVolume()
        
        #Check volume of each ring that intersects the brain
        ring_int_vol[0] = roi.get_intersecting_volume('ring90', cerveau_name, examination=exam)
        ring_int_vol[1] = roi.get_intersecting_volume('ring80', cerveau_name, examination=exam)
        ring_int_vol[2] = roi.get_intersecting_volume('ring70', cerveau_name, examination=exam)
        ring_int_vol[3] = roi.get_intersecting_volume('ring60', cerveau_name, examination=exam)
        ring_int_vol[4] = roi.get_intersecting_volume('ring50', cerveau_name, examination=exam)
        ring_int_vol[5] = roi.get_intersecting_volume('ring40', cerveau_name, examination=exam)
        
        #Expand and contract PTV to smooth
        roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
        roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
        big_small_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()
        sum_big_small += big_small_vol
         
        #Check for tronc overlap
        tronc_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV tronc", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        tronc_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[i]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [tronc_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        tronc_overlap.UpdateDerivedGeometry(Examination=exam)
        ptv_tronc_overlap[i] = roi.get_roi_volume(tronc_overlap.Name, exam=exam) / ptv_vol[i]
        tronc_overlap.DeleteRoi()
        
        #Generate output
        ptv_output += ptv_names[i] + ',' + str(rx[i]) + ',' + str(ptv_coverage[0]*100) + ',' + str(ptv_vol[i]) + ',' + str(ptv_rad[i]) + ',' + str(big_small_vol) + ','
        for j in range(6):
            ptv_output += str(ring_vol[j]) + ',' + str(ring_int_vol[j]) + ','
        ptv_output += str(ptv_tronc_overlap[i]) + ','
        
        #Delete temporary ROIs
        delete_list = ['stats_ptv+0.25cm','stats_ptv+0.4cm','stats_ptv+0.6cm','stats_ptv+0.8cm','stats_ptv+1.1cm','ring90','ring80','ring70','ring60','ring50','ring40','stats_ptv+3cm','stats_ptv+3cm-2.95cm']
        for contour in delete_list:
            patient.PatientModel.RegionsOfInterest[contour].DeleteRoi() 
    
    
    #Create sum of all PTVs, then expand and contract to smooth
    #I CAN'T THINK OF A GOOD WAY TO DO THIS
    smooth = True
    if ptv_names[1] == "": #Only one PTV
        total_smoothed_vol = sum_big_small
        smooth = False
    elif ptv_names[2] == "": #Two PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    elif ptv_names[3] == "": #Three PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    else: #Four PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1],ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)   

    if smooth:
        roi.create_expanded_ptv(total_ptv.Name, color="LightBlue", examination=exam, margeptv=3, output_name='stats_total_ptv')
        roi.create_expanded_ptv('stats_total_ptv+3cm', color="LightBlue", examination=exam, margeptv=2.95, output_name='stats_total_ptv+3cm',operation='Contract')
        total_smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_total_ptv+3cm-2.95cm'].GetRoiVolume()
        total_ptv.DeleteRoi() 
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm'].DeleteRoi()
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm-2.95cm'].DeleteRoi()
        
    #Get DVH information (since we're using Fractiondose we have to compensate for nb_fx)
    #Note that dose_in_brain excludes the volume of the PTV, while dose_in_body includes it
    rx_dose = max(rx) #Use highest prescription value for OAR dose calculations
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume()
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V40,12Gy,10Gy)
    
    #Calculate D1% for OARs
    oar_list = [moelle_name,oeild_name,oeilg_name,tronc_name,'CHIASMA','NERF OPT DRT','NERF OPT GCHE']
    oar_d1 = [0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = body_name,RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx
    
    #Check whether GTV has Min Dose objective
    gtv_objective = 'Non'
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
            gtv_objective = 'Oui'
            break
            
    #Check number of beams
    num_beams = 0
    num_segments = 0
    for beam in beamset.Beams:
        num_beams +=1
        for segment in beam.Segments:         
            num_segments += 1
    
    
    #Generate output string
    patient_header = "Name,ID,Plan,Beamset,Nb de PTVs,"
    patient_output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' + str(num_ptvs) + ',' #Demographic information
    
    dose_header = "CERV vol,CERV radius,CERV-PTV V100,CERV-PTV V90,CERV-PTV V80,CERV-PTV V70,CERV-PTV V60,CERV-PTV V50,CERV-PTV V40,CERV-PTV V12Gy,CERV-PTV V10Gy,CERV-PTV V12Gy cc,CERV-PTV V10Gy cc,"
    dose_header += "V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,V40 radius,12Gy radius,10Gy radius,"
    dose_header += "D1% MOELLE (Gy),D0.01 OEIL DRT (Gy),D0.01 OEIL GCHE (Gy),D0.01 TR CEREBRAL (Gy),D0.01 CHIASMA (Gy),D0.01 NERF OPT DRT (Gy),D0.01 NERF OPT GCHE (Gy),Max globale (Gy),"
    dose_header += "Min dose objective sur GTV,Nb de fractions,Nb de faisceaux,Nb de segments,Technique,Volume du PTV combiné smoothé (cc)"
    

    output = "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*100,dose_in_brain[1]*100,dose_in_brain[2]*100,dose_in_brain[3]*100,dose_in_brain[4]*100,dose_in_brain[5]*100,dose_in_brain[6]*100,dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V100...V40,V10Gy,V12Gy in percentage
    output += "%.3f,%.3f," % (dose_in_brain[7]*brain_minus_ptv_vol,dose_in_brain[8]*brain_minus_ptv_vol) #CERV-PTV V12 and V10 in cc
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8]) #Estimated radii for V100,V90...V40,V12Gy,V10Gy in body
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d,%d,%d,%s," % (nb_fx,num_beams,num_segments,technique)
    output += str(total_smoothed_vol)
    
    
    #Write to file       
    file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane_v2.txt'
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a') as stat_file:
        #The line below prints the key, only do so if starting the stats text file over from scratch 
        if not file_exists:
            stat_file.write(patient_header + ptv_header + dose_header + '\n')
        stat_file.write(patient_output + ptv_output + output + '\n')
    return "Calcul terminé"
        

#First attempt to calculate dose falloff in patients using automation
def dose_falloff_v1(num_ptvs, ptv_names, rx, technique,patient,plan,beamset):
    #patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    #plan = lib.get_current_plan()
    #beamset = lib.get_current_beamset()    
   
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
        return patient.PatientName + ": ROI pour cerveau pas trouvé"
        
    if "BodyRS" in roi_names:
        body_name = "BodyRS"
    elif "BODY" in roi_names:
        body_name = "BODY"    
    else:
        return patient.PatientName + ": ROI pour body pas trouvé"
        
    if "CERVEAU-PTV" in roi_names:
        cerv_ptv_name = "CERVEAU-PTV"
    elif "CERV-PTV" in roi_names:
        cerv_ptv_name = "CERV-PTV"
    elif "CERVEAU-PTVs" in roi_names:
        cerv_ptv_name = "CERVEAU-PTVs"
    else:
        return patient.PatientName + ": CERVEAU-PTV pas trouvé"

    if "MOELLE*" in roi_names:
        moelle_name = "MOELLE*"
    else:
        moelle_name = "MOELLE"
        
    if "TR CEREBRAL*" in roi_names:
        tronc_name = "TR CEREBRAL*"
    elif "TR CEREBRAL" in roi_names:
        tronc_name = "TR CEREBRAL" 
    elif "TRONC CEREBRAL" in roi_names:
        tronc_name = "TRONC CEREBRAL" 
    elif "TRONC CEREBRAL*" in roi_names:
        tronc_name = "TRONC CEREBRAL*" 
    else:
        return patient.PatientName + ": ROI pour tronc cérébral pas trouvé"
                
    if "OEIL DRT*" in roi_names:
        oeild_name = "OEIL DRT*"
    else:
        oeild_name = "OEIL DRT"           

    if "OEIL GCHE*" in roi_names:
        oeilg_name = "OEIL GCHE*"
    else:
        oeilg_name = "OEIL GCHE"               
               
    #Get prescription information
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    #Get brain volume and radius
    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerveau_name].GetRoiVolume()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerv_ptv_name].GetRoiVolume()
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    
    #PTV stats
    ptv_output = ""
    ptv_header = ""
    ptv_vol = [0,0,0,0]
    ptv_rad = [0,0,0,0]
    ptv_tronc_overlap = [0,0,0,0]
    sum_big_small = 0
    for i,ptv in enumerate(ptv_names):
        if i>0: #For this test, we're only looking at the first PTV
            continue
        
        ring_vol = [0,0,0,0,0,0]
        ring_int_vol = [0,0,0,0,0,0]
        
        #PTV Header
        ptv_header += "Nom du PTV" + str(i+1) + ",Dose Rx (cGy),Couverture par 100%,Vol PTV(cc),Rayon estimé(cm),Vol smoothé(cc),"
        ptv_header += "Ring90 vol(cc),Ring90dsCERV vol(cc),Ring80 vol(cc),Ring80dsCERV vol(cc),Ring70 vol(cc),Ring70dsCERV vol(cc),Ring60 vol(cc),Ring60dsCERV vol(cc),Ring50 vol(cc),Ring50dsCERV vol(cc),Ring40 vol(cc),Ring40dsCERV vol(cc),Fraction PTV ds tronc,"        
        
        if ptv_names[i] == "":
            ptv_output += "Aucun PTV" + str(i+1) + ","
            ptv_output += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," #repeat a whole bunch for each empty field
            continue
            
        ptv_vol[i] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume()
        ptv_rad[i] = math.pow(3*ptv_vol[i]/(4*math.pi),1.0/3)
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        
        #Calculate radii of the isodoses
        marge_lat = 0.1 #Margin to compensate for the fact that the 100% isodose usually exceeds the PTV
        marge_sup_inf = 0.1 #Margin may or may not be different in sup-inf, needs testing
        
        rad100 = marge_lat
        rad90 = 0.0017*ptv_vol[i] + 0.0994 + marge_lat
        rad80 = 0.0036*ptv_vol[i] + 0.2149 + marge_lat
        rad70 = 0.0064*ptv_vol[i] + 0.3582 + marge_lat
        rad60 = 0.0105*ptv_vol[i] + 0.5631 + marge_lat
        rad50 = 0.0169*ptv_vol[i] + 0.8363 + marge_lat
        rad40 = 0.0267*ptv_vol[i] + 1.3136 + marge_lat
        
        rad100_si = marge_sup_inf
        rad90_si = 0.0002*ptv_vol[i] + 0.0728 + marge_sup_inf
        rad80_si = 0.0013*ptv_vol[i] + 0.1301 + marge_sup_inf
        rad70_si = 0.0030*ptv_vol[i] + 0.1831 + marge_sup_inf
        rad60_si = 0.0047*ptv_vol[i] + 0.2357 + marge_sup_inf
        rad50_si = 0.0060*ptv_vol[i] + 0.3114 + marge_sup_inf
        rad40_si = 0.0082*ptv_vol[i] + 0.3762 + marge_sup_inf        
        
        
        #Create rings
        roi.create_expanded_roi(ptv_names[i], color="Yellow", examination=exam, marge_lat=rad100, marge_sup_inf = rad100_si, output_name='stats_r100')
        roi.create_expanded_roi(ptv_names[i], color="Green",  examination=exam, marge_lat=rad90,  marge_sup_inf = rad90_si, output_name='stats_r90')
        roi.create_expanded_roi(ptv_names[i], color="Red",    examination=exam, marge_lat=rad80,  marge_sup_inf = rad80_si, output_name='stats_r80')
        roi.create_expanded_roi(ptv_names[i], color="Pink",   examination=exam, marge_lat=rad70,  marge_sup_inf = rad70_si, output_name='stats_r70')
        roi.create_expanded_roi(ptv_names[i], color="Blue",   examination=exam, marge_lat=rad60,  marge_sup_inf = rad60_si, output_name='stats_r60')
        roi.create_expanded_roi(ptv_names[i], color="Tomato", examination=exam, marge_lat=rad50,  marge_sup_inf = rad50_si, output_name='stats_r50')
        roi.create_expanded_roi(ptv_names[i], color="Brown",  examination=exam, marge_lat=rad40,  marge_sup_inf = rad40_si, output_name='stats_r40')
        
        roi.subtract_rois('stats_r90','stats_r100',color='White',examination=exam,output_name='ring90')
        roi.subtract_rois('stats_r80','stats_r90', color='White',examination=exam,output_name='ring80')
        roi.subtract_rois('stats_r70','stats_r80', color='White',examination=exam,output_name='ring70')
        roi.subtract_rois('stats_r60','stats_r70', color='White',examination=exam,output_name='ring60')
        roi.subtract_rois('stats_r50','stats_r60', color='White',examination=exam,output_name='ring50')
        roi.subtract_rois('stats_r40','stats_r50', color='White',examination=exam,output_name='ring40')

        
        #Check volume of each ring
        ring_vol[0] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring90'].GetRoiVolume()
        ring_vol[1] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring80'].GetRoiVolume()
        ring_vol[2] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring70'].GetRoiVolume()
        ring_vol[3] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring60'].GetRoiVolume()
        ring_vol[4] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring50'].GetRoiVolume()
        ring_vol[5] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring40'].GetRoiVolume()
        
        #Check volume of each ring that intersects the brain
        ring_int_vol[0] = roi.get_intersecting_volume('ring90', cerveau_name, examination=exam)
        ring_int_vol[1] = roi.get_intersecting_volume('ring80', cerveau_name, examination=exam)
        ring_int_vol[2] = roi.get_intersecting_volume('ring70', cerveau_name, examination=exam)
        ring_int_vol[3] = roi.get_intersecting_volume('ring60', cerveau_name, examination=exam)
        ring_int_vol[4] = roi.get_intersecting_volume('ring50', cerveau_name, examination=exam)
        ring_int_vol[5] = roi.get_intersecting_volume('ring40', cerveau_name, examination=exam)
        
        #Expand and contract PTV to smooth
        roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
        roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
        big_small_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()
        sum_big_small += big_small_vol
         
        #Check for tronc overlap
        tronc_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV tronc", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        tronc_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[i]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [tronc_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        tronc_overlap.UpdateDerivedGeometry(Examination=exam)
        ptv_tronc_overlap[i] = roi.get_roi_volume(tronc_overlap.Name, exam=exam) / ptv_vol[i]
        tronc_overlap.DeleteRoi()
        
        #Generate output
        ptv_output += ptv_names[i] + ',' + str(rx[i]) + ',' + str(ptv_coverage[0]*100) + ',' + str(ptv_vol[i]) + ',' + str(ptv_rad[i]) + ',' + str(big_small_vol) + ','
        for j in range(6):
            ptv_output += str(ring_vol[j]) + ',' + str(ring_int_vol[j]) + ','
        ptv_output += str(ptv_tronc_overlap[i]) + ','
        
        #Delete temporary ROIs
        delete_list = ['stats_r100','stats_r90','stats_r80','stats_r70','stats_r60','stats_r50','stats_r40','ring90','ring80','ring70','ring60','ring50','ring40','stats_ptv+3cm','stats_ptv+3cm-2.95cm']
        for contour in delete_list:
            patient.PatientModel.RegionsOfInterest[contour].DeleteRoi() 
    
    
    #Create sum of all PTVs, then expand and contract to smooth
    #I CAN'T THINK OF A GOOD WAY TO DO THIS
    smooth = True
    if ptv_names[1] == "": #Only one PTV
        total_smoothed_vol = sum_big_small
        smooth = False
    elif ptv_names[2] == "": #Two PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    elif ptv_names[3] == "": #Three PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    else: #Four PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1],ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)   

    if smooth:
        roi.create_expanded_ptv(total_ptv.Name, color="LightBlue", examination=exam, margeptv=3, output_name='stats_total_ptv')
        roi.create_expanded_ptv('stats_total_ptv+3cm', color="LightBlue", examination=exam, margeptv=2.95, output_name='stats_total_ptv+3cm',operation='Contract')
        total_smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_total_ptv+3cm-2.95cm'].GetRoiVolume()
        total_ptv.DeleteRoi() 
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm'].DeleteRoi()
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm-2.95cm'].DeleteRoi()
        
    #Get DVH information (since we're using Fractiondose we have to compensate for nb_fx)
    #Note that dose_in_brain excludes the volume of the PTV, while dose_in_body includes it
    rx_dose = max(rx) #Use highest prescription value for OAR dose calculations
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume()
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V40,12Gy,10Gy)
    
    #Calculate D1% for OARs
    oar_list = [moelle_name,oeild_name,oeilg_name,tronc_name,'CHIASMA','NERF OPT DRT','NERF OPT GCHE']
    oar_d1 = [0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = body_name,RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx
    
    #Check whether GTV has Min Dose objective
    gtv_objective = 'Non'
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
            gtv_objective = 'Oui'
            break
            
    #Check number of beams
    num_beams = 0
    num_segments = 0
    for beam in beamset.Beams:
        num_beams +=1
        for segment in beam.Segments:         
            num_segments += 1
    
    
    #Generate output string
    patient_header = "Name,ID,Plan,Beamset,Nb de PTVs,"
    patient_output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' + str(num_ptvs) + ',' #Demographic information
    
    dose_header = "CERV vol,CERV radius,CERV-PTV V100 cc,CERV-PTV V90 cc,CERV-PTV V80 cc,CERV-PTV V70 cc,CERV-PTV V60 cc,CERV-PTV V50 cc,CERV-PTV V40 cc,CERV-PTV V12Gy cc,CERV-PTV V10Gy cc,CERV-PTV V12Gy %,CERV-PTV V10Gy %,"
    dose_header += "V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,V40 radius,12Gy radius,10Gy radius,"
    dose_header += "D1% MOELLE (Gy),D0.01 OEIL DRT (Gy),D0.01 OEIL GCHE (Gy),D0.01 TR CEREBRAL (Gy),D0.01 CHIASMA (Gy),D0.01 NERF OPT DRT (Gy),D0.01 NERF OPT GCHE (Gy),Max globale (Gy),"
    dose_header += "Min dose objective sur GTV,Nb de fractions,Nb de faisceaux,Nb de segments,Technique,Volume du PTV combiné smoothé (cc)"
    

    output = "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,dose_in_brain[7]*brain_minus_ptv_vol,dose_in_brain[8]*brain_minus_ptv_vol) #CERV-PTV V100...V40,V12Gy,V10Gy in cc
    output += "%.3f,%.3f," % (dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V12 and V10 in percentage
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8]) #Estimated radii for V100,V90...V40,V12Gy,V10Gy in body
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d,%d,%d,%s," % (nb_fx,num_beams,num_segments,technique)
    output += str(total_smoothed_vol)
    
    
    #Write to file       
    file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\falloff_output.txt'
    file_exists = os.path.exists(file_path)
    
    #Print the key, only if starting the stats text file over from scratch
    with open(file_path, 'a') as stat_file:        
        if not file_exists:
            stat_file.write(patient_header + ptv_header + dose_header + '\n')
            
    write_to_file = patient_output + ptv_output + output + '\n'
    return write_to_file
 
  
  
  
  
  
  #Test version for practicing opening patients via scripting
def stereo_brain_statistics_test(num_ptvs, ptv_names, rx, technique,patient,plan,beamset):
    #patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    #plan = lib.get_current_plan()
    #beamset = lib.get_current_beamset()    
   
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
        return "ROI pour cerveau pas trouvé"
        
    if "BodyRS" in roi_names:
        body_name = "BodyRS"
    elif "BODY" in roi_names:
        body_name = "BODY"    
    else:
        return "ROI pour body pas trouvé"
        
    if "CERVEAU-PTV" in roi_names:
        cerv_ptv_name = "CERVEAU-PTV"
    elif "CERV-PTV" in roi_names:
        cerv_ptv_name = "CERV-PTV"
    elif "CERVEAU-PTVs" in roi_names:
        cerv_ptv_name = "CERVEAU-PTVs"
    else:
        return "CERVEAU-PTV pas trouvé"

    if "MOELLE*" in roi_names:
        moelle_name = "MOELLE*"
    else:
        moelle_name = "MOELLE"
        
    if "TR CEREBRAL*" in roi_names:
        tronc_name = "TR CEREBRAL*"
    elif "TR CEREBRAL" in roi_names:
        tronc_name = "TR CEREBRAL" 
    elif "TRONC CEREBRAL" in roi_names:
        tronc_name = "TRONC CEREBRAL" 
    elif "TRONC CEREBRAL*" in roi_names:
        tronc_name = "TRONC CEREBRAL*" 
    else:
        return "ROI pour tronc cérébral pas trouvé"
                
    if "OEIL DRT*" in roi_names:
        oeild_name = "OEIL DRT*"
    else:
        oeild_name = "OEIL DRT"           

    if "OEIL GCHE*" in roi_names:
        oeilg_name = "OEIL GCHE*"
    else:
        oeilg_name = "OEIL GCHE"               
               
    #Get prescription information
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    #Get brain volume and radius
    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerveau_name].GetRoiVolume()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerv_ptv_name].GetRoiVolume()
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    
    #PTV stats
    ptv_output = ""
    ptv_header = ""
    ptv_vol = [0,0,0,0]
    ptv_rad = [0,0,0,0]
    ptv_tronc_overlap = [0,0,0,0]
    sum_big_small = 0
    for i,ptv in enumerate(ptv_names):
        ring_vol = [0,0,0,0,0,0]
        ring_int_vol = [0,0,0,0,0,0]
        
        #PTV Header
        ptv_header += "Nom du PTV" + str(i+1) + ",Dose Rx (cGy),Couverture par 100%,Vol PTV(cc),Rayon estimé(cm),Vol smoothé(cc),"
        ptv_header += "Ring90 vol(cc),Ring90dsCERV vol(cc),Ring80 vol(cc),Ring80dsCERV vol(cc),Ring70 vol(cc),Ring70dsCERV vol(cc),Ring60 vol(cc),Ring60dsCERV vol(cc),Ring50 vol(cc),Ring50dsCERV vol(cc),Ring40 vol(cc),Ring40dsCERV vol(cc),Fraction PTV ds tronc,"        
        
        if ptv_names[i] == "":
            ptv_output += "Aucun PTV" + str(i+1) + ","
            ptv_output += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," #repeat a whole bunch for each empty field
            continue
            
        ptv_vol[i] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume()
        ptv_rad[i] = math.pow(3*ptv_vol[i]/(4*math.pi),1.0/3)
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
        
        #Create rings
        roi.create_expanded_ptv(ptv_names[i], color="Yellow", examination=exam, margeptv=0.25, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Pink", examination=exam, margeptv=0.4, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Blue", examination=exam, margeptv=0.6, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="Tomato", examination=exam, margeptv=0.8, output_name='stats_ptv')
        roi.create_expanded_ptv(ptv_names[i], color="YellowGreen", examination=exam, margeptv=1.1, output_name='stats_ptv')
        
        roi.create_ring(ptv_names[i], r2=0.25, r1=0, new_name='ring90')
        roi.create_ring('stats_ptv+0.25cm', r2=0.15, r1=0, new_name='ring80')
        roi.create_ring('stats_ptv+0.4cm', r2=0.2, r1=0, new_name='ring70')
        roi.create_ring('stats_ptv+0.6cm', r2=0.2, r1=0, new_name='ring60')
        roi.create_ring('stats_ptv+0.8cm', r2=0.3, r1=0, new_name='ring50')
        roi.create_ring('stats_ptv+1.1cm', r2=0.4, r1=0, new_name='ring40')
        
        #Check volume of each ring
        ring_vol[0] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring90'].GetRoiVolume()
        ring_vol[1] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring80'].GetRoiVolume()
        ring_vol[2] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring70'].GetRoiVolume()
        ring_vol[3] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring60'].GetRoiVolume()
        ring_vol[4] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring50'].GetRoiVolume()
        ring_vol[5] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['ring40'].GetRoiVolume()
        
        #Check volume of each ring that intersects the brain
        ring_int_vol[0] = roi.get_intersecting_volume('ring90', cerveau_name, examination=exam)
        ring_int_vol[1] = roi.get_intersecting_volume('ring80', cerveau_name, examination=exam)
        ring_int_vol[2] = roi.get_intersecting_volume('ring70', cerveau_name, examination=exam)
        ring_int_vol[3] = roi.get_intersecting_volume('ring60', cerveau_name, examination=exam)
        ring_int_vol[4] = roi.get_intersecting_volume('ring50', cerveau_name, examination=exam)
        ring_int_vol[5] = roi.get_intersecting_volume('ring40', cerveau_name, examination=exam)
        
        #Expand and contract PTV to smooth
        roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
        roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
        big_small_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()
        sum_big_small += big_small_vol
         
        #Check for tronc overlap
        tronc_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV tronc", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        tronc_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[i]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [tronc_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        tronc_overlap.UpdateDerivedGeometry(Examination=exam)
        ptv_tronc_overlap[i] = roi.get_roi_volume(tronc_overlap.Name, exam=exam) / ptv_vol[i]
        tronc_overlap.DeleteRoi()
        
        #Generate output
        ptv_output += ptv_names[i] + ',' + str(rx[i]) + ',' + str(ptv_coverage[0]*100) + ',' + str(ptv_vol[i]) + ',' + str(ptv_rad[i]) + ',' + str(big_small_vol) + ','
        for j in range(6):
            ptv_output += str(ring_vol[j]) + ',' + str(ring_int_vol[j]) + ','
        ptv_output += str(ptv_tronc_overlap[i]) + ','
        
        #Delete temporary ROIs
        delete_list = ['stats_ptv+0.25cm','stats_ptv+0.4cm','stats_ptv+0.6cm','stats_ptv+0.8cm','stats_ptv+1.1cm','ring90','ring80','ring70','ring60','ring50','ring40','stats_ptv+3cm','stats_ptv+3cm-2.95cm']
        for contour in delete_list:
            patient.PatientModel.RegionsOfInterest[contour].DeleteRoi() 
    
    
    #Create sum of all PTVs, then expand and contract to smooth
    #I CAN'T THINK OF A GOOD WAY TO DO THIS
    smooth = True
    if ptv_names[1] == "": #Only one PTV
        total_smoothed_vol = sum_big_small
        smooth = False
    elif ptv_names[2] == "": #Two PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    elif ptv_names[3] == "": #Three PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)
    else: #Four PTVs
        total_ptv = patient.PatientModel.CreateRoi(Name="stats_total_ptv", Color="Orange", Type="Ptv", TissueName=None, RoiMaterial=None)
        total_ptv.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1],ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[3]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        total_ptv.UpdateDerivedGeometry(Examination=exam)
        total_smoothed_vol = roi.get_roi_volume(total_ptv.Name, exam=exam)   

    if smooth:
        roi.create_expanded_ptv(total_ptv.Name, color="LightBlue", examination=exam, margeptv=3, output_name='stats_total_ptv')
        roi.create_expanded_ptv('stats_total_ptv+3cm', color="LightBlue", examination=exam, margeptv=2.95, output_name='stats_total_ptv+3cm',operation='Contract')
        total_smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_total_ptv+3cm-2.95cm'].GetRoiVolume()
        total_ptv.DeleteRoi() 
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm'].DeleteRoi()
        patient.PatientModel.RegionsOfInterest['stats_total_ptv+3cm-2.95cm'].DeleteRoi()
        
    #Get DVH information (since we're using Fractiondose we have to compensate for nb_fx)
    #Note that dose_in_brain excludes the volume of the PTV, while dose_in_body includes it
    rx_dose = max(rx) #Use highest prescription value for OAR dose calculations
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume()
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V40,12Gy,10Gy)
    
    #Calculate D1% for OARs
    oar_list = [moelle_name,oeild_name,oeilg_name,tronc_name,'CHIASMA','NERF OPT DRT','NERF OPT GCHE']
    oar_d1 = [0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = body_name,RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx
    
    #Check whether GTV has Min Dose objective
    gtv_objective = 'Non'
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
            gtv_objective = 'Oui'
            break
            
    #Check number of beams
    num_beams = 0
    num_segments = 0
    for beam in beamset.Beams:
        num_beams +=1
        for segment in beam.Segments:         
            num_segments += 1
    
    
    #Generate output string
    patient_header = "Name,ID,Plan,Beamset,Nb de PTVs,"
    patient_output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' + str(num_ptvs) + ',' #Demographic information
    
    dose_header = "CERV vol,CERV radius,CERV-PTV V100,CERV-PTV V90,CERV-PTV V80,CERV-PTV V70,CERV-PTV V60,CERV-PTV V50,CERV-PTV V40,CERV-PTV V12Gy,CERV-PTV V10Gy,CERV-PTV V12Gy cc,CERV-PTV V10Gy cc,"
    dose_header += "V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,V40 radius,12Gy radius,10Gy radius,"
    dose_header += "D1% MOELLE (Gy),D0.01 OEIL DRT (Gy),D0.01 OEIL GCHE (Gy),D0.01 TR CEREBRAL (Gy),D0.01 CHIASMA (Gy),D0.01 NERF OPT DRT (Gy),D0.01 NERF OPT GCHE (Gy),Max globale (Gy),"
    dose_header += "Min dose objective sur GTV,Nb de fractions,Nb de faisceaux,Nb de segments,Technique,Volume du PTV combiné smoothé (cc)"
    

    output = "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*100,dose_in_brain[1]*100,dose_in_brain[2]*100,dose_in_brain[3]*100,dose_in_brain[4]*100,dose_in_brain[5]*100,dose_in_brain[6]*100,dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V100...V40,V10Gy,V12Gy in percentage
    output += "%.3f,%.3f," % (dose_in_brain[7]*brain_minus_ptv_vol,dose_in_brain[8]*brain_minus_ptv_vol) #CERV-PTV V12 and V10 in cc
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8]) #Estimated radii for V100,V90...V40,V12Gy,V10Gy in body
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d,%d,%d,%s," % (nb_fx,num_beams,num_segments,technique)
    output += str(total_smoothed_vol)
    
    
    #Write to file       
    file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\test_stats.txt'
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a') as stat_file:
        #The line below prints the key, only do so if starting the stats text file over from scratch 
        if not file_exists:
            stat_file.write(patient_header + ptv_header + dose_header + '\n')
        stat_file.write(patient_output + ptv_output + output + '\n')
    return "Calcul terminé"
        

        
        
        
        
    """
    with open(output_file_path, 'a') as output_file:
        header = 'Essai,Cerv-PTV V100(cc),Cerv-PTV V90(cc),Cerv-PTV V80(cc),Cerv-PTV V70(cc),Cerv-PTV V60(cc),Cerv-PTV V50(cc),Cerv-PTV V40(cc),Couverture PTV(%),Dose de Rx(Gy)\n'
        header += 'Prediction,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6],99.0,rx[0]/100.0)
        #Add clinical plan here, it's going to take some effort
        output_file.write(header)   
    
    #Run optimizations according to Malik's crazy new idea
    optim.triple_optimization()

    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    results = '80% weight 50,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n' % (dose_in_brain[0],dose_in_brain[1],dose_in_brain[2],dose_in_brain[3],dose_in_brain[4],dose_in_brain[5],dose_in_brain[6],ptv_coverage*100,rx[0]/100.0.)
    with open(output_file_path, 'a') as output_file:
        output_file.write(results)
    
    

    for j in range(4):
        #Increase weight for PTV min dose objective if coverage is inadequate
        if ptv_coverage < 0.975:
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue

                if f_type == "MinDose" and objective.ForRegionOfInterest.Name == ptv_names[0]:    
                    objective.DoseFunctionParameters.Weight = 2*objective.DoseFunctionParameters.Weight #Double weight
            
            #Reset plan and reoptimize
            plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
            optim.set_optimization_parameters(plan=plan,fluence_iterations=30, max_iterations=90, compute_intermediate_dose=False)
            plan.PlanOptimizations[0].RunOptimization()
            optim.set_optimization_parameters(plan=plan,fluence_iterations=0, max_iterations=30, compute_intermediate_dose=False)
            plan.PlanOptimizations[0].RunOptimization()
            plan.PlanOptimizations[0].RunOptimization()
            
            #Calculate new PTV coverage
            ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    hello = True
    """        
    
    #Forumlas used when testing out different KBP techniques for stereo crane
    """
    #Run optimizations - first 30 fluence + 60 leaves, then 30 leaves-only
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True

    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text = 'dvh80,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)        

    #Second plan: Increase DVHs to 90% of predicted values
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 90*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 90*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 90*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 90*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.85, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.25, rad50, weight=1.0, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'dvh90,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    

    #Third plan: Increase DVHs to 95% of predicted values
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 95*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 95*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 95*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 95*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.9, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.25, rad50, weight=1.0, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                 
                
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'dvh95,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    

    #Fourth plan: DVHs at 80% of predicted values, dose falloff weight x10
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 80*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 80*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 80*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 80*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.8, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.25, rad50, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'dvh80 dosefalloff10,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             


    #Fifth plan: DVHs at 90% of predicted values, dose falloff weight x10
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 90*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 90*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 90*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 90*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.85, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.25, rad50, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'dvh90 dosefalloff10,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    

    #Sixth plan: DVHs at 95% of predicted values, dose falloff weight x10
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 95*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 95*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 95*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 95*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('KBP RING PROX',  rx[0]*0.9, weight=25, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.25, rad50, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'dvh95 dosefalloff10,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             

    

    #Seventh plan: Only dose falloffs (version MBB)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.40, 0.4, weight=5, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0.15, 1.0, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'Falloff only MBB,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             



    #Eighth plan: Only dose falloffs (version RaySearch)
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
        objective.DeleteFunction()

    optim.add_mindose_objective(ptv_names[0], rx[0], weight=100, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*1.02, rx[0]*0.50, 0.5, weight=10, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective('BodyRS',     rx[0]*0.6, rx[0]*0, 0.5, weight=1, plan=plan, plan_opt=0)
    optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)                        
    
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization()
    optim.triple_optimization()
    initial_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = True
    
    #Evaluate plan
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[0], DoseValues=[rx[0]/nb_fx])    
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx[0]/nb_fx,rx[0]*0.9/nb_fx,rx[0]*0.8/nb_fx,rx[0]*0.7/nb_fx,rx[0]*0.6/nb_fx,rx[0]*0.5/nb_fx,rx[0]*0.4/nb_fx])
    
    result_text += 'Falloff only RS,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f \n' % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,ptv_coverage[0]*100,initial_coverage[0]*100,(dose_in_brain[0]*brain_minus_ptv_vol + ptv_vol)/ptv_vol,rx[0]/100.0)             
    """
           
    