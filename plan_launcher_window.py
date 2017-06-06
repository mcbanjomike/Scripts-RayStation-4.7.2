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

 
def plan_launcher():

    class ScriptLauncher(Form):
        def __init__(self):
            self.Text = "Planning Script Launcher v3"

            self.Width = 750
            self.Height = 580

            self.setupPlanningScriptLauncher()
            self.setupOKButtons()
            self.setupMachineSelectPanel()

            self.Controls.Add(self.LauncherPanel)
            self.Controls.Add(self.OKbuttonPanel)
            self.Controls.Add(self.MachineSelectPanel)
            
        def newPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 350
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
            self.PatientLabel.Text = "Choissisez le site à planifier:                       Patient: " + patient.PatientName.replace('^', ', ')
            self.PatientLabel.Location = Point(25, 25)
            self.PatientLabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.PatientLabel.AutoSize = True

            self.sitecombo = ComboBox()
            self.sitecombo.Parent = self
            self.sitecombo.Size = Size(200,40)
            self.sitecombo.Location = Point(25, 50)
            self.sitecombo.Items.Add("Prostate")
            self.sitecombo.Items.Add("Poumon")     
            self.sitecombo.Items.Add("Crâne")
            self.sitecombo.Items.Add("Crâne 2 niveaux")
            self.sitecombo.Items.Add("Foie")                 
            self.sitecombo.Items.Add("Vertebre")              
            self.sitecombo.Text = "Choisissez site"
            self.sitecombo.TextChanged += self.siteselectionChanged           
    
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
            
            
            #self.Status = Label()
            #self.Status.Text = ""
            #self.Status.Location = Point(300, 190)
            #self.Status.AutoSize = True
            #self.Status.Font = Font("Arial", 12, FontStyle.Bold)
            #self.Status.ForeColor = Color.Black

            self.Reminder = Label()
            self.Reminder.Text = ""
            self.Reminder.Location = Point(300, 220)
            self.Reminder.AutoSize = True
            self.Reminder.Font = Font("Arial", 11, FontStyle.Italic)
            self.Reminder.ForeColor = Color.Black
            
            self.RxLabel = Label()
            self.RxLabel.Text = "Prescription:"
            self.RxLabel.Location = Point(25, 90)
            self.RxLabel.Font = Font("Arial", 10)
            self.RxLabel.AutoSize = True  
            
            self.comboBoxRx = ComboBox()
            self.comboBoxRx.Parent = self
            self.comboBoxRx.Size = Size(90,40)
            self.comboBoxRx.Location = Point(135,90)
            
            
            #self.DoseLabel = Label()
            #self.DoseLabel.Text = "Dose (Gy):"
            #self.DoseLabel.Location = Point(25, 90)
            #self.DoseLabel.Font = Font("Arial", 10)
            #self.DoseLabel.AutoSize = True               

            #self.dosebox = TextBox()
            #self.dosebox.Text = "----"
            #self.dosebox.Location = Point(135, 90)
            #self.dosebox.Width = 40
              
            #self.FxLabel = Label()
            #self.FxLabel.Text = "Nb de fx:"
            #self.FxLabel.Location = Point(25, 120)
            #self.FxLabel.Font = Font("Arial", 10)
            #self.FxLabel.AutoSize = True               

            #self.Fxbox = TextBox()
            #self.Fxbox.Text = "----"
            #self.Fxbox.Location = Point(135, 120)
            #self.Fxbox.Width = 40                        
                        
            self.techniqueLabel = Label()
            self.techniqueLabel.Text = "Technique:"
            self.techniqueLabel.Location = Point(25, 120)
            self.techniqueLabel.Font = Font("Arial", 10)
            self.techniqueLabel.AutoSize = True                
            
            self.techniquecombo = ComboBox()
            self.techniquecombo.Parent = self
            self.techniquecombo.Size = Size(55,40)
            self.techniquecombo.Location = Point(135, 120)                          
            
            self.isodoseLabel = Label()
            self.isodoseLabel.Text = "Créér dose table?"
            self.isodoseLabel.Location = Point(25, 150)
            self.isodoseLabel.Font = Font("Arial", 10)
            self.isodoseLabel.AutoSize = True               
            
            self.isodosecombo = ComboBox()
            self.isodosecombo.Parent = self
            self.isodosecombo.Size = Size(55,40)
            self.isodosecombo.Location = Point(135, 150)   
            self.isodosecombo.Items.Add("Oui")     
            self.isodosecombo.Items.Add("Non")                 
            self.isodosecombo.Text = 'Oui'                   

            self.SiteLabel = Label()
            self.SiteLabel.Text = "Nom du site:"
            self.SiteLabel.Location = Point(25, 180)
            self.SiteLabel.Font = Font("Arial", 10)
            self.SiteLabel.AutoSize = True               

            self.SiteBox = TextBox()
            self.SiteBox.Text = "A1"
            self.SiteBox.Location = Point(135, 180)
            self.SiteBox.Width = 40                 
   
            self.scanLabel = Label()
            self.scanLabel.Text = "Scan de planif"
            self.scanLabel.Location = Point(25, 210)
            self.scanLabel.Font = Font("Arial", 10)
            self.scanLabel.AutoSize = True               
            
            self.scancombo = ComboBox()
            self.scancombo.Parent = self
            self.scancombo.Size = Size(55,40)
            self.scancombo.Location = Point(135, 210)              
            self.isodosecombo.Text = 'Choissisez'            

            
            self.OptionsLabel = Label()
            self.OptionsLabel.Text = "Options:"
            self.OptionsLabel.Location = Point(25, 250)
            self.OptionsLabel.Font = Font("Arial", 10)
            self.OptionsLabel.AutoSize = True            
                      
            self.check1 = CheckBox()
            self.check1.Text = "Double optimization initiale?"
            self.check1.Location = Point(40, 270)
            self.check1.Width = 300
            self.check1.Checked = False
            
            self.check2 = CheckBox()
            self.check2.Text = ""
            self.check2.Location = Point(40, 295)
            self.check2.Width = 300            

            self.check3 = CheckBox()
            self.check3.Text = ""
            self.check3.Location = Point(40, 320)
            self.check3.Width = 300    
            
            
            
            self.LauncherPanel.Controls.Add(self.PatientLabel)
            self.LauncherPanel.Controls.Add(self.Label2)
            self.LauncherPanel.Controls.Add(self.Label3)
            self.LauncherPanel.Controls.Add(self.Label4)
            self.LauncherPanel.Controls.Add(self.Label5)
            #self.LauncherPanel.Controls.Add(self.Status)
            self.LauncherPanel.Controls.Add(self.Reminder)    
            self.LauncherPanel.Controls.Add(self.RxLabel) 
            #self.LauncherPanel.Controls.Add(self.DoseLabel)
            #self.LauncherPanel.Controls.Add(self.dosebox)  
            #self.LauncherPanel.Controls.Add(self.FxLabel)
            #self.LauncherPanel.Controls.Add(self.Fxbox)
            self.LauncherPanel.Controls.Add(self.isodoseLabel)
            self.LauncherPanel.Controls.Add(self.scanLabel)
            self.LauncherPanel.Controls.Add(self.techniqueLabel)         
            self.LauncherPanel.Controls.Add(self.SiteLabel)
            self.LauncherPanel.Controls.Add(self.SiteBox)      
            self.LauncherPanel.Controls.Add(self.OptionsLabel)            
            self.LauncherPanel.Controls.Add(self.check1)
            self.LauncherPanel.Controls.Add(self.check2)
            self.LauncherPanel.Controls.Add(self.check3)            


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
                    
        def siteselectionChanged(self, sender, args):

            # Erase error messages and clear prescription selection menu
            self.Label2.Text = ""
            self.Label3.Text = ""
            self.Label4.Text = ""
            self.Label5.Text = ""
            self.Status.Text = ""
            self.Reminder.Text = ""            
            self.Label2.ForeColor = Color.Black
            self.Label3.ForeColor = Color.Black
            self.Label4.ForeColor = Color.Black
            self.Label5.ForeColor = Color.Black
            self.Status.ForeColor = Color.Black
            self.Reminder.ForeColor = Color.Black    
            self.check1.Text = "Double optimization initiale?"            
            self.check1.Checked = False            
            self.check2.Text = ""
            self.check2.Checked = False
            self.check3.Text = ""
            self.check3.Checked = False
            self.comboBoxRx.Items.Clear()
            self.comboBoxRx.Text = "-----"
            self.techniquecombo.Items.Clear()
            self.techniquecombo.Items.Add("VMAT")                 
            self.techniquecombo.Text = 'VMAT'
            PACE = False
            
            roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                        
            if self.sitecombo.Text == "Prostate":      
                # add items
                self.comboBoxRx.Items.Add("80Gy-40")
                self.comboBoxRx.Items.Add("66Gy-33")
                self.comboBoxRx.Items.Add("60Gy-20")
                self.comboBoxRx.Items.Add("37.5Gy-15")
                self.comboBoxRx.Items.Add("PACE 78Gy-39")
                self.comboBoxRx.Items.Add("PACE 36.25Gy-5")
                self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("80Gy-40")
                self.Reminder.Text = "Pour les plans de prostate, le nom du site est\nchoisi de façon automatique (donc la boîte\nNom du site sera ignorée.)"
                self.check1.Text = "Auto-optimisation initial"
                self.check1.Checked = True
                self.check2.Text = "Est-ce qu'il y a un plan 3D conforme?"
            
                boost = False
                for name in roi_names:
                    if 'PTVBOOST' in name.replace(' ', '').upper():
                        boost = True
                        boost_name = name

                #Find ROI(s) that will be used to create PTV A1
                if 'PTV A1' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV A1 déjà existent"
                elif 'PTV 1.5cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1.5cm"
                elif 'PTV 1cm' in roi_names:
                    if 'PTV VS' in roi_names:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm + PTV VS"
                    else:
                        self.Label2.Text = "Source pour PTV A1: PTV 1cm"
                elif 'PTV_7800' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_7800"
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("PACE 78Gy-39")
                    PACE = True
                elif 'PTV_3625' in roi_names:
                    self.Label2.Text = "Source pour PTV A1: PTV_3625"  
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("PACE 36.25Gy-5")
                    PACE = True
                else:
                    self.Label2.Text = "Attention: Aucun ROI source trouvé pour le PTV A1!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Find ROI that will be used to create PTV A2
                if boost:
                    self.Label3.Text = "Source pour PTV A2: " + boost_name
                elif 'PTV 1cm' in roi_names:
                    self.Label3.Text = "Source pour PTV A2: PTV 1cm"
                elif not PACE:
                    self.Label3.Text = "Attention: Aucun ROI source trouvé pour le PTV A2!"     
                    self.Label3.ForeColor = Color.Orange                       
                
                #Verify presence of essential contours
                if not PACE:
                    essential_list = ["Table","RECTUM","VESSIE"]
                else:
                    essential_list = ["Table","Rectum","Bladder"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    if not PACE:
                        self.Label4.Text = "ROIs Table, RECTUM et VESSIE trouvés"
                    else:
                        self.Label4.Text = "ROIs Table, Rectum et Bladder trouvés"

                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                 
 

            elif self.sitecombo.Text == "Crâne":     
                self.check1.Checked = True  #Double optimization
                
                ptv_name = "NoValue"
                #roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                for name in roi_names:
                    n = name.replace(' ', '').upper()
                    if 'PTV' in n and '-' not in n:
                        if n[3:] not in ['1','2','3','4','5','6','7','8','9']:
                            try:
                               presc_dose = float(name[3:])
                            except:
                                continue
                            ptv_name = name
                            break  
                if ptv_name != "NoValue":
                    self.Label2.Text = ptv_name + " trouvé"
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-1")
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-3")
                    if presc_dose > 20:
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact(ptv_name[3:]+"Gy-3")
                    else:
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact(ptv_name[3:]+"Gy-1")
                    self.techniquecombo.Items.Add("IMRT")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red                  
                
                if 'CERVEAU' not in roi_names:
                    self.Label3.Text = "ROI CERVEAU pas trouvé!"
                    self.Label3.ForeColor = Color.Red          
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red    
                    
            elif self.sitecombo.Text == "Crâne 2 niveaux":     
                self.check1.Checked = True  #Double optimization
                #Identify the PTV
                if 'PTV18' in roi_names and 'PTV15' in roi_names:
                    self.Label2.Text = "PTV18 et PTV15 trouvés"
                    self.comboBoxRx.Items.Add("18 et 15Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18 et 15Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "15"
                    #self.Fxbox.Text = "1"
                elif 'PTV15' in roi_names and 'PTV12' in roi_names:
                    self.Label2.Text = "PTV15 et PTV12 trouvés"
                    self.comboBoxRx.Items.Add("15 et 12Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("15 et 12Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "18"
                    #self.Fxbox.Text = "1"
                else:
                    self.Label2.Text = "Attention: Aucun ou seulement un PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                if 'CERVEAU' not in roi_names:
                    self.Label3.Text = "ROI CERVEAU pas trouvé!"
                    self.Label3.ForeColor = Color.Red          

                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red    
                    
                    
            elif self.sitecombo.Text == "Poumon":   
                self.Reminder.Text = "Pour les plans de poumon, le nom du site est\nchoisi de façon automatique (donc la boîte\nNom du site sera ignorée.)"
                self.check1.Checked = True  #Double optimization 
                self.check2.Text = "Ajouter deuxième arc? (plans difficiles)"            
                self.comboBoxRx.Items.Add("48Gy-4")
                self.comboBoxRx.Items.Add("54Gy-3")
                self.comboBoxRx.Items.Add("56Gy-4")
                self.comboBoxRx.Items.Add("60Gy-5")
                self.comboBoxRx.Items.Add("60Gy-8")
                self.comboBoxRx.Items.Add("LUSTRE 48Gy-4")                
                self.comboBoxRx.Items.Add("LUSTRE 60Gy-8")
                self.comboBoxRx.Items.Add("LUSTRE 60Gy-15")

                
                #Identify the PTV
                if 'PTV48' in roi_names:
                    if 'ITV48' in roi_names:
                        self.Label2.Text = "PTV48 et ITV48 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("48Gy-4")
                        self.techniquecombo.Items.Add("IMRT")
                    else: 
                        self.Label2.Text = "Attention: PTV48 trouveé, mais ITV48 absent!"     
                        self.Label2.ForeColor = Color.Red   
                elif 'PTV54' in roi_names:
                    if 'ITV54' in roi_names:
                        self.Label2.Text = "PTV54 et ITV54 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("54Gy-3")
                        self.techniquecombo.Items.Add("IMRT")
                    else:
                        self.Label2.Text = "Attention: PTV54 trouveé, mais ITV54 absent!"     
                        self.Label2.ForeColor = Color.Red       
                elif 'PTV56' in roi_names:
                    if 'ITV56' in roi_names:
                        self.Label2.Text = "PTV56 et ITV56 trouvés"
                        self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("56Gy-4")
                        self.techniquecombo.Items.Add("IMRT")
                    else:
                        self.Label2.Text = "Attention: PTV56 trouveé, mais ITV56 absent!"     
                        self.Label2.ForeColor = Color.Red                           
                elif 'PTV60' in roi_names:
                    if 'ITV60' in roi_names:
                        self.Label2.Text = "PTV60 et ITV60 trouvés"
                        self.comboBoxRx.Text = "-----"
                        self.techniquecombo.Items.Add("IMRT")
                        
                    else:
                        self.Label2.Text = "Attention: PTV60 trouveé, mais ITV60 absent!"     
                        self.Label2.ForeColor = Color.Red      
                elif 'PTV A1' in roi_names:
                    if 'ITV A1' in roi_names:
                        self.Label2.Text = "PTV A1 et ITV A1 trouvés"
                        self.comboBoxRx.Text = "-----"
                        self.techniquecombo.Items.Add("IMRT")
                    else:
                        self.Label2.Text = "Attention: PTV A1 trouveé, mais ITV A1 absent!"     
                        self.Label2.ForeColor = Color.Red    
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé pour plan A1!"     
                    self.Label2.ForeColor = Color.Red     
                if 'PTV B1' in roi_names:
                    if 'ITV B1' in roi_names:
                        if poi.poi_exists("ISO B1"):
                            self.Label5.Text = "PTV B1, ITV B1 et ISO B1 trouvés, possible d'ajouter un plan B1"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"
                        else:
                            self.Label5.Text = "PTV B1 et ITV B1 trouvés, mais ISO B1 absent"
                            self.check3.Text = "Créer plan B1 (seulement si plan A1 existe déjà)"            
                            self.Reminder.Text = "RAPPEL: Pour la création d'un plan B1, il est possible\nd'utiliser un nouvel isocentre avec le nom ISO B1."
                    else:
                        self.Label5.Text = "Attention: PTV B1 trouvé, mais ITV B1 absent!"     
                        self.Label5.ForeColor = Color.Red  
                    
                #Verify presence of essential contours
                essential_list = ["Table","POUMON DRT","POUMON GCHE","BR SOUCHE"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, BR SOUCHE et POUMONs trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO", patient.Examinations['CT 1']):           
                    self.Label4.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN", patient.Examinations['CT 1']):           
                    self.Label4.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     


            elif self.sitecombo.Text == "Foie":     
                self.check1.Checked = True  #Double optimization       
                #Identify the PTV
                ptv_name = "NoValue"
                #roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                for name in roi_names:
                    n = name.replace(' ', '').upper()
                    if 'PTV' in n and '-' not in n:
                        try:
                            presc_dose = float(name[3:])
                            if presc_dose < 10: #Contours named PTV1, PTV2, etc don't actually correspond to treatments of 1 or 2 Gy!
                                continue
                        except:
                            continue
                        ptv_name = name
                        break  
                if ptv_name != "NoValue":
                    self.Label2.Text = ptv_name + " trouvé"
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-3")
                    self.comboBoxRx.Items.Add(ptv_name[3:]+"Gy-5")
                    self.comboBoxRx.Text = "Choisissez"
                    self.techniquecombo.Items.Add("IMRT")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red     
                
                #Verify presence of essential contours
                essential_list = ["Table","FOIE EXPI","GTV"]
                missing_roi = []
                for roi in essential_list:
                    if roi not in roi_names:
                        missing_roi.append(roi)
                    
                if len(missing_roi) > 0:
                    error_message = ""
                    for roi in missing_roi:
                        error_message += roi + ",  "
                    if error_message[-3:]==",  ":
                        error_message = error_message[:-3]
                    self.Label3.Text = "ROI(s) pas trouvés: " + error_message
                    self.Label3.ForeColor = Color.Red
                else:
                    self.Label3.Text = "ROIs Table, FOIE EXPI et GTV trouvés"      
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red     
                 
                 
            elif self.sitecombo.Text == "Vertebre":     
                self.check1.Checked = True  #Double optimization        
                #Identify the PTV
                if 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                else:
                    self.Label2.Text = "Attention: Aucun PTV trouvé!"     
                    self.Label2.ForeColor = Color.Red                         
       
                #Determine which POI will be used for the isocenter
                if poi.poi_exists("ISO"):           
                    self.Label5.Text = "Point ISO sera utilisé comme isocentre"                        
                elif poi.poi_exists("REF SCAN"):           
                    self.Label5.Text = "L'isocentre sera créé à partir du point REF SCAN"      
                else:
                    self.Label4.Text = "Aucun POI trouvé pour l'isocentre"
                    self.Label4.ForeColor = Color.Red                     
                 
                    
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
                
            #Check whether to create isodose lines
            if self.isodosecombo.Text == 'Oui':
                isodose_creation = True
            else:
                isodose_creation = False
                
            #Check treatment techniqueLabel
            if self.techniquecombo.Text == 'IMRT':
                treatment_technique = 'SMLC'
            else:
                treatment_technique = 'VMAT'
                
            #Ensure that a prescription has been selected
            if self.comboBoxRx.Text == '-----' or self.comboBoxRx.SelectedIndex == -1:
                self.Status.Text = "Il faut choisir une prescription avant de continuer"
                self.Status.ForeColor = Color.Red              
                return
            
            #Determine prescription dose (in cGy) and number of fractions
            pace = False
            temp_string = self.comboBoxRx.Text
            if temp_string[:5] == 'PACE ':
                temp_string = temp_string[5:]
                pace = True
            elif temp_string[:7] == 'LUSTRE ':
                temp_string = temp_string[7:]
                lustre = True                
            try:
                if 'et' in temp_string.split('Gy-')[0]: #if 2 dose levels
                    temp_rx_dose = temp_string.split('Gy-')[0]
                    rx_dose = int(float(temp_rx_dose.split()[0])*100)
                    rx_dose_low = int(float(temp_rx_dose.split()[2])*100)
                    nb_fx = int(temp_string.split('Gy-')[1])
                else:
                    rx_dose = int(float(temp_string.split('Gy-')[0]) * 100)
                    nb_fx = int(temp_string.split('Gy-')[1])
            except:
                self.Status.Text = "Impossible de lire dose de prescription ou nombre de fractions"
                self.Status.ForeColor = Color.Red              
                return
                

            #Check to see which site is treated (and therefore which script to launch)
            if self.sitecombo.Text == 'Prostate':
            
                if nb_fx == 15: #37.5Gy-15 plans are initially planned as 60Gy-24 using clinical goals for a 60Gy-20 prescription
                    nb_fx = 24
                    rx_dose = 6000
                    
                #Set the plan type (used for adding clinical goals later)
                if pace:
                    plan_type = 'Prostate PACE'
                elif nb_fx == 40:
                    plan_type = 'Prostate'
                else:
                    plan_type = 'Lit Prostatique'

                d = dict(patient = patient,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         treatment_technique = treatment_technique,
                         plan_type = plan_type)        

                
                
                self.Status.ForeColor = Color.Black
                
                if patient.BodySite == '':
                    patient.BodySite = 'Prostate'                
                
                self.Status.Text = "En cours: Gestion des POIs"
                prostate.prostate_A1_pois(plan_data = d)
                
                self.Status.Text = "En cours: Création des ROIs (peut prendre un peu de temps)"
                prostate.prostate_A1_rois(plan_data = d)
                
                self.Status.Text = "En cours: Ajout du plan et beamset"
                prostate.prostate_A1_add_plan_and_beamset(plan_data = d)

                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    prostate.prostate_A1_create_isodose_lines(plan_data = d)

                self.Status.Text = "En cours: Ajout des faisceaux"
                beams.add_beams_prostate_A1(beamset=patient.TreatmentPlans['A1 seul'].BeamSets['A1'])          

                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                prostate.prostate_A1_opt_settings(plan_data = d)                
            
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation"
                optimization_objectives.add_opt_obj_prostate_A1(plan=patient.TreatmentPlans['A1 seul'])
                
                self.Status.Text = "En cours: Ajout des clinical goals"
                if nb_fx == 24: #37.5Gy-15 plans are initially planned as 60Gy-24 using clinical goals for a 60Gy-20 prescription
                    clinical_goals.add_dictionary_cg(plan_type, rx_dose/100, 20, plan=patient.TreatmentPlans['A1 seul'])
                else:
                    clinical_goals.add_dictionary_cg(plan_type, rx_dose/100, nb_fx, plan=patient.TreatmentPlans['A1 seul'])
                
                if self.check2.Checked and plan_type != 'Prostate PACE': #If 3DCRT grand bassin plan exists
                    self.Status.Text = "En cours: Changement de noms pour A2-A3"
                    prostate.prostate_A1_rename(plan_data = d)
                    isodose_creation = False
            
                
            
                if plan_type == 'Prostate PACE':
                    self.Status.Text = "En cours: Changement du nom du PTV"
                    if roi.roi_exists("PTV_7800"):
                        patient.PatientModel.RegionsOfInterest["PTV_7800"].Name = "PTV A1 78Gy"
                    if roi.roi_exists("PTV_3625"):
                        patient.PatientModel.RegionsOfInterest["PTV_3625"].Name = "PTV A1 36.25Gy"                        
                    
                # Auto optimization if requested by user    
                if self.check1.Checked:
                    if self.check2.Checked and plan_type != 'Prostate PACE': #If A1 grand bassin already exists
                        opt_plan = patient.TreatmentPlans["A2 seul"]  
                    else:
                        opt_plan = patient.TreatmentPlans["A1 seul"]                       
                    self.Status.Text = "Auto-optimization en cours (1er opt avant fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Auto-optimization en cours (2er opt avant fit)"
                    optim.set_optimization_parameters(plan=patient.TreatmentPlans['A1 seul'],fluence_iterations=0, max_iterations=20, compute_intermediate_dose=False)
                    opt_plan.PlanOptimizations[0].RunOptimization()                     
                    self.Status.Text = "Auto-optimization en cours (Ajustement des objectifs)"                        
                    prostate.fit_obj_prostate(plan=opt_plan, beamset = opt_plan.BeamSets[0])
                    opt_plan.PlanOptimizations[0].AutoScaleToPrescription = False
                    opt_plan.PlanOptimizations[0].ResetOptimization()
                    self.Status.Text = "Auto-optimization en cours (1er opt après fit)"
                    optim.set_optimization_parameters(plan=patient.TreatmentPlans['A1 seul'],fluence_iterations=20, max_iterations=80, compute_intermediate_dose=True)
                    opt_plan.PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Auto-optimization en cours (2er opt après fit)"
                    optim.set_optimization_parameters(plan=patient.TreatmentPlans['A1 seul'],fluence_iterations=0, max_iterations=20, compute_intermediate_dose=False)
                    opt_plan.PlanOptimizations[0].RunOptimization()                   
                    
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green      
                
 
            elif self.sitecombo.Text == 'Crâne' or self.sitecombo.Text == 'Crâne 2 niveaux':
                if self.sitecombo.Text == 'Crâne 2 niveaux':
                    if rx_dose == 1500:
                        ptv = patient.PatientModel.RegionsOfInterest["PTV15"]
                        ptv_low = patient.PatientModel.RegionsOfInterest["PTV12"]
                    elif rx_dose == 1800:  
                        ptv = patient.PatientModel.RegionsOfInterest["PTV18"]
                        ptv_low = patient.PatientModel.RegionsOfInterest["PTV15"]  
                        
                else:
                    ptv = patient.PatientModel.RegionsOfInterest[self.Label2.Text.split()[0]]
                    ptv_low = None
                    rx_dose_low = None
                    
                    
                #Create the plan data dictionary to send to the component scripts                        
                #d = {'plan_name':'A1'}
                d = dict(patient = patient,
                         plan_name = 'Stereo Crane',
                         beamset_name = 'Stereo Crane',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = ptv,
                         rx_dose_low = rx_dose_low,
                         ptv_low = ptv_low,
                         treatment_technique = treatment_technique)                        
                
                   
                
                self.Status.ForeColor = Color.Black
                
                if patient.BodySite == '':
                    patient.BodySite = 'Crâne'
                
                self.Status.Text = "En cours: Gestion des POIs"
                crane.crane_stereo_pois(plan_data = d)
                
                self.Status.Text = "En cours: Création des ROIs (peut prendre un peu de temps)"
                if ptv_low == None:
                    crane.crane_stereo_rois(plan_data = d)
                else:
                    crane.crane_stereo_2niveaux_rois(plan_data = d)
                
                self.Status.Text = "En cours: Ajout du plan et beamset"
                crane.crane_stereo_add_plan_and_beamset(plan_data = d)

                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    crane.crane_stereo_create_isodose_lines(plan_data = d)

                self.Status.Text = "En cours: Ajout des faisceaux"
                crane.crane_stereo_add_beams(plan_data = d)    

                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                crane.crane_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation"
                optimization_objectives.add_opt_obj_brain_stereo_v2(plan_data = d)

                self.Status.Text = "En cours: Ajout des clinical goals"
                eval.add_clinical_goal(ptv.Name, rx_dose, 'AtLeast', 'VolumeAtDose', 99, plan = patient.TreatmentPlans[d['plan_name']])
                eval.add_clinical_goal('BodyRS', rx_dose*1.5, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan = patient.TreatmentPlans[d['plan_name']])
                clinical_goals.add_dictionary_cg('Crane Stereo', 15, 1, plan = patient.TreatmentPlans[d['plan_name']]) #Same CG no matter what the Rx dose is
                if ptv_low != None:
                    eval.add_clinical_goal('Mod_ptvL', rx_dose_low, 'AtLeast', 'VolumeAtDose', 99, plan = patient.TreatmentPlans[d['plan_name']])
                
                self.Status.Text = "En cours: Changement du nom du PTV"
                crane.crane_stereo_rename_ptv(plan_data = d)
                                 
                
                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "En cours: Première optimization"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "En cours: Deuxième optimization"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   
                
                    
            elif self.sitecombo.Text == 'Poumon':            
                # Check if the user wants to add plan B1 to an existing plan
                if self.check3.Checked:
                    site_name = 'B1'
                    plan_opt = 1 #Assume for now that B1 will be added as a second beamset in the original plan
                    self.SiteBox.Text = 'B1'
                    ptv_name = 'PTV B1'
                    itv_name = 'ITV B1'
                else:
                    site_name = 'A1' #It's too complicated to accept arbitrary site names for lung cases, sorry
                    plan_opt = 0
                    #Determine PTV and ITV names (based on message displayed in Label2 - does not work for B1 plans because message is changed!)
                    ptv_name = self.Label2.Text
                    ptv_name = ptv_name[0:6] #Include 6 characters in case PTV A1 is used
                    if ptv_name[-1] == ' ':
                        ptv_name = ptv_name[0:5] #Drop blank space at the end if applicable
                    itv_name = 'I' + ptv_name[1:]

                # See if second arc was requested
                if self.check2.Checked: 
                    two_arcs = True
                else:
                    two_arcs = False
            
                #Create the plan data dictionary to send to the component scripts                        
                d = dict(patient = patient,
                         plan_name = 'Stereo Poumon',
                         beamset_name = site_name,
                         site_name = site_name,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest[ptv_name],
                         itv = patient.PatientModel.RegionsOfInterest[itv_name],
                         treatment_technique = treatment_technique,
                         two_arcs = two_arcs)                            
                    
                
                
                self.Status.ForeColor = Color.Black

                #SECRET OPTION: If you want to add a KBP plan (regular plan must already exist), create an ROI called kbp or KBP and give it some geometry
                roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
                if 'kbp' in roi_names or 'KBP' in roi_names or 'vide_kbp' in roi_names or 'vide_KBP' in roi_names:
                    add_kbp_plan = True      
                else:
                    add_kbp_plan = False
                
                if add_kbp_plan is False:
                    if patient.BodySite == '':
                        patient.BodySite = 'Poumon'                
                    
                    self.Status.Text = "En cours: Gestion des POIs"
                    poumon.poumon_stereo_pois(plan_data = d)
                    
                    self.Status.Text = "En cours: Création des ROIs"
                    new_names = poumon.poumon_stereo_rois(plan_data = d)

                    self.Status.Text = "En cours: Ajout du plan et beamset"
                    new_plan_name = poumon.poumon_stereo_add_plan_and_beamset(plan_data = d)
                    d['plan_name'] = new_plan_name #Update plan name because B1 plan will either be added to existing Stereo Poumon or else will be called B1
                    
                    if isodose_creation:
                        self.Status.Text = "En cours: Reglage du Dose Color Table"
                        poumon.poumon_stereo_create_isodose_lines(plan_data=d)
                    
                    if d['treatment_technique']=='VMAT':
                        self.Status.Text = "En cours: Ajout des faisceaux"
                        beams.add_beams_lung_stereo(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], examination=d['exam'], ptv_name=d['ptv'].Name, two_arcs=d['two_arcs'])                    
                        
                    if d['treatment_technique']=='SMLC':
                        self.Status.Text = "En cours: Ajout des faisceaux"
                        beams.add_beams_imrt_lung_stereo(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']],examination=d['exam'], ptv_name=d['ptv'].Name)                    
                        
                    self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                    poumon.poumon_stereo_opt_settings(plan_data = d)
                        
                    self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                    clinical_goals.smart_cg_lung_stereo(plan=patient.TreatmentPlans[d['plan_name']], examination=d['exam'], nb_fx=nb_fx, rx_dose=rx_dose, ptv=d['ptv'], beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']])              
                            
                    
                    
                    # Double optimization if requested by user                 
                    if self.check1.Checked:
                        if new_plan_name == 'B1': #This indicates a new plan was made (because old one was locked) which only has one beamset, so we need to set plan_opt to 0
                            plan_opt = 0
                        self.Status.Text = "Première optimization en cours"
                        patient.TreatmentPlans[d['plan_name']].PlanOptimizations[plan_opt].RunOptimization()
                        self.Status.Text = "Deuxième optimization en cours"
                        patient.TreatmentPlans[d['plan_name']].PlanOptimizations[plan_opt].RunOptimization()
                    

                # ADD SECOND PLAN USING NEW TECHNIQUE
                if add_kbp_plan:
                    self.Status.Text = "Test: Vérification des OARs"
                    oar_list,laterality = poumon.poumon_stereo_kbp_identify_rois(plan_data=d)
                    self.Status.Text = "Test: Ajout du plan et beamset test"                    
                    poumon.poumon_stereo_kbp_add_plan_and_beamset(plan_data=d,laterality=laterality)
                    self.Status.Text = "Test: Configuration des paramêtres d'optimisation"
                    poumon.poumon_stereo_kbp_opt_settings(plan_data=d)
                    self.Status.Text = "Test: Création et optimisation du plan inital"
                    poumon.poumon_stereo_kbp_initial_plan(plan_data=d,oar_list=oar_list)
                    self.Status.Text = "Test: Modification des objectifs d'optimisation"
                    poumon.poumon_stereo_kbp_modify_plan(plan_data=d,oar_list=oar_list)
                    self.Status.Text = "Test: Optimisation du plan modifié"
                    poumon.poumon_stereo_kbp_iterate_plan(plan_data=d,oar_list=oar_list)
                    self.Status.Text = "Test: Impression des resultats"
                    poumon.poumon_stereo_kbp_evaluate_plan(plan_data=d,oar_list=oar_list)

                
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   
                
                
            elif self.sitecombo.Text == 'Foie':
            
                d = dict(patient = patient,
                         plan_name = 'Stereo Foie',
                         beamset_name = 'Stereo',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest[self.Label2.Text.split()[0]],
                         treatment_technique = treatment_technique)     
                
                
                         
                self.Status.ForeColor = Color.Black
                
                if patient.BodySite == '':
                    patient.BodySite = 'Foie'                
                
                self.Status.Text = "En cours: Gestion des POIs"
                poi.create_iso(exam = d['exam'])
                poi.auto_assign_poi_types()
                poi.erase_pois_not_in_list()
                
                self.Status.Text = "En cours: Création des ROIs"
                roi.auto_assign_roi_types_v2()
                roi.generate_BodyRS_plus_Table()
                foie.foie_stereo_rois(plan_data = d)

                self.Status.Text = "En cours: Ajout du plan et beamset"
                foie.foie_stereo_add_plan_and_beamset(plan_data = d)
                
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    foie.foie_stereo_create_isodose_lines(plan_data = d)

                self.Status.Text = "En cours: Ajout des faisceaux"     
                if d['treatment_technique']=='VMAT':
                    beams.add_beams_prostate_A1(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], site_name=d['site_name'])
                if d['treatment_technique']=='SMLC':
                    beams.add_beams_brain_static(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']],site_name=d['site_name'],iso_name='ISO', exam=d['exam'], nb_beams = 9)
                
                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                foie.foie_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                clinical_goals.smart_cg_foie_sbrt(plan=patient.TreatmentPlans[d['plan_name']], ptv=d['ptv'], Rx_dose=d['rx_dose']/100.0)
                

                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "Première optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Deuxième optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   

                
            elif self.sitecombo.Text == 'Vertebre':
                
                d = dict(patient = patient,
                         plan_name = 'Stereo Vertebre',
                         beamset_name = 'Stereo',
                         site_name = self.SiteBox.Text,
                         exam = patient.Examinations[self.scancombo.Text],
                         machine = machine,
                         nb_fx = nb_fx,
                         rx_dose = rx_dose,
                         ptv = patient.PatientModel.RegionsOfInterest['PTV18'],
                         treatment_technique = treatment_technique)     
                        
                
                self.Status.ForeColor = Color.Black
                
                if patient.BodySite == '':
                    patient.BodySite = 'Vertebre'                
                
                self.Status.Text = "En cours: Gestion des POIs"
                poi.create_iso(exam = d['exam'])
                poi.auto_assign_poi_types()
                poi.erase_pois_not_in_list()
                
                self.Status.Text = "En cours: Création des ROIs"
                roi.auto_assign_roi_types_v2()
                roi.generate_BodyRS_plus_Table()
                foie.vertebre_stereo_rois(plan_data = d)

                self.Status.Text = "En cours: Ajout du plan et beamset"
                foie.foie_stereo_add_plan_and_beamset(plan_data = d) #OK to use same function as for liver cases
                
                if isodose_creation:
                    self.Status.Text = "En cours: Reglage du Dose Color Table"
                    foie.vertebre_stereo_create_isodose_lines(plan_data = d)

                self.Status.Text = "En cours: Ajout des faisceaux"     
                beams.add_beams_vertebre_stereo(beamset=patient.TreatmentPlans[d['plan_name']].BeamSets[d['beamset_name']], site_name=d['site_name'])
                
                self.Status.Text = "En cours: Reglage des paramètres d'optimisation"
                foie.vertebre_stereo_opt_settings(plan_data = d)
                
                self.Status.Text = "En cours: Ajout des objectifs d'optimisation et les clinical goals"
                clinical_goals.smart_cg_vertebre(plan=patient.TreatmentPlans[d['plan_name']])
              
                self.Status.Text = "En cours: Changement du nom du PTV"
                crane.crane_stereo_rename_ptv(plan_data = d) #OK to borrow from crâne
              
                

                # Double optimization if requested by user    
                if self.check1.Checked:
                    self.Status.Text = "Première optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Deuxième optimization en cours"
                    patient.TreatmentPlans[d['plan_name']].PlanOptimizations[0].RunOptimization()
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green   
                    
                    
                    
            else:
                self.Status.Text = "Le site n'a pas été sélectionné!"                
                self.Status.ForeColor = Color.Red

        def cancelClicked(self, sender, args):
            self.Close()

        def setupMachineSelectPanel(self):
            self.MachineSelectPanel = self.miniPanel(0, 350)
            
            self.MachineLabel = Label()
            self.MachineLabel.Text = "Appareil de traitement:"
            self.MachineLabel.Location = Point(25, 30)
            self.MachineLabel.Font = Font("Arial", 10)
            self.MachineLabel.AutoSize = True

            self.BeamModButton = RadioButton()
            self.BeamModButton.Text = "BeamMod (salles 11-12)"
            self.BeamModButton.Location = Point(40, 55)
            self.BeamModButton.Checked = True
            self.BeamModButton.AutoSize = True
            
            self.InfinityButton = RadioButton()
            self.InfinityButton.Text = "Infinity (salles 1-2-6)"
            self.InfinityButton.Location = Point(40, 80)
            self.InfinityButton.Checked = False 
            self.InfinityButton.AutoSize = True            

            self.MachineSelectPanel.Controls.Add(self.MachineLabel)
            self.MachineSelectPanel.Controls.Add(self.BeamModButton)
            self.MachineSelectPanel.Controls.Add(self.InfinityButton)            
            
            
        def setupOKButtons(self):
            self.OKbuttonPanel = self.newPanel(0, 455)

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
            
            if roi.roi_exists('CERVEAU'):
                self.sitecombo.Text = 'Crâne'
            elif roi.roi_exists('PROSTATE'):
                self.sitecombo.Text = 'Prostate'   
            elif roi.roi_exists('ITV48') or roi.roi_exists('ITV54') or roi.roi_exists('ITV56') or roi.roi_exists('ITV60'):
                self.sitecombo.Text = 'Poumon'
            elif roi.roi_exists('FOIE EXPI'):
                self.sitecombo.Text = 'Foie'                   

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
        message.message_window('Aucun patient sélectionné')
        return      
        
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = ScriptLauncher()
    Application.Run(form)     
   
    
