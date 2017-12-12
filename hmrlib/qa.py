# -*- coding: utf-8 -*-
import sys
import os.path
import lib
import poi
import message

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


def process_ac_qa():
    patient = lib.get_current_patient()
    print '{process_ac_qa}\t\t\tPatient : %s, ID : %s' % (patient.PatientName, patient.PatientID)
    for tp in patient.TreatmentPlans:
        if (tp.Name.startswith('D2IS_')):
            create_ac_qa_plan(tp, phantom_name='QAVMAT ARCCHECK')
            compute_ac_qa_plan_dose((vp for vp in tp.VerificationPlans if (vp.ForTreatmentPlan.Name == tp.Name)).next())
    print 'done ...'


def create_ac_qa_plan(plan, phantom_name=None, qa_plan_name=None, iso=None, grid=None, compute=False):
    phantom_name = 'QA VMAT ARCCHECK' if (phantom_name is None) else phantom_name
    qa_plan_name = 'QA AC' if (qa_plan_name is None) else qa_plan_name
    iso = {'x': -0.05, 'y': 2.75, 'z': 6.103515625e-06} if (iso is None) else iso
    grid = {'x': 0.2, 'y': 0.2, 'z': 0.2} if (grid is None) else grid
    print '{create_ac_qa_plan}\t\tTTPlan : %s, QAPlan : %s' % (plan.Name, qa_plan_name)
    logger.info('Creating AC QA plan %s with phantom %s, isocenter %s and grid %s', qa_plan_name, phantom_name, iso, grid)
    for bs in plan.BeamSets:
        bs.CreateQAPlan(PhantomName=phantom_name, QAPlanName=qa_plan_name, IsoCenter=iso, DoseGrid=grid, ComputeDoseWhenPlanIsCreated=compute)


# Modification par MA pour auto-générer les noms des plans QA
def create_ac_qa_plans(plan=None, phantom_name='ARCCHECK', iso_name='ISO AC'):

    ui = get_current("ui")
    patient = lib.get_current_patient()
    if plan is None:
        plan = lib.get_current_plan()

    # Change dose color table reference value to dose of one fraction
    rx_dose = plan.BeamSets[0].Prescription.DosePrescriptions[0].DoseValue
    nb_fx = plan.BeamSets[0].FractionationPattern.NumberOfFractions
    patient.CaseSettings.DoseColorMap.ReferenceValue = rx_dose * 1.1 / nb_fx  # Increase ref dose by 10% because small size of ArcCheck typically leads to higher max dose in phantom than in patient

    # RayStation asks you to save the plan before continuing. This is done automatically, because errors can occur if the user doesn't respond promptly and the script continues.
    patient.Save()

    # Create QA plan (for each beamset) - NOPE just this one
    #for bs in plan.BeamSets:
    
    bs = lib.get_current_beamset()
    bs_name = bs.DicomPlanLabel
    if len(bs_name) > 6:  # To prevent crashes if resulting name will be > 16 characters long
        bs_name = bs.DicomPlanLabel[:6]
    
    if iso_name =='ISO AC':
        name = 'QA ' + patient.PatientName[:4] + ' ' + bs_name
    else:
        name = 'PD ' + patient.PatientName[:4] + ' ' + bs_name

    # Open the QA Preparation tab
    if lib.check_version(4.7):
        ui.MenuItem[6].Button_QAPreparation.Click()
    elif lib.check_version(4.6):
        ui.MenuItem[8].Button_QAPreparation.Click()
    # Click button "New QA plan"
    ui.TabControl_ToolBar.ToolBarGroup.__0.Button_NewQAPlan.Click()
    # Enter a name in the plan name text box
    ui.TextBox_VerificationPlanName.Text = name
    # Open the phantom list dropdown and selects phantom
    ui.ComboBox_PhantomList.ToggleButton.Click()
    ui.ComboBox_PhantomList.Popup.ComboBoxItem[phantom_name].Select()
    # ui.ComboBox_PhantomList.Popup.ComboBoxItem['QAVMAT ARCCHECK_2016'].Select() #Phantom for use in Dev database
    # Check the box to compute dose after plan is created
    ui.CheckBox._Compute_dose_when_the_QA_plan_is_created.Click()
    # Select POI position for isocenter, open dropdown menu and select ISO AC
    ui.RayRadionButton._1.Click()
    ui.ComboBox_PointsOfInterests.ToggleButton.Click()
    ui.ComboBox_PointsOfInterests.Popup.ComboBoxItem[iso_name].Select()
    # Marks checkbox to use uniform resolution and set to 0.2cm
    ui.CheckBox._Use_uniform_resolution.Click()
    ui.TextBox_DoseGridResolutionPresentationX.Text = ".2"
    # Collapse all angles couch, gantry and coll to 0 degrees
    if iso_name == '2cm EPID'or iso_name == '4.8cm MapCheck IMF':
        ui.RayRadionButton._4.Click()
        ui.RayRadionButton._6.Click()
        ui.RayRadionButton._8.Click()
    
    ui.Button_OK.Click()
    
    #si c'est des Mapcheck
    if iso_name == '2cm EPID' or iso_name == '4.8cm MapCheck IMF':
        ui.TabControl_ToolBar.ToolBarGroup._DATA_EXPORT.Button_ExportPlan___.Click()
        # Unselect RT Dose for each beam, RT structures and CT Image
        ui.QADicomExportDialogContent.CheckBox[3].Click()
        ui.QADicomExportDialogContent.CheckBox[4].Click()
        # Export plan, total dose and beam doses to Maggie
        ui.QADicomExportDialogContent.PropertyRow[1].RadioButton.Click()  # Select DICOM Store for export
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.ToggleButton.Click()
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.Popup.ComboBoxItem['MAGGIE [11.1.7.5]'].Select()
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.ToggleButton.Click()
        
        
        #to actually click OK for export
        ui.QADicomExportDialogContent.Button['Export'].Click()
        #message.message_window('Les fichiers des plannar doses sont maintenant dans MAGGIE')
    
    # Open the Export QA plan
    else: 
        ui.TabControl_ToolBar.ToolBarGroup._DATA_EXPORT.Button_ExportPlan___.Click()
        # Unselect RT Dose for each beam, RT structures and CT Image
        ui.QADicomExportDialogContent.CheckBox[2].Click()
        ui.QADicomExportDialogContent.CheckBox[3].Click()
        ui.QADicomExportDialogContent.CheckBox[4].Click()
        # Export plan, total dose and beam doses to Maggie
        ui.QADicomExportDialogContent.PropertyRow[1].RadioButton.Click()  # Select DICOM Store for export
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.ToggleButton.Click()
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.Popup.ComboBoxItem['MAGGIE [11.1.7.5]'].Select()
        ui.QADicomExportDialogContent.PropertyRow[1].ComboBox.ToggleButton.Click()
        
        
        #to actually click OK for export
        ui.QADicomExportDialogContent.Button['Export'].Click()
        #message.message_window('Les fichiers RP et RD sont maintenant dans MAGGIE')
        
        
        

        
def compute_ac_qa_plan_dose(verif_plan):
    print '{compute_ac_qa_plan_dose}\t\tTTPlan : %s, QAPlan : %s' % (verif_plan.ForTreatmentPlan.Name, verif_plan.BeamSet.DicomPlanLabel)
    verif_plan.BeamSet.ComputeDose(ComputeBeamDoses=False, DoseAlgorithm='CCDose', ForceRecompute=False, ScaleToPrescription=False)


def compute_qa_plan_dose(compute_beam_doses=False, dose_algorithm='CCDose', scale_to_prescription=False, plan=None):
    """
        Calculates the QA plan dose for QA plans associated with the currently
        selected plan.

        If the dose is already computed with the same algorithm, this function
        will not force recomputation.

        Args:
            compute_beam_doses (bool, optional): whether or not to compute individual beam doses (default *False*)
            dose_algorithm (str, optional): one onef *CCDose* (accurate) or *SVD* (fast) (default *CCDose*)
            scale_to_prescription (bool, optional): whether or not to scale MUs to dose prescription ? (default *False*)
    """

    if plan is None:
        plan = lib.get_current_plan()

    for vp in plan.VerificationPlans:
        if vp.ForTreatmentPlan.Name == plan.Name:
            vp.BeamSet.ComputeDose(ComputeBeamDoses=compute_beam_doses, DoseAlgorithm=dose_algorithm, ScaleToPrescription=scale_to_prescription)


def export_planar_dose_images(poi_name='planar dose', orientation='coronal', px_size_cm=0.1, size_cm=1):
    """
        Exports planar dose images for the currently selected beamset.

        Each beam will be exported in a separate image.

        BETA/EXPERIMENTAL

        TODO: finalize implementation, allow to choose save path of file.
    """

    beamset = lib.get_current_beamset()

    point = poi.get_poi_coordinates(poi_name)

    n = int(size_cm / px_size_cm)
    points = []

    if orientation == 'coronal':
        # horiz = DICOM x-axis
        # vert = DICOM z axis

        # Initial corner
        pt = point - lib.RSPoint(0.5 * size_cm, 0, 0.5 * size_cm)
        dx = lib.RSPoint(px_size_cm, 0, 0)
        dy = lib.RSPoint(0, 0, px_size_cm)

        for iy in range(0, n + 1):
            for ix in range(0, n + 1):

                points.append(pt.value)
                pt = pt + dx

            pt = pt + dy
            pt = pt - lib.RSPoint(size_cm, 0, 0)

    ret = beamset.FractionDose.InterpolateDoseInPoints(Points=points)

    for c, d in zip(points, ret):
        print c, d

    # logger.warning(x_coord)
    # logger.warning(y_coord)
    # logger.warning(d_value)

    ""


def shift_plans_QA(print_results=True):
    """
    Checks all existing QA plans to see if they have a dose specification
    point (which should correspond to the point of dose max).

    If a DSP is found, the isocenter is shifted and the plan is recalculated,
    which should usually move the MicroLion to the point of dose max.

    This script should only be used if the beams are currently on the phantom isocenter point
    (where the MicroLion is situated). If not, then the displacements printed to file may be incorrect!
    """
    patient = lib.get_current_patient()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    grid = {'x': 0.2, 'y': 0.2, 'z': 0.2}

    #Determine which verification plan we are currently
    vp = None
    for vpl in plan.VerificationPlans:
        if vpl.ForTreatmentPlan.Name == plan.Name and vpl.OfRadiationSet.DicomPlanLabel == beamset.DicomPlanLabel:
            vp = vpl
            break
    
    #If no appropriate verification plan is found, do nothing
    if vp == None:
        message.message_window('Aucun plan QA trouvé')
        return
    
    message.message_window('Le nom du plan QA trouvé est ' + vpl.BeamSet.DicomPlanLabel)
    
    #for vp in plan.VerificationPlans:
    try:
        p = lib.RSPoint(point=vp.BeamSet.DoseSpecificationPoints[0].Coordinates)  # get coords of first DSP (if it exists)
    except:
        message.message_window('Aucun DSP trouvé dans le plan QA')
        return

    # Find coordinates of current isocenter (rounded to a tenth of a millimeter)
    iso_x = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.x, 2)
    iso_y = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.y, 2)
    iso_z = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.z, 2)

    # Formula for new isocenter: 2*(iso coordinate) - dose max coordinate (rounded)
    p.x = 2 * iso_x - round(p.x, 2)
    p.y = 2 * iso_y - round(p.y, 2)  # difference between DICOM and patient coordinate systems, y=-z
    p.z = 2 * iso_z - round(p.z, 2)  # difference between DICOM and patient coordinate systems, z=y

    # Round DSP coordinates to avoid sub-millimeter table displacements
    p.x = round(p.x, 1) + (iso_x - round(iso_x, 1))
    p.y = round(p.y, 1) + (iso_y - round(iso_y, 1))  # If iso_y = 2.75, then you get (2.75-2.8) = -0.05
    p.z = round(p.z, 1) + (iso_z - round(iso_z, 1))

    # Eliminate displacements that are 2mm or less
    if abs(p.x - iso_x) < 0.21:
        p.x = iso_x
    if abs(p.y - iso_y) < 0.21:
        p.y = iso_y
    if abs(p.z - iso_z) < 0.21:
        p.z = iso_z

    # Add SHIFT to plan name (truncate name if resulting name will be >16 characters)
    if len(vp.BeamSet.DicomPlanLabel) > 9:  # To prevent crashes if resulting name will be > 16 characters long
        name = vp.BeamSet.DicomPlanLabel[:9] + ' SHIFT'
    else:
        name = vp.BeamSet.DicomPlanLabel + ' SHIFT'
    vp.BeamSet.DicomPlanLabel = name

    # Shift isocenter
    #plan.BeamSets[vp.OfRadiationSet.Number-1].CreateQAPlan(PhantomName='QA VMAT ARCCHECK', QAPlanName=name, IsoCenter=p.value, DoseGrid=grid, ComputeDoseWhenPlanIsCreated=True)
    for beam in vp.BeamSet.Beams:
        beam.PatientToBeamMapping.IsocenterPoint = {'x': p.x, 'y': p.y, 'z': p.z}

    # Move DSP to isocenter coordinates and assign as spec point for all beams
    try:
        dsp = vp.BeamSet.DoseSpecificationPoints[0]
        dsp.Name = "ISO MicroLion"
        dsp.Coordinates = {'x': iso_x, 'y': iso_y, 'z': iso_z}
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise

    for beam in vp.BeamSet.Beams:
        beam.SetDoseSpecificationPoint(Name="ISO MicroLion")

    # Compute dose (this is done last, because otherwise changing beam spec points erases dose)
    vp.BeamSet.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)

    # Write displacement to file
    # Get demographic information
    patient_ID = patient.PatientID
    patient_name = patient.PatientName.replace("^", ", ")

    if print_results is True:        
        try:
            file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\QA'
            file_path += '\\' + patient_name + '~' + patient_ID + '-TESTSUPERBRIDGE'

            # Write to file

            with open(file_path + '\\Déplacement ArcCheck ' + name + ".txt", 'w') as dvh_file:
                dvh_file.write('Patient:                    ' + patient_name + '\n')
                dvh_file.write('No. HMR:                    ' + patient_ID + '\n\n\n')
                dvh_file.write('Déplacement ArcCheck pour QA plan: ' + name + '\n\n')

                shift_x = p.x - iso_x
                if shift_x > 0:
                    direction_x = 'vers A'
                elif shift_x < 0:
                    direction_x = 'vers B'
                if shift_x != 0:
                    dvh_file.write('          LATERAL: ' + str(abs(shift_x)) + 'cm ' + direction_x + '\n')
                else:
                    dvh_file.write('          LATERAL: Aucun shift\n')

                shift_z = p.z - iso_z
                if shift_z > 0:
                    direction_z = 'OUT'
                elif shift_z < 0:
                    direction_z = 'IN'
                if shift_z != 0:
                    dvh_file.write('     LONGITUDINAL: ' + str(abs(shift_z)) + 'cm ' + direction_z + '\n')
                else:
                    dvh_file.write('     LONGITUDINAL: Aucun shift\n')

                shift_y = p.y - iso_y
                if shift_y > 0:
                    direction_y = 'UP'
                elif shift_y < 0:
                    direction_y = 'DOWN'
                if shift_y != 0:
                    dvh_file.write('          HAUTEUR: ' + str(abs(shift_y)) + 'cm ' + direction_y + '\n')
                else:
                    dvh_file.write('          HAUTEUR: Aucun shift\n')

                # Print dose to MicroLion with AC shift
                dsp_temp = lib.RSPoint(dsp.Coordinates.x, dsp.Coordinates.y, dsp.Coordinates.z)
                dsp_dose = vp.BeamSet.FractionDose.InterpolateDoseInPoint(Point=dsp_temp.value)
                dvh_file.write("\n\nNouveau dose au point %s : %.3fGy" % (dsp.Name, dsp_dose / 100.0))
                dvh_file.write("\n\nDose par faisceau: ")
                for beamdose in vp.BeamSet.FractionDose.BeamDoses:
                    dose_per_beam = beamdose.InterpolateDoseInPoint(Point=dsp_temp.value)
                    dvh_file.write("\n     %s : %.3fGy" % (beamdose.ForBeam.Name, dose_per_beam / 100.0))
    
        except:
            texte = 'Impossible de créer le fichier texte avec les déplacements. SVP, notez les valeurs ci-dessous:\n\n'
            shift_x = p.x - iso_x
            if shift_x > 0:
                direction_x = 'vers A'
            elif shift_x < 0:
                direction_x = 'vers B'
            if shift_x != 0:
                texte += '          LATERAL: ' + str(abs(shift_x)) + 'cm ' + direction_x + '\n'
            else:
                texte += '          LATERAL: Aucun shift\n'

            shift_z = p.z - iso_z
            if shift_z > 0:
                direction_z = 'OUT'
            elif shift_z < 0:
                direction_z = 'IN'
            if shift_z != 0:
                texte += '     LONGITUDINAL: ' + str(abs(shift_z)) + 'cm ' + direction_z + '\n'
            else:
                texte += '     LONGITUDINAL: Aucun shift\n'

            shift_y = p.y - iso_y
            if shift_y > 0:
                direction_y = 'UP'
            elif shift_y < 0:
                direction_y = 'DOWN'
            if shift_y != 0:
                texte += '          HAUTEUR: ' + str(abs(shift_y)) + 'cm ' + direction_y + '\n'
            else:
                texte += '          HAUTEUR: Aucun shift\n'

            message.message_window(texte)
  
  
def find_current_verification_plan(plan,beamset):
    
    #Determine which verification plan we are currently
    vp = None
    for vpl in plan.VerificationPlans:
        if vpl.ForTreatmentPlan.Name == plan.Name and vpl.OfRadiationSet.DicomPlanLabel == beamset.DicomPlanLabel:
            vp = vpl
            break        
    
    return vp

    
def preparation_qa():

    #QA preparation script for dosimetrists
    # - Creates QA plan for the currently selected beamset on the ArcCheck phantom
    # - Notes dose to MicroLion
    # - Notes max dose and its location
    # - Shifts the isocenter to put the point of max dose on the MicroLion (most of the time)
    # - Recomputes dose and then exports dose to MicroLion before and after shift, along with instructions for the shift

    patient = lib.get_current_patient()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    
    output = "Patient: %s\nPlan: %s\nBeamset: %s\n" % (patient.PatientName.replace("^", ", "),plan.Name,beamset.DicomPlanLabel)
    
    #Create QA plan centered on ISO AC
    create_ac_qa_plans()
    ui = get_current("ui")
    ui.MessageBoxWindowContent.Button['OK'].Click() #Clears away dialogue after exporting DICOM files (or failing to)
    vp = find_current_verification_plan(plan,beamset)
    output += "Plan QA: " + vp.BeamSet.DicomPlanLabel + '\n'
    
    #Find coordinates of current isocenter (rounded to a tenth of a millimeter)
    iso_x = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.x, 2)
    iso_y = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.y, 2)
    iso_z = round(vp.BeamSet.Beams[0].PatientToBeamMapping.IsocenterPoint.z, 2)
    
    #Get total dose at isocenter as well as each beam's contribution
    isocenter_rsp = lib.RSPoint(iso_x, iso_y, iso_z)
    isocenter_dose = vp.BeamSet.FractionDose.InterpolateDoseInPoint(Point=isocenter_rsp.value)
    output += "\nPLAN CENTRÉ\nDose à l'isocentre: %.2fGy" % (isocenter_dose/100.0)
    for beamdose in vp.BeamSet.FractionDose.BeamDoses:
        dose_per_beam = beamdose.InterpolateDoseInPoint(Point=isocenter_rsp.value)
        output += "\n     %s : %.2fGy" % (beamdose.ForBeam.Name, dose_per_beam / 100.0)

    #Determine location of max dose point and the dose it receives
    fraction_dose = vp.BeamSet.FractionDose
    grid = vp.DoseGrid
    max_dose,max_coords = poi.get_max_dose_coordinates(fraction_dose,grid)
    
    #Create a DSP at this point
    vp.BeamSet.CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': max_coords.x, 'y': max_coords.y, 'z': max_coords.z })
    
    # Formula for new isocenter: 2*(iso coordinate) - dose max coordinate (rounded)
    new_iso = lib.RSPoint(0, 0, 0)
    new_iso.x = 2 * iso_x - round(max_coords.x, 2)
    new_iso.y = 2 * iso_y - round(max_coords.y, 2)
    new_iso.z = 2 * iso_z - round(max_coords.z, 2)

    # Round DSP coordinates to avoid sub-millimeter table displacements
    new_iso.x = round(new_iso.x, 1) + (iso_x - round(iso_x, 1))
    new_iso.y = round(new_iso.y, 1) + (iso_y - round(iso_y, 1))  # If iso_y = 2.75, then you get (2.75-2.8) = -0.05
    new_iso.z = round(new_iso.z, 1) + (iso_z - round(iso_z, 1))

    # Eliminate displacements that are 2mm or less
    if abs(new_iso.x - iso_x) < 0.21:
        new_iso.x = iso_x
    if abs(new_iso.y - iso_y) < 0.21:
        new_iso.y = iso_y
    if abs(new_iso.z - iso_z) < 0.21:
        new_iso.z = iso_z
    
    #Set all beams to the new isocenter
    for beam in vp.BeamSet.Beams:
        beam.PatientToBeamMapping.IsocenterPoint = {'x': new_iso.x, 'y': new_iso.y, 'z': new_iso.z}    
    
    #Now that we're done with our DSP, set it back to the original isocenter coordinates to get dose to MicroLion
    dsp = vp.BeamSet.DoseSpecificationPoints[0]
    dsp.Name = "ISO MicroLion"
    dsp.Coordinates = {'x': iso_x, 'y': iso_y, 'z': iso_z}        

    for beam in vp.BeamSet.Beams:
        beam.SetDoseSpecificationPoint(Name="ISO MicroLion")

    # Compute dose (this is done last, because otherwise changing beam spec points erases dose)
    vp.BeamSet.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)
    
    #Calculate shift
    shift_x = new_iso.x - iso_x    
    shift_y = new_iso.y - iso_y
    shift_z = new_iso.z - iso_z
    
    if shift_x == 0 and shift_y == 0 and shift_z == 0:
        output += "\n\nL'isocentre se trouve sur le point de dose max. Aucun shift automatique a été calculé."
    else:
        if (isocenter_dose/max_dose) < 0.75:
            output += "\n\nLa dose à l'isocentre est inférieure à 75% de la dose maximale.\nIl est nécessaire de mesurer la dose au MicroLion avec le shift suivant:\n\n"
        else:
            output += "\n\nLa dose à l'isocentre est supérieure à 75% de la dose maximale.\nIl n'est probablement pas nécessaire de faire un shift, mais voici une possibilité de shift au cas ou:\n\n"
        
        if shift_x > 0:
            direction_x = 'vers A'
        elif shift_x < 0:
            direction_x = 'vers B'
        if shift_x != 0:
            output += '          LATERAL: ' + str(abs(shift_x)) + 'cm ' + direction_x + '\n'
        else:
            output += '          LATERAL: Aucun shift\n'

        if shift_y > 0:
            direction_y = 'UP'
        elif shift_y < 0:
            direction_y = 'DOWN'
        if shift_y != 0:
            output += '          HAUTEUR: ' + str(abs(shift_y)) + 'cm ' + direction_y + '\n'
        else:
            output += '          HAUTEUR: Aucun shift\n'
            
        if shift_z > 0:
            direction_z = 'OUT'
        elif shift_z < 0:
            direction_z = 'IN'
        if shift_z != 0:
            output += '     LONGITUDINAL: ' + str(abs(shift_z)) + 'cm ' + direction_z + '\n'
        else:
            output += '     LONGITUDINAL: Aucun shift\n'            
            
        if direction_z == 'IN':
            output += "ATTENTION: Suite au déplacement vers IN, assurez-vous que le faisceau n'irradierais pas l'électronique du ArcCheck\n"

        # Print dose to MicroLion with AC shift
        isocenter_dose = vp.BeamSet.FractionDose.InterpolateDoseInPoint(Point=isocenter_rsp.value)
        output += "\nPLAN AVEC SHIFT\nDose à l'isocentre: %.2fGy" % (isocenter_dose/100.0)
        for beamdose in vp.BeamSet.FractionDose.BeamDoses:
            dose_per_beam = beamdose.InterpolateDoseInPoint(Point=isocenter_rsp.value)
            output += "\n     %s : %.2fGy" % (beamdose.ForBeam.Name, dose_per_beam / 100.0)  
            
    
    #For IMRT plans, make a second QA plan to create EPIDStan files
    if vp.BeamSet.DeliveryTechnique == "SMLC":
        num_beams = 0
        num_segments = 0
        for beam in vp.BeamSet.Beams:
            num_beams += 1
            for seg in beam.Segments:
                num_segments += 1
        
        if num_segments > num_beams: #If this is an IMRT plan and not a 3DC plan
            if lib.check_version(4.7):
                phantom_name = '48x48x48 FANTOME'
            elif lib.check_version(4.6):
                phantom_name = '48x48x48 FANTOME'
            create_ac_qa_plans(plan=None,phantom_name=phantom_name,iso_name='2cm EPID')
            ui = get_current("ui")
            ui.MessageBoxWindowContent.Button['OK'].Click() #Clears away dialogue after exporting DICOM files (or failing to)
            output += "\n\nLe plan est fait en IMRT, n'oubliez pas de vérifier la dose 2D à l'aide de EPIDStan\nLes fichiers EPID se trouvent sur MAGGIE"
    
    #Print all results to text file
    try:
        file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\QA'
        file_path += '\\' + patient_name + '~' + patient_ID + '-TESTSUPERBRIDGE'    
        with open(file_path + '\\QA patient ' + vp.BeamSet.DicomPlanLabel + ".txt", 'w') as dvh_file:
            dvh_file.write(output)
    except:
        texte = 'Impossible de créer le fichier texte avec les résultats. SVP, notez les valeurs ci-dessous:\n\n'
        message.message_window(texte + output)
    