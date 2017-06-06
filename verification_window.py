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
import verification
import report
import statistics
import message

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

   
def verification_initiale():

    class Verif1Window(Form):
        def __init__(self):
            self.Text = "Vérification 1"

            self.Width = 450
            self.Height = 1050

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
            #Create the dictionary that will be used to pass the verification info to the print function
            self.d = dict(patient_name = patient.PatientName.replace('^', ', '),
                     plan_name = plan.Name,
                     beamset_name = beamset.DicomPlanLabel,
                     patient_number = patient.PatientID,
                     #planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
                     planned_by_name = plan.PlannedBy,
                     verified_by_name = lib.get_user_name(os.getenv('USERNAME')),
                     ext_text = "Script pas roulé",
                     iso_text = "Script pas roulé",
                     beam_text = "Script pas roulé",
                     presc_text = "Script pas roulé",
                     opt_text = "Script pas roulé",
                     check_bonscan = "Pas vérifié",
                     check_scanOK = "Pas vérifié",
                     check_ext = "Pas vérifié",
                     check_isoOK = "Pas vérifié",
                     check_beams_Rx = "Pas vérifié",
                     check_contours = "Pas vérifié",
                     check_optimisation = "Pas vérifié",
                     check_distribution_dose = "Pas vérifié")
            
            #Create dictionaries for window/level switching
            self.lung_dict = dict(x=-600,y=1600)
            self.lw_dict = dict(x=-exam.Series[0].LevelWindow.x,y=exam.Series[0].LevelWindow.y)
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 450
            panel.Height = 860
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 450
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "            Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(15, 25)
            self.PatientIDHeader.Font = Font("Arial", 11, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 35
            offset = 20   
            
            self.label_bonscan = Label()
            self.label_bonscan.Text = "Le bon scan est utilisé pour la planification"
            self.label_bonscan.Location = Point(15, offset)
            self.label_bonscan.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_bonscan.AutoSize = True              
            
            self.check_bonscan = CheckBox()
            self.check_bonscan.Location = Point(410, offset - 2)
            self.check_bonscan.Width = 30
            self.check_bonscan.Checked = False        

            
       
            self.label_scanOK = Label()
            self.label_scanOK.Text = "Scan OK (artéfactes, étendu du scan, objets sur la table)"
            self.label_scanOK.Location = Point(15, offset + vert_spacer)
            self.label_scanOK.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_scanOK.AutoSize = True              
            
            self.check_scanOK = CheckBox()
            self.check_scanOK.Location = Point(410, offset + vert_spacer - 2)
            self.check_scanOK.Width = 30
            self.check_scanOK.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External' + overrides"
            button_ext.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_ext.Location = Point(15, offset + vert_spacer*2)
            button_ext.Width = 375 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(410, offset + vert_spacer*2 - 2)
            self.check_ext.Width = 30
            self.check_ext.Checked = False  
         
         
         
            self.label_contours = Label()
            self.label_contours.Text = "Les contours d'optimisation sont corrects"
            self.label_contours.Location = Point(15, offset + vert_spacer*3)
            self.label_contours.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_contours.AutoSize = True              
            
            self.check_contours = CheckBox()
            self.check_contours.Location = Point(410, offset + vert_spacer*3 - 2)
            self.check_contours.Width = 30
            self.check_contours.Checked = False                        
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre"
            button_isoOK.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_isoOK.Location = Point(15, offset + vert_spacer*4)
            button_isoOK.Width = 375
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(410, offset + vert_spacer*4 - 2)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False              
           

           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_beams_Rx.Location = Point(15, offset + vert_spacer*5)
            button_beams_Rx.Width = 375 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(410, offset + vert_spacer*5 - 2)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              

            
            
            button_optimisation = Button()
            button_optimisation.Text = "Objectifs et paramètres d'optimisation"
            button_optimisation.Font = Font("Arial", 10.25, FontStyle.Bold)
            #button_optimisation.TextAlign = HorizontalAlignment.Center
            button_optimisation.Location = Point(15, offset + vert_spacer*6)
            button_optimisation.Width = 375 
            button_optimisation.Click += self.button_opt_Clicked          
            
            self.check_optimisation = CheckBox()
            self.check_optimisation.Location = Point(410, offset + vert_spacer*6 - 2)
            self.check_optimisation.Width = 30
            self.check_optimisation.Checked = False                  


            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(15, offset + vert_spacer*7)
            self.label_distribution_dose.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(410, offset + vert_spacer*7 - 2)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         


            #Count up beamsets
            bs_text = ""
            num_bs = 0
            for bs in plan.BeamSets:
                bs_text += bs.DicomPlanLabel + ", "
                num_bs += 1            
            
            self.label_results_header = Label()
            self.label_results_header.Text = "Résultats"
            self.label_results_header.Location = Point(15, offset + vert_spacer*9)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = "Nombre de beamsets dans le plan: " + str(num_bs) + ' (' + bs_text[0:-2] + ')'
            self.label_results.Location = Point(15, offset + vert_spacer*10)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = "Rappel:\nRoulez le script de vérification pour chaque beamset"
            self.label_reminder.Location = Point(15, offset + vert_spacer*11)
            self.label_reminder.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_reminder.ForeColor = Color.Red
            self.label_reminder.AutoSize = True                 
            
            
            
            self.MainWindow.Controls.Add(self.label_bonscan)
            self.MainWindow.Controls.Add(self.check_bonscan)
            
            self.MainWindow.Controls.Add(self.label_scanOK)
            self.MainWindow.Controls.Add(self.check_scanOK)  
            
            self.MainWindow.Controls.Add(button_ext)  
            self.MainWindow.Controls.Add(self.check_ext)            
            
            self.MainWindow.Controls.Add(button_isoOK)   
            self.MainWindow.Controls.Add(self.check_isoOK)                 
            
            self.MainWindow.Controls.Add(button_beams_Rx)            
            self.MainWindow.Controls.Add(self.check_beams_Rx)
                      
            self.MainWindow.Controls.Add(self.label_contours)
            self.MainWindow.Controls.Add(self.check_contours)               

            self.MainWindow.Controls.Add(button_optimisation)            
            self.MainWindow.Controls.Add(self.check_optimisation)
            
            self.MainWindow.Controls.Add(self.label_distribution_dose)
            self.MainWindow.Controls.Add(self.check_distribution_dose)            

            self.MainWindow.Controls.Add(self.label_results_header)
            self.MainWindow.Controls.Add(self.label_results)
            self.MainWindow.Controls.Add(self.label_reminder)            

            
        def button_ext_Clicked(self, sender, args):       
            self.message.Text = "Vérification du contour External en cours"
            self.d['ext_text'] = verification.verify_external_and_overrides()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['ext_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 100)
            self.label_reminder.Text = "Rappel:\nVérifiez que la table (ou la planche ORL) est comprise dans\nle contour External avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_isoOK_Clicked(self, sender, args):
            uis.show_plan_optimization()
            uis.show_po_bev()
            uis.show_po_cg()        
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            #self.label_results.Text = d['presc_text']
            #d['iso_text'] = a #+ "\n" + b + "\n" + c + "\n\n" + d
            #self.label_results.Text = d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 130)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
            uis.show_plan_optimization()
            uis.show_po_2D()        
            self.label_reminder.Text = ""
            self.label_results.Text = ""
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification de la prescription en cours"
            self.d['presc_text'] = verification.verify_prescription()
            self.label_results.Text = self.d['presc_text']
            self.message.Text = "Vérification des faisceaux en cours"
            a,b,c,d,e = verification.verify_beams()   #d and e are not needed for a first verification (machine type and energy)
            self.d['beam_text'] = a + "\n\n" + e  + "\n\n" + c 
            self.label_results.Text += "\n\nFaisceaux:\n" + self.d['beam_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 150 + 15*b)
            self.label_reminder.Text = "Rappel:\nVérifiez que les angles de gantry et collimateur sont bien\nchoisis avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_opt_Clicked(self, sender, args):       
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification des paramètres d'optimisation"              
            a,b,c,d = verification.verify_opt_parameters()
            #self.d['opt_text']  = a + "\n" + b + "\n" + d + "\n" + c   
            self.d['opt_text']  = c   
            self.label_results.Text = self.d['opt_text']
            #d['opt_text'] = a + "\n" + b + "\n" + d + "\n" + c
            #self.label_results.Text = d['opt_text'] 
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 90)
            self.label_reminder.Text = "Rappel:\nVérifiez tous les objectifs d'optimisation avant de\nprocéder à la prochaine étape"
            self.message.Text = ""            
            
        #def cancelClicked(self, sender, args):
        #    self.Close()    

        def levelwindowClicked(self, sender, args):
            if exam.Series[0].LevelWindow.x == -600 and exam.Series[0].LevelWindow.y == 1600:
                exam.Series[0].LevelWindow = self.lw_dict
            else:
                exam.Series[0].LevelWindow = self.lung_dict            

        def referencedoseClicked(self, sender, args):
            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"       
            prostate.toggle_reference_dose()              
            self.message.Text = ""    
                
        def nbfxClicked(self, sender, args):            
            #uis.display_loc_point() 
            uis.open_plan_settings()                
                
        def printClicked(self, sender, args):     

            #Verify that all boxes have been checked
            warning = False
            if self.check_bonscan.Checked:
                self.d['check_bonscan'] = 'OK'
            else:
                warning = True
            if self.check_scanOK.Checked:
                self.d['check_scanOK'] = 'OK'
            else:
                warning = True                
            if self.check_ext.Checked:
                self.d['check_ext'] = 'OK'
            else:
                warning = True                
            if self.check_isoOK.Checked:
                self.d['check_isoOK'] = 'OK'
            else:
                warning = True                
            if self.check_beams_Rx.Checked:
                self.d['check_beams_Rx'] = 'OK'
            else:
                warning = True                
            if self.check_contours.Checked:
                self.d['check_contours'] = 'OK'
            else:
                warning = True                
            if self.check_optimisation.Checked:
                self.d['check_optimisation'] = 'OK'
            else:
                warning = True                
            if self.check_distribution_dose.Checked:
                self.d['check_distribution_dose'] = 'OK'                
            else:
                warning = True                
                

            self.message.ForeColor = Color.Black
            self.message.Text = "Impression en cours"
            report.create_verif1_report(data=self.d)
            
            if warning:
                self.message.ForeColor = Color.Red
                self.message.Text = "Impression terminé - vérification incomplète"
            else:
                self.message.ForeColor = Color.Green
                self.message.Text = "Impression terminé"
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 950)
            
            printButton = Button()
            printButton.Text = "Imprimer"
            printButton.Location = Point(25, 28)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            #cancelButton = Button()
            #cancelButton.Text = "Annuler"
            #cancelButton.Location = Point(110,10)
            #self.CancelButton = cancelButton
            #cancelButton.Click += self.cancelClicked

            levelwindowButton = Button()
            levelwindowButton.Text = "Level/Window"
            levelwindowButton.Location = Point(25,28)
            levelwindowButton.Width = 85
            levelwindowButton.Click += self.levelwindowClicked            
            
            referencedoseButton = Button()
            referencedoseButton.Text = "Toggle Reference Dose"
            referencedoseButton.Location = Point(117,28)
            referencedoseButton.Width = 140
            referencedoseButton.Click += self.referencedoseClicked                
            
            nbfxButton = Button()
            nbfxButton.Text = "Nb. de fx"
            nbfxButton.Location = Point(263,28)
            nbfxButton.Width = 70
            nbfxButton.Click += self.nbfxClicked  
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(30, 0)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            #Printing has been disabled for verif 1, simply add the printButton back if you want to reactivate it
            self.OKbuttonPanel.Controls.Add(nbfxButton)
            self.OKbuttonPanel.Controls.Add(levelwindowButton)
            self.OKbuttonPanel.Controls.Add(referencedoseButton)
            self.OKbuttonPanel.Controls.Add(self.message)
               
               
                
                
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
    try:
        temp = patient.ModificationInfo.UserName
    except:
        message.message_window('ATTENTION: Le plan a été modifié depuis la dernière sauvegarde.\n\nFermez cette fenêtre pour poursuivre avec la vérification.')
        #return        
              
    form = Verif1Window()
    Application.Run(form)   
     
       
def verification_finale():

    class Verif1Window(Form):
        def __init__(self):
            self.Text = "Vérification 2"

            self.Width = 450
            self.Height = 1000

            self.setupHeaderWindow()
            self.setupMainWindow()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
            #Create the dictionary that will be used to pass the verification info to the print function
            self.d = dict(patient_name = patient.PatientName.replace('^', ', '),
                     plan_name = plan.Name,
                     beamset_name = beamset.DicomPlanLabel,
                     patient_number = patient.PatientID,
                     #planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
                     planned_by_name = plan.PlannedBy,
                     verified_by_name = lib.get_user_name(os.getenv('USERNAME')),
                     ext_text = "Script pas roulé",
                     grid_text = "Script pas roulé",
                     DSP_text = "Script pas roulé",
                     iso_text = "Script pas roulé",
                     beam_text = "Script pas roulé",
                     presc_text = "Script pas roulé",
                     segments_text = "Script pas roulé",
                     check_billes = "Pas vérifié",
                     check_ext = "Pas vérifié",
                     check_isoOK = "Pas vérifié",
                     check_grid = "Pas vérifié",                     
                     check_beams_Rx = "Pas vérifié",
                     check_segments = "Pas vérifié",
                     check_distribution_dose = "Pas vérifié",
                     check_noteMD = "Pas vérifié",
                     check_DSP = "Pas vérifié",
                     check_mise_en_place = "Pas vérifié",
                     check_doctx = "Pas vérifié",
                     check_codestat = "Pas vérifié")
            
            #Create dictionaries for window/level switching
            self.lung_dict = dict(x=-600,y=1600)
            self.lw_dict = dict(x=-exam.Series[0].LevelWindow.x,y=exam.Series[0].LevelWindow.y)          

            #Display localisation point
            uis.display_loc_point()
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 450
            panel.Height = 800
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 450
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "            Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(15, 25)
            self.PatientIDHeader.Font = Font("Arial", 11, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 32
            offset = 15   

            
            self.label_billes = Label()
            self.label_billes.Text = "Billes sur point de localisation"
            self.label_billes.Location = Point(15, offset)
            self.label_billes.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_billes.AutoSize = True              
            
            self.check_billes = CheckBox()
            self.check_billes.Location = Point(410, offset - 2)
            self.check_billes.Width = 30
            self.check_billes.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External' et overrides"
            button_ext.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_ext.Location = Point(15, offset + vert_spacer)
            button_ext.Width = 375 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(410, offset + vert_spacer - 2)
            self.check_ext.Width = 30
            self.check_ext.Checked = False   
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre et point de localisation"
            button_isoOK.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_isoOK.Location = Point(15, offset + vert_spacer*2)
            button_isoOK.Width = 375 
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(410, offset + vert_spacer*2 - 2)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False                                         

            
            
            button_segments = Button()
            button_segments.Text = "Les segments sont corrects/flashé au besoin"
            button_segments.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_segments.Location = Point(15, offset + vert_spacer*3)
            button_segments.Width = 375 
            button_segments.Click += self.button_segments_Clicked                        
            
            self.check_segments = CheckBox()
            self.check_segments.Location = Point(410, offset + vert_spacer*3 - 2)
            self.check_segments.Width = 30
            self.check_segments.Checked = False               
           
           
           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_beams_Rx.Location = Point(15, offset + vert_spacer*4)
            button_beams_Rx.Width = 375 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(410, offset + vert_spacer*4 - 2)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              


            
            button_grid = Button()
            button_grid.Text = "La grille de dose est correcte"
            button_grid.Font = Font("Arial", 10.25, FontStyle.Bold)
            button_grid.Location = Point(15, offset + vert_spacer*5)
            button_grid.Width = 375 
            button_grid.Click += self.button_grid_Clicked              
                    
            self.check_grid = CheckBox()
            self.check_grid.Location = Point(410, offset + vert_spacer*5 - 2)
            self.check_grid.Width = 30
            self.check_grid.Checked = False     
            
            
            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(15, offset + vert_spacer*6)
            self.label_distribution_dose.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(410, offset + vert_spacer*6 - 2)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         

            
            
            self.label_noteMD = Label()
            self.label_noteMD.Text = "Vérif note de planif du MD                          NON"
            self.label_noteMD.Location = Point(15, offset + vert_spacer*7)
            self.label_noteMD.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_noteMD.AutoSize = True              
            
            self.check_noteMD_non = CheckBox()
            self.check_noteMD_non.Location = Point(340, offset + vert_spacer*7 - 2)
            self.check_noteMD_non.Width = 30
            self.check_noteMD_non.Checked = False                    
            
            self.label_OK1 = Label()
            self.label_OK1.Text = "OK"
            self.label_OK1.Location = Point(370, offset + vert_spacer*7)
            self.label_OK1.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_OK1.AutoSize = True               
            
            self.check_noteMD_OK = CheckBox()
            self.check_noteMD_OK.Location = Point(410, offset + vert_spacer*7 - 2)
            self.check_noteMD_OK.Width = 30
            self.check_noteMD_OK.Checked = False                     
            
            
            
            self.label_DSP = Label()
            self.label_DSP.Text = "Vérif note positionnement: HT, DSPs, matching"
            self.label_DSP.Location = Point(15, offset + vert_spacer*8)
            self.label_DSP.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_DSP.AutoSize = True              
            
            self.check_DSP = CheckBox()
            self.check_DSP.Location = Point(410, offset + vert_spacer*8 - 2)
            self.check_DSP.Width = 30
            self.check_DSP.Checked = False        
            
            
            
            self.label_mise_en_place = Label()
            self.label_mise_en_place.Text = "Vérif mise en place: ISO DICOM, struct, phase"
            self.label_mise_en_place.Location = Point(15, offset + vert_spacer*9)
            self.label_mise_en_place.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_mise_en_place.AutoSize = True              
            
            self.check_mise_en_place = CheckBox()
            self.check_mise_en_place.Location = Point(410, offset + vert_spacer*9 - 2)
            self.check_mise_en_place.Width = 30
            self.check_mise_en_place.Checked = False        
            
            
            
            self.label_doctx = Label()
            self.label_doctx.Text = "Vérification Document de Tx                      NON"
            self.label_doctx.Location = Point(15, offset + vert_spacer*10)
            self.label_doctx.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_doctx.AutoSize = True              
            
            self.check_doctx_non = CheckBox()
            self.check_doctx_non.Location = Point(340, offset + vert_spacer*10 - 2)
            self.check_doctx_non.Width = 30
            self.check_doctx_non.Checked = False                   
            
            self.label_OK2 = Label()
            self.label_OK2.Text = "OK"
            self.label_OK2.Location = Point(370, offset + vert_spacer*10)
            self.label_OK2.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_OK2.AutoSize = True                 
            
            self.check_doctx_OK = CheckBox()
            self.check_doctx_OK.Location = Point(410, offset + vert_spacer*10 - 2)
            self.check_doctx_OK.Width = 30
            self.check_doctx_OK.Checked = False                 
            
            
            
            self.label_codestat = Label()
            self.label_codestat.Text = "Vérification des codes statistiques"
            self.label_codestat.Location = Point(15, offset + vert_spacer*11)
            self.label_codestat.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_codestat.AutoSize = True              
            
            self.check_codestat = CheckBox()
            self.check_codestat.Location = Point(410, offset + vert_spacer*11 - 2)
            self.check_codestat.Width = 30
            self.check_codestat.Checked = False     

            
            #Count up beamsets
            bs_text = ""
            num_bs = 0
            for bs in plan.BeamSets:
                bs_text += bs.DicomPlanLabel + ", "
                num_bs += 1

            self.label_results_header = Label()
            self.label_results_header.Text = "Résultats"
            self.label_results_header.Location = Point(15, offset + vert_spacer*12.5)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = "Nombre de beamsets dans le plan: " + str(num_bs) + ' (' + bs_text[0:-2] + ')'
            self.label_results.Location = Point(15, offset + vert_spacer*13.5)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = "Rappel:\nRoulez le script de vérification pour chaque beamset"
            self.label_reminder.Location = Point(15, offset + vert_spacer*14.5)
            self.label_reminder.Font = Font("Arial", 10.25, FontStyle.Bold)
            self.label_reminder.ForeColor = Color.Red
            self.label_reminder.AutoSize = True                 
            
                
           
            self.MainWindow.Controls.Add(self.label_billes)
            self.MainWindow.Controls.Add(self.check_billes)  
            
            self.MainWindow.Controls.Add(button_ext)  
            self.MainWindow.Controls.Add(self.check_ext)            
            
            self.MainWindow.Controls.Add(button_isoOK)   
            self.MainWindow.Controls.Add(self.check_isoOK)     
            
            self.MainWindow.Controls.Add(button_segments)
            self.MainWindow.Controls.Add(self.check_segments)          
            
            self.MainWindow.Controls.Add(button_beams_Rx)            
            self.MainWindow.Controls.Add(self.check_beams_Rx)
                      
            self.MainWindow.Controls.Add(button_grid)
            self.MainWindow.Controls.Add(self.check_grid)                   
            
            self.MainWindow.Controls.Add(self.label_distribution_dose)
            self.MainWindow.Controls.Add(self.check_distribution_dose)

            self.MainWindow.Controls.Add(self.label_noteMD)
            self.MainWindow.Controls.Add(self.check_noteMD_non)            
            self.MainWindow.Controls.Add(self.label_OK1)
            self.MainWindow.Controls.Add(self.check_noteMD_OK)               

            self.MainWindow.Controls.Add(self.label_DSP)
            self.MainWindow.Controls.Add(self.check_DSP)               

            self.MainWindow.Controls.Add(self.label_mise_en_place)
            self.MainWindow.Controls.Add(self.check_mise_en_place)  

            self.MainWindow.Controls.Add(self.label_doctx)
            self.MainWindow.Controls.Add(self.check_doctx_non)  
            self.MainWindow.Controls.Add(self.label_OK2)          
            self.MainWindow.Controls.Add(self.check_doctx_OK)              
            
            self.MainWindow.Controls.Add(self.label_codestat)
            self.MainWindow.Controls.Add(self.check_codestat)  
            
            self.MainWindow.Controls.Add(self.label_results_header)
            self.MainWindow.Controls.Add(self.label_results)
            self.MainWindow.Controls.Add(self.label_reminder)            
                        
            
        def button_ext_Clicked(self, sender, args):              
            uis.show_patient_modeling()
            uis.select_roi_tab()
            self.message.ForeColor = Color.Black        
            self.message.Text = "Vérification du contour External en cours"
            self.d['ext_text'] = verification.verify_external_and_overrides()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['ext_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 100)
            self.label_reminder.Text = "Rappel:\nVérifiez que la table (ou la planche ORL) est comprise dans\nle contour External avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_grid_Clicked(self, sender, args):       
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de la grille de dose en cours"
            self.d['grid_text'] = verification.verify_dose_grid_resolution()
            self.d['DSP_text'] = verification.verify_dose_specification_points()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['grid_text']
            self.label_results.Text += "\n" + self.d['DSP_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
            self.label_reminder.Text = ""
            self.message.Text = ""            
            
        def button_isoOK_Clicked(self, sender, args):
            uis.show_plan_optimization()
            uis.show_po_bev()
            uis.show_po_cg()
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 130)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
            uis.show_plan_optimization()
            uis.show_po_2D()
            self.label_reminder.Text = ""
            self.label_results.Text = ""
            self.label_results_header.Text = "Résultats"
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de la prescription en cours"
            self.d['presc_text'] = verification.verify_prescription()
            self.label_results.Text = self.d['presc_text']
            self.message.Text = "Vérification des faisceaux en cours"
            a,b,c,d,e = verification.verify_beams()
            self.d['beam_text'] = a + "\n\n" + d + "\n" + e + "\n\n" + c  
            self.label_results.Text += "\n\nFaisceaux:\n" + self.d['beam_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 160 + 15*b)
            #self.label_reminder.Text = "Rappel:\nS'il y a un prothèse, un pacemaker ou un membre qui\ndépasse le FOV du scan, vérifiez que les angles de gantry\nsont bien choisis"
            self.label_reminder.Text = "Rappel:\nVérifiez que les angles de gantry et collimateur sont bien\nchoisis avant de procéder à la prochaine étape"            
            self.message.Text = ""
            
        def button_segments_Clicked(self, sender, args):   
            self.message.ForeColor = Color.Black        
            self.label_reminder.Text = ""
            self.label_results.Text = ""        
            self.message.Text = "Vérification des segments en cours"
            self.d['segments_text'] = verification.verify_segments()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['segments_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 90)
            self.label_reminder.Text = "Rappel:\nVérifiez les segments en mode BEV avant de procéder"
            self.message.Text = ""            
            
        #def cancelClicked(self, sender, args):
        #    self.Close()          
            
        def levelwindowClicked(self, sender, args):
            if exam.Series[0].LevelWindow.x == -600 and exam.Series[0].LevelWindow.y == 1600:
                exam.Series[0].LevelWindow = self.lw_dict
            else:
                exam.Series[0].LevelWindow = self.lung_dict                   
            
        def referencedoseClicked(self, sender, args):
            self.message.ForeColor = Color.Black
            self.message.Text = "En cours"       
            prostate.toggle_reference_dose_verif2()              
            self.message.Text = ""    
            
        def nbfxClicked(self, sender, args):            
            #uis.display_loc_point() 
            uis.open_plan_settings()
            
        def printClicked(self, sender, args):     

            #Verify that all boxes have been checked
            warning = False
            if self.check_billes.Checked:
                self.d['check_billes'] = 'OK'
            else:
                warning = True
            if self.check_ext.Checked:
                self.d['check_ext'] = 'OK'
            else:
                warning = True
            if self.check_isoOK.Checked:
                self.d['check_isoOK'] = 'OK'
            else:
                warning = True
            if self.check_grid.Checked:
                self.d['check_grid'] = 'OK'
            else:
                warning = True
            if self.check_beams_Rx.Checked:
                self.d['check_beams_Rx'] = 'OK'
            else:
                warning = True
            if self.check_segments.Checked:
                self.d['check_segments'] = 'OK'
            else:
                warning = True
            if self.check_distribution_dose.Checked:
                self.d['check_distribution_dose'] = 'OK'                
            else:
                warning = True
            if self.check_noteMD_non.Checked:
                self.d['check_noteMD'] = 'A completer'
            elif self.check_noteMD_OK.Checked:
                self.d['check_noteMD'] = 'OK'                
            else:
                warning = True                    
            if self.check_DSP.Checked:
                self.d['check_DSP'] = 'OK'
            else:
                warning = True                
            if self.check_mise_en_place.Checked:
                self.d['check_mise_en_place'] = 'OK'
            else:
                warning = True     
            if self.check_doctx_non.Checked:
                self.d['check_doctx'] = 'A approuver'
            elif self.check_doctx_OK.Checked:
                self.d['check_doctx'] = 'OK'                
            else:
                warning = True                     
            if self.check_codestat.Checked:
                self.d['check_codestat'] = 'OK'
            else:
                warning = True                     

            self.message.ForeColor = Color.Black
            self.message.Text = "Impression en cours"
            report.create_verif2_report(data=self.d)
            
            if warning:
                self.message.ForeColor = Color.Red
                self.message.Text = "Impression terminé - vérification incomplète"
            else:
                self.message.ForeColor = Color.Green
                self.message.Text = "Impression terminé"
            

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 900)
            
            printButton = Button()
            printButton.Text = "Imprimer"
            printButton.Location = Point(25, 28)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            #cancelButton = Button()
            #cancelButton.Text = "Annuler"
            #cancelButton.Location = Point(110,10)
            #self.CancelButton = cancelButton
            #cancelButton.Click += self.cancelClicked

            levelwindowButton = Button()
            levelwindowButton.Text = "Level/Window"
            levelwindowButton.Location = Point(108,28)
            levelwindowButton.Width = 85
            levelwindowButton.Click += self.levelwindowClicked            
            
            referencedoseButton = Button()
            referencedoseButton.Text = "Toggle Reference Dose"
            referencedoseButton.Location = Point(200,28)
            referencedoseButton.Width = 140
            referencedoseButton.Click += self.referencedoseClicked                
            
            nbfxButton = Button()
            nbfxButton.Text = "Nb. de fx"
            nbfxButton.Location = Point(345,28)
            nbfxButton.Width = 70
            nbfxButton.Click += self.nbfxClicked  
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(30, 0)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(printButton)
            self.OKbuttonPanel.Controls.Add(levelwindowButton)
            self.OKbuttonPanel.Controls.Add(referencedoseButton)
            self.OKbuttonPanel.Controls.Add(nbfxButton)
            self.OKbuttonPanel.Controls.Add(self.message)
               
                
                
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
    try:
        temp = patient.ModificationInfo.UserName
    except:
        message.message_window('ATTENTION: Le plan a été modifié depuis la dernière sauvegarde.\n\nFermez cette fenêtre pour poursuivre avec la vérification.')
        #return
        
    form = Verif1Window()
    Application.Run(form)   
      

