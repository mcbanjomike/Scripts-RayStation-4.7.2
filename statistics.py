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
   
    rx_dose = beamset.Prescription.PrimaryDosePrescription.DoseValue

    brain_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU'].GetRoiVolume()
    brain_center = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU'].GetCenterOfRoi()
    brain_minus_ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['CERVEAU-PTV'].GetRoiVolume()
    
    ptv_name = 'PTV A1 15Gy'  # Need to make this more flexible
    ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
    ptv_center = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetCenterOfRoi()
    
    brain_radius = math.pow(3*brain_vol/(4*math.pi),1.0/3) #Assume a spherical brain...
    ptv_radius = math.pow(3*ptv_vol/(4*math.pi),1.0/3)
    distance_brain_ptv = math.sqrt((brain_center.x - ptv_center.x)**2 + (brain_center.y - ptv_center.y)**2 + (brain_center.z - ptv_center.z)**2)
    
    dose_in_brain = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='CERVEAU-PTV', DoseValues=[rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5,1200,1000])
    dose_in_body = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='BodyRS', DoseValues=[rx_dose*0.9,rx_dose*0.8,rx_dose*0.7,rx_dose*0.6,rx_dose*0.5])
    body_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['BodyRS'].GetRoiVolume()
    dose_radius = [math.pow(3*i*body_vol/(4*math.pi),1.0/3) for i in dose_in_body] #Estimated radius for each dose level (V90, V80...V50)
    
    output = "Coordonnées du centre du CERVEAU (DICOM): %.2f,%.2f,%.2f" % (brain_center.x,brain_center.y,brain_center.z)
    output += "\nCoordonnées du centre du PTV (DICOM): %.2f,%.2f,%.2f" % (ptv_center.x,ptv_center.y,ptv_center.z)
    output += "\nDistance from brain to PTV: %.2fcm" % distance_brain_ptv
    output += "\nBrain volume: %.2f,    Brain radius: %.2f" % (brain_vol,brain_radius)
    output += "\nPTV volume: %.2f,    PTV radius: %.2f" % (ptv_vol,ptv_radius)
    output += "\nV90: %.2f\nV80: %.2f\nV70: %.2f\nV60: %.2f\nV50: %.2f" % (dose_in_brain[0]*100,dose_in_brain[1]*100,dose_in_brain[2]*100,dose_in_brain[3]*100,dose_in_brain[4]*100)
    output += "\nV10Gy: %.2fcc, V12Gy: %.2fcc" % (dose_in_brain[5]*brain_minus_ptv_vol,dose_in_brain[6]*brain_minus_ptv_vol)
    output += "\nr90: %.2f\nr80: %.2f\nr70: %.2f\nr60: %.2f\nr50: %.2f" % (dose_radius[0],dose_radius[1],dose_radius[2],dose_radius[3],dose_radius[4])
    message.message_window(output)
    
    """
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