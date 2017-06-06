# -*- coding: utf-8 -*-

import sys
import os.path
import setpath
import hmrlib.lib as lib
import hmrlib.eval as eval
import hmrlib.optim as optim
import hmrlib.poi as poi
import hmrlib.roi as roi
import hmrlib.qa as qa
import hmrlib.uis as uis
import beams
import optimization_objectives
import clinical_goals

import logging
from hmrlib.HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

# To test GUI stuff
import clr
import System.Array

import verification
import report
import statistics
import message
import orl

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

def ORL_launcher():

    class ScriptLauncher(Form):
        def __init__(self):
            self.Text = "ORL Script Launcher"

            self.Width = 750
            self.Height = 780

            self.setupPlanningScriptLauncher()
            self.setupOKButtons()
            self.setupMachineSelectPanel()

            self.Controls.Add(self.LauncherPanel)
            self.Controls.Add(self.OKbuttonPanel)
            self.Controls.Add(self.MachineSelectPanel)
            
        def newPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 450
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
            self.PatientLabel.Text = "Patient: " + patient.PatientName.replace('^', ', ')
            self.PatientLabel.Location = Point(25, 25)
            self.PatientLabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.PatientLabel.AutoSize = True
            
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
            
            self.Reminder = Label()
            self.Reminder.Text = ""
            self.Reminder.Location = Point(300, 220)
            self.Reminder.AutoSize = True
            self.Reminder.Font = Font("Arial", 11, FontStyle.Italic)
            self.Reminder.ForeColor = Color.Black
            
            self.PTV1Label = Label()
            self.PTV1Label.Text = "PTV 1 (+haut):"
            self.PTV1Label.Location = Point(25, 60)
            self.PTV1Label.Font = Font("Arial", 10)
            self.PTV1Label.AutoSize = True  
            
            self.PTV1name = TextBox()
            self.PTV1name.Text = " "
            self.PTV1name.Size = Size(60,60)
            self.PTV1name.Location = Point(120,60)
            
            self.dose1Label = Label()
            self.dose1Label.Text = "dose:"
            self.dose1Label.Location = Point(200, 60)
            self.dose1Label.Font = Font("Arial", 10)
            self.dose1Label.AutoSize = True  
            
            self.PTV1dose = TextBox()
            self.PTV1dose.Text = " "
            self.PTV1dose.Size = Size(40,30)
            self.PTV1dose.Location = Point(260,60)
            
            self.fractionLabel = Label()
            self.fractionLabel.Text = "nbr fraction:"
            self.fractionLabel.Location = Point(320, 60)
            self.fractionLabel.Font = Font("Arial", 10)
            self.fractionLabel.AutoSize = True  
            
            self.fraction = TextBox()
            self.fraction.Text = " "
            self.fraction.Size = Size(40,30)
            self.fraction.Location = Point(430,60)
            
            self.PTV2Label = Label()
            self.PTV2Label.Text = "PTV 2:"
            self.PTV2Label.Location = Point(25, 90)
            self.PTV2Label.Font = Font("Arial", 10)
            self.PTV2Label.AutoSize = True  
            
            self.PTV2name = TextBox()
            self.PTV2name.Text = " "
            self.PTV2name.Size = Size(60,60)
            self.PTV2name.Location = Point(120,90)
            
            self.dose2Label = Label()
            self.dose2Label.Text = "dose:"
            self.dose2Label.Location = Point(200, 90)
            self.dose2Label.Font = Font("Arial", 10)
            self.dose2Label.AutoSize = True  
            
            self.PTV2dose = TextBox()
            self.PTV2dose.Text = " "
            self.PTV2dose.Size = Size(40,30)
            self.PTV2dose.Location = Point(260,90)
            
            self.champLabel = Label()
            self.champLabel.Text = "nbr champs/arcs:"
            self.champLabel.Location = Point(320, 90)
            self.champLabel.Font = Font("Arial", 10)
            self.champLabel.AutoSize = True  
            
            self.champ = TextBox()
            self.champ.Text = " "
            self.champ.Size = Size(40,30)
            self.champ.Location = Point(430,90)
            
            self.PTV3Label = Label()
            self.PTV3Label.Text = "PTV 3:"
            self.PTV3Label.Location = Point(25, 120)
            self.PTV3Label.Font = Font("Arial", 10)
            self.PTV3Label.AutoSize = True  
            
            self.PTV3name = TextBox()
            self.PTV3name.Text = " "
            self.PTV3name.Size = Size(60,60)
            self.PTV3name.Location = Point(120,120)
            
            self.dose3Label = Label()
            self.dose3Label.Text = "dose:"
            self.dose3Label.Location = Point(200, 120)
            self.dose3Label.Font = Font("Arial", 10)
            self.dose3Label.AutoSize = True  
            
            self.PTV3dose = TextBox()
            self.PTV3dose.Text = " "
            self.PTV3dose.Size = Size(40,30)
            self.PTV3dose.Location = Point(260,120)
            
            self.avertissement = Label()
            self.avertissement.Text = "(2 arcs maximum):"
            self.avertissement.Location = Point(320, 110)
            self.avertissement.Font = Font("Arial", 8)
            self.avertissement.AutoSize = True  
            
            self.PTV4Label = Label()
            self.PTV4Label.Text = "PTV 4:"
            self.PTV4Label.Location = Point(25, 150)
            self.PTV4Label.Font = Font("Arial", 10)
            self.PTV4Label.AutoSize = True  
            
            self.PTV4name = TextBox()
            self.PTV4name.Text = " "
            self.PTV4name.Size = Size(60,60)
            self.PTV4name.Location = Point(120,150)
            
            self.dose4Label = Label()
            self.dose4Label.Text = "dose:"
            self.dose4Label.Location = Point(200, 150)
            self.dose4Label.Font = Font("Arial", 10)
            self.dose4Label.AutoSize = True  
            
            self.PTV4dose = TextBox()
            self.PTV4dose.Text = " "
            self.PTV4dose.Size = Size(40,30)
            self.PTV4dose.Location = Point(260,150)
            
            self.techniqueLabel = Label()
            self.techniqueLabel.Text = "Technique:"
            self.techniqueLabel.Location = Point(25, 180)
            self.techniqueLabel.Font = Font("Arial", 10)
            self.techniqueLabel.AutoSize = True                
            
            self.techniquecombo = ComboBox()
            self.techniquecombo.Parent = self
            self.techniquecombo.Size = Size(55,40)
            self.techniquecombo.Location = Point(135, 180)
            self.techniquecombo.Items.Add("IMRT")     
            self.techniquecombo.Items.Add("VMAT")                 
            self.techniquecombo.Text = 'IMRT'            
            
            self.SiteLabel = Label()
            self.SiteLabel.Text = "Nom du site:"
            self.SiteLabel.Location = Point(25, 210)
            self.SiteLabel.Font = Font("Arial", 10)
            self.SiteLabel.AutoSize = True               

            self.SiteBox = TextBox()
            self.SiteBox.Text = "A1"
            self.SiteBox.Location = Point(135, 210)
            self.SiteBox.Width = 40                 
    
            self.scanLabel = Label()
            self.scanLabel.Text = "Scan de planif"
            self.scanLabel.Location = Point(25, 240)
            self.scanLabel.Font = Font("Arial", 10)
            self.scanLabel.AutoSize = True               
            
            self.scancombo = ComboBox()
            self.scancombo.Parent = self
            self.scancombo.Size = Size(55,40)
            self.scancombo.Location = Point(135, 240)              
            self.scancombo.Text = 'Choissisez'            

            self.OptionsLabel = Label()
            self.OptionsLabel.Text = "Options:"
            self.OptionsLabel.Location = Point(25, 300)
            self.OptionsLabel.Font = Font("Arial", 10)
            self.OptionsLabel.AutoSize = True            
            
            self.check1 = CheckBox()
            self.check1.Text = "Double optimization initiale + extra?"
            self.check1.Location = Point(40, 330)
            self.check1.Width = 300
            self.check1.Checked = False
            
            self.check3 = CheckBox()
            self.check3.Text = "Inclure structures optiques?"
            self.check3.Location = Point(40, 360)
            self.check3.Width = 300
            self.check3.Checked = False

            self.check2 = CheckBox()
            self.check2.Text = "Adapter dose color table? -non recommandé-"
            self.check2.Location = Point(40, 390)
            self.check2.Width = 300
            self.check2.Checked = False
            
            self.Entete = Label()
            self.Entete.Text = ""
            self.Entete.Location = Point(300, 25)
            self.Entete.AutoSize = True
            self.Entete.Font = Font("Arial", 12, FontStyle.Bold)
            self.Entete.ForeColor = Color.Black
            
            self.LauncherPanel.Controls.Add(self.PatientLabel)
            self.LauncherPanel.Controls.Add(self.Label2)
            self.LauncherPanel.Controls.Add(self.Label3)
            self.LauncherPanel.Controls.Add(self.Label4)
            self.LauncherPanel.Controls.Add(self.Label5)
            self.LauncherPanel.Controls.Add(self.Entete)
            self.LauncherPanel.Controls.Add(self.Reminder)    
            #self.LauncherPanel.Controls.Add(self.RxLabel)
            self.LauncherPanel.Controls.Add(self.PTV1Label)
            self.LauncherPanel.Controls.Add(self.PTV1name)
            self.LauncherPanel.Controls.Add(self.dose1Label)
            self.LauncherPanel.Controls.Add(self.PTV1dose)
            self.LauncherPanel.Controls.Add(self.PTV2Label)
            self.LauncherPanel.Controls.Add(self.PTV2name)
            self.LauncherPanel.Controls.Add(self.dose2Label)
            self.LauncherPanel.Controls.Add(self.PTV2dose)
            self.LauncherPanel.Controls.Add(self.PTV3Label)
            self.LauncherPanel.Controls.Add(self.PTV3name)
            self.LauncherPanel.Controls.Add(self.dose3Label)
            self.LauncherPanel.Controls.Add(self.PTV3dose)
            self.LauncherPanel.Controls.Add(self.PTV4Label)
            self.LauncherPanel.Controls.Add(self.PTV4name)
            self.LauncherPanel.Controls.Add(self.dose4Label)
            self.LauncherPanel.Controls.Add(self.PTV4dose)
            self.LauncherPanel.Controls.Add(self.fractionLabel)
            self.LauncherPanel.Controls.Add(self.fraction)
            #self.LauncherPanel.Controls.Add(self.isodoseLabel)
            self.LauncherPanel.Controls.Add(self.scanLabel)
            self.LauncherPanel.Controls.Add(self.techniqueLabel)
            self.LauncherPanel.Controls.Add(self.champLabel)
            self.LauncherPanel.Controls.Add(self.champ)
            self.LauncherPanel.Controls.Add(self.avertissement)            
            self.LauncherPanel.Controls.Add(self.SiteLabel)
            self.LauncherPanel.Controls.Add(self.SiteBox)      
            self.LauncherPanel.Controls.Add(self.OptionsLabel)            
            self.LauncherPanel.Controls.Add(self.check1)
            self.LauncherPanel.Controls.Add(self.check2)
            self.LauncherPanel.Controls.Add(self.check3)
            #self.LauncherPanel.Controls.Add(self.check3)            


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
        
        
            self.trouvePTV()
                    
        def trouvePTV(self):

            # Erase error messages and clear prescription selection menu
            self.Label2.Text = ""
            self.Label3.Text = ""
            self.Label4.Text = ""
            self.Label5.Text = ""
            #self.Entete.Text = "test DM"
            self.Reminder.Text = ""            
            self.Label2.ForeColor = Color.Black
            self.Label3.ForeColor = Color.Black
            self.Label4.ForeColor = Color.Black
            self.Label5.ForeColor = Color.Black
            #self.Entete.ForeColor = Color.Black
            #self.Reminder.ForeColor = Color.Black    
            #self.check1.Text = "Double optimization initiale + extra?"            
            #self.check1.Checked = False            
            #self.check2.Text = ""
            #self.check2.Checked = False
            #self.check3.Text = ""
            #self.check3.Checked = False
            #self.comboBoxRx.Items.Clear()
            #self.comboBoxRx.Text = "-----"
            #self.techniquecombo.Items.Clear()
            #self.techniquecombo.Items.Add("VMAT")                 
            #self.techniquecombo.Text = 'VMAT'
            PACE = False
            
            roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
            ptv_name_list = []
            presc_dose_list = []
            
            for name in roi_names:
                n = name.replace(' ', '').upper()
                debut = name[0:3]
                if debut == 'PTV':
                    try:
                        presc_dose = float(name[3:])
                    except IndexError:
                        continue
                    except ValueError:
                        continue
                    ptv_name_list.append(name)
                    presc_dose_list.append(presc_dose)
                    
            ptv_name_list.sort(reverse=True)
            presc_dose_list.sort(reverse=True)
            
            if len(ptv_name_list) == 0:
                self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                self.Label2.ForeColor = Color.Red
            else:
                self.PTV1name.Text = ptv_name_list[0]
                self.PTV1dose.Text = '%.2f'%presc_dose_list[0]
                try:
                    self.PTV2name.Text = ptv_name_list[1]
                    self.PTV2dose.Text = '%.2f'%presc_dose_list[1]
                except IndexError:
                    pass
                try:
                    self.PTV3name.Text = ptv_name_list[2]
                    self.PTV3dose.Text = '%.2f'%presc_dose_list[2]
                except IndexError:
                    pass
                try:
                    self.PTV4name.Text = ptv_name_list[3]
                    self.PTV4dose.Text = '%.2f'%presc_dose_list[3]
                except IndexError:
                    pass
            
            
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
                
            #Check treatment techniqueLabel and nbr of field
            
            if self.techniquecombo.Text == 'IMRT':
                treatment_technique = 'SMLC'
                beamset_name = 'ORL IMRT'
            else:
                treatment_technique = 'VMAT'
                beamset_name = 'ORL VMAT'
                
                
                
            #Determine prescription dose (in Gy) and number of fractions
            
            rx_dose = []
            ptv = []
            
            try:
                rx_dose_PTV1 = int(float(self.PTV1dose.Text)*100)
                rx_dose.append(rx_dose_PTV1)
                ptv.append(self.PTV1name.Text)
            except ValueError:
                pass
            try:
                rx_dose_PTV2 = int(float(self.PTV2dose.Text)*100)
                rx_dose.append(rx_dose_PTV2)
                ptv.append(self.PTV2name.Text)
            except ValueError:
                pass
            try:
                rx_dose_PTV3 = int(float(self.PTV3dose.Text)*100)
                rx_dose.append(rx_dose_PTV3)
                ptv.append(self.PTV3name.Text)
            except ValueError:
                pass
            try:
                rx_dose_PTV4 = int(float(self.PTV4dose.Text)*100)
                rx_dose.append(rx_dose_PTV4)
                ptv.append(self.PTV4name.Text)
            except ValueError:
                pass
                
            try:
                nb_fx = int(self.fraction.Text)
            except ValueError:
                self.Status.Text = "Impossible de lire le nombre de fractions"
                self.Status.ForeColor = Color.Red
            
                
            try:
                nb_ch = int(self.champ.Text)
            except ValueError:
                self.Status.Text = "Impossible de lire le nombre de champ"
                self.Status.ForeColor = Color.Red                  
            
            
            
            #Create the plan data dictionary to send to the component scripts                        
            #d = {'plan_name':'A1'}
            d = dict(patient = patient,
                     plan_name = beamset_name,
                     beamset_name = beamset_name,
                     site_name = self.SiteBox.Text,
                     exam = patient.Examinations[self.scancombo.Text],
                     ct = self.scancombo.Text,
                     machine = machine,
                     nb_fx = nb_fx,
                     nb_ch = nb_ch,
                     rx_dose = rx_dose,
                     ptv = ptv,
                     treatment_technique = treatment_technique)
                    
            
            self.Status.ForeColor = Color.Black
            
            if patient.BodySite == '':
                patient.BodySite = 'ORL'
            #POIS assignation, ROIS creation, plan and beamset adding
            self.Status.Text = "En cours: Gestion des POIs"
            orl.orl_pois(plan_data = d)
            
            self.Status.Text = "En cours: Création des ROIs (peut prendre un peu de temps)"
            
            orl.orl_rois(plan_data = d)
            
            self.Status.Text = "En cours: Ajout du plan et beamset"
            orl.orl_add_plan_and_beamset(plan_data = d)
            
            #dose color table adjustment if selected
            if self.check2.Checked:
                self.Status.Text = "En cours: Reglage du Dose Color Table"
                orl.orl_create_isodose_lines(plan_data = d)
            
            #add beams or arcs
            self.Status.Text = "En cours: Ajout des faisceaux"
            orl.orl_add_beams(plan_data = d)
            
            #optimisation parameters and objectives
            self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
            orl.orl_opt_settings(plan_data = d)
            
            self.Status.Text = "En cours: Ajout des objectifs d'optimisation"
            if self.check3.Checked:
                optimization_objectives.add_opt_obj_orl(plan_data=d,yeux=True)
            else:
                optimization_objectives.add_opt_obj_orl(plan_data=d)
            
            self.Status.Text = "En cours: Ajout des clinical goals"
            clinical_goals.cg_orl(plan_data=d)
            
            
            # Double optimization if requested by user    
            if self.check1.Checked:
                self.Status.Text = "En cours: Première optimization"
                patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "En cours: Deuxième optimization"
                patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "En cours: Ajustement des paramètres d'optimisation"
                optim.fit_objectives_orl(plan=patient.TreatmentPlans[d['plan_name']], beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[0])
                patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 29
                self.Status.Text = "En cours: Optimisation post ajustement -30 itérations- "
                patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
            self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
            self.Status.ForeColor = Color.Green   
            
            

        def cancelClicked(self, sender, args):
            self.Close()

        def setupMachineSelectPanel(self):
            self.MachineSelectPanel = self.miniPanel(0, 450)
            
            self.MachineLabel = Label()
            self.MachineLabel.Text = "Appareil de traitement:"
            self.MachineLabel.Location = Point(25, 30)
            self.MachineLabel.Font = Font("Arial", 10)
            self.MachineLabel.AutoSize = True

            self.BeamModButton = RadioButton()
            self.BeamModButton.Text = "BeamMod (salles 11-12)"
            self.BeamModButton.Location = Point(40, 55)
            self.BeamModButton.Checked = False
            self.BeamModButton.AutoSize = True
            
            self.InfinityButton = RadioButton()
            self.InfinityButton.Text = "Infinity (salles 1-2-6)"
            self.InfinityButton.Location = Point(40, 80)
            self.InfinityButton.Checked = True 
            self.InfinityButton.AutoSize = True            

            self.MachineSelectPanel.Controls.Add(self.MachineLabel)
            self.MachineSelectPanel.Controls.Add(self.BeamModButton)
            self.MachineSelectPanel.Controls.Add(self.InfinityButton)            
            
            
        def setupOKButtons(self):
            self.OKbuttonPanel = self.newPanel(0, 600)

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
   
