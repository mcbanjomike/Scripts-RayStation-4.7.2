
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
        