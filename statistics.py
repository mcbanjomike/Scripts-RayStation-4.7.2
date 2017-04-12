# -*- coding: utf-8 -*-

"""
Ce module contient les outils pour la vérification des plans.
"""

import hmrlib.lib as lib
import hmrlib.poi as poi
import hmrlib.roi as roi
import hmrlib.eval as eval
import hmrlib.optim as optim
import message
import math

from connect import *

import crane
import beams

#This script runs automatically during plan finalization
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
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU'].GetRoiVolume()
    
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
    
    #Get DVH information (since we're using Fractiondose we have to compensate for nb_fx)
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='CERVEAU-PTV', DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,1200/nb_fx,1000/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='BodyRS', DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,1200/nb_fx,1000/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['BodyRS'].GetRoiVolume()
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V50,12Gy,10Gy)
    
    #Calculate D1% for OARs
    oar_list = ['MOELLE','OEIL DRT','OEIL GCHE','TR CEREBRAL','CHIASMA','NERF OPT DRT','NERF OPT GCHE']
    oar_d1 = [0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'BodyRS',RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx
    
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
    output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' #Demographic information
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
    

#This script runs automatically during plan finalization
def stereo_lung_statistics():
    patient = lib.get_current_patient()
    exam = lib.get_current_examination()
    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()    
   
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    #Get prescription information
    rx_dose = beamset.Prescription.PrimaryDosePrescription.DoseValue
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name  # Need to run statistics before converting to point dose
    
    #Get lung volume
    pmn_drt_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['POUMON DRT'].GetRoiVolume()
    pmn_gche_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['POUMON GCHE'].GetRoiVolume()
    opt_pmns_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['OPT COMBI PMN'].GetRoiVolume()
    
    #Get PTV volume and radius
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
    ptv_radius = math.pow(3*ptv_vol/(4*math.pi),1.0/3)
    
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
            
    #Get DVH information - IMPORTANT: FractionDose is used for evaluation, so it is important to multiply or divide values by nb_fx to get DVH values for total plan
    dose_in_pmns = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='COMBI PMN-ITV-BR', DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])
    dose_in_pmn_drt = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='POUMON DRT', DoseValues=[rx_dose/nb_fx])
    dose_in_pmn_gche = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='POUMON GCHE', DoseValues=[rx_dose/nb_fx])
    avg_dose_pmns = nb_fx * beamset.FractionDose.GetDoseStatistic(RoiName='COMBI PMN-ITV-BR', DoseType='Average')
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='BodyRS', DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['BodyRS'].GetRoiVolume()
    r50_max = nb_fx * beamset.FractionDose.GetDoseStatistic(RoiName='r50', DoseType='Max')
    
    #Estimate radius of each isodose
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V100...V50,20Gy,15Gy,10Gy,5Gy)
    
    #Calculate D1% for OARs
    oar_list = ['BR SOUCHE','TRACHEE','COTES','PLEXUS BRACHIAL','MOELLE','OESOPHAGE','COEUR','PAROI']
    oar_d1 = [0,0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = 'BodyRS',RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx
    
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
    
    #Generate output string
    output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' #Demographic information
    output += "%.2f,%d," % (rx_dose/100.0,nb_fx) #Prescription information 
    output += "%.3f,%.3f," % (ptv_vol,ptv_radius) #Volume and (estimated) radius of PTV
    output += "%.3f,%.3f,%.3f," % (pmn_drt_vol,pmn_gche_vol,opt_pmns_vol) #Volumes of each lung and of OPT COMBI PMNS (ie both lungs - PTV)
    output += "%.3f,%.3f," % (dose_in_pmn_drt[0]*100,dose_in_pmn_gche[0]*100) #Rx dose in each lung (to determine laterality)
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_pmns[0]*100,dose_in_pmns[1]*100,dose_in_pmns[2]*100,dose_in_pmns[3]*100,dose_in_pmns[4]*100,dose_in_pmns[5]*100,dose_in_pmns[6]*100,dose_in_pmns[7]*100,dose_in_pmns[8]*100,dose_in_pmns[9]*100) #COMBI PMN-ITV-BR V100...V50,V20Gy,V15Gy,V10Gy,V5Gy in percentage
    output += "%.3f," % (avg_dose_pmns / 100.0)
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8],dose_radius[9]) #Estimated radii for V100...V50,V20Gy,V15Gy,V10Gy,V5Gy in body
    output += "%.3f," % (r50_max/100.0) #Max dose at 2cm
    output += "%d,%.3f," % (number_sub_ptvs,sub_ptv_vol_total)
    output += "%.3f," % bb_vol #Volume of bounding box (cc)
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6],oar_d1[7]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d" % num_beams + ','
    output += beamset.DeliveryTechnique + ','
    
    #Write to file
    file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\poumon.txt'
    with open(file_path, 'a') as stat_file:
        #The line below prints the key, only do so if starting the stats text file over from scratch        
        #stat_file.write('Name,ID,Plan name,Beamset name,Rx dose (Gy),Nb of fractions,PTV vol,PTV radius,PMN DRT vol,PMN GCHE vol,OPT COMBI PMN vol,PMN DRT V100,PMN GCHE V100,COMBI PMN-ITV-BR V100,COMBI PMN-ITV-BR V90,COMBI PMN-ITV-BR V80,COMBI PMN-ITV-BR V70,COMBI PMN-ITV-BR V60,COMBI PMN-ITV-BR V50,COMBI PMN-ITV-BR V20Gy,COMBI PMN-ITV-BR V15Gy,COMBI PMN-ITV-BR V10Gy,COMBI PMN-ITV-BR V5Gy,COMBI PMN-ITV-BR avg dose,V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,20Gy radius,15Gy radius,10Gy radius,5Gy radius,Dose max à 2cm,Number sub-PTVs,combined vol sub-PTVs,PTV bounding box vol,D1% BR SOUCHE (Gy),D0.01 TRACHEE (Gy),D0.01 COTES (Gy),D0.01 PLEXUS BRACHIAL (Gy),D0.01 MOELLE (Gy),D0.01 OESOPHAGE (Gy),D0.01 COEUR (Gy),D0.01 PAROI (Gy),Max globale (Gy),Min dose objective sur GTV, Nb de faisceaux,Technique\n')
        stat_file.write(output + '\n')

        
#Second attempt to calculate dose falloff in patients using automation, replacing rings with donuts
def dose_falloff_crane(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=False):

    exam = lib.get_current_examination() 
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
        return patient.PatientName + ": ROI pour cerveau pas trouvé\n"
        
    if "BodyRS" in roi_names:
        body_name = "BodyRS"
    elif "BODY" in roi_names:
        body_name = "BODY"    
    else:
        return patient.PatientName + ": ROI pour body pas trouvé\n"
        
    if "CERVEAU-PTV" in roi_names:
        cerv_ptv_name = "CERVEAU-PTV"
    elif "CERV-PTV" in roi_names:
        cerv_ptv_name = "CERV-PTV"
    elif "CERVEAU-PTVs" in roi_names:
        cerv_ptv_name = "CERVEAU-PTVs"
    else:
        return patient.PatientName + ": CERVEAU-PTV pas trouvé\n"

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
    elif "TR cerebral" in roi_names:
        tronc_name = "TR cerebral" 
    elif "TRONC" in roi_names:
        tronc_name = "TRONC"         
    elif "TRONC*" in roi_names:
        tronc_name = "TRONC*"           
    else:
        return patient.PatientName + ": ROI pour tronc cérébral pas trouvé\n"
                
    if "OEIL DRT*" in roi_names:
        oeild_name = "OEIL DRT*"
    else:
        oeild_name = "OEIL DRT"           

    if "OEIL GCHE*" in roi_names:
        oeilg_name = "OEIL GCHE*"
    else:
        oeilg_name = "OEIL GCHE"               
               
    #Get modification date (before we do anything that will cause it to disappear)
    try:
        mod_date = split(beamset.ModificationInfo.ModificationTime)[0]
    except:
        mod_date = 'Unknown'
               
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
        
        ring_vol = [0,0,0,0,0,0,0]
        predicted_vol = [0,0,0,0,0,0,0]
        
        #Expand and contract PTV to smooth
        roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
        roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
        big_small_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()
        sum_big_small += big_small_vol        
        
        #PTV Header
        ptv_header += "Nom du PTV" + str(i+1) + ",Dose Rx (cGy),Couverture par 100%,Vol PTV(cc),Rayon estimé(cm),Vol smoothé(cc),Vol PTV smoothé dans cerveau(cc),"
        ptv_header += "Donut100 vol(cc),Donut100dsCERV vol(cc),Donut90 vol(cc),Donut90dsCERV vol(cc),Donut80 vol(cc),Donut80dsCERV vol(cc),Donut70 vol(cc),Donut70dsCERV vol(cc),Donut60 vol(cc),Donut60dsCERV vol(cc),Donut50 vol(cc),Donut50dsCERV vol(cc),Donut40 vol(cc),Donut40dsCERV vol(cc),Fraction PTV ds tronc,"        
        
        if ptv_names[i] == "":
            ptv_output += "Aucun PTV" + str(i+1) + ","
            ptv_output += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," #repeat a whole bunch for each empty field
            continue
            
        ptv_vol[i] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume()
        ptv_rad[i] = math.pow(3*ptv_vol[i]/(4*math.pi),1.0/3)
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])
       
        #REVISION 1:
        #Expand base margin because we need to increase volume for V90 (and a little for V80)
        #Reduce constants for V60/50/40 because they are too big
        #Calculate radii of the isodoses
        marge_lat = 0.07 #0.2mm bigger for R2
        marge_sup_inf = 0.02 #0.2mm bigger for R2
        
        rad100 = marge_lat
        rad90 = 0.0013*ptv_vol[i] + 0.1314 + marge_lat #0.2mm bigger for R2
        rad80 = 0.0029*ptv_vol[i] + 0.2386 + marge_lat
        rad70 = 0.0048*ptv_vol[i] + 0.4109 + marge_lat
        rad60 = 0.0078*ptv_vol[i] + 0.6000 + marge_lat #0.5mm smaller for R1
        rad50 = 0.0122*ptv_vol[i] + 0.8800 + marge_lat #0.5mm smaller for R1, another 0.5mm for R2
        rad40 = 0.0165*ptv_vol[i] + 1.4200 + marge_lat #0.7mm smaller for R1, another 0.7mm for R2, and another 0.7mm for R3
        
        rad100_si = marge_sup_inf
        rad90_si = 0.0000*ptv_vol[i] + 0.0818 + marge_sup_inf
        rad80_si = 0.0014*ptv_vol[i] + 0.1293 + marge_sup_inf
        rad70_si = 0.0028*ptv_vol[i] + 0.1906 + marge_sup_inf
        rad60_si = 0.0048*ptv_vol[i] + 0.2351 + marge_sup_inf     
        rad50_si = 0.0058*ptv_vol[i] + 0.2931 + marge_sup_inf #92% of the old constant
        rad40_si = 0.0084*ptv_vol[i] + 0.3449 + marge_sup_inf #92% of the old constant
        
        
        #Create rings using the smoothed PTV as a starting point
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Yellow", examination=exam, marge_lat=rad100, marge_sup_inf = rad100_si, output_name='stats_r100')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Green",  examination=exam, marge_lat=rad90,  marge_sup_inf = rad90_si, output_name='stats_r90')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Red",    examination=exam, marge_lat=rad80,  marge_sup_inf = rad80_si, output_name='stats_r80')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Pink",   examination=exam, marge_lat=rad70,  marge_sup_inf = rad70_si, output_name='stats_r70')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Blue",   examination=exam, marge_lat=rad60,  marge_sup_inf = rad60_si, output_name='stats_r60')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Tomato", examination=exam, marge_lat=rad50,  marge_sup_inf = rad50_si, output_name='stats_r50')
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Brown",  examination=exam, marge_lat=rad40,  marge_sup_inf = rad40_si, output_name='stats_r40')
        
        #Check volume of each donut (obtained by removing PTV volume from expanded volume)
        ring_vol[0] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r100'].GetRoiVolume() - ptv_vol[i]
        ring_vol[1] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r90'].GetRoiVolume() - ptv_vol[i]
        ring_vol[2] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r80'].GetRoiVolume() - ptv_vol[i]
        ring_vol[3] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r70'].GetRoiVolume() - ptv_vol[i]
        ring_vol[4] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r60'].GetRoiVolume() - ptv_vol[i]
        ring_vol[5] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r50'].GetRoiVolume() - ptv_vol[i]
        ring_vol[6] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r40'].GetRoiVolume() - ptv_vol[i]
        
        #Check volume of each ring that intersects the brain - corresponds to predicted dose in CERVEAU-PTV
        ptv_in_cerv_vol =  roi.get_intersecting_volume('stats_ptv+3cm-2.95cm', cerveau_name, examination=exam)
        predicted_vol[0] = roi.get_intersecting_volume('stats_r100', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[1] = roi.get_intersecting_volume('stats_r90', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[2] = roi.get_intersecting_volume('stats_r80', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[3] = roi.get_intersecting_volume('stats_r70', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[4] = roi.get_intersecting_volume('stats_r60', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[5] = roi.get_intersecting_volume('stats_r50', cerveau_name, examination=exam) - ptv_in_cerv_vol
        predicted_vol[6] = roi.get_intersecting_volume('stats_r40', cerveau_name, examination=exam) - ptv_in_cerv_vol
        
        #Correct volumes for 70/60/50/40 according to formulas that Malik devised
        predicted_vol[3] = predicted_vol[3] - big_small_vol*0.063 - 0.17
        predicted_vol[4] = predicted_vol[4] - big_small_vol*0.011 - 0.9
        predicted_vol[5] = predicted_vol[5] - big_small_vol*0.048 - 1.3
        predicted_vol[6] = predicted_vol[6] + big_small_vol*0.03 - 6.4        
        
        #Check for tronc overlap
        tronc_overlap = patient.PatientModel.CreateRoi(Name="temp stats PTV tronc", Color="Red", Type="Ptv", TissueName=None, RoiMaterial=None)
        tronc_overlap.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[i]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [tronc_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        tronc_overlap.UpdateDerivedGeometry(Examination=exam)
        ptv_tronc_overlap[i] = roi.get_roi_volume(tronc_overlap.Name, exam=exam) / ptv_vol[i]
        tronc_overlap.DeleteRoi()
        
        #Generate output
        ptv_output += ptv_names[i] + ',' + str(rx[i]) + ',' + str(ptv_coverage[0]*100) + ',' + str(ptv_vol[i]) + ',' + str(ptv_rad[i]) + ',' + str(big_small_vol) + ',' + str(ptv_in_cerv_vol) + ','
        for j in range(7):
            ptv_output += str(ring_vol[j]) + ',' + str(predicted_vol[j]) + ','
        ptv_output += str(ptv_tronc_overlap[i]) + ','
        
        #Add optimization objectives if creating a new plan
        if add_new_plan:
         
            #Make a ring based on the estimated radius of the 40% isodose (with an added margin in sup-inf to control which leaf pairs are open), but restricted to the brain and excluding the PTV
            if not roi.roi_exists('KBP OPT CERVEAU'):
                roi.create_expanded_roi('stats_r40', color="Brown",  examination=exam, marge_lat=0,  marge_sup_inf = 0.5, output_name='stats_r40_mod')
                patient.PatientModel.CreateRoi(Name="KBP OPT CERVEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
                patient.PatientModel.RegionsOfInterest['KBP OPT CERVEAU'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["stats_r40_mod", cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                patient.PatientModel.RegionsOfInterest['KBP OPT CERVEAU'].UpdateDerivedGeometry(Examination=exam)       
                patient.PatientModel.RegionsOfInterest['stats_r40_mod'].DeleteRoi()             

            ring_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['KBP OPT CERVEAU'].GetRoiVolume()            
                      
            #Make a ring to control the high dose levels near the PTV
            if not roi.roi_exists('KBP RING PROX'):
                roi.subtract_rois('stats_r70', 'stats_r90', color="Pink", examination=exam, output_name='KBP RING PROX')
            
            #Detailed analysis to predict dose to tronc
            tronc_est = 0 #Dose that we expect the tronc to receive (in cGy)
            ring_list = ['stats_r40','stats_r50','stats_r60','stats_r70','stats_r80','stats_r90','stats_r100']
            for r in ring_list:
                if roi.get_intersecting_volume(tronc_name, r, examination=exam) > 0: #Tronc overlaps with this predicted dose level
                    tronc_est = int(r.split('_r')[1])*rx[0]/100
                else:
                    break
            
            if tronc_est > 800:
                tronc_max = 800
            elif tronc_est > 500 and tronc_est <= 800:
                tronc_max = tronc_est
            else:
                tronc_max = 500
            
            """
            #Add optimization objectives for the PTV
            optim.add_mindose_objective(ptv_names[0], rx[0], weight=100.0, plan=plan, plan_opt=0)
            #optim.add_maxdose_objective(ptv_names[0], rx[0]*1.5, weight=1.0, plan=plan, plan_opt=0)
            
            #Add optimization objectives based on predicted dose values in the brain-PTV
            optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.8, 80*predicted_vol[2]/ring_vol, weight=10, plan=plan, plan_opt=0) #Ask for 80% of predicted volume to force optimizer to work a bit
            optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.7, 80*predicted_vol[3]/ring_vol, weight=10, plan=plan, plan_opt=0)
            optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.6, 80*predicted_vol[4]/ring_vol, weight=5, plan=plan, plan_opt=0)
            optim.add_maxdvh_objective('KBP OPT CERVEAU', rx[0]*0.5, 80*predicted_vol[5]/ring_vol, weight=1, plan=plan, plan_opt=0)
            optim.add_maxdose_objective('KBP RING PROX', rx[0]*0.8, weight=25, plan=plan, plan_opt=0)
            
            #And a dose falloff to control the lower doses far from the PTV for good measure
            optim.add_dosefalloff_objective('BodyRS', rx[0]*1.02, rx[0]*0.25, rad50, weight=1.0, plan=plan, plan_opt=0)
            
            #Max dose on the tronc based on our estimation
            optim.add_maxdose_objective(tronc_name, tronc_max, weight=1.0, plan=plan, plan_opt=0)
            """
            
            #Clinical goals!
            eval.add_clinical_goal(ptv_names[0], rx[0], 'AtLeast', 'VolumeAtDose', 99, plan = plan)
            eval.add_clinical_goal(ptv_names[0], rx[0]*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)
            
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.9, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[1], plan=plan)
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.8, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[2], plan=plan)
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.7, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[3], plan=plan)
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.6, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[4], plan=plan)
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.5, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[5], plan=plan)
            eval.add_clinical_goal(cerv_ptv_name, rx[0]*0.4, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[6], plan=plan)
            
            eval.add_clinical_goal(tronc_name, tronc_max, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)
        
        
        #Delete temporary ROIs
        delete_list = ['stats_r100','stats_r90','stats_r80','stats_r70','stats_r60','stats_r50','stats_r40','stats_ptv+3cm','stats_ptv+3cm-2.95cm']
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
    try:
        for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
            if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
                gtv_objective = 'Oui'
                break
    except:
        pass
            
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
    dose_header += "Min dose objective sur GTV,Nb de fractions,Nb de faisceaux,Nb de segments,Technique,Volume du PTV combiné smoothé (cc),Date de modification"
    
    output = "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,dose_in_brain[7]*brain_minus_ptv_vol,dose_in_brain[8]*brain_minus_ptv_vol) #CERV-PTV V100...V40,V12Gy,V10Gy in cc
    output += "%.3f,%.3f," % (dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V12 and V10 in percentage
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8]) #Estimated radii for V100,V90...V40,V12Gy,V10Gy in body
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d,%d,%d,%s," % (nb_fx,num_beams,num_segments,technique)
    output += str(total_smoothed_vol) + ',' + mod_date
    
    
    #Return results
    combined_output = patient_output + ptv_output + output + '\n'
    combined_header = patient_header + ptv_header + dose_header + '\n'
    return combined_output,combined_header,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max
        
   
        
#Third attempt to estimate dose when patient has multiple PTVs (with same dose level for all)
def dose_falloff_crane_multi(num_ptvs, ptv_names, rx, technique,patient,plan,beamset,add_new_plan=False,fix_brain=False):

    exam = lib.get_current_examination() 
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    if "CERVEAU*" in roi_names:
        cerveau_name = "CERVEAU*"
    elif "CERVEAU" in roi_names:
        cerveau_name = "CERVEAU"
    else:
        return patient.PatientName + ": ROI pour cerveau pas trouvé\n"
        
    if "BodyRS" in roi_names:
        body_name = "BodyRS"
    elif "BODY" in roi_names:
        body_name = "BODY"    
    else:
        return patient.PatientName + ": ROI pour body pas trouvé\n"
        
    if "CERVEAU-PTV" in roi_names:
        cerv_ptv_name = "CERVEAU-PTV"
    elif "CERV-PTV" in roi_names:
        cerv_ptv_name = "CERV-PTV"
    elif "CERVEAU-PTVs" in roi_names:
        cerv_ptv_name = "CERVEAU-PTVs"
    else:
        return patient.PatientName + ": CERVEAU-PTV pas trouvé\n"

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
    elif "TR cerebral" in roi_names:
        tronc_name = "TR cerebral" 
    elif "TRONC" in roi_names:
        tronc_name = "TRONC"         
    elif "TRONC*" in roi_names:
        tronc_name = "TRONC*"           
    else:
        return patient.PatientName + ": ROI pour tronc cérébral pas trouvé\n"
                
    if "OEIL DRT*" in roi_names:
        oeild_name = "OEIL DRT*"
    else:
        oeild_name = "OEIL DRT"           

    if "OEIL GCHE*" in roi_names:
        oeilg_name = "OEIL GCHE*"
    else:
        oeilg_name = "OEIL GCHE"               
               
    #Get modification date (before we do anything that will cause it to disappear)
    try:
        mod_date = split(beamset.ModificationInfo.ModificationTime)[0]
    except:
        mod_date = 'Unknown'
    
    if fix_brain:
        patient.PatientModel.CreateRoi(Name="stats_cerv_ptv", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        if num_ptvs == 1:
            patient.PatientModel.RegionsOfInterest['stats_cerv_ptv'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        if num_ptvs == 2:
            patient.PatientModel.RegionsOfInterest['stats_cerv_ptv'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        if num_ptvs == 3:
            patient.PatientModel.RegionsOfInterest['stats_cerv_ptv'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[0],ptv_names[1],ptv_names[2]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['stats_cerv_ptv'].UpdateDerivedGeometry(Examination=exam)   
        cerv_ptv_name = 'stats_cerv_ptv'
    
    #Get prescription information
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    #Get brain volume and radius
    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerveau_name].GetRoiVolume()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[cerv_ptv_name].GetRoiVolume()
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    
    #PTV stats
    ptv_output = ""
    ptv_header = ""
    ptv_vol = [0,0,0]
    ptv_rad = [0,0,0]
    for i,ptv in enumerate(ptv_names): #Create expanded PTVs corresponding to dose levels for each PTV
        #if i>0: #For now we're back to 1 PTV only
        #    continue
        
        #PTV Header
        ptv_header += "Nom du PTV" + str(i+1) + ",Dose Rx (cGy),Couverture par 100%,Vol PTV(cc),Rayon estimé(cm),Vol smoothé(cc),"     
        
        #If there is no PTV, output a bunch of junk and move on to the next one
        if "Aucun PTV" in ptv_names[i] or ptv_names[i] == "":
            ptv_output += "Aucun PTV" + str(i+1) + ",NA,NA,NA,NA,NA,"
            continue
            
        #Expand and contract PTV to smooth
        roi.create_expanded_ptv(ptv_names[i], color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
        roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
        smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()                        
            
        ptv_vol[i] = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_names[i]].GetRoiVolume()
        ptv_rad[i] = math.pow(3*ptv_vol[i]/(4*math.pi),1.0/3)
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_names[i], DoseValues=[rx[i]/nb_fx])

        #Generate output
        ptv_output += ptv_names[i] + ',' + str(rx[i]) + ',' + str(ptv_coverage[0]*100) + ',' + str(ptv_vol[i]) + ',' + str(ptv_rad[i]) + ',' + str(smoothed_vol) + ','  
       
        #Calculate radii of the isodoses
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
        
        #Create expanded volumes using the smoothed PTV as a starting point
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Yellow", examination=exam, marge_lat=rad100, marge_sup_inf = rad100_si, output_name='stats_r100_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Green",  examination=exam, marge_lat=rad90,  marge_sup_inf = rad90_si, output_name='stats_r90_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Red",    examination=exam, marge_lat=rad80,  marge_sup_inf = rad80_si, output_name='stats_r80_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Pink",   examination=exam, marge_lat=rad70,  marge_sup_inf = rad70_si, output_name='stats_r70_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Blue",   examination=exam, marge_lat=rad60,  marge_sup_inf = rad60_si, output_name='stats_r60_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Tomato", examination=exam, marge_lat=rad50,  marge_sup_inf = rad50_si, output_name='stats_r50_'+str(i))
        roi.create_expanded_roi('stats_ptv+3cm-2.95cm', color="Brown",  examination=exam, marge_lat=rad40,  marge_sup_inf = rad40_si, output_name='stats_r40_'+str(i))
        
        #Clean up smoothed volumes
        patient.PatientModel.RegionsOfInterest['stats_ptv+3cm'].DeleteRoi()
        #patient.PatientModel.RegionsOfInterest['stats_ptv+3cm-2.95cm'].DeleteRoi()
        patient.PatientModel.RegionsOfInterest['stats_ptv+3cm-2.95cm'].Name = 'ptv_smooth_' + str(i)
       

    #Sum the smoothed volumes for the different PTVs
    if num_ptvs == 1:
        patient.PatientModel.CreateRoi(Name="stats_sum_ptvs_smooth", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].UpdateDerivedGeometry(Examination=exam)        
    elif num_ptvs == 2:
        patient.PatientModel.CreateRoi(Name="stats_sum_ptvs_smooth", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].UpdateDerivedGeometry(Examination=exam)
    elif num_ptvs == 3:
        patient.PatientModel.CreateRoi(Name="stats_sum_ptvs_smooth", Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['ptv_smooth_1','ptv_smooth_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        patient.PatientModel.RegionsOfInterest['stats_sum_ptvs_smooth'].UpdateDerivedGeometry(Examination=exam)    
    
    #Create total smoothed volume
    smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_sum_ptvs_smooth'].GetRoiVolume()    
    ptv_in_cerv_vol =  roi.get_intersecting_volume('stats_sum_ptvs_smooth', cerveau_name, examination=exam)    
    
    #Combine the expanded volumes (except if there's only one PTV, in which case we just rename the existing ones)
    if num_ptvs == 1:
        patient.PatientModel.RegionsOfInterest['stats_r100_0'].Name = 'stats_r100'
        patient.PatientModel.RegionsOfInterest['stats_r90_0'].Name = 'stats_r90'
        patient.PatientModel.RegionsOfInterest['stats_r80_0'].Name = 'stats_r80'
        patient.PatientModel.RegionsOfInterest['stats_r70_0'].Name = 'stats_r70'
        patient.PatientModel.RegionsOfInterest['stats_r60_0'].Name = 'stats_r60'
        patient.PatientModel.RegionsOfInterest['stats_r50_0'].Name = 'stats_r50'
        patient.PatientModel.RegionsOfInterest['stats_r40_0'].Name = 'stats_r40'
    else:
        patient.PatientModel.CreateRoi(Name="stats_r100", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r90", Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r80", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r70", Color="Blue", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r60", Color="Tomato", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r50", Color="Brown", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.CreateRoi(Name="stats_r40", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)
        
        if num_ptvs == 2:
            patient.PatientModel.RegionsOfInterest['stats_r100'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r100_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r100_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r90'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r90_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r90_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r80'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r80_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r80_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r70'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r70_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r70_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r60'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r60_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r60_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r50'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r50_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r50_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r40'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r40_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r40_1'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        elif num_ptvs == 3:
            patient.PatientModel.RegionsOfInterest['stats_r100'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r100_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r100_1','stats_r100_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r90'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r90_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r90_1','stats_r90_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r80'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r80_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r80_1','stats_r80_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r70'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r70_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r70_1','stats_r70_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r60'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r60_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r60_1','stats_r60_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r50'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r50_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r50_1','stats_r50_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['stats_r40'].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ['stats_r40_0'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_r40_1','stats_r40_2'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                
        patient.PatientModel.RegionsOfInterest['stats_r100'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r90'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r80'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r70'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r60'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r50'].UpdateDerivedGeometry(Examination=exam)
        patient.PatientModel.RegionsOfInterest['stats_r40'].UpdateDerivedGeometry(Examination=exam)
            
    #Predict V100 in body (this value is needed for calculating conformity index of predicted plan in a different script)
    predicted_100_body = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_r100'].GetRoiVolume()
        
    #Check to see what part of volume is in brain-(PTVs in brain): this corresponds to predicted DVH (hopefully)
    predicted_vol = [0,0,0,0,0,0,0]
    predicted_vol[0] = roi.get_intersecting_volume('stats_r100', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[1] = roi.get_intersecting_volume('stats_r90', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[2] = roi.get_intersecting_volume('stats_r80', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[3] = roi.get_intersecting_volume('stats_r70', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[4] = roi.get_intersecting_volume('stats_r60', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[5] = roi.get_intersecting_volume('stats_r50', cerveau_name, examination=exam) - ptv_in_cerv_vol
    predicted_vol[6] = roi.get_intersecting_volume('stats_r40', cerveau_name, examination=exam) - ptv_in_cerv_vol
    
    #Correct volumes for 70/60/50/40 according to formulas that Malik devised, using average volume of PTVs
    predicted_vol[3] = predicted_vol[3] - (smoothed_vol/num_ptvs)*0.063 - 0.17
    predicted_vol[4] = predicted_vol[4] - (smoothed_vol/num_ptvs)*0.011 - 0.9
    predicted_vol[5] = predicted_vol[5] - (smoothed_vol/num_ptvs)*0.048 - 1.3
    predicted_vol[6] = predicted_vol[6] + (smoothed_vol/num_ptvs)*0.03 - 6.4        


    #Add optimization objectives if creating a new plan
    if add_new_plan:
     
        #Make a ring based on the estimated radius of the 40% isodose (with an added margin in sup-inf to control which leaf pairs are open), but restricted to the brain and excluding the PTV
        if not roi.roi_exists('KBP OPT CERVEAU'):
            roi.create_expanded_roi('stats_r40', color="Brown",  examination=exam, marge_lat=0,  marge_sup_inf = 0.5, output_name='stats_r40_mod')
            patient.PatientModel.CreateRoi(Name="KBP OPT CERVEAU", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
            patient.PatientModel.RegionsOfInterest['KBP OPT CERVEAU'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["stats_r40_mod", cerveau_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['stats_sum_ptvs_smooth'], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            patient.PatientModel.RegionsOfInterest['KBP OPT CERVEAU'].UpdateDerivedGeometry(Examination=exam)       
            patient.PatientModel.RegionsOfInterest['stats_r40_mod'].DeleteRoi()                     
                  
        #Make a ring to control the high dose levels near the PTV
        #if not roi.roi_exists('KBP RING PROX'):
        #    roi.subtract_rois('stats_r70', 'stats_r90', color="Pink", examination=exam, output_name='KBP RING PROX')

    
    #Detailed analysis to predict dose to tronc
    tronc_est = 0 #Dose that we expect the tronc to receive (in cGy)
    ring_list = ['stats_r40','stats_r50','stats_r60','stats_r70','stats_r80','stats_r90','stats_r100']
    for r in ring_list:
        if roi.get_intersecting_volume(tronc_name, r, examination=exam) > 0: #Tronc overlaps with this predicted dose level
            tronc_est = int(r.split('_r')[1])*rx[0]/100
        else:
            break
    
    if tronc_est > 800:
        tronc_max = 800
    elif tronc_est > 500 and tronc_est <= 800:
        tronc_max = tronc_est
    else:
        tronc_max = 500
        

    
    #Clinical goals!
    
    eval.add_clinical_goal(ptv_names[0], rx[0], 'AtLeast', 'VolumeAtDose', 99, plan = plan)
    eval.add_clinical_goal(ptv_names[0], rx[0]*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)
    
    if num_ptvs > 1:
        eval.add_clinical_goal(ptv_names[1], rx[1], 'AtLeast', 'VolumeAtDose', 99, plan = plan)
        eval.add_clinical_goal(ptv_names[1], rx[1]*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)          
    if num_ptvs > 2:
        eval.add_clinical_goal(ptv_names[2], rx[2], 'AtLeast', 'VolumeAtDose', 99, plan = plan)
        eval.add_clinical_goal(ptv_names[2], rx[2]*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)            
    
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.9, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[1], plan=plan)
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.8, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[2], plan=plan)
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.7, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[3], plan=plan)
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.6, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[4], plan=plan)
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.5, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[5], plan=plan)
    eval.add_clinical_goal(cerv_ptv_name, max(rx)*0.4, 'AtMost', 'AbsoluteVolumeAtDose', predicted_vol[6], plan=plan)
    
    eval.add_clinical_goal(tronc_name, tronc_max, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)
    
    
        #Delete temporary ROIs
        #delete_list = ['stats_r100','stats_r90','stats_r80','stats_r70','stats_r60','stats_r50','stats_r40','stats_ptv+3cm','stats_ptv+3cm-2.95cm']
        #for contour in delete_list:
        #    patient.PatientModel.RegionsOfInterest[contour].DeleteRoi() 

    
    #Get DVH information (since we're using Fractiondose we have to compensate for nb_fx)
    #Note that dose_in_brain excludes the volume of the PTV, while dose_in_body includes it
    rx_dose = max(rx) #Use highest prescription value for OAR dose calculations
    dose_in_brain = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerv_ptv_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume()
    
    #message.message_window(cerv_ptv_name+'\n'+str(dose_in_brain[0])+' '+str(dose_in_brain[1])+' '+str(dose_in_brain[2])+' '+str(dose_in_brain[3])+' '+str(dose_in_brain[4])+' '+str(dose_in_brain[5])+' '+str(dose_in_brain[6]))
    
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
    try:
        for objective in plan.PlanOptimizations[beamset.Number-1].Objective.ConstituentFunctions:
            if 'GTV' in objective.ForRegionOfInterest.Name.upper() and objective.DoseFunctionParameters.FunctionType == 'MinDose':
                gtv_objective = 'Oui'
                break
    except:
        pass
            
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
    #dose_header += "V100 radius,V90 radius,V80 radius,V70 radius,V60 radius,V50 radius,V40 radius,12Gy radius,10Gy radius,"
    dose_header += "D1% MOELLE (Gy),D0.01 OEIL DRT (Gy),D0.01 OEIL GCHE (Gy),D0.01 TR CEREBRAL (Gy),D0.01 CHIASMA (Gy),D0.01 NERF OPT DRT (Gy),D0.01 NERF OPT GCHE (Gy),Max globale (Gy),"
    dose_header += "Min dose objective sur GTV,Nb de fractions,Nb de faisceaux,Nb de segments,Technique,Volume du PTV combiné smoothé (cc),Date de modification,"
    
    output = "%.3f,%.3f," % (brain_vol,brain_radius) #Volume and (estimated) radius of brain
    
    
    
    #PUT THESE LINES BACK LATER
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain[0]*brain_minus_ptv_vol,dose_in_brain[1]*brain_minus_ptv_vol,dose_in_brain[2]*brain_minus_ptv_vol,dose_in_brain[3]*brain_minus_ptv_vol,dose_in_brain[4]*brain_minus_ptv_vol,dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol,dose_in_brain[7]*brain_minus_ptv_vol,dose_in_brain[8]*brain_minus_ptv_vol) #CERV-PTV V100...V40,V12Gy,V10Gy in cc
    output += "%.3f,%.3f," % (dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V12 and V10 in percentage
    
    
    #ERASE THESE AFTER COLLECTING STATS FOR OLDIES
    #ptv1_in_cerv_vol =  roi.get_intersecting_volume(ptv_names[0], cerveau_name, examination=exam)  #REMOVE THIS LATER
    #dose_in_brain_mod = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=cerveau_name, DoseValues=[rx_dose/nb_fx,rx_dose*0.9/nb_fx,rx_dose*0.8/nb_fx,rx_dose*0.7/nb_fx,rx_dose*0.6/nb_fx,rx_dose*0.5/nb_fx,rx_dose*0.4/nb_fx,1200/nb_fx,1000/nb_fx])
    #output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_in_brain_mod[0]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[1]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[2]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[3]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[4]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[5]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[6]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[7]*brain_vol-ptv1_in_cerv_vol,dose_in_brain_mod[8]*brain_vol-ptv1_in_cerv_vol) #CERV-PTV V100...V40,V12Gy,V10Gy in cc
    #output += "%.3f,%.3f," % (dose_in_brain[7]*100,dose_in_brain[8]*100) #CERV-PTV V12 and V10 in percentage (approx, since CERVEAU-PTV was created in Pinnacle and there is a gap around the PTV)   
    
    #output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4],dose_radius[5],dose_radius[6],dose_radius[7],dose_radius[8]) #Estimated radii for V100,V90...V40,V12Gy,V10Gy in body
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (oar_d1[0],oar_d1[1],oar_d1[2],oar_d1[3],oar_d1[4],oar_d1[5],oar_d1[6]) #D1% for OARs
    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += gtv_objective + ','
    output += "%d,%d,%d,%s," % (nb_fx,num_beams,num_segments,technique)
    output += str(smoothed_vol) + ',' + mod_date + ','

    dose_header += "V100 prédite(cc),V90 prédite(cc),V80 prédite(cc),V70 prédite(cc),V60 prédite(cc),V50 prédite(cc),V40 prédite(cc)"
    output += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6])
    
    #Return results
    combined_output = patient_output + ptv_output + output + '\n'
    combined_header = patient_header + ptv_header + dose_header + '\n'
    return combined_output,combined_header,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body


   
#The script to run if you want to collect statistics from all the patients in the crane_v2 file        
def auto_collect_crane_stats(startpoint=1,endpoint=999,min_vol=3.999):

    pdb = get_current("PatientDB")
    
    input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane_v2.txt'
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\oldies_nouveau_cerveau-ptv.txt'         
    statsfile = open(input_file_path)
    
    for i,l in enumerate(statsfile):
        #Start from the requested point in the file; reject first line of the file if it contains header information
        if i < startpoint or i > endpoint or l.split(',')[0] == 'Name':
            continue
    
        #Locate and open patient
        try:
            fullname = l.split(',')[0]
            displayname = '^' + fullname.split('^')[1] + ' ' + fullname.split('^')[0] + '$'
            patient_id = '^' + l.split(',')[1] + '$'   
            num_ptvs = int(l.split(',')[4])
            vol_ptv1 = float(l.split(',')[8])            
            my_patient = pdb.QueryPatientInfo(Filter={'PatientID':patient_id,'DisplayName':displayname})
            
            if len(my_patient) > 0 and num_ptvs == 1 and vol_ptv1 > min_vol:
                    pdb.LoadPatient(PatientInfo=my_patient[0])
            else:
                #output = 'Patient not found: ' + displayname[1:-1] + ', No. HMR ' + patient_id[1:-1] + '\n'
                #with open(output_file_path, 'a') as output_file:
                #    output_file.write(output)                
                continue

        except:
            output = 'Incorrect formatting for patient ' + l.split(',')[0] + ', check source file\n' 
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue

        
        #Read prescription and ROI information
        try:
            ptv_names = [l.split(',')[5],l.split(',')[24],l.split(',')[43]]
            rx = [int(l.split(',')[6]),int(l.split(',')[25]),int(l.split(',')[44])]
            technique = l.split(',')[-2]
        except:
            output = displayname[1:-1] + ': Unable to determine PTV names or prescription values\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)
            continue


            
        #Locate plan and beamset
        try:
            patient = lib.get_current_patient()
            plan = patient.TreatmentPlans[l.split(',')[2]]
            beamset = plan.BeamSets[l.split(',')[3]]
        except:
            output = displayname[1:-1] + ': Unable to locate plan or beamset\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue

        
        #Run the statistics collection script
        output,header,predicted_vol,rad50,brain_minus_ptv_vol,cerv_ptv_name,tronc_name,tronc_max,body_name,predicted_100_body = dose_falloff_crane_multi(num_ptvs,ptv_names,rx,technique,patient,plan,beamset,fix_brain=False)   
        file_exists = os.path.exists(output_file_path)
        with open(output_file_path, 'a') as output_file:
            if not file_exists:
                output_file.write(header) #Only want to write the header if we're starting a new file
            output_file.write(output)

            
       
#The script to run if you want to add a whole bunch of new plans to a whole bunch of patients   
def batch_autoplan_crane(startpoint=1,endpoint=999,min_vol=3.999):

    pdb = get_current("PatientDB")
    
    #input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\golden_patients_crane_1PTV.txt'
    #input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\multi_tumeurs_fix.txt'
    input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\golden_oldies.txt'
    statsfile = open(input_file_path)
    
    for i,l in enumerate(statsfile):
        #Start from the requested point in the file; reject first line of the file if it contains header information
        if i < startpoint or i > endpoint or l.split(',')[0] == 'Name':
            continue
    
        #Locate and open patient
        try:
            fullname = l.split(',')[0]
            displayname = '^' + fullname.split('^')[1] + ' ' + fullname.split('^')[0] + '$'
            patient_id = '^' + l.split(',')[1] + '$'   
            num_ptvs = int(l.split(',')[4])
            #vol_ptv1 = float(l.split(',')[8])            
            my_patient = pdb.QueryPatientInfo(Filter={'PatientID':patient_id,'DisplayName':displayname})
            
            if len(my_patient) > 0:
                pdb.LoadPatient(PatientInfo=my_patient[0])
            else:            
                continue

        except:       
            continue

        
        #Read prescription and ROI information
        #try:
            #ptv_names = [l.split(',')[5],'','',''] #Fix this if you ever want to analyse multiple PTVs
            #technique = l.split(',')[-3]
            #nb_fx = int(l.split(',')[-6])

        
        #Config for multi-tumor patient file
        #ptv_names = [l.split(',')[5],l.split(',')[11],l.split(',')[17]] #For multi-tumor patients        
        #if l.split(',')[18] == 'NA':
        #    rx3 = 0
        #else:
        #    rx3 = int(l.split(',')[18])
        #rx = [int(l.split(',')[6]),int(l.split(',')[12]),rx3]  
        #technique = l.split(',')[-10]
        #nb_fx = int(l.split(',')[-13])            
        
        #Config for golden oldies
        technique = l.split(',')[-10]
        nb_fx = int(l.split(',')[-13])   
        rx = [int(l.split(',')[6]),0,0]        
        ptv_names = [l.split(',')[5],'Aucun PTV','Aucun PTV']        
        
        patient = lib.get_current_patient()
        plan = patient.TreatmentPlans[l.split(',')[2]]
        beamset = plan.BeamSets[l.split(',')[3]]             
        #except:
        #    continue
        
        #Run the autoplanning script
        crane.kbp_test_phase3(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan=plan,clinical_beamset=beamset)
        #crane.kbp_test_multi_v4(num_ptvs,ptv_names,rx,technique,patient,nb_fx,plan,beamset) 

       
#The script to run if you want to add a whole bunch of new plans to the currently opened patient
def single_autoplan_crane(startpoint=1,endpoint=999,min_vol=0):

    pdb = get_current("PatientDB")
    patient = lib.get_current_patient() 
    
    input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane_v2.txt'
    statsfile = open(input_file_path)
    
    for i,l in enumerate(statsfile):   
        #Locate and open patient
        try:
            patient_id = l.split(',')[1]
            num_ptvs = int(l.split(',')[4])
            vol_ptv1 = float(l.split(',')[8])         
            plan = patient.TreatmentPlans[l.split(',')[2]]
            beamset = plan.BeamSets[l.split(',')[3]]            
        except:       
            continue

            
        if patient_id != patient.PatientID:
            continue
        
        #Read prescription and ROI information
        try:
            ptv_names = [l.split(',')[5],l.split(',')[24],l.split(',')[43]]
            rx = [int(l.split(',')[6]),int(l.split(',')[25]),int(l.split(',')[44])]
            technique = l.split(',')[-2]
            nb_fx = int(l.split(',')[-5])
            patient = lib.get_current_patient()
        except:
            continue
        
        #Run the autoplanning script
        #crane.kbp_test_phase3(num_ptvs,ptv_names,rx,technique,patient,nb_fx,clinical_plan=plan,clinical_beamset=beamset)
        crane.kbp_test_multi_v4(num_ptvs,ptv_names,rx,technique,patient,nb_fx,plan,beamset)   
       
       
       
       
       
   
#The script to run if you want to collect statistics from all the patients in the Poumon Master List file        
def auto_collect_lung_stats(startpoint=1,endpoint=999,test_plans=False,print_results=True,show_plan=False):

    pdb = get_current("PatientDB")
        
    input_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\Poumon Master List.txt'
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\Poumon stats v1.txt'         
    statsfile = open(input_file_path)
    
    for i,l in enumerate(statsfile):
        #Start from the requested point in the file; reject first line of the file if it contains header information
        if i < startpoint or i > endpoint or l.split(',')[0] == 'Name':
            continue
    
        #Locate and open patient
        try:
            fullname = l.split(',')[0]
            displayname = '^' + fullname.split('^')[1] + ' ' + fullname.split('^')[0] + '$'
            patient_id = '^' + l.split(',')[1] + '$'             
            my_patient = pdb.QueryPatientInfo(Filter={'PatientID':patient_id,'DisplayName':displayname})
            
            if len(my_patient) > 0:
                    pdb.LoadPatient(PatientInfo=my_patient[0])
            else:           
                continue

        except:
            output = 'Incorrect formatting for patient ' + l.split(',')[0] + ', check source file\n' 
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue
        
        #Read prescription and ROI information
        try:
            ptv_name = l.split(',')[4]
            rx = int(l.split(',')[5])
            #technique = l.split(',')[8]
        except:
            output = displayname[1:-1] + ': Unable to determine PTV name or prescription value\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)
            continue
            
        #Locate plan and beamset
        try:
            patient = lib.get_current_patient()
            plan = patient.TreatmentPlans[l.split(',')[2]]
            beamset = plan.BeamSets[l.split(',')[3]]
            exam = patient.Examinations[l.split(',')[13]]
            iso_name = l.split(',')[12]
        except:
            output = displayname[1:-1] + ': Unable to locate plan or beamset\n'
            with open(output_file_path, 'a') as output_file:
                output_file.write(output)            
            continue
        
        #Run the statistics collection script
        output,header,laterality,body_name,opt_pmns_name,nb_fx = lung_stats(ptv_name,rx,patient,plan,beamset,exam,iso_name)  
        if test_plans:
            test_lung_plans(ptv_name,rx,patient,nb_fx,exam,iso_name,laterality,body_name,opt_pmns_name,plan,beamset,show_plan)
        
        #Print results
        if print_results:
            file_exists = os.path.exists(output_file_path)
            with open(output_file_path, 'a') as output_file:
                if not file_exists:
                    output_file.write(header) #Only want to write the header if we're starting a new file
                output_file.write(output)

         
         
         
        
#First attempt to collect information on lung patients
def lung_stats(ptv_name,rx,patient,plan,beamset,exam,iso_name):

    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
   
    poumon_d_name = "Not found"
    poumon_g_name = "Not found"
    coeur_name = "Not found"
    bronches_name = "Not found"
    trachee_name = "Not found"
    oesophage_name = "Not found"
    moelle_name = "Not found" 
    cotes_name = "Not found"
    body_name = "Not found"
    opt_pmns_name = "Not found"
   
    #Check names for ROIs
    name_list = ['POUMON DRT','POUMON DRT*','POUMON D','POUMON D*']
    for name in name_list:
        if name in roi_names:
            poumon_d_name = name
            break
      
    name_list = ['POUMON GCHE','POUMON GCHE*','POUMON G','POUMON G*']
    for name in name_list:
        if name in roi_names:
            poumon_g_name = name
            break
            
    name_list = ['COEUR','COEUR*']
    for name in name_list:
        if name in roi_names:
            coeur_name = name
            break

    name_list = ['BR SOUCHE','BR SOUCHE*']
    for name in name_list:
        if name in roi_names:
            bronches_name = name
            break            
                        
    name_list = ['TRACHEE','TRACHEE*']
    for name in name_list:
        if name in roi_names:
            trachee_name = name
            break      

    name_list = ['OESOPHAGE','OESOPHAGE*']
    for name in name_list:
        if name in roi_names:
            oesophage_name = name
            break                

    name_list = ['MOELLE','MOELLE*']
    for name in name_list:
        if name in roi_names:
            moelle_name = name
            break    

    name_list = ['COTES','COTES*']
    for name in name_list:
        if name in roi_names:
            cotes_name = name
            break    
            
    name_list = ['BodyRS','BODY']
    for name in name_list:
        if name in roi_names:
            body_name = name
            break                
            
    name_list = ['COMBI PMN-ITV-BR','COMBI PMN-ITV-BR*']
    for name in name_list:
        if name in roi_names:
            opt_pmns_name = name
            break                
    
    #Determine laterality
    if patient.PatientID == '1846570': #Patient with only one lung
        pmn_ipsi_name = poumon_d_name
        laterality = 'DRT'
    else:
        pmn_ipsi_name = roi.find_most_intersecting_roi(ptv_name,[poumon_d_name,poumon_g_name], examination=exam)
        if pmn_ipsi_name == poumon_d_name:
            laterality = 'DRT'
        else:
            laterality = 'GCHE'
          
    #Get prescription information
    nb_fx = beamset.FractionationPattern.NumberOfFractions
    
    #Expand and contract PTV to smooth
    roi.create_expanded_ptv(ptv_name, color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
    roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
    smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()                        
        
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
    ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])

    #PTV Header
    ptv_header = "Nom du PTV,Dose Rx(cGy),Couverture par 100%,Couverture par 95%,Vol PTV(cc),Vol smoothé(cc),"     
    
    #Generate output    
    ptv_output = '%s,%d,%.3f,%.3f,%.3f,%.3f,' % (ptv_name,rx,ptv_coverage[0]*100,ptv_coverage[1]*100,ptv_vol,smoothed_vol)
   
    #Get dose in body
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume()
    dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx])        
    
    #Get dose in COMBI PMN-ITV-BR
    opt_pmns_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[opt_pmns_name].GetRoiVolume()
    dose_in_opt_pmns = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=opt_pmns_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx])    
    
    #Calculate D1% for OARs
    oar_list = [poumon_d_name,poumon_g_name,coeur_name,bronches_name,trachee_name,oesophage_name,moelle_name,cotes_name]
    oar_d1 = [0,0,0,0,0,0,0,0]
    for i,oar in enumerate(oar_list):
        try:
            oar_d1[i] = nb_fx * beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = oar,RelativeVolumes = [0.01])[0] / 100.0 #Returns an array, so we select element 0 and divide by 100 to convert to Gy
        except:
            oar_d1[i] = -999

    #Find D0.03cc in BodyRS
    dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = body_name,RelativeVolumes = [0.03/body_vol])
    dmax[0] = dmax[0] * nb_fx

    #Check number of beams
    num_beams = 0
    num_segments = 0
    for beam in beamset.Beams:
        num_beams +=1
        for segment in beam.Segments:         
            num_segments += 1
    
    
    #Generate output string
    patient_header = "Name,ID,Plan,Beamset,"
    patient_output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + beamset.DicomPlanLabel + ',' #Demographic information
    
    dose_header = "Body vol,Body V100 cc,Body V90 cc,Body V80 cc,Body V70 cc,Body V60 cc,Body V50 cc,Body V40 cc,Body V30 cc,Body V20 cc,Body V10 cc,"
    dose_header += "COMBI PMN-ITV-BR vol,PMN-ITV-BR V100(cc),PMN-ITV-BR V90(cc),PMN-ITV-BR V80(cc),PMN-ITV-BR V70(cc),PMN-ITV-BR V60(cc),PMN-ITV-BR V50(cc),PMN-ITV-BR V40(cc),PMN-ITV-BR V30(cc),PMN-ITV-BR V20(cc),PMN-ITV-BR V10(cc),"
    dose_header += "D1% Poumon drt (Gy),D0.01 Poumon gche (Gy),D0.01 Coeur (Gy),D0.01 Bronches (Gy),D0.01 Trachée (Gy),D0.01 Oesophage (Gy),D0.01 Moelle (Gy),D0.01 Côtes (Gy),Max globale (Gy),"
    dose_header += "Nb de fractions,Nb de faisceaux,Nb de segments"

    output = "%.3f," % body_vol
    for i,dose in enumerate(dose_in_body):
        output += "%.3f," % (dose_in_body[i]*body_vol)
        
    output += "%.3f," % opt_pmns_vol
    for i,dose in enumerate(dose_in_opt_pmns):
        output += "%.3f," % (dose_in_opt_pmns[i]*opt_pmns_vol)
        
    for dose in oar_d1:
        output += "%.3f," % dose

    output += "%.3f," % (dmax[0] / 100.0) #Global max
    output += "%d,%d,%d" % (nb_fx,num_beams,num_segments)

    patient.PatientModel.RegionsOfInterest['stats_ptv+3cm'].DeleteRoi() 
    patient.PatientModel.RegionsOfInterest['stats_ptv+3cm-2.95cm'].DeleteRoi() 
    
    
    #Return results
    combined_output = patient_output + ptv_output + output + '\n'
    combined_header = patient_header + ptv_header + dose_header + '\n'
    return combined_output,combined_header,laterality,body_name,opt_pmns_name,nb_fx

    
    
        
#Script for adding testing multiple plans on a patient with multiple PTVs - now with more iterations on PTV min doses
def test_lung_plans(ptv_name,rx,patient,nb_fx,exam,iso_name,laterality,body_name,opt_pmns_name,clinical_plan,clinical_beamset,show_plan=False):

    exam = lib.get_current_examination()

    if patient.BodySite == '':
        patient.BodySite = 'Poumon'    

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
        beamset.AddDosePrescriptionToRoi(RoiName=ptv_name, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=rx, RelativePrescriptionLevel=1)
        
        #Add beams
        if laterality == 'DRT':
            pmn_contra_name = 'POUMON GCHE'
        else:
            pmn_contra_name = 'POUMON DRT'
        beams.add_beams_lung_stereo(contralateral_lung=pmn_contra_name, beamset=beamset, examination=exam, ptv_name=ptv_name, two_arcs=False)
        optim.set_optimization_parameters(plan=plan)
        optim.set_vmat_conversion_parameters(max_leaf_travel_per_degree=0.1,max_arc_delivery_time=350, plan=plan)

    

    if show_plan:
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

    
    
    
    #Clinical goals!
    eval.add_clinical_goal(ptv_name, rx, 'AtLeast', 'VolumeAtDose', 95, plan = plan)
    eval.add_clinical_goal(ptv_name, rx*0.95, 'AtLeast', 'VolumeAtDose', 99, plan = plan)
    eval.add_clinical_goal(ptv_name, rx*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = plan)

    eval.add_clinical_goal(opt_pmns_name, 2000, 'AtMost', 'AbsoluteVolumeAtDose', 5, plan=plan)
    eval.add_clinical_goal(opt_pmns_name, 1000, 'AtMost', 'AbsoluteVolumeAtDose', 10, plan=plan)
    eval.add_clinical_goal(opt_pmns_name, 500, 'AtMost', 'AbsoluteVolumeAtDose', 20, plan=plan)

    #Collect ROI info
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()  
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[body_name].GetRoiVolume() 
    opt_pmns_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[opt_pmns_name].GetRoiVolume() 
    result_text = ""

    #Estimate dose falloff range
    falloff_range = 1.0 + (ptv_vol - 10) * 0.0125
    if falloff_range < 1:
        falloff_range = 1
    elif falloff_range > 2:
        falloff_range = 2
    
    #Create COMBI PMN KBP
    roi.create_expanded_roi('r50', color="Yellow", examination=exam, marge_lat=5, marge_sup_inf = 0, output_name='temp KBP1')
    roi.create_expanded_roi('temp KBP1', color="Lightblue", examination=exam, marge_lat=5, marge_sup_inf = 0, output_name='temp KBP2')
    patient.PatientModel.CreateRoi(Name="COMBI PMN KBP", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest['COMBI PMN KBP'].SetAlgebraExpression(ExpressionA={'Operation': "Intersection", 'SourceRoiNames': ["temp KBP2"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [opt_pmns_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest['COMBI PMN KBP'].UpdateDerivedGeometry(Examination=exam)
    combi_pmn_kbp_col = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['COMBI PMN KBP'].GetRoiVolume() 
    
    #First set: Dose falloff only, adjust min dose weight if necessary
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    optim.add_mindose_objective(ptv_name, rx, weight=50, plan=plan, plan_opt=0)
    optim.add_dosefalloff_objective(body_name, rx*1.00, rx*0.25, falloff_range, weight=25, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('r50', (rx/2)-100, weight=5, plan=plan, plan_opt=0) 

    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(8):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        else:
            #Get DVH values for use in the second set
            dose_in_pmn_kbp = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='COMBI PMN KBP', DoseValues=[2000/nb_fx,1000/nb_fx,500/nb_fx])
                  
        #Get initial coverage before scaling        
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])   
        init_ptv_cov = ptv_coverage
            
        #Modify weight of PTV min dose objective
        new_weight = 1
        if ptv_coverage[0] < 0.93:
            new_weight = 2
        elif ptv_coverage[0] > 0.97:
            new_weight = 0.5 
        
        #Scale dose to prescription
        beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=95, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)

        #Get coverage after scaling
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])

        #Evaluate plan
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx])        
        dose_in_opt_pmns = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=opt_pmns_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx,2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])        
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_name,RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        
        #Add results
        if j == 0:
            result_text += 'Falloff only plan initial,'
        else:
            result_text += 'Falloff only après %d révisions,' % j
        
        for i,dose in enumerate(dose_in_body):
            result_text += "%.3f," % (dose_in_body[i]*body_vol)
            
        for i,dose in enumerate(dose_in_opt_pmns):
            result_text += "%.3f," % (dose_in_opt_pmns[i]*opt_pmns_vol)

        result_text += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%d\n" % (max_in_ptv,ptv_coverage[0]*100,ptv_coverage[1]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,(dose_in_body[0]*body_vol)/ptv_vol,rx/100.0)             

        if j<7:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name == ptv_name:    
                    objective.DoseFunctionParameters.Weight = new_weight*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=init_ptv_cov[0]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
        
        
 


 
 
 
    #Second set: Dose falloff and max DVH, adjust min dose weight if necessary
    plan.PlanOptimizations[beamset.Number-1].AutoScaleToPrescription = False
    try:
        for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions:
            objective.DeleteFunction()   
    except:
        pass

    #Optimization objectives
    optim.add_mindose_objective(ptv_name, rx, weight=50, plan=plan, plan_opt=0)
      
    optim.add_dosefalloff_objective(body_name, rx*1.00, rx*0.25, falloff_range, weight=25, plan=plan, plan_opt=0)
    optim.add_maxdose_objective('r50', (rx/2)-100, weight=5, plan=plan, plan_opt=0) 

    optim.add_maxdvh_objective('COMBI PMN KBP', 2000, dose_in_pmn_kbp[0]*80, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('COMBI PMN KBP', 1000, dose_in_pmn_kbp[1]*80, weight=10, plan=plan, plan_opt=0)
    optim.add_maxdvh_objective('COMBI PMN KBP', 500, dose_in_pmn_kbp[2]*80, weight=5, plan=plan, plan_opt=0) 
    
    #Reset and then run initial set of optimizations
    plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
    optim.optimization_90_30(plan=plan,beamset=beamset)
    
    for j in range(8):
        if j > 0:
            plan.PlanOptimizations[beamset.Number-1].RunOptimization()
        
        #Get initial coverage before scaling        
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])   
        init_ptv_cov = ptv_coverage
            
        #Modify weight of PTV min dose objective
        new_weight = 1
        if ptv_coverage[0] < 0.93:
            new_weight = 2
        elif ptv_coverage[0] > 0.97:
            new_weight = 0.5 
        
        #Scale dose to prescription
        beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=95, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)

        #Get coverage after scaling
        ptv_coverage = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])

        #Evaluate plan
        dose_in_body = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx])        
        dose_in_opt_pmns = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=opt_pmns_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx,2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])        
        dmax = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_name,RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        
        #Add results
        if j == 0:
            result_text += 'Falloff avec DVHs plan initial,'
        else:
            result_text += 'Falloff avec DVHs après %d révisions,' % j
        
        for i,dose in enumerate(dose_in_body):
            result_text += "%.3f," % (dose_in_body[i]*body_vol)
            
        for i,dose in enumerate(dose_in_opt_pmns):
            result_text += "%.3f," % (dose_in_opt_pmns[i]*opt_pmns_vol)

        result_text += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%d\n" % (max_in_ptv,ptv_coverage[0]*100,ptv_coverage[1]*100,init_ptv_cov[0]*100,init_ptv_cov[1]*100,(dose_in_body[0]*body_vol)/ptv_vol,rx/100.0)             

        if j<7:
            #Modify weights and reoptimize
            for objective in plan.PlanOptimizations[beamset.Number - 1].Objective.ConstituentFunctions: 
                try:
                    f_type = objective.DoseFunctionParameters.FunctionType  # Dose falloff objectives do not have a FunctionType and must be skipped
                except:
                    continue
                if f_type == "MinDose" and objective.ForRegionOfInterest.Name == ptv_name:    
                    objective.DoseFunctionParameters.Weight = new_weight*objective.DoseFunctionParameters.Weight
            
            #Put the monitor units back to where they were before scaling
            beamset.NormalizeToPrescription(RoiName=ptv_name, DoseValue=rx, DoseVolume=init_ptv_cov[0]*100, PrescriptionType="DoseAtVolume", LockedBeamNames=None, EvaluateAfterScaling=True)    
         
 
 
 
 
 
 
    #Write to file
    output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques'
    output_file_path += '\\Resultats ' + patient.PatientName + '_' + patient.PatientID + '_multiplan_poumon_v1(bon V20-15-10-5).txt'
    with open(output_file_path, 'a') as output_file:
        #Prepare header
        header = "Essai,Body V100 cc,Body V90 cc,Body V80 cc,Body V70 cc,Body V60 cc,Body V50 cc,Body V40 cc,Body V30 cc,Body V20 cc,Body V10 cc,"
        header += "PMN-ITV-BR V100(cc),PMN-ITV-BR V90(cc),PMN-ITV-BR V80(cc),PMN-ITV-BR V70(cc),PMN-ITV-BR V60(cc),PMN-ITV-BR V50(cc),PMN-ITV-BR V40(cc),PMN-ITV-BR V30(cc),PMN-ITV-BR V20(cc),PMN-ITV-BR V10(cc),PMN-ITV-BR V20Gy(cc),PMN-ITV-BR V15Gy(cc),PMN-ITV-BR V10Gy(cc),PMN-ITV-BR V5Gy(cc),"
        header += "Max in PTV(Gy),Couverture par 100%,Couverture par 95%,Couverture 100% avant scaling,Couverture 95% avant scaling,Indice de conformité,Prescription (Gy)\n"
        
        #Add clinical plan information
        ptv_coverage = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx/nb_fx,0.95*rx/nb_fx])  
        dose_in_body = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=body_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx])        
        dose_in_opt_pmns = clinical_beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=opt_pmns_name, DoseValues=[rx/nb_fx,0.9*rx/nb_fx,0.8*rx/nb_fx,0.7*rx/nb_fx,0.6*rx/nb_fx,0.5*rx/nb_fx,0.4*rx/nb_fx,0.3*rx/nb_fx,0.2*rx/nb_fx,0.1*rx/nb_fx,2000/nb_fx,1500/nb_fx,1000/nb_fx,500/nb_fx])        
        dmax = clinical_beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName = ptv_name,RelativeVolumes = [0.03/ptv_vol])
        max_in_ptv = dmax[0] * nb_fx / 100.0
        header += 'Plan clinique,'
        for i,dose in enumerate(dose_in_body):
            header += "%.3f," % (dose_in_body[i]*body_vol)        
        for i,dose in enumerate(dose_in_opt_pmns):
            header += "%.3f," % (dose_in_opt_pmns[i]*opt_pmns_vol)
        header += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%d\n" % (max_in_ptv,ptv_coverage[0]*100,ptv_coverage[1]*100,ptv_coverage[0]*100,ptv_coverage[1]*100,(dose_in_body[0]*body_vol)/ptv_vol,rx/100.0)             
        
        output_file.write(header)      
        output_file.write(result_text)
                
                
