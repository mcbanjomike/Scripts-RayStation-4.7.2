# -*- coding: utf-8 -*-

"""
Ce module contient la code pour les GUIs dans RayStation.

Auteur: MA
"""

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

import prostate
import crane
import poumon
import foie
import verification
import report
import statistics
import message
import orl

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

    
def eud_window():

    class EudWindow(Form):
        def __init__(self):
            self.Text = "Calcul des EUDs"

            self.Width = 600
            self.Height = 500

            self.setupHeaderWindow()
            self.setupEudWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.EudWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 340
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupEudWindow(self):
            self.EudWindow = self.Panel(0, 60)
            
            vert_spacer = 30
            offset = 50   
            
            self.toplabel = Label()
            self.toplabel.Text = "EUD Calculé"
            self.toplabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.toplabel.Location = Point(340, 20)
            self.toplabel.AutoSize = True  
                   
            self.ROI1combo = ComboBox()
            self.ROI1combo.Parent = self
            self.ROI1combo.Size = Size(200,40)
            self.ROI1combo.Location = Point(25, offset)
            self.ROI1combo.Text = "Choisissez ROI" 
            
            self.a1 = Label()
            self.a1.Text = "a = "
            self.a1.Location = Point(250, offset)
            self.a1.Font = Font("Arial", 11, FontStyle.Bold)
            self.a1.AutoSize = True              

            self.ROI1_a_value = TextBox()
            self.ROI1_a_value.Text = "50"
            self.ROI1_a_value.Location = Point(280, offset)
            self.ROI1_a_value.Width = 40              
            
            self.ROI1_result = Label()
            self.ROI1_result.Text = "- - - - - -"
            self.ROI1_result.Location = Point(355, offset)
            self.ROI1_result.Font = Font("Arial", 10)
            self.ROI1_result.AutoSize = True                         

            AddObj1Button = Button()
            AddObj1Button.Text = "Ajouter objectif"
            AddObj1Button.Location = Point(440, offset - 2)
            AddObj1Button.Width = 100 
            AddObj1Button.Click += self.AddObj1Clicked          

            self.ROI2combo = ComboBox()
            self.ROI2combo.Parent = self
            self.ROI2combo.Size = Size(200,40)
            self.ROI2combo.Location = Point(25, offset + vert_spacer)
            self.ROI2combo.Text = "Choisissez ROI" 
            
            self.a2 = Label()
            self.a2.Text = "a = "
            self.a2.Location = Point(250, offset + vert_spacer)
            self.a2.Font = Font("Arial", 11, FontStyle.Bold)
            self.a2.AutoSize = True              

            self.ROI2_a_value = TextBox()
            self.ROI2_a_value.Text = "50"
            self.ROI2_a_value.Location = Point(280, offset + vert_spacer)
            self.ROI2_a_value.Width = 40              
            
            self.ROI2_result = Label()
            self.ROI2_result.Text = "- - - - - -"
            self.ROI2_result.Location = Point(355, offset + vert_spacer)
            self.ROI2_result.Font = Font("Arial", 10)
            self.ROI2_result.AutoSize = True                         

            AddObj2Button = Button()
            AddObj2Button.Text = "Ajouter objectif"
            AddObj2Button.Location = Point(440, offset + vert_spacer - 2)
            AddObj2Button.Width = 100 
            AddObj2Button.Click += self.AddObj2Clicked         

            self.ROI3combo = ComboBox()
            self.ROI3combo.Parent = self
            self.ROI3combo.Size = Size(200,40)
            self.ROI3combo.Location = Point(25, offset + 2*vert_spacer)
            self.ROI3combo.Text = "Choisissez ROI" 
            
            self.a3 = Label()
            self.a3.Text = "a = "
            self.a3.Location = Point(250, offset + 2*vert_spacer)
            self.a3.Font = Font("Arial", 11, FontStyle.Bold)
            self.a3.AutoSize = True              

            self.ROI3_a_value = TextBox()
            self.ROI3_a_value.Text = "50"
            self.ROI3_a_value.Location = Point(280, offset + 2*vert_spacer)
            self.ROI3_a_value.Width = 40              
            
            self.ROI3_result = Label()
            self.ROI3_result.Text = "- - - - - -"
            self.ROI3_result.Location = Point(355, offset + 2*vert_spacer)
            self.ROI3_result.Font = Font("Arial", 10)
            self.ROI3_result.AutoSize = True                         

            AddObj3Button = Button()
            AddObj3Button.Text = "Ajouter objectif"
            AddObj3Button.Location = Point(440, offset + 2*vert_spacer - 2)
            AddObj3Button.Width = 100 
            AddObj3Button.Click += self.AddObj3Clicked         

            self.ROI4combo = ComboBox()
            self.ROI4combo.Parent = self
            self.ROI4combo.Size = Size(200,40)
            self.ROI4combo.Location = Point(25, offset + 3*vert_spacer)
            self.ROI4combo.Text = "Choisissez ROI" 
            
            self.a4 = Label()
            self.a4.Text = "a = "
            self.a4.Location = Point(250, offset + 3*vert_spacer)
            self.a4.Font = Font("Arial", 11, FontStyle.Bold)
            self.a4.AutoSize = True              

            self.ROI4_a_value = TextBox()
            self.ROI4_a_value.Text = "50"
            self.ROI4_a_value.Location = Point(280, offset + 3*vert_spacer)
            self.ROI4_a_value.Width = 40              
            
            self.ROI4_result = Label()
            self.ROI4_result.Text = "- - - - - -"
            self.ROI4_result.Location = Point(355, offset + 3*vert_spacer)
            self.ROI4_result.Font = Font("Arial", 10)
            self.ROI4_result.AutoSize = True                         

            AddObj4Button = Button()
            AddObj4Button.Text = "Ajouter objectif"
            AddObj4Button.Location = Point(440, offset + 3*vert_spacer - 2)
            AddObj4Button.Width = 100 
            AddObj4Button.Click += self.AddObj4Clicked                  

            self.shiftlabel = Label()
            self.shiftlabel.Text = "En enlevant"
            self.shiftlabel.Location = Point(415, offset + 4*vert_spacer)
            self.shiftlabel.Font = Font("Arial", 10, FontStyle.Italic)
            self.shiftlabel.AutoSize = True     
            
            self.shift_value = TextBox()
            self.shift_value.Text = "2"
            self.shift_value.Location = Point(492, offset + 4*vert_spacer)
            self.shift_value.Width = 25        

            self.Gylabel = Label()
            self.Gylabel.Text = "Gy"
            self.Gylabel.Location = Point(520, offset + 4*vert_spacer)
            self.Gylabel.Font = Font("Arial", 10, FontStyle.Italic)
            self.Gylabel.AutoSize = True              
            
            self.bottomlabel = Label()
            self.bottomlabel.Text = "La EUD est toujours calculée à partir de la dose totale du plan (Plan Dose)\n\nLes objectifs d'optimisation MaxEUD sont ajoutés dans le beamset actif\n(il faut fermer la fenêtre et redemarrer le script si vous voulez changer de BeamSet)"
            self.bottomlabel.Location = Point(25, 265)
            self.bottomlabel.Font = Font("Arial", 10, FontStyle.Italic)
            self.bottomlabel.AutoSize = True              
            
            #Check to see if plan is approved; if so, disable buttons for adding objectives (which would case a crash)
            try: #If the plan is not approved, then plan.Review doesn't exist and querying it will crash the script
                if plan.Review.ApprovalStatus == "Approved":
                    AddObj1Button.Enabled = False
                    AddObj2Button.Enabled = False
                    AddObj3Button.Enabled = False
                    AddObj4Button.Enabled = False  
                    self.shiftlabel.Location = Point(430, offset + 4*vert_spacer)
                    self.shiftlabel.Text = "Plan est approuvé;\nimpossible d'ajouter\ndes objectifs"       
                    self.shift_value.Text = ""
                    self.Gylabel.Text = ""
            except: #If the plan is not approved, we don't actually need to do anything
                temp_8 = True
            
            
            self.EudWindow.Controls.Add(self.toplabel)
            self.EudWindow.Controls.Add(self.ROI1combo)
            self.EudWindow.Controls.Add(self.a1)
            self.EudWindow.Controls.Add(self.ROI1_a_value)
            self.EudWindow.Controls.Add(self.ROI1_result)
            self.EudWindow.Controls.Add(AddObj1Button)
            self.EudWindow.Controls.Add(self.ROI2combo)
            self.EudWindow.Controls.Add(self.a2)
            self.EudWindow.Controls.Add(self.ROI2_a_value)
            self.EudWindow.Controls.Add(self.ROI2_result)
            self.EudWindow.Controls.Add(AddObj2Button)
            self.EudWindow.Controls.Add(self.ROI3combo)
            self.EudWindow.Controls.Add(self.a3)
            self.EudWindow.Controls.Add(self.ROI3_a_value)
            self.EudWindow.Controls.Add(self.ROI3_result)
            self.EudWindow.Controls.Add(AddObj3Button)            
            self.EudWindow.Controls.Add(self.bottomlabel)
            self.EudWindow.Controls.Add(self.ROI4combo)
            self.EudWindow.Controls.Add(self.a4)
            self.EudWindow.Controls.Add(self.ROI4_a_value)
            self.EudWindow.Controls.Add(self.ROI4_result)
            self.EudWindow.Controls.Add(AddObj4Button)   
            self.EudWindow.Controls.Add(self.shiftlabel)    
            self.EudWindow.Controls.Add(self.shift_value)   
            self.EudWindow.Controls.Add(self.Gylabel)            
            self.EudWindow.Controls.Add(self.bottomlabel)            
                      
            
            
        def AddObj1Clicked(self, sender, args):       
            if self.ROI1_result.Text != "- - - - - -":
                try:
                    shift = float(self.shift_value.Text)*100
                except:
                    shift = 200
                optim.add_maxeud_objective(self.ROI1combo.Text, float(self.ROI1_result.Text[:-3])*100-shift, int(self.ROI1_a_value.Text), 1, plan=plan, plan_opt=beamset.Number-1)
                self.message.Text = "Objective 1 added"
                self.message.ForeColor = Color.Green            
            
        def AddObj2Clicked(self, sender, args):     
            if self.ROI2_result.Text != "- - - - - -":    
                try:
                    shift = float(self.shift_value.Text)*100
                except:
                    shift = 200            
                optim.add_maxeud_objective(self.ROI2combo.Text, float(self.ROI2_result.Text[:-3])*100-shift, int(self.ROI2_a_value.Text), 1, plan=plan, plan_opt=beamset.Number-1)
                self.message.Text = "Objective 2 added"
                self.message.ForeColor = Color.Green        

        def AddObj3Clicked(self, sender, args):       
            if self.ROI3_result.Text != "- - - - - -":
                try:
                    shift = float(self.shift_value.Text)*100
                except:
                    shift = 200
                optim.add_maxeud_objective(self.ROI3combo.Text, float(self.ROI3_result.Text[:-3])*100-shift, int(self.ROI3_a_value.Text), 1, plan=plan, plan_opt=beamset.Number-1)
                self.message.Text = "Objective 3 added"
                self.message.ForeColor = Color.Green        

        def AddObj4Clicked(self, sender, args):    
            if self.ROI4_result.Text != "- - - - - -":        
                try:
                    shift = float(self.shift_value.Text)*100
                except:
                    shift = 200        
                optim.add_maxeud_objective(self.ROI4combo.Text, float(self.ROI4_result.Text[:-3])*100-shift, int(self.ROI4_a_value.Text), 1, plan=plan, plan_opt=beamset.Number-1)
                self.message.Text = "Objective 4 added"
                self.message.ForeColor = Color.Green                    
            
        def cancelClicked(self, sender, args):
            self.Close()          
            
        def okClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            dose = plan.TreatmentCourse.TotalDose
            self.message.Text = "Calcul en cours, veuillez patienter"
            if roi.roi_exists(self.ROI1combo.Text):               
                #self.message.Text = "Calcul en cours (" + self.ROI1combo.Text + ")"
                a = float(self.ROI1_a_value.Text)
                eud1=optim.compute_eud(dose,self.ROI1combo.Text,a)
                string = str(eud1/100.0)
                self.ROI1_result.Text = string[:5] + " Gy"
            if roi.roi_exists(self.ROI2combo.Text):
                #self.message.Text = "Calcul en cours (" + self.ROI2combo.Text + ")"
                a = float(self.ROI2_a_value.Text)
                eud2=optim.compute_eud(dose,self.ROI2combo.Text,a)
                string = str(eud2/100.0)
                self.ROI2_result.Text = string[:5] + " Gy"                
            if roi.roi_exists(self.ROI3combo.Text):
                #self.message.Text = "Calcul en cours (" + self.ROI3combo.Text + ")"
                a = float(self.ROI3_a_value.Text)
                eud3=optim.compute_eud(dose,self.ROI3combo.Text,a)
                string = str(eud3/100.0)
                self.ROI3_result.Text = string[:5] + " Gy"                
            if roi.roi_exists(self.ROI4combo.Text):
                #self.message.Text = "Calcul en cours (" + self.ROI4combo.Text + ")"
                a = float(self.ROI4_a_value.Text)
                eud4=optim.compute_eud(dose,self.ROI4combo.Text,a)
                string = str(eud4/100.0)
                self.ROI4_result.Text = string[:5] + " Gy"                         
        
            self.message.Text = "Calcul terminé"
            self.message.ForeColor = Color.Green
 
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 410)
            
            okButton = Button()
            okButton.Text = "Calculer"
            okButton.Location = Point(25, 10)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(125,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(225, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate ROI selection comboboxes
            self.ROI1combo.Items.Add("Choisissez ROI")
            self.ROI2combo.Items.Add("Choisissez ROI")
            self.ROI3combo.Items.Add("Choisissez ROI")
            self.ROI4combo.Items.Add("Choisissez ROI")            
            for roi in patient.PatientModel.RegionsOfInterest:       
                self.ROI1combo.Items.Add(roi.Name)
                self.ROI2combo.Items.Add(roi.Name)
                self.ROI3combo.Items.Add(roi.Name)
                self.ROI4combo.Items.Add(roi.Name)          
                
                
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        message.message_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        message.message_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        message.message_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = EudWindow()
    Application.Run(form)   
 
 
def crane_3DC_window():

    class MainWindow(Form):
        def __init__(self):
            self.Text = "Outils Crâne 3DC"

            self.Width = 600
            self.Height = 500

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 340
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ')
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 30
            offset = 50   
            
            #Create plan group
            self.toplabel = Label()
            self.toplabel.Text = "Créér un nouveau plan"
            self.toplabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.toplabel.Location = Point(25, 20)
            self.toplabel.AutoSize = True  
                   
            self.PTVcombo = ComboBox()
            self.PTVcombo.Parent = self
            self.PTVcombo.Size = Size(200,40)
            self.PTVcombo.Location = Point(25, offset)
            self.PTVcombo.Text = "Choisissez PTV" 
            self.PTVcombo.TextChanged += self.PTVselectionChanged
            
            self.doselabel = Label()
            self.doselabel.Text = "Dose (Gy)"
            self.doselabel.Location = Point(240, 20)
            self.doselabel.Font = Font("Arial", 9)
            self.doselabel.AutoSize = True              
            
            self.fxlabel = Label()
            self.fxlabel.Text = "Nb de fx"
            self.fxlabel.Location = Point(310, 20)
            self.fxlabel.Font = Font("Arial", 9)
            self.fxlabel.AutoSize = True                 

            self.sitelabel = Label()
            self.sitelabel.Text = "Site"
            self.sitelabel.Location = Point(380, 20)
            self.sitelabel.Font = Font("Arial", 9)
            self.sitelabel.AutoSize = True               
            
            self.dose_value = TextBox()
            self.dose_value.Text = "- - -"
            self.dose_value.Location = Point(240, offset)
            self.dose_value.Width = 40              

            self.fx_value = TextBox()
            self.fx_value.Text = "- - -"
            self.fx_value.Location = Point(310, offset)
            self.fx_value.Width = 40                      
                        
            self.site_value = TextBox()
            self.site_value.Text = "A1"
            self.site_value.Location = Point(380, offset)
            self.site_value.Width = 40                                  
                        
            CreatePlanButton = Button()
            CreatePlanButton.Text = "Créér plan"
            CreatePlanButton.Location = Point(440, offset - 2)
            CreatePlanButton.Width = 120 
            CreatePlanButton.Click += self.CreatePlanButtonClicked     

            self.plan_warning = Label()
            self.plan_warning.Text = "Pré-réquis: PTV15/PTV18/PTV24, CERVEAU, ISO ou REF SCAN"
            self.plan_warning.Location = Point(25, offset + vert_spacer) 
            self.plan_warning.Font = Font("Arial", 9)
            self.plan_warning.AutoSize = True                  

            self.checkbox = CheckBox()
            self.checkbox.Text = "Créér Dose Color Table"
            self.checkbox.Location = Point(25, offset + 1.8*vert_spacer)
            self.checkbox.Width = 300
            self.checkbox.Checked = False           

            self.checkbox2 = CheckBox()
            self.checkbox2.Text = "Optimization angles collimateur (plusieurs PTVs - attention, c'est long!)"
            self.checkbox2.Location = Point(25, offset + 2.5*vert_spacer)
            self.checkbox2.Width = 500
            self.checkbox2.Checked = False      
            
            
            
            #Erase beams group
            self.eraselabel = Label()
            self.eraselabel.Text = "Supprimer faisceaux"
            self.eraselabel.Location = Point(25, offset + 4*vert_spacer)
            self.eraselabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.eraselabel.AutoSize = True        
            
            EraseBeamsButton = Button()
            EraseBeamsButton.Text = "Supprimer faisceaux"
            EraseBeamsButton.Location = Point(440, offset + vert_spacer*5 - 2)
            EraseBeamsButton.Width = 120 
            EraseBeamsButton.Click += self.EraseBeamsButtonClicked              
                        
            self.MUlabel = Label()
            self.MUlabel.Text = "Effacer les faisceaux avec moins que"
            self.MUlabel.Location = Point(25, offset + vert_spacer*5)
            self.MUlabel.Font = Font("Arial", 9)
            self.MUlabel.AutoSize = True                                    
                        
            self.MU_value = TextBox()
            self.MU_value.Text = "25"
            self.MU_value.Location = Point(240, offset + 5*vert_spacer)
            self.MU_value.Width = 30              
            
            self.MUlabel2 = Label()
            self.MUlabel2.Text = "UMs"
            self.MUlabel2.Location = Point(280, offset + vert_spacer*5)
            self.MUlabel2.Font = Font("Arial", 9)
            self.MUlabel2.AutoSize = True                         


            
            #Add beams group
            self.addbeamslabel = Label()
            self.addbeamslabel.Text = "Ajouter faisceaux pour couvrir sous-PTV"
            self.addbeamslabel.Location = Point(25, offset + 7*vert_spacer)
            self.addbeamslabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.addbeamslabel.AutoSize = True                
            
            self.subPTVcombo = ComboBox()
            self.subPTVcombo.Parent = self
            self.subPTVcombo.Size = Size(200,40)
            self.subPTVcombo.Location = Point(25, offset + vert_spacer*8)
            self.subPTVcombo.Text = "Choisissez sous-PTV"              
            
            AddBeamsButton = Button()
            AddBeamsButton.Text = "Ajouter faisceaux"
            AddBeamsButton.Location = Point(440, offset + vert_spacer*8 - 2)
            AddBeamsButton.Width = 120 
            AddBeamsButton.Click += self.AddBeamsButtonClicked     
           
          
            
            self.MainWindow.Controls.Add(self.toplabel)
            self.MainWindow.Controls.Add(self.doselabel)
            self.MainWindow.Controls.Add(self.fxlabel)            
            self.MainWindow.Controls.Add(self.sitelabel)             
            self.MainWindow.Controls.Add(self.PTVcombo)
            self.MainWindow.Controls.Add(self.dose_value)
            self.MainWindow.Controls.Add(self.fx_value)            
            self.MainWindow.Controls.Add(self.site_value)            
            self.MainWindow.Controls.Add(CreatePlanButton)
            self.MainWindow.Controls.Add(self.plan_warning)
            self.MainWindow.Controls.Add(self.checkbox)            
            self.MainWindow.Controls.Add(self.checkbox2) 

            self.MainWindow.Controls.Add(self.eraselabel)
            self.MainWindow.Controls.Add(self.MUlabel)   
            self.MainWindow.Controls.Add(self.MU_value)        
            self.MainWindow.Controls.Add(self.MUlabel2)  
            self.MainWindow.Controls.Add(EraseBeamsButton)
            
            self.MainWindow.Controls.Add(self.addbeamslabel)            
            self.MainWindow.Controls.Add(self.subPTVcombo)        
            self.MainWindow.Controls.Add(AddBeamsButton)            

     
            
            
        def CreatePlanButtonClicked(self, sender, args):       
            if not roi.roi_exists('CERVEAU'):
                self.plan_warning.Text = "ROI CERVEAU pas trouvé, impossible de continuer"                 
                self.plan_warning.ForeColor = Color.Red
                return
                
            if not poi.poi_exists('ISO'):
                if not poi.poi_exists('REF SCAN'):
                    self.plan_warning.Text = "Aucun point trouvé pour l'isocentre, impossible de continuer"                 
                    self.plan_warning.ForeColor = Color.Red   
                    return
            
            if self.checkbox.Checked:
                isodose_creation = True
            else:
                isodose_creation = False
                
            if self.checkbox2.Checked:
                opt_collimator_angles = True
            else:
                opt_collimator_angles = False
            
            presc_dose = self.dose_value.Text*100
            nb_fx = int(self.fx_value.Text)
            self.plan_warning.Text = "Ne touchez pas à RayStation pendant l'execution du script!"
            self.message.Text = "Création du plan en cours"
            crane.plan_crane_3DC(site_name=self.site_value.Text, presc_dose=presc_dose, nb_fx=nb_fx, isodose_creation = isodose_creation, opt_collimator_angles = opt_collimator_angles)
            self.message.Text = "Terminé avec succès!"
            self.message.ForeColor = Color.Green
            self.plan_warning.Text = ""
  
        def EraseBeamsButtonClicked(self, sender, args):     
            try:
                MU_threshold = float(self.MU_value.Text)
            except:
                self.message.Text = "Threshold doit être un nombre"
                self.message.ForeColor = Color.Red
                return
            self.message.Text = "Suppression des faisceaux en cours"
            num_erased = crane.crane_3DC_erase_beams(MU_threshold=MU_threshold)
            if num_erased == 0:
                self.message.Text = "Aucun faisceaux avec moins que " + self.MU_value.Text + " UMs."
                self.message.ForeColor = Color.Black
            if num_erased > 0:
                self.message.Text = "Terminé avec succès! " + str(num_erased) + " faisceau(x) effacé(s)."
                self.message.ForeColor = Color.Green                
            
        def AddBeamsButtonClicked(self, sender, args):     
            subptv_name = self.subPTVcombo.Text
            if subptv_name[:3] != 'PTV':
                self.message.Text = "Le nom du sous-PTV doit commencer par PTV"                 
                self.message.ForeColor = Color.Red
                return
            self.message.Text = "Ajout de faisceaux en cours"   
            crane.crane_3DC_add_beams(subptv_name = subptv_name)    
            self.message.Text = "Terminé avec succès!"
            self.message.ForeColor = Color.Green            
              
        def PTVselectionChanged(self, sender, args):   
            self.plan_warning.Text = ""          
            if self.PTVcombo.Text == "PTV15":
                self.dose_value.Text = "15"
                self.fx_value.Text = "1"
            elif self.PTVcombo.Text == "PTV18":
                self.dose_value.Text = "18"
                self.fx_value.Text = "1"       
            elif self.PTVcombo.Text == "PTV24":
                self.dose_value.Text = "24"
                self.fx_value.Text = "3"                  
            else:
                self.plan_warning.Text = "Le PTV doit s'appeler PTV15, PTV18 ou PTV24"                 
                self.plan_warning.ForeColor = Color.Red
            
            
        def cancelClicked(self, sender, args):
            self.Close()          
 
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 410)
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(25,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(125, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate ROI selection comboboxes
            self.PTVcombo.Items.Add("Choisissez PTV")
            self.subPTVcombo.Items.Add("Choisissez sous-PTV")
         
            for roi in patient.PatientModel.RegionsOfInterest:       
                if roi.Name in ['PTV15','PTV18','PTV24']:
                    self.PTVcombo.Items.Add(roi.Name)
                    self.PTVcombo.SelectedIndex = self.PTVcombo.FindStringExact(roi.Name)
                if roi.Name in ['PTV1','PTV2','PTV3','PTV4']:
                    self.subPTVcombo.Items.Add(roi.Name)
         
                
                
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        message.message_window('Aucun patient sélectionné')
        return                    
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = MainWindow()
    Application.Run(form)   
   
    
def crane_stats_window():

    class CraneStatsWindow(Form):
        def __init__(self):
            self.Text = "Statistiques"

            self.Width = 600
            self.Height = 500

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 340
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 30
            offset = 50   
            
            self.toplabel = Label()
            self.toplabel.Text = "PTV                                      Dose (Gy)"
            self.toplabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.toplabel.Location = Point(100, 20)
            self.toplabel.AutoSize = True  
                   
            self.PTV1combo = ComboBox()
            self.PTV1combo.Parent = self
            self.PTV1combo.Size = Size(200,40)
            self.PTV1combo.Location = Point(25, offset)
            self.PTV1combo.Text = "Choisissez ROI" 
     
            self.dose1_value = TextBox()
            self.dose1_value.Text = ""
            self.dose1_value.Location = Point(280, offset)
            self.dose1_value.Width = 50              

            self.PTV2combo = ComboBox()
            self.PTV2combo.Parent = self
            self.PTV2combo.Size = Size(200,40)
            self.PTV2combo.Location = Point(25, offset + vert_spacer)
            self.PTV2combo.Text = "Choisissez ROI" 

            self.dose2_value = TextBox()
            self.dose2_value.Text = ""
            self.dose2_value.Location = Point(280, offset + vert_spacer)
            self.dose2_value.Width = 50                                

            self.PTV3combo = ComboBox()
            self.PTV3combo.Parent = self
            self.PTV3combo.Size = Size(200,40)
            self.PTV3combo.Location = Point(25, offset + 2*vert_spacer)
            self.PTV3combo.Text = "Choisissez ROI" 
                      
            self.dose3_value = TextBox()
            self.dose3_value.Text = ""
            self.dose3_value.Location = Point(280, offset + 2*vert_spacer)
            self.dose3_value.Width = 50            
                                      
            self.PTV4combo = ComboBox()
            self.PTV4combo.Parent = self
            self.PTV4combo.Size = Size(200,40)
            self.PTV4combo.Location = Point(25, offset + 3*vert_spacer)
            self.PTV4combo.Text = "Choisissez ROI"        

            self.dose4_value = TextBox()
            self.dose4_value.Text = ""
            self.dose4_value.Location = Point(280, offset + 3*vert_spacer)
            self.dose4_value.Width = 50            
         
            
            self.bottomlabel = Label()
            self.bottomlabel.Text = "Technique"
            self.bottomlabel.Location = Point(25, offset + 5*vert_spacer)
            self.bottomlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.bottomlabel.AutoSize = True              
            
            
            self.techcombo = ComboBox()
            self.techcombo.Parent = self
            self.techcombo.Size = Size(100,40)
            self.techcombo.Location = Point(25, offset + 6*vert_spacer)
            self.techcombo.Text = "Technique" 
            
            
            self.MainWindow.Controls.Add(self.toplabel)
            
            self.MainWindow.Controls.Add(self.PTV1combo)
            self.MainWindow.Controls.Add(self.dose1_value)
            self.MainWindow.Controls.Add(self.PTV2combo)
            self.MainWindow.Controls.Add(self.dose2_value)
            self.MainWindow.Controls.Add(self.PTV3combo)
            self.MainWindow.Controls.Add(self.dose3_value)
            self.MainWindow.Controls.Add(self.PTV4combo)
            self.MainWindow.Controls.Add(self.dose4_value)            
         
            self.MainWindow.Controls.Add(self.techcombo)
            self.MainWindow.Controls.Add(self.bottomlabel)            
                                     
            
        def cancelClicked(self, sender, args):
            self.Close()          
            
        def okClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            dose = plan.TreatmentCourse.TotalDose
            self.message.Text = "Calcul en cours, veuillez patienter"
            
            ptv_names = ['','','','']
            rx = [0,0,0,0]            
            error_message = ""
            num_ptvs = 0
            
            if roi.roi_exists(self.PTV1combo.Text):       
                ptv_names[0] = self.PTV1combo.Text
                num_ptvs += 1
                try:
                    rx[0] = int(float(self.dose1_value.Text) * 100)
                except:
                    error_message = "Dose du PTV 1 illisible"

            if roi.roi_exists(self.PTV2combo.Text):       
                ptv_names[1] = self.PTV2combo.Text
                num_ptvs += 1
                try:
                    rx[1] = int(float(self.dose2_value.Text) * 100)
                except:
                    error_message = "Dose du PTV 2 illisible"

            if roi.roi_exists(self.PTV3combo.Text):       
                ptv_names[2] = self.PTV3combo.Text
                num_ptvs += 1
                try:
                    rx[2] = int(float(self.dose3_value.Text) * 100)
                except:
                    error_message = "Dose du PTV 3 illisible"
                    
            if roi.roi_exists(self.PTV4combo.Text):       
                ptv_names[3] = self.PTV4combo.Text
                num_ptvs += 1
                try:
                    rx[3] = int(float(self.dose4_value.Text) * 100)
                except:
                    error_message = "Dose du PTV 4 illisible"                    
                    
            if error_message != "":
                self.message.Text = error_message
                self.message.ForeColor = Color.Red
            else:
                technique = self.techcombo.Text
                if num_ptvs > 0:
                    #statistics.stereo_brain_statistics_v2(num_ptvs, ptv_names, rx, technique)
                    #self.message.Text = "Calcul terminé"
                    self.message.Text = statistics.stereo_brain_statistics_v2(num_ptvs, ptv_names, rx, technique)
                    if self.message.Text == "Calcul terminé":
                        self.message.ForeColor = Color.Green
                    else:
                        self.message.ForeColor = Color.Red  
                else:
                    self.message.Text = "Aucun PTV sélectionné"
                    self.message.ForeColor = Color.Red                
 
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 410)
            
            okButton = Button()
            okButton.Text = "Calculer"
            okButton.Location = Point(25, 10)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(125,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(225, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate ROI selection comboboxes
            self.PTV1combo.Items.Add("Choisissez ROI")
            self.PTV2combo.Items.Add("Choisissez ROI")
            self.PTV3combo.Items.Add("Choisissez ROI")
            self.PTV4combo.Items.Add("Choisissez ROI")            
            for roi in patient.PatientModel.RegionsOfInterest:       
                self.PTV1combo.Items.Add(roi.Name)
                self.PTV2combo.Items.Add(roi.Name)
                self.PTV3combo.Items.Add(roi.Name)
                self.PTV4combo.Items.Add(roi.Name)          

                if "PTV" in roi.Name and roi.Name[-3:] == "Gy*":
                    self.PTV1combo.Text = roi.Name
                    self.dose1_value.Text = str(beamset.Prescription.PrimaryDosePrescription.DoseValue/100.0)
            
            if beamset.DeliveryTechnique == "Arc":
                self.techcombo.Text = 'VMAT'
            else:
                self.techcombo.Items.Add('3DC')
                self.techcombo.Items.Add('IMRT')
                
                num_segments = 0
                num_beams = 0
                for beam in beamset.Beams:
                    num_beams += 1
                    for segment in beam.Segments:         
                        num_segments += 1
                
                if num_segments > num_beams:
                    self.techcombo.Text = 'IMRT'
                else:
                    self.techcombo.Text = '3DC'

                        
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        message.message_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        message.message_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        message.message_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = CraneStatsWindow()
    Application.Run(form)   
 
   
def lung_stats_window():

    class LungStatsWindow(Form):
        def __init__(self):
            self.Text = "Statistiques"

            self.Width = 600
            self.Height = 500

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 340
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 30
            offset = 50   
            
            self.toplabel = Label()
            self.toplabel.Text = "PTV                                      Dose (Gy)"
            self.toplabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.toplabel.Location = Point(100, 20)
            self.toplabel.AutoSize = True  
                   
            self.PTV1combo = ComboBox()
            self.PTV1combo.Parent = self
            self.PTV1combo.Size = Size(200,40)
            self.PTV1combo.Location = Point(25, offset)
            self.PTV1combo.Text = "Choisissez ROI" 
     
            self.dose1_value = TextBox()
            self.dose1_value.Text = ""
            self.dose1_value.Location = Point(280, offset)
            self.dose1_value.Width = 50              

            self.ISOcombo = ComboBox()
            self.ISOcombo.Parent = self
            self.ISOcombo.Size = Size(200,40)
            self.ISOcombo.Location = Point(25, offset + vert_spacer)
            self.ISOcombo.Text = "Choisissez ISO" 

            self.comments = TextBox()
            self.comments.Text = ""
            self.comments.Location = Point(25, offset + 2*vert_spacer)
            self.comments.Width = 300                
            
            self.bottomlabel = Label()
            self.bottomlabel.Text = "Technique"
            self.bottomlabel.Location = Point(25, offset + 5*vert_spacer)
            self.bottomlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.bottomlabel.AutoSize = True              
            
            
            self.techcombo = ComboBox()
            self.techcombo.Parent = self
            self.techcombo.Size = Size(100,40)
            self.techcombo.Location = Point(25, offset + 6*vert_spacer)
            self.techcombo.Text = "Technique" 
            
            
            self.MainWindow.Controls.Add(self.toplabel)
            
            self.MainWindow.Controls.Add(self.PTV1combo)
            self.MainWindow.Controls.Add(self.dose1_value)
            self.MainWindow.Controls.Add(self.ISOcombo)
            self.MainWindow.Controls.Add(self.comments)
      
         
            self.MainWindow.Controls.Add(self.techcombo)
            self.MainWindow.Controls.Add(self.bottomlabel)            
                                     
            
        def cancelClicked(self, sender, args):
            self.Close()          
            
        def okClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            dose = plan.TreatmentCourse.TotalDose
            self.message.Text = "Calcul en cours, veuillez patienter"
                      
            error_message = ""
            
            #Check if PTV exists and dose can be read
            if roi.roi_exists(self.PTV1combo.Text):     
                ptv_name = self.PTV1combo.Text
                try:
                    rx = int(float(self.dose1_value.Text) * 100)
                except:
                    error_message = "Dose du PTV 1 illisible"      
            else:
                error_message = "PTV pas trouvé"
            
            #Collect info on plan
            if error_message != "":
                self.message.Text = error_message
                self.message.ForeColor = Color.Red
            else:
                technique = self.techcombo.Text
                
                self.message.Text = "Counting segments"
                
                num_segments = 0
                num_beams = 0
                for beam in beamset.Beams:
                    num_beams += 1
                    for segment in beam.Segments:         
                        num_segments += 1                
 
                self.message.Text = "Date and nb of fractions"
                try:
                    mod_date = str(patient.ModificationInfo.ModificationTime.Year) + '-' + str(patient.ModificationInfo.ModificationTime.Month) + '-' + str(patient.ModificationInfo.ModificationTime.Day)
                except:
                    mod_date = 'Unknown'
                nb_fx = beamset.FractionationPattern.NumberOfFractions
                
                self.message.Text = "Getting PTV volume"
                ptv_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetRoiVolume()
                self.message.Text = "Smoothing PTV"
                roi.create_expanded_ptv(ptv_name, color="SteelBlue", examination=exam, margeptv=3, output_name='stats_ptv')
                roi.create_expanded_ptv('stats_ptv+3cm', color="SteelBlue", examination=exam, margeptv=2.95, output_name='stats_ptv+3cm',operation='Contract')
                smoothed_vol = patient.PatientModel.StructureSets[exam.Name].RoiGeometries['stats_ptv+3cm-2.95cm'].GetRoiVolume()    
                
                #Print to file
                header = 'Nom du patient,No. HMR,Plan,Beamset,Nom du PTV,Rx(cGy),Vol PTV,Vol PTV smoothé,Technique,Nb de fx,Nb de faisceaux,Nb de segments,Nom isocentre,Scan de planif,Date de modification,Commentaires\n'
                output = '%s,%s,%s,%s,%s,%d,%.3f,%.3f,%s,%d,%d,%d,%s,%s,%s,%s\n' % (patient.PatientName,patient.PatientID,plan.Name,beamset.DicomPlanLabel,ptv_name,rx,ptv_vol,smoothed_vol,technique,nb_fx,num_beams,num_segments,self.ISOcombo.Text,exam.Name,mod_date,self.comments.Text)
                
                output_file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\Poumon Master List.txt'     
                file_exists = os.path.exists(output_file_path)
                with open(output_file_path, 'a') as output_file:
                    if not file_exists:
                        output_file.write(header) #Only want to write the header if we're starting a new file
                    output_file.write(output)
                    
                self.message.Text = 'Finished!'
                self.message.ForeColor = Color.Green
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 410)
            
            okButton = Button()
            okButton.Text = "Calculer"
            okButton.Location = Point(25, 10)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(125,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(225, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate ROI selection comboboxes
            self.PTV1combo.Items.Add("Choisissez ROI")         
            for roi in patient.PatientModel.RegionsOfInterest:       
                self.PTV1combo.Items.Add(roi.Name)
                if "PTV" in roi.Name and roi.Name[-3:] == "Gy*":
                    self.PTV1combo.Text = roi.Name
                    self.dose1_value.Text = str(beamset.Prescription.PrimaryDosePrescription.DoseValue/100.0)
            
            for poi in patient.PatientModel.PointsOfInterest:       
                self.ISOcombo.Items.Add(poi.Name)            
                if poi.Name == "ISO":
                    self.ISOcombo.Text = 'ISO'
            
            if beamset.DeliveryTechnique == "Arc":
                self.techcombo.Text = 'VMAT'
            else:
                self.techcombo.Items.Add('3DC')
                self.techcombo.Items.Add('IMRT')
                
                num_segments = 0
                num_beams = 0
                for beam in beamset.Beams:
                    num_beams += 1
                    for segment in beam.Segments:         
                        num_segments += 1
                
                if num_segments > num_beams:
                    self.techcombo.Text = 'IMRT'
                else:
                    self.techcombo.Text = '3DC'

                        
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        message.message_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        message.message_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        message.message_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = LungStatsWindow()
    Application.Run(form)   
 
 
def tool_window():

    class ToolWindow(Form):
        def __init__(self):
            self.Text = "Outils de planification"

            self.Width = 600
            self.Height = 500

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 340
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 600
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 30
            offset = 20   
            
            #NTCP group
            self.NTCPlabel = Label()
            self.NTCPlabel.Text = "Calculer NTCP"
            self.NTCPlabel.Location = Point(25, offset)
            self.NTCPlabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.NTCPlabel.AutoSize = True              
            
            self.roilabel = Label()
            self.roilabel.Text = "ROI:"
            self.roilabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.roilabel.Location = Point(25, offset + vert_spacer)
            self.roilabel.AutoSize = True  
                   
            self.ROIcombo = ComboBox()
            self.ROIcombo.Parent = self
            self.ROIcombo.Size = Size(150,40)
            self.ROIcombo.Location = Point(65, offset + vert_spacer)
            self.ROIcombo.Text = "Choisissez ROI"                                
                   
            self.diaglabel = Label()
            self.diaglabel.Text = "Diagnostique:"
            self.diaglabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.diaglabel.Location = Point(235, offset + vert_spacer)
            self.diaglabel.AutoSize = True                     
                   
            self.diagcombo = ComboBox()
            self.diagcombo.Parent = self
            self.diagcombo.Size = Size(75,40)
            self.diagcombo.Location = Point(335, offset + vert_spacer)
            self.diagcombo.Text = "Méta" 
            self.diagcombo.Items.Add('Méta')
            self.diagcombo.Items.Add('CHC')
            
            self.NTCPButton = Button()
            self.NTCPButton.Text = "Calculer NTCP"
            self.NTCPButton.Size = Size(100,20)
            self.NTCPButton.Location = Point(450, offset + vert_spacer)
            self.NTCPButton.Click += self.NTCPClicked                 
            
            
            
            #Conformity Index group
            self.CIHIlabel = Label()
            self.CIHIlabel.Text = "Calculer CI/HI"
            self.CIHIlabel.Location = Point(25, offset + vert_spacer * 2.5)
            self.CIHIlabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.CIHIlabel.AutoSize = True              
            
            self.ptvlabel = Label()
            self.ptvlabel.Text = "PTV:"
            self.ptvlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.ptvlabel.Location = Point(25, offset + vert_spacer * 3.5)
            self.ptvlabel.AutoSize = True  
                   
            self.ptvcombo = ComboBox()
            self.ptvcombo.Parent = self
            self.ptvcombo.Size = Size(100,40)
            self.ptvcombo.Location = Point(65, offset + vert_spacer * 3.5)
            self.ptvcombo.Text = "Choisissez PTV"                                
                   
            self.isodoselabel = Label()
            self.isodoselabel.Text = "ROI isodose:"
            self.isodoselabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.isodoselabel.Location = Point(175, offset + vert_spacer * 3.5)
            self.isodoselabel.AutoSize = True                     
                   
            self.isodosecombo = ComboBox()
            self.isodosecombo.Parent = self
            self.isodosecombo.Size = Size(100,40)
            self.isodosecombo.Location = Point(265, offset + vert_spacer * 3.5)
            self.isodosecombo.Text = "Choissisez ROI" 

            self.dosebox = TextBox()
            self.dosebox.Parent = self
            self.dosebox.Size = Size(60,40)
            self.dosebox.Location = Point(380,offset + vert_spacer * 3.5)          
            
            self.CIHIButton = Button()
            self.CIHIButton.Text = "Calculer CI/HI"
            self.CIHIButton.Size = Size(100,20)
            self.CIHIButton.Location = Point(450, offset + vert_spacer * 3.5)
            self.CIHIButton.Click += self.CIHIClicked                 
            
            
            #Rename beams group
            self.renamelabel = Label()
            self.renamelabel.Text = "Renommer les faisceaux"
            self.renamelabel.Location = Point(25, offset + vert_spacer * 5)
            self.renamelabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.renamelabel.AutoSize = True          

            self.renamewarninglabel = Label()
            self.renamewarninglabel.Text = "Seulement pour patients en position dorsal avec couch à zéro"
            self.renamewarninglabel.Location = Point(25, offset + vert_spacer * 5.7)
            self.renamewarninglabel.Font = Font("Arial", 10, FontStyle.Italic)
            self.renamewarninglabel.AutoSize = True                  
            
            self.sitelabel = Label()
            self.sitelabel.Text = "Site:"
            self.sitelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.sitelabel.Location = Point(25, offset + vert_spacer * 6.7)
            self.sitelabel.AutoSize = True   
            
            self.sitebox = TextBox()
            self.sitebox.Parent = self
            self.sitebox.Size = Size(60,40)
            self.sitebox.Location = Point(75,offset + vert_spacer * 6.7)
            self.sitebox.Text = "A1"
            
            self.renameButton = Button()
            self.renameButton.Text = "Renommer les faisceaux"
            self.renameButton.Size = Size(150,20)
            self.renameButton.Location = Point(420,offset + vert_spacer * 6.7)
            self.renameButton.Click += self.renameClicked            
            
            
            self.DICOMButton = Button()
            self.DICOMButton.Text = "Afficher coordonnées DICOM des POIs"
            self.DICOMButton.Size = Size(400,20)
            self.DICOMButton.Location = Point(25,offset + vert_spacer * 8.2)
            self.DICOMButton.Click += self.DICOMClicked               
            
            self.changertechButton = Button()
            self.changertechButton.Text = "Changer technique VMAT<->IMRT"
            self.changertechButton.Size = Size(400,20)
            self.changertechButton.Location = Point(25,offset + vert_spacer * 9.2)
            self.changertechButton.Click += self.changertechClicked                
            
            self.MainWindow.Controls.Add(self.NTCPlabel)
            self.MainWindow.Controls.Add(self.roilabel)
            self.MainWindow.Controls.Add(self.diaglabel)            
            self.MainWindow.Controls.Add(self.ROIcombo)
            self.MainWindow.Controls.Add(self.diagcombo)
            self.MainWindow.Controls.Add(self.NTCPButton)
            
            self.MainWindow.Controls.Add(self.CIHIlabel)
            self.MainWindow.Controls.Add(self.ptvlabel)                      
            self.MainWindow.Controls.Add(self.ptvcombo)
            self.MainWindow.Controls.Add(self.isodoselabel)             
            self.MainWindow.Controls.Add(self.isodosecombo)
            self.MainWindow.Controls.Add(self.dosebox)            
            self.MainWindow.Controls.Add(self.CIHIButton)            
                        
            self.MainWindow.Controls.Add(self.renamelabel)
            self.MainWindow.Controls.Add(self.renamewarninglabel)
            self.MainWindow.Controls.Add(self.sitelabel)
            self.MainWindow.Controls.Add(self.sitebox)
            self.MainWindow.Controls.Add(self.renameButton)
            
            self.MainWindow.Controls.Add(self.DICOMButton)
            self.MainWindow.Controls.Add(self.changertechButton)

            
        def cancelClicked(self, sender, args):
            self.Close()          
            
        def NTCPClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            self.message.Text = "Calcul en cours, veuillez patienter"
                      
            error_message = ""
            
            #Check if PTV exists and dose can be read
            if roi.roi_exists(self.ROIcombo.Text):     
                roi_name = self.ROIcombo.Text
            else:
                error_message = "ROI pas trouvé"
            
            if self.diagcombo.Text == 'CHC':
                CHC = True
            elif self.diagcombo.Text == 'Méta':
                CHC = False
            else:
                error_message = "SVP choisissez CHC ou Méta"
            
            #Collect info on plan
            if error_message != "":
                self.message.Text = error_message
                self.message.ForeColor = Color.Red
                return

            veff,ntcp = foie.calculer_NTCP_foie(rx_dose=None, nb_fx=None, CHC=CHC, roi_name=roi_name)

              
            self.message.Text = 'Calcul terminé. Veff = %.2f, NTCP = %.2f%%' % (veff,ntcp)
            self.message.ForeColor = Color.Green
            

        def renameClicked(self, sender, args):
            
            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"
        
            #Check if the plan has been approved
            try:
                if plan.Review.ApprovalStatus == "Approved":      
                    self.message.Text = "Le plan est locké"
                    self.message.ForeColor = Color.Red
                    return
            except:
                pass

            #Make sure there are beams
            try:
                beam_name = beamset.Beams[0].Name
                beams = True
            except:
                beams = False
                self.message.Text = "Aucun faisceau trouvé"
                self.message.ForeColor = Color.Red
                return
            
            couched_beams = False
            for i,beam in enumerate(beamset.Beams):
                beam.Name = self.sitebox.Text + '.' + str(i+1)
                
                try: #Checks whether beam has a stop angle (for arcs)
                    beam.Description = 'ARC %d-%d' % (beam.GantryAngle, beam.ArcStopGantryAngle)
                except:
                    if beam.GantryAngle == 0:
                        incidence = 'ANT'
                    elif beam.GantryAngle > 0 and beam.GantryAngle < 90:
                        incidence = 'OAG'
                    elif beam.GantryAngle == 90:
                        incidence = 'LAT G'
                    elif beam.GantryAngle > 90 and beam.GantryAngle < 180:
                        incidence = 'OPG'                        
                    elif beam.GantryAngle == 180:
                        incidence = 'POST'
                    elif beam.GantryAngle > 180 and beam.GantryAngle < 270:
                        incidence = 'OPD'                        
                    elif beam.GantryAngle == 270:
                        incidence = 'LAT D'
                    elif beam.GantryAngle > 270:
                        incidence = 'OAD'                        
                    
                    beam.Description = "%s %d" % (incidence,beam.GantryAngle)
                    
                    if beam.CouchAngle != 0:
                        couched_beams = True

            if couched_beams:
                self.message.Text = "Terminé - Il faut entrer les noms manuellement\nsi couch pas égal à 0"
            else:
                self.message.Text = "Terminé"
            self.message.ForeColor = Color.Green
  

        def CIHIClicked(self, sender, args):                
                     
            self.message.ForeColor = Color.Black
            self.message.Text = "Calcul en cours, veuillez patienter"                       
                     
            if roi.roi_exists(self.ptvcombo.Text) and roi.roi_exists(self.isodosecombo.Text):         
                ptv_name = self.ptvcombo.Text
                isodose_name = self.isodosecombo.Text
            else:
                self.message.Text = "PTV et/ou ROI isodose pas trouvé"
                self.message.ForeColor = Color.Red
                return              

            try:
                rx_dose = float(self.dosebox.Text)
            except:
                self.message.Text = "Dose illisible"
                self.message.ForeColor = Color.Red
                return
        
            cirtog,hi,cipaddick = eval.calculate_cihi(ptv_name,isodose_name,rx_dose)
            self.message.Text = "CIRTOG: %.2f, HI: %.2f, CIPADDICK: %.2f" % (cirtog,hi,cipaddick)
            self.message.ForeColor = Color.Green
            

        def DICOMClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            self.message.Text = poi.show_all_poi_coordinates()    
            
        def changertechClicked(self, sender, args):     

            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"                
            optim.essai_autre_technique()
            self.message.Text = "Terminé!"
            self.message.ForeColor = Color.Green
  
        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 410)                  
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(25,0)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(125, 2)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate ROI selection comboboxes
            self.ROIcombo.Items.Add("Choisissez ROI")         
            for roi in patient.PatientModel.RegionsOfInterest:       
                self.ROIcombo.Items.Add(roi.Name)
                if roi.Name == 'FOIE EXPI-GTV':
                    self.ROIcombo.Text = roi.Name
                if 'PTV' in roi.Name or 'ptv' in roi.Name:
                    self.ptvcombo.Items.Add(roi.Name)
                if 'ISO' in roi.Name or 'iso' in roi.Name:
                    self.isodosecombo.Items.Add(roi.Name)
                    
            try:
                self.dosebox.Text = str((beamset.Prescription.PrimaryDosePrescription.DoseValue)/100.0)
            except:
                self.dosebox.Text = 'Dose (Gy)'

                        
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        message.message_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        message.message_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        message.message_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = ToolWindow()
    Application.Run(form)   
   
    
