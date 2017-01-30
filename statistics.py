# -*- coding: utf-8 -*-

"""
Ce module contient les outils pour la vérification des plans.
"""

import hmrlib.lib as lib
import hmrlib.poi as poi
import hmrlib.roi as roi
import message
import math

from connect import *

def stereo_brain_statistics():
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()    
   
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    #Get prescription information
    rx_dose = beamset.Prescription.PrimaryDosePrescription.DoseValue
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name  # Need to run statistics before converting to point dose
    
    #Get brain volume and position
    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU'].GetRoiVolume()
    brain_center = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU'].GetCenterOfRoi()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU-PTV'].GetRoiVolume()
    
    #Get PTV volume and position
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
    ptv_center = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetCenterOfRoi()
    
    #Check for sub-PTVs
    sub_ptvs = []
    sub_ptv_vol_total = 0
    for name in roi_names:
        if name in ['PTV1','PTV2','PTV3','PTV4','PTV5','PTV6','PTV7','PTV8','PTV9']:
            sub_ptvs.append(name)
            sub_ptv_vol_total += patient.PatientModel.StructureSets[exam.Name].RoiGeometries[name].GetRoiVolume()
    if len(sub_ptvs) == 0:
        number_sub_ptvs = 1
        sub_ptv_vol_total = ptv_vol
    else:
        number_sub_ptvs = len(sub_ptvs)
    
    #Compute volume of bounding box (should be roughly 6/pi or 1.91 times volume of spherical PTV if only one tumor) - use to check if multiple tumors
    bb = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetBoundingBox()
    bb_vol = abs((bb[0].x-bb[1].x)*(bb[0].y-bb[1].y)*(bb[0].z-bb[1].z))
    
    
    #Compute radii of brain and PTV
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    ptv_radius = math.pow(3*ptv_vol/(4*math.pi),1.0/3)
    
    #Find distance from brain center to PTV center
    distance_brain_ptv = math.sqrt((brain_center.x - ptv_center.x)**2 + (brain_center.y - ptv_center.y)**2 + (brain_center.z - ptv_center.z)**2)
    
    #Get DVH information
    #dose_in_brain = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='CERVEAU-PTV', DoseValues=[rx_dose,rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5,1200,1000])
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='CERVEAU-PTV', DoseValues=[rx_dose,rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5,1200,1000])
    #dose_in_body = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='BodyRS', DoseValues=[rx_dose,rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5,1200,1000])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='BodyRS', DoseValues=[rx_dose,rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5,1200,1000])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['BodyRS'].GetRoiVolume()
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V50,12Gy,10Gy)
    
    #Calculate D1% for OARs
    oar_list = ['MOELLE','OEIL DRT','OEIL GCHE','TR CEREBRAL','CHIASMA','NERF OPT DRT','NERF OPT GCHE']
    oar_d1 = [0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'BodyRS',RelativeVolumes = [0.03/body_vol])
    
    #Check whether GTV has Min Dose objective
    gtv_objective = 'Non'
    for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
        if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
            gtv_objective = 'Oui'
            break
            
    #Check number of beams
    num_beams = 0
    for beam in beamset.Beams:
        num_beams +=1
    
    #Add checks to see whether PTV overlaps with TR CEREBRAL and whether PTV extends outside of brain, but this will require creating volumes in RS and will slow down the stats collecting a bit
    #TEST THESE FURTHER
    tronc_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV tronc", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
    tronc_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["TR CEREBRAL"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    tronc_overlap.UpdateDerivedGeometry(Examination=exam)
    ptv_tronc_overlap = roi.get_roi_volume(tronc_overlap.Name, exam=exam) / ptv_vol
    tronc_overlap.DeleteRoi()
    
    brain_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV brain", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
    brain_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["CERVEAU"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    brain_overlap.UpdateDerivedGeometry(Examination=exam)
    ptv_brain_overlap = roi.get_roi_volume(brain_overlap.Name, exam=exam) / ptv_vol
    brain_overlap.DeleteRoi()
    
    #Generate output string
    output = patient.PatientName + ',' #+ patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' #Demographic information
    output += "%.2f,%d," % (rx_dose/100.0,nb_fx) #Prescription information
    output += "%.3f,%.3f,%.3f," % (ptv_center.x,ptv_center.y,ptv_center.z) #DICOM coordinates of PTV center        
    output += "%.3f,%.3f," % (ptv_vol,ptv_radius) #Volume and (estimated) radius of PTV
    output += "%.3f,%.3f,%.3f," % (brain_center.x,brain_center.y,brain_center.z) #DICOM coordinates of brain center
    output += "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    output += "%.3f," % distance_brain_ptv #Distance from PTV center to brain center in cm
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*100,dose_in_brain[1]*100,dose_in_brain[2]*100,dose_in_brain[3]*100,dose_in_brain[4]*100,dose_in_brain[5]*100,dose_in_brain[6]*100,dose_in_brain[7]*100) #CERV-PTV V100...V50,V10Gy,V12Gy in percentage
    output += "%.3f,%.3f," % (dose_in_brain[6]*brain_minus_ptv_vol,dose_in_brain[7]*brain_minus_ptv_vol) #CERV-PTV V12 and V10 in cc
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7]) #Estimated radii for V100,V90...V50,V12Gy,V10Gy in body
    output += "%d,%.3f," % (number_sub_ptvs,sub_ptv_vol_total)
    output += "%.3f," % bb_vol #Volume of bounding box (cc)
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d" % num_beams + ','
    output += beamset.DeliveryTechnique + ','
    output += "%.2f,%.2f" % (ptv_tronc_overlap,ptv_brain_overlap)
    #message.message_window(output)
    
    #Write to file
    file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane.txt'
    #file_path += '\\crane.txt'
    with open(file_path, 'a') as stat_file:
        #The line below prints the key, only do so if starting the stats text file over from scratch        
        #stat_file.write('Name,ID,Plan name,Beamset name,Rx dose (Gy),Nb of fractions,PTV x,PTV y,PTV z,PTV vol,PTV radius,CERV x,CERV y,CERV z,CERV vol,CERV radius,Dist CERV-PTV,CERV-PTV V100,CERV-PTV V90,CERV-PTV V80,CERV-PTV V70,CERV-PTV V60,CERV-PTV V50,CERV-PTV V12Gy,CERV-PTV V10Gy,CERV-PTV V12Gy cc,CERV-PTV V10Gy cc,V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,12Gy radius,10Gy radius,Number sub-PTVs,combined vol sub-PTVs,PTV bounding box vol,D1% MOELLE (Gy),D0.01 OEIL DRT (Gy),D0.01 OEIL GCHE (Gy),D0.01 TR CEREBRAL (Gy),D0.01 CHIASMA (Gy),D0.01 NERF OPT DRT (Gy),D0.01 NERF OPT GCHE (Gy),Max globale (Gy),Min dose objective sur GTV, Nb de faisceaux,Technique,Fraction PTV ds TRONC, Fraction PTV ds CERVEAU\n')
        stat_file.write(output + '\n')

    
    """
    ADD:
    Dmax (global)
    D1% for OARs
    (maybe) check if PTV overlaps TRONC
    (maybe) check if PTV exits brain
    
    THINGS TO OUTPUT:
    Vol of PTV-cerveau - OK
    Vol of brain - OK
    Percentage of PTV in brain
    V90/80/70... for brain
    V90/80/70... for BodyRS
    Obtained V10/V12
    Determine how far from PTV to outside brain
    Determine how far from PTV to outside body
        Use series of expansions on PTV, intersect with brain/body, see what percentage falls outside?
        Alternately, compare position of PTV to middle of brain, assume sphere to determine brain radius, compare those values
    """