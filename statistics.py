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
def dose_falloff_v1(num_ptvs, ptv_names, rx, technique):
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
        
        roi.subtract_rois('stats_r100','stats_r90',color='White',examination=exam,output_name='ring90')
        roi.subtract_rois('stats_r90','stats_r80',color='White',examination=exam,output_name='ring80')
        roi.subtract_rois('stats_r80','stats_r70',color='White',examination=exam,output_name='ring70')
        roi.subtract_rois('stats_r70','stats_r60',color='White',examination=exam,output_name='ring60')
        roi.subtract_rois('stats_r60','stats_r50',color='White',examination=exam,output_name='ring50')
        roi.subtract_rois('stats_r50','stats_r40',color='White',examination=exam,output_name='ring40')

        
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

