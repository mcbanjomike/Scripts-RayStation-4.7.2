

    # ERASING CLINICAL GOALS APPARENTLY STILL CRASHES RAYSTATION. Great.
    if total_dose < 66:        
        for cg in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
            if cg.ForRegionOfInterest.Name == "RECTUM*" or cg.ForRegionOfInterest.Name == "VESSIE*":
                if cg.PlanningGoal.Type == "VolumeAtDose":
                    cg.DeleteFunction()



    
    #Remove * from the end of ROI names
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        if '*' in name:
            patient.PatientModel.RegionsOfInterest[name].Name = name[:-1]

            
    
    
    #AUTO PROSTATE PLAN SCRIPT
    plan.PlanOptimizations[0].RunOptimization()
    plan.PlanOptimizations[0].RunOptimization()
    #Evaluate overlap of rectum and PTV A1, adjust starting DVH objectives to follow
    if roi.roi_exists("RECTUM ds PTV A1"):
        vol_dans_PTV = roi.get_roi_volume("RECTUM ds PTV A1", exam=patient.Examinations["CT 1"])
        vol_total = roi.get_roi_volume("RECTUM*", exam=patient.Examinations["CT 1"])
        overlap = 100*vol_dans_PTV/vol_total
        for objective in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
            if objective.ForRegionOfInterest.Name == "RECTUM*":
                if objective.DoseFunctionParameters.DoseLevel == 7500:
                    objective.DoseFunctionParameters.PercentVolume = int(overlap)
                elif objective.DoseFunctionParameters.DoseLevel == 7000:
                    objective.DoseFunctionParameters.PercentVolume = int(overlap + 5)   
  
    #Scale plan dose to prescription, but only if dose is lower than prescribed (do not scale down to avoid MU/segment conflicts)
    nb_fx = float(beamset.FractionationPattern.NumberOfFractions)
    if beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName="PTV A1*", DoseValues=[7600/nb_fx]) < 0.995:
        plan.PlanOptimizations[0].AutoScaleToPrescription = True
        increase_weight = True #Weight on min dose objective was inadequate, coverage was not obtained
    else:
        increase_weight = False
    
    #Get DVH values for chosen ROI
    roi_name = "RECTUM*"
    Vrect = beamset.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=roi_name, DoseValues=[7500/nb_fx,7000/nb_fx,6500/nb_fx,6000/nb_fx])

    #Adjust opitimization objectives to reflect obtained DVH values
    for objective in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        if objective.ForRegionOfInterest.Name == "RECTUM*":
            if objective.DoseFunctionParameters.DoseLevel == 7500:
                objective.DoseFunctionParameters.PercentVolume = int(Vrect[0]*100 - 2)
            elif objective.DoseFunctionParameters.DoseLevel == 7000:
                objective.DoseFunctionParameters.PercentVolume = int(Vrect[1]*100 - 2)    
            elif objective.DoseFunctionParameters.DoseLevel == 6500:
                objective.DoseFunctionParameters.PercentVolume = int(Vrect[2]*100 - 2)
            elif objective.DoseFunctionParameters.DoseLevel == 6000:
                objective.DoseFunctionParameters.PercentVolume = int(Vrect[3]*100 - 2)  
        #If PTV coverage was inadequate with baseline dosimetry, increase weight of PTV min dose objective
        elif objective.ForRegionOfInterest.Name == "PTV A1*" and objective.DoseFunctionParameters.FunctionType == "MinDose" and increase_weight==True:
            objective.DoseFunctionParameters.Weight *= 2

    #Reset and optimize twice
    plan.PlanOptimizations[0].AutoScaleToPrescription = False
    plan.PlanOptimizations[0].ResetOptimization()
    plan.PlanOptimizations[0].RunOptimization()
    plan.PlanOptimizations[0].RunOptimization()

    
    
    #Write to test file
    file_path = r'\\radonc.hmr\Departements\Physiciens\TPS\RayStation\Scripts.hmr30489'
    with open(file_path + '\\Output_TEST_MA.txt','w') as test_file:
        test_file.write('V75: %.4f\n' % Vrect[0])
        test_file.write('V70: %.4f\n' % Vrect[1])
        test_file.write('V65: %.4f\n' % Vrect[2])
        test_file.write('V60: %.4f\n' % Vrect[3])        

    # Print methods for an object (SUPER USEFUL)
    test_file.write(str(dir(beam_iso_poi[0])))
        
        
    #Excel test
    import clr
    clr.AddReference("Office")
    clr.AddReference("Microsoft.Office.Interop.Excel")
    import Microsoft.Office.Interop.Excel as excel

    #Open Excel application
    app = excel.ApplicationClass(Visible=True)
    #Add a workbook
    workbook = app.Workbooks.Add(excel.XlWBATemplate.xlWBATWorksheet)
    #Access the first worksheet of this workbook
    worksheet = workbook.Worksheets[1]
    #Write to cell A1
    worksheet.Range("A1").Value = 'Hello'
    
    #Save workbook
    filename = r"C:\output\RayStationExcelTest.xlsx"
    app.DisplayAlerts = False
    workbook.SaveAs(filename)


    # WISH LIST
    # Erase clinical goals (or change target ROI)
    # Override ROI material
    # Create ROI from dose level (95% isodose line)
    # Create summed dose for evaluation - it can be done! But it might not be worth the effort, since time saved would be minimal.
