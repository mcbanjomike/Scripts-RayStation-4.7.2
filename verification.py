# -*- coding: utf-8 -*-

"""
Ce module contient les outils pour la vérification des plans.
"""

import hmrlib.lib as lib
import hmrlib.poi as poi
import hmrlib.roi as roi
from connect import *

def verify_external_and_overrides():
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    
    override_roi = []
    external_roi = "Aucun trouvé"
    
    #Determine name of external ROI and list of all contours with material overrides
    for roi in patient.PatientModel.StructureSets[exam.Name].RoiGeometries:
        if roi.OfRoi.Type == "External":
            external_roi = roi.OfRoi.Name
        try:
            override_material = roi.OfRoi.RoiMaterial.OfMaterial.Name
            override_roi.append((roi.OfRoi.Name + " (" + override_material + ")"))
        except:
            continue

    #Write results to string
    if external_roi == "Aucun trouvé":
        result_text = "AVERTISSEMENT: Aucun ROI external défini"
    else:        
        result_text = "Nom du contour External: " + external_roi
        
    if len(override_roi) > 0:
        result_text += "\nROIs avec override de matériel: "                
        for item in override_roi:
            result_text += item + "  "
    else:
        result_text += "\nROIs avec override de matériel: Aucun"      
        
    return result_text
    

def verify_prescription():        

    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()    

    # Check if beamset dose is dependent
    try:
        bkgdose_name = plan.PlanOptimizations[beamset.Number-1].BackgroundDose.ForBeamSet.DicomPlanLabel
    except:
        bkgdose_name = "None"
        
    # Determine prescription dose, fractions and target
    try:
        presc_text = str((beamset.Prescription.PrimaryDosePrescription.DoseValue)/100.0) + "Gy"
        presc_text += " en %dfx " % beamset.FractionationPattern.NumberOfFractions
        # Display prescription type and dose
        if beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtPoint':
            presc_text += "au point " + beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
        elif beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtVolume':
            presc_text += "à " + str(beamset.Prescription.PrimaryDosePrescription.DoseVolume) + r'% du volume du ' + beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
        if bkgdose_name != "None":
            presc_text += " (dépendente sur beamset " + bkgdose_name + ")"
        presc_text = presc_text.replace(".0Gy","Gy")
        presc_text = presc_text.replace(".0%","%")
    except:
        presc_text = "Prescription non définie"
    presc_text = "Prescription: " + presc_text                 
    
    return presc_text
    
     
def verify_isocenter():     

    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()

    loc_coords = None
    iso_coords = None
    
    # Isocenter and localization point
    try:
        loc_point_name = beamset.PatientSetup.LocalizationPoiGeometrySource.LocalizationPoiGeometry.OfPoi.Name
        loc_coords = poi.get_poi_coordinates(loc_point_name,exam)
    except:
        loc_point_name = "Aucun point de localisation trouvé"
    
    num_iso = 0                
    if poi.poi_exists("ISO", exam):
        iso_point_name = "ISO"
        num_iso +=1                          
    if poi.poi_exists("ISO B1", exam):
        iso_point_name = "ISO B1"
        num_iso +=1
     
    if num_iso == 0:
        iso_point_name = "Aucun point trouvé pour l'isocentre" 
    elif num_iso > 1:
        iso_point_name = "Plus qu'un candidat trouvé pour l'isocentre"            
    elif num_iso == 1:            
        iso_coords = poi.get_poi_coordinates(iso_point_name,exam) 
    
    if loc_coords is None:
        loc_poi_text = "Aucun point de localisation trouvé"
    else:
        loc_poi_text = "POI localization: %s     (%.2f, %.2f, %.2f)" % (loc_point_name, loc_coords.x, loc_coords.z, -1*loc_coords.y)
    
    if iso_coords is None:
        iso_poi_text = iso_point_name
    else:
        iso_poi_text = "POI isocentre: %s         (%.2f, %.2f, %.2f)" % (iso_point_name, iso_coords.x, iso_coords.z, -1*iso_coords.y)    
    
    shift_text = ""
    
    #Check to find shift from reference point to isocenter
    if loc_coords != None and iso_coords != None:
        if iso_point_name != loc_point_name:
            if (loc_coords.x-iso_coords.x ==0 ) and (loc_coords.y-iso_coords.y == 0) and (loc_coords.z-iso_coords.z == 0):
                shift_text += "Le point de localisation et le point " + iso_point_name + " ont les mêmes coordonnés"
            else:
                shift_text += "Shift de %.2fcm, %.2fcm, %.2fcm entre point de localisation et point %s" % (loc_coords.x-iso_coords.x, loc_coords.z-iso_coords.z, iso_coords.y-loc_coords.y, iso_point_name)     

    # Beam isocenters
    beam_iso_text = "Coordonnées faisceaux: "
    mismatch = False
    try:              
        for i, beam in enumerate(beamset.Beams): #Verify that coordinates are the same for all beams
            if i > 0:
                old_iso_poi = beam_iso_poi
            beam_iso_poi = [x for x in beam.PatientToBeamMapping.IsocenterPoint]
            if i>0:
                if abs(beam_iso_poi[0].Value - old_iso_poi[0].Value) > 0.005 or abs(beam_iso_poi[1].Value - old_iso_poi[1].Value) > 0.005 or abs(beam_iso_poi[2].Value - old_iso_poi[2].Value) > 0.005:
                    beam_iso_text = "Coordonnées faisceaux: Coordonnées différentes pour faisceaux " + beamset.Beams[i-1].Name + " et " + beam.Name + "!"
                    mismatch = True
                    break
        if not mismatch:
            beam_iso_text += "(%.2f, %.2f, %.2f)" % (beam_iso_poi[0].Value, beam_iso_poi[2].Value, beam_iso_poi[1].Value*-1)
    except:
        beam_iso_text += "Coordonnées pas trouvés"

        
    # Verify if beams are centered on isocenter point
    if beam_iso_poi != None and iso_coords != None and not mismatch:
        iso_shift_x = iso_coords.x - beam_iso_poi[0].Value
        iso_shift_y = iso_coords.y - beam_iso_poi[1].Value
        iso_shift_z = iso_coords.z - beam_iso_poi[2].Value
        if abs(iso_shift_x) > 0.005 or abs(iso_shift_y) > 0.005 or abs(iso_shift_z) > 0.005:
            shift_text += "\nShift de %.2fcm, %.2fcm, %.2fcm entre les faisceaux et le point %s" % (-1*iso_shift_x, -1*iso_shift_z, iso_shift_y, iso_point_name)
        else:
            shift_text += "\nTous les faisceaux partagent les coordonnés du point " + iso_point_name
            
    return loc_poi_text, iso_poi_text, beam_iso_text, shift_text
          
     
def verify_beams():
    #patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()     
     
    #Beam details
    number_of_beams = 0
    beam_info = "Nom    /   Description   /    Gantry    /    Sens    /   Colli   /  Couch"
    beams = True
    try:
        beam_name = beamset.Beams[0].Name
    except:
        beams = False
        beam_info = "Aucun faisceau trouvé"
    if beams: #Creat table of beam info
        for i,beam in enumerate(beamset.Beams):
            number_of_beams += 1
            beam_info += "\n" + beam.Name + "    /   "
            beam_info += beam.Description
            #Pad out beam description to try to keep columns aligned if name is short
            if len(beam.Description) < 6:
                beam_info += "       "
            elif len(beam.Description) < 7:
                beam_info += "      "
            elif len(beam.Description) < 9:
                beam_info += "    "
            beam_info += "   /  "
            try: #Checks whether beam has a stop angle (for arcs)
                stop_angle = beam.ArcStopGantryAngle
                beam_info += "  %d-%d   /  " % (beam.GantryAngle, beam.ArcStopGantryAngle)
            except:
                if beam.GantryAngle < 10:
                    beam_info += "  "
                beam_info += "     %d      /  " % (beam.GantryAngle)
            if beam.ArcRotationDirection == "Clockwise":
                beam_info += "  CW   "
            elif beam.ArcRotationDirection == "CounterClockwise":
                beam_info += "  CCW  "
            else:
                beam_info += "Statique"
            beam_info += " /   " + str(beam.InitialCollimatorAngle)
            if beam.InitialCollimatorAngle >= 0 and beam.InitialCollimatorAngle < 10:
                beam_info += "    "   #Adds a spacer to keep the columns aligned
            elif beam.InitialCollimatorAngle >= 10 and beam.InitialCollimatorAngle < 100:
                beam_info += " "   #Adds a spacer to keep the columns aligned
            beam_info += "   /      %d     " % (beam.CouchAngle)
    
        #Check if first and last leaf pairs are open (anywhere)
        machine_type = beam.MachineReference.MachineName   
        first_leaf_open = False
        last_leaf_open = False    
        leaf_open_text = ""
        for beam in beamset.Beams:
            try:
                temp = beam.Segments[0].CollimatorAngle #Just to see if there are segments defined for the beam
                for seg in beam.Segments:
                    if first_leaf_open == False: #Stop checking if a segment is found where leaves are open
                        if machine_type == "BeamMod":
                            if seg.LeafPositions[0][0] != seg.LeafPositions[1][0]:
                                first_leaf_open = True
                                #first_leaf_open_seg = seg.SegmentNumber
                                #first_leaf_open_name = beam.Name                              
                    if last_leaf_open == False:
                        if machine_type == "BeamMod":
                            if seg.LeafPositions[0][39] != seg.LeafPositions[1][39]:
                                last_leaf_open = True
                                #last_leaf_open_seg = seg.SegmentNumber
                                #last_leaf_open_name = beam.Name
            except:             
                leaf_open_text += "Impossible de vérifier les segments car\nau moins un faisceau n'a pas de segments valides"
                return beam_info, number_of_beams, leaf_open_text
                                
        if machine_type != 'BeamMod': 
            leaf_open_text += "Vérification des lames seulement possible sur Beam Modulator"
        elif first_leaf_open and last_leaf_open:
            leaf_open_text += "Première et dernère paire de lames ouvertes dans au moins un segment,\nPTV potentiellement trop large pour collimateur"
        elif first_leaf_open and not last_leaf_open:
            leaf_open_text += "Première paire de lames ouverte dans au moins un segment,\nil est peut-être nécessaire de déplacer l'isocentre"
        elif not first_leaf_open and last_leaf_open:
            leaf_open_text += "Dernière paire de lames ouverte dans au moins un segment,\nil est peut-être nécessaire de déplacer l'isocentre"
        elif not first_leaf_open and not last_leaf_open:
            leaf_open_text += "Première et dernière paires de lames fermées pour tous les segments"

    
    return beam_info, number_of_beams, leaf_open_text  

    
def verify_opt_parameters():
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset() 
    
    opt = plan.PlanOptimizations[beamset.Number-1]
    
    # Number of optimizations and tolerance
    iterations_text = "Optimization: "    
    iterations_text += "%d iterations / %d avant la conversion" % (opt.OptimizationParameters.Algorithm.MaxNumberOfIterations, opt.OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase)
    iterations_text += ", Stopping Tolerance " + str(opt.OptimizationParameters.Algorithm.OptimalityTolerance)
    
    # Computation of intermediate/final dose    
    dose_calc_text = "Compute Intermediate Dose / Final Dose: "
    if opt.OptimizationParameters.DoseCalculation.ComputeIntermediateDose == True:
        dose_calc_text += "oui / "
    else:
        dose_calc_text += "non / "
    if opt.OptimizationParameters.DoseCalculation.ComputeFinalDose == True:
        dose_calc_text += "oui"
    else:
        dose_calc_text += "non"
        
        
    #Beam optimization parameters (these depend on whether the plan is VMAT or static)
    time_mismatch = False
    spacing_mismatch = False
    opt_types_mismatch = False            
    
    if beamset.DeliveryTechnique == "Arc":
        settings_text = "Constrain Leaf Motion: "
        if beamset.DeliveryTechnique == "Arc":
            if opt.OptimizationParameters.SegmentConversion.ArcConversionProperties.UseMaxLeafTravelDistancePerDegree == True:
                settings_text += "%.1fcm/deg\n" % opt.OptimizationParameters.SegmentConversion.ArcConversionProperties.MaxLeafTravelDistancePerDegree
            else:
                settings_text += "pas coché\n"
    
    
        settings_text = "Gantry Spacing / Max Delivery Time: "
        
        old_time = 0
        new_time = 0
        old_spacing = 0
        new_spacing = 0
        old_opt_types = ""
        new_opt_types = ""              
        
        for ts in opt.OptimizationParameters.TreatmentSetupSettings:
            for i, beam_setting in enumerate(ts.BeamSettings):
                new_spacing = beam_setting.ArcConversionPropertiesPerBeam.FinalArcGantrySpacing
                new_time = beam_setting.ArcConversionPropertiesPerBeam.MaxArcDeliveryTime
                new_opt_types = ""
                for opt_type in beam_setting.OptimizationTypes:
                    new_opt_types += opt_type
                if i > 0:
                    if old_spacing != new_spacing:
                        spacing_mismatch = True
                    if old_time != new_time:
                        time_mismatch = True
                    if old_opt_types != new_opt_types:
                        opt_types_mismatch = True
                old_spacing = new_spacing
                old_time = new_time
                old_opt_types = new_opt_types
        if spacing_mismatch:
            settings_text += "pas pareil pour tous les faisceaux / "
        else:
            settings_text += "%d degrés / " % new_spacing
        if time_mismatch:
            settings_text += "pas pareil pour tous les faisceaux"
        else:
            settings_text += "%ds" % new_time               
        
    else: #For IMRT and 3DC
        settings_text = "Segment MU / Segment Area / Leaf Pairs / Leaf End Separation / Nb Segments"  
        settings_text += "\n       %dUMs      /        %d cm2       /        %d        /              %dcm              /          %d" % (opt.OptimizationParameters.SegmentConversion.MinSegmentMUPerFraction, opt.OptimizationParameters.SegmentConversion.MinSegmentArea, opt.OptimizationParameters.SegmentConversion.MinNumberOfOpenLeafPairs, opt.OptimizationParameters.SegmentConversion.MinLeafEndSeparation, opt.OptimizationParameters.SegmentConversion.MaxNumberOfSegments)
        
        old_opt_types = ""
        new_opt_types = ""
        
        for ts in opt.OptimizationParameters.TreatmentSetupSettings:
            for i, beam_setting in enumerate(ts.BeamSettings):
                new_opt_types = ""
                for opt_type in beam_setting.OptimizationTypes:
                    new_opt_types += opt_type
                if i > 0 and old_opt_types != new_opt_types:
                    opt_types_mismatch = True
                old_opt_types = new_opt_types

    opt_types_text = "Optimize Segment Shapes / Segment MU: "
    if opt_types_mismatch:
        opt_types_text += "pas pareil pour tous les faisceaux"
    else:
        if new_opt_types == "SegmentOptSegmentMU" or new_opt_types == "SegmentMUSegmentOpt":
            opt_types_text += "oui / oui"
        elif new_opt_types == "SegmentOpt":
            opt_types_text += "oui / non"
        elif new_opt_types == "SegmentMU":
            opt_types_text += "non / oui"
        elif new_opt_types == "":
            opt_types_text += "non / non"
            
            
    return iterations_text, dose_calc_text, settings_text, opt_types_text
            
    #if time_mismatch or spacing_mismatch or opt_types_mismatch:
        #warning_text += "AVERTISSEMENT: Beam Optimization Parameters pas pareils pour tous les faisceaux\n"                