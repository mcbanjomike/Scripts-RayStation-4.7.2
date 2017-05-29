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
#import hmrlib.gui as gui
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

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

 
def plan_launcher_v3():

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
        debug_window('Aucun patient sélectionné')
        return      
        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
        
    form = ScriptLauncher()
    Application.Run(form)     
   

def debug_window(input = "Everything's fine"):

    class DebugWindow(Form):
        def __init__(self):
            self.Text = "Erreur"

            self.Width = 750
            self.Height = 750

            self.setupMessageWindow()
            self.setupOKButtons()

            self.Controls.Add(self.MessageWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def bigPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 600
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 150
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupMessageWindow(self):
            self.MessageWindow = self.bigPanel(0, 0)

            self.Label1 = Label()
            self.Label1.Text = input
            self.Label1.Location = Point(25, 25)
            self.Label1.Font = Font("Arial", 10)
            self.Label1.AutoSize = True
            
            self.MessageWindow.Controls.Add(self.Label1)

        def cancelClicked(self, sender, args):
            self.Close()

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 600)
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(25,25)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked

            self.OKbuttonPanel.Controls.Add(cancelButton)


    form = DebugWindow()
    Application.Run(form)   

    
def final_launcher():

    class FinalisationWindow(Form):
        def __init__(self):
            self.Text = "Finalisation des plans RayStation version 1.0"

            self.Width = 900
            self.Height = 780

            self.setupHeaderWindow()
            self.setupBeamset1Window()
            self.setupBeamset2Window()
            self.setupBeamset3Window()
            self.setupOKButtons()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.Beamset1Window)
            self.Controls.Add(self.Beamset2Window)
            self.Controls.Add(self.Beamset3Window)
            self.Controls.Add(self.OKbuttonPanel)
            
        def beamsetPanel(self, x, y):
            panel = Panel()
            panel.Width = 300
            panel.Height = 600
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.FixedSingle
            return panel

        def medPanel(self, x, y):
            panel = Panel()
            panel.Width = 300
            panel.Height = 300
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.FixedSingle
            return panel            
            
        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 900
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
            
        def setupBeamset1Window(self):
            self.Beamset1Window = self.beamsetPanel(0, 60)
            
            vert_spacer = 30
            offset = 28

            self.beamset1Header = Label()
            self.beamset1Header.Text = "Beamset 1"
            self.beamset1Header.Location = Point(25, 25)
            self.beamset1Header.Font = Font("Arial", 11, FontStyle.Bold)
            self.beamset1Header.AutoSize = True      
            
            self.Label1 = Label()
            self.Label1.Text = "Beamset:"
            self.Label1.Location = Point(25, vert_spacer + offset)
            self.Label1.Font = Font("Arial", 10)
            self.Label1.AutoSize = True
         
            self.beamset1combo = ComboBox()
            self.beamset1combo.Parent = self
            self.beamset1combo.Size = Size(120,40)
            self.beamset1combo.Location = Point(100,vert_spacer + offset)
            self.beamset1combo.Text = "Choisissez beamset"
            self.beamset1combo.TextChanged += self.beamset1selectionChanged

            self.Label2 = Label()
            self.Label2.Text = "Site:"
            self.Label2.Location = Point(25, 2*vert_spacer + offset)
            self.Label2.Font = Font("Arial", 10)
            self.Label2.AutoSize = True
            
            self.site1combo = ComboBox()
            self.site1combo.Parent = self
            self.site1combo.Size = Size(120,40)
            self.site1combo.Location = Point(100, 2*vert_spacer + offset)
            self.site1combo.Items.Add("Prostate")
            self.site1combo.Items.Add("Poumon")     
            self.site1combo.Items.Add("Crâne")
            self.site1combo.Items.Add("Foie")                 
            self.site1combo.Items.Add("Vertebre")              
            self.site1combo.Text = "Choisissez site"
            self.site1combo.TextChanged += self.site1selectionChanged
            
            self.Label3 = Label()
            self.Label3.Text = "Gy en"
            self.Label3.Location = Point(70, 3*vert_spacer + offset)
            self.Label3.Font = Font("Arial", 10)
            self.Label3.AutoSize = True        

            self.Label4 = Label()
            self.Label4.Text = "fractions"
            self.Label4.Location = Point(160, 3*vert_spacer + offset)
            self.Label4.Font = Font("Arial", 10)
            self.Label4.AutoSize = True               

            self.dosebox = TextBox()
            self.dosebox.Text = "----"
            self.dosebox.Location = Point(25, 3*vert_spacer + offset)
            self.dosebox.Width = 40
            
            self.fxbox = TextBox()
            self.fxbox.Text = "----"
            self.fxbox.Location = Point(115, 3*vert_spacer + offset)
            self.fxbox.Width = 40            
            
            self.Label5 = Label()
            self.Label5.Text = "Nom du PTV: "
            self.Label5.Location = Point(25, 4.75*vert_spacer + offset)
            self.Label5.Font = Font("Arial", 10)
            self.Label5.AutoSize = True                    

            self.Label6 = Label()
            self.Label6.Text = "Contour isodose: "
            self.Label6.Location = Point(25, 5.5*vert_spacer + offset)
            self.Label6.Font = Font("Arial", 10)
            self.Label6.AutoSize = True     

            self.Label7 = Label()
            self.Label7.Text = "Nom final du beamset: "
            self.Label7.Location = Point(25, 6.25*vert_spacer + offset)
            self.Label7.Font = Font("Arial", 10)
            self.Label7.AutoSize = True     
            
            self.Label8 = Label()
            self.Label8.Text = "OARs pour transfert SuperBridge: "
            self.Label8.Location = Point(25, 8*vert_spacer + offset)
            self.Label8.Font = Font("Arial", 10)
            self.Label8.AutoSize = True                 
            
            self.Beamset1Window.Controls.Add(self.beamset1Header)
            self.Beamset1Window.Controls.Add(self.Label1)
            self.Beamset1Window.Controls.Add(self.beamset1combo)
            self.Beamset1Window.Controls.Add(self.Label2)
            self.Beamset1Window.Controls.Add(self.site1combo)
            self.Beamset1Window.Controls.Add(self.Label3)            
            self.Beamset1Window.Controls.Add(self.Label4)                 
            self.Beamset1Window.Controls.Add(self.dosebox)
            self.Beamset1Window.Controls.Add(self.fxbox)    
            self.Beamset1Window.Controls.Add(self.Label5)            
            self.Beamset1Window.Controls.Add(self.Label6)              
            self.Beamset1Window.Controls.Add(self.Label7)    
            self.Beamset1Window.Controls.Add(self.Label8)                
            
        def setupBeamset2Window(self):
            self.Beamset2Window = self.medPanel(300, 60)
            
            vert_spacer = 30
            offset = 28

            self.Beamset2Header = Label()
            self.Beamset2Header.Text = "Beamset 2"
            self.Beamset2Header.Location = Point(25, 25)
            self.Beamset2Header.Font = Font("Arial", 11, FontStyle.Bold)
            self.Beamset2Header.AutoSize = True      
            
            self.Label21 = Label()
            self.Label21.Text = "Beamset:"
            self.Label21.Location = Point(25, vert_spacer + offset)
            self.Label21.Font = Font("Arial", 10)
            self.Label21.AutoSize = True
         
            self.beamset2combo = ComboBox()
            self.beamset2combo.Parent = self
            self.beamset2combo.Size = Size(120,40)
            self.beamset2combo.Location = Point(100,vert_spacer + offset)
            self.beamset2combo.Text = "Choisissez beamset"
            self.beamset2combo.TextChanged += self.beamset2selectionChanged

            self.Label22 = Label()
            self.Label22.Text = "Site:" # Site for Beamset2 is copied from Beamset1
            self.Label22.Location = Point(25, 2*vert_spacer + offset)
            self.Label22.Font = Font("Arial", 10)
            self.Label22.AutoSize = True
            
            self.Label23 = Label()
            self.Label23.Text = "Gy en"
            self.Label23.Location = Point(70, 3*vert_spacer + offset)
            self.Label23.Font = Font("Arial", 10)
            self.Label23.AutoSize = True        

            self.Label24 = Label()
            self.Label24.Text = "fractions"
            self.Label24.Location = Point(160, 3*vert_spacer + offset)
            self.Label24.Font = Font("Arial", 10)
            self.Label24.AutoSize = True               

            self.dosebox2 = TextBox()
            self.dosebox2.Text = "----"
            self.dosebox2.Location = Point(25, 3*vert_spacer + offset)
            self.dosebox2.Width = 40
            
            self.fxbox2 = TextBox()
            self.fxbox2.Text = "----"
            self.fxbox2.Location = Point(115, 3*vert_spacer + offset)
            self.fxbox2.Width = 40            
            
            self.Label25 = Label()
            self.Label25.Text = "Nom du PTV: "
            self.Label25.Location = Point(25, 4.75*vert_spacer + offset)
            self.Label25.Font = Font("Arial", 10)
            self.Label25.AutoSize = True                    

            self.Label26 = Label()
            self.Label26.Text = "Contour isodose: "
            self.Label26.Location = Point(25, 5.5*vert_spacer + offset)
            self.Label26.Font = Font("Arial", 10)
            self.Label26.AutoSize = True     

            self.Label27 = Label()
            self.Label27.Text = "Nom final du beamset: "
            self.Label27.Location = Point(25, 6.25*vert_spacer + offset)
            self.Label27.Font = Font("Arial", 10)
            self.Label27.AutoSize = True     

            self.Beamset2Window.Controls.Add(self.Beamset2Header)
            self.Beamset2Window.Controls.Add(self.Label21)
            self.Beamset2Window.Controls.Add(self.beamset2combo)
            self.Beamset2Window.Controls.Add(self.Label22)
            self.Beamset2Window.Controls.Add(self.Label23)            
            self.Beamset2Window.Controls.Add(self.Label24)                 
            self.Beamset2Window.Controls.Add(self.dosebox2)
            self.Beamset2Window.Controls.Add(self.fxbox2)    
            self.Beamset2Window.Controls.Add(self.Label25)            
            self.Beamset2Window.Controls.Add(self.Label26)              
            self.Beamset2Window.Controls.Add(self.Label27)    
                  
        def setupBeamset3Window(self):
            self.Beamset3Window = self.medPanel(300, 360)
            
            vert_spacer = 30
            offset = 28

            self.Beamset3Header = Label()
            self.Beamset3Header.Text = "Beamset 3"
            self.Beamset3Header.Location = Point(25, 25)
            self.Beamset3Header.Font = Font("Arial", 11, FontStyle.Bold)
            self.Beamset3Header.AutoSize = True      
            
            self.Label31 = Label()
            self.Label31.Text = "Beamset:"
            self.Label31.Location = Point(25, vert_spacer + offset)
            self.Label31.Font = Font("Arial", 10)
            self.Label31.AutoSize = True
         
            self.beamset3combo = ComboBox()
            self.beamset3combo.Parent = self
            self.beamset3combo.Size = Size(120,40)
            self.beamset3combo.Location = Point(100,vert_spacer + offset)
            self.beamset3combo.Text = "Choisissez beamset"
            self.beamset3combo.TextChanged += self.beamset3selectionChanged

            self.Label32 = Label()
            self.Label32.Text = "Site:" # Site for Beamset3 is copied from Beamset1
            self.Label32.Location = Point(25, 2*vert_spacer + offset)
            self.Label32.Font = Font("Arial", 10)
            self.Label32.AutoSize = True
            
            self.Label33 = Label()
            self.Label33.Text = "Gy en"
            self.Label33.Location = Point(70, 3*vert_spacer + offset)
            self.Label33.Font = Font("Arial", 10)
            self.Label33.AutoSize = True        

            self.Label34 = Label()
            self.Label34.Text = "fractions"
            self.Label34.Location = Point(160, 3*vert_spacer + offset)
            self.Label34.Font = Font("Arial", 10)
            self.Label34.AutoSize = True               

            self.dosebox3 = TextBox()
            self.dosebox3.Text = "----"
            self.dosebox3.Location = Point(25, 3*vert_spacer + offset)
            self.dosebox3.Width = 40
            
            self.fxbox3 = TextBox()
            self.fxbox3.Text = "----"
            self.fxbox3.Location = Point(115, 3*vert_spacer + offset)
            self.fxbox3.Width = 40            
            
            self.Label35 = Label()
            self.Label35.Text = "Nom du PTV: "
            self.Label35.Location = Point(25, 4.75*vert_spacer + offset)
            self.Label35.Font = Font("Arial", 10)
            self.Label35.AutoSize = True                    

            self.Label36 = Label()
            self.Label36.Text = "Contour isodose: "
            self.Label36.Location = Point(25, 5.5*vert_spacer + offset)
            self.Label36.Font = Font("Arial", 10)
            self.Label36.AutoSize = True     

            self.Label37 = Label()
            self.Label37.Text = "Nom final du beamset: "
            self.Label37.Location = Point(25, 6.25*vert_spacer + offset)
            self.Label37.Font = Font("Arial", 10)
            self.Label37.AutoSize = True     

            self.Beamset3Window.Controls.Add(self.Beamset3Header)
            self.Beamset3Window.Controls.Add(self.Label31)
            self.Beamset3Window.Controls.Add(self.beamset3combo)
            self.Beamset3Window.Controls.Add(self.Label32)
            self.Beamset3Window.Controls.Add(self.Label33)            
            self.Beamset3Window.Controls.Add(self.Label34)                 
            self.Beamset3Window.Controls.Add(self.dosebox3)
            self.Beamset3Window.Controls.Add(self.fxbox3)    
            self.Beamset3Window.Controls.Add(self.Label35)            
            self.Beamset3Window.Controls.Add(self.Label36)              
            self.Beamset3Window.Controls.Add(self.Label37)    
                  
                  
        def beamset1selectionChanged(self, sender, args):
            try:
                beamset = plan.BeamSets[self.beamset1combo.Text]
            except:
                return
        
            # Attempt to determine site and prescription
            dose_scale = 100.0
            if roi.roi_exists("PROSTATE"):
                self.site1combo.Text = "Prostate"
                dose_scale = 95.0
            elif roi.roi_exists("CERVEAU"):
                self.site1combo.Text = "Crâne"                
            elif roi.roi_exists("BR SOUCHE"):
                self.site1combo.Text = "Poumon"
            elif roi.roi_exists("FOIE EXPI-GTV"):
                self.site1combo.Text = "Foie"
            try:
                self.dosebox.Text = "%.2f" % ((beamset.Prescription.PrimaryDosePrescription.DoseValue)/dose_scale)
            except:
                hello = True
            self.fxbox.Text = str(beamset.FractionationPattern.NumberOfFractions)
        
            # Determine PTV and isodose contours
            if beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtVolume':
                ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                new_beamset_name = ptv_name.split()[1]
                self.Label5.Text = "Nom du PTV:                 " + ptv_name
                if roi.roi_exists("isodose "+new_beamset_name):
                    self.Label6.Text = "Contour isodose:           isodose " + new_beamset_name
                else:
                    self.Label6.Text = "Contour isodose:           pas trouvé"
                self.Label7.Text = "Nom final du beamset:   " + new_beamset_name
            else:
                self.Label5.Text = "Nom du PTV: Rx pas sur un ROI"
                self.Label7.Text = "Nom final du beamset: impossible de continuer"                  
                
                
        def beamset2selectionChanged(self, sender, args):
            #Set text windows to default values if beamset selection is cleared
            if self.beamset2combo.Text == "Choisissez beamset":
                self.dosebox2.Text = "----"
                self.fxbox2.Text = "----"
                self.Label25.Text = "Nom du PTV: "
                self.Label26.Text = "Contour isodose: "
                self.Label27.Text = "Nom final du beamset: "
                return                
        
            try:
                beamset = plan.BeamSets[self.beamset2combo.Text]
            except:
                return
                
            self.Label22.Text = "Site: " + self.site1combo.Text #Copy directly from first beamset
        
            # Attempt to determine site and prescription
            if roi.roi_exists("PROSTATE"):
                dose_scale = 95.0
            else:
                dose_scale = 100.0
            try:
                self.dosebox2.Text = "%.2f" % ((beamset.Prescription.PrimaryDosePrescription.DoseValue)/dose_scale)
            except:
                hello = True
            self.fxbox2.Text = str(beamset.FractionationPattern.NumberOfFractions)
        
        
            # Determine PTV and isodose contours
            if beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtVolume':
                ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                new_beamset_name = ptv_name.split()[1]     
                self.Label25.Text = "Nom du PTV:                 " + ptv_name
                if roi.roi_exists("isodose "+new_beamset_name):
                    self.Label26.Text = "Contour isodose:           isodose " + new_beamset_name
                else:
                    self.Label26.Text = "Contour isodose:           pas trouvé"
                self.Label27.Text = "Nom final du beamset:   " + new_beamset_name
            else:
                self.Label25.Text = "Nom du PTV: Rx pas sur un ROI"
                self.Label27.Text = "Nom final du beamset: impossible de continuer"                             
                    
                    
        def beamset3selectionChanged(self, sender, args):
            #Set text windows to default values if beamset selection is cleared
            if self.beamset3combo.Text == "Choisissez beamset":
                self.dosebox3.Text = "----"
                self.fxbox3.Text = "----"
                self.Label35.Text = "Nom du PTV: "
                self.Label36.Text = "Contour isodose: "
                self.Label37.Text = "Nom final du beamset: "
                return                
        
            try:
                beamset = plan.BeamSets[self.beamset3combo.Text]
            except:
                return
                
            self.Label32.Text = "Site: " + self.site1combo.Text #Copy directly from first beamset
        
            # Attempt to determine site and prescription
            if roi.roi_exists("PROSTATE"):
                dose_scale = 95.0
            else:
                dose_scale = 100.0
            try:
                self.dosebox3.Text = "%.2f" % ((beamset.Prescription.PrimaryDosePrescription.DoseValue)/dose_scale)
            except:
                hello = True
            self.fxbox3.Text = str(beamset.FractionationPattern.NumberOfFractions)
        
        
            # Determine PTV and isodose contours
            if beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtVolume':
                ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                new_beamset_name = ptv_name.split()[1]     
                self.Label35.Text = "Nom du PTV:                 " + ptv_name
                if roi.roi_exists("isodose "+new_beamset_name):
                    self.Label36.Text = "Contour isodose:           isodose " + new_beamset_name
                else:
                    self.Label36.Text = "Contour isodose:           pas trouvé"
                self.Label37.Text = "Nom final du beamset:   " + new_beamset_name
            else:
                self.Label35.Text = "Nom du PTV: Rx pas sur un ROI"
                self.Label37.Text = "Nom final du beamset: impossible de continuer"      
                    
                    
        def site1selectionChanged(self, sender, args):
            site_list = ["Prostate","Poumon","Crâne","Foie","Vertebre"]
            if self.site1combo.Text in site_list:
                roi_list = check_rois(self.site1combo.Text)     
            else:
                return

            found_rois = ""
            for roi in patient.PatientModel.RegionsOfInterest:
                if roi.Name in roi_list:
                    found_rois += "\n    " + roi.Name     
            self.Label8.Text = "OARs pour transfert SuperBridge: " + found_rois
            
            if self.beamset2combo.Text != "Choisissez beamset":
                self.Label22.Text = "Site: " + self.site1combo.Text #Copy from first beamset
            if self.beamset3combo.Text != "Choisissez beamset":
                self.Label32.Text = "Site: " + self.site1combo.Text #Copy from first beamset
            
            
        def cancelClicked(self, sender, args):
            self.Close()
            
        def okClicked(self, sender, args):
            #Check for errors
            site_list = ["Prostate","Poumon","Crâne","Foie","Vertebre"]                
            self.message.ForeColor = Color.Black
            error_text = None
            
            if self.beamset1combo.Text == "Choisissez beamset":
                error_text = "Aucun beamset choisi pour Beamset1"        
            elif self.beamset1combo.Text == self.beamset2combo.Text or self.beamset1combo.Text == self.beamset3combo.Text:
                error_text = "Même beamset choisi deux fois"
            elif self.beamset2combo.Text == self.beamset3combo.Text and self.beamset2combo.Text != "Choisissez beamset":
                error_text = "Même beamset choisi pour Beamset 2 et Beamset 3"

            elif self.site1combo.Text == "Choisissez site":
                error_text = "Il faut indiquer le site"
            elif self.site1combo.Text not in site_list:
                error_text = "Le site indiqué n'est pas supporté"

            elif "Rx pas sur un ROI" in self.Label5.Text:
                error_text = "Impossible d'identifier PTV pour Beamset 1"
            elif self.beamset2combo.Text != "Choisissez beamset" and "Rx pas sur un ROI" in self.Label25.Text:
                error_text = "Impossible d'identifier PTV pour Beamset 2"       
            elif self.beamset3combo.Text != "Choisissez beamset" and "Rx pas sur un ROI" in self.Label35.Text:
                error_text = "Impossible d'identifier PTV pour Beamset 3"      
                
            elif "pas trouvé" in self.Label6.Text:
                error_text = "Contour isodose pas trouvé pour Beamset 1"
            elif self.beamset2combo.Text != "Choisissez beamset" and "pas trouvé" in self.Label26.Text:
                error_text = "Contour isodose pas trouvé pour Beamset 2"       
            elif self.beamset3combo.Text != "Choisissez beamset" and "pas trouvé" in self.Label36.Text:
                error_text = "Contour isodose pas trouvé pour Beamset 3"              
                
            elif self.dosebox.Text == "----":
                error_text = "Dose pas définie pour Beamset 1"            
            elif self.dosebox2.Text == "----" and self.beamset2combo.Text != "Choisissez beamset":
                error_text = "Dose pas définie pour Beamset 2"
            elif self.dosebox3.Text == "----" and self.beamset3combo.Text != "Choisissez beamset":
                error_text = "Dose pas définie pour Beamset 3"        

            elif self.fxbox.Text == "----":
                error_text = "Dose pas définie pour Beamset 1"            
            elif self.fxbox2.Text == "----" and self.beamset2combo.Text != "Choisissez beamset":
                error_text = "Nombre de fx pas définie pour Beamset 2"
            elif self.fxbox3.Text == "----" and self.beamset3combo.Text != "Choisissez beamset":
                error_text = "Nombre de fx pas définie pour Beamset 3"             

            try:
                temp = float(self.dosebox.Text)
            except:
                error_text = "Dose de prescription indiquée pour Beamset 1 n'est pas un chiffre"
            if self.beamset2combo.Text != "Choisissez beamset":
                try:
                    temp = float(self.dosebox2.Text)
                except:
                    error_text = "Dose de prescription indiquée pour Beamset 2 n'est pas un chiffre"          
            if self.beamset3combo.Text != "Choisissez beamset":
                try:
                    temp = float(self.dosebox3.Text)
                except:
                    error_text = "Dose de prescription indiquée pour Beamset 3 n'est pas un chiffre"          

            try:
                temp = int(self.fxbox.Text)
            except:
                error_text = "Nombre de fractions pour Beamset 1 n'est pas un chiffre"
            if self.beamset2combo.Text != "Choisissez beamset":
                try:
                    temp = int(self.fxbox2.Text)
                except:
                    error_text = "Nombre de fractions pour Beamset 2 n'est pas un chiffre"          
            if self.beamset3combo.Text != "Choisissez beamset":
                try:
                    temp = int(self.fxbox3.Text)
                except:
                    error_text = "Nombre de fractions pour Beamset 3 n'est pas un chiffre"         

            if self.message.Text == "Finalisation terminée" or self.message.Text == "La finalisation est déjà terminée! Cliquez sur Annuler.":
                error_text = "La finalisation est déjà terminée! Cliquez sur Annuler."
                    
                    
            if error_text != None:
                self.message.Text = error_text
                self.message.ForeColor = Color.Red
                return       
        
            beamset_name = self.beamset1combo.Text
            beamset = plan.BeamSets[beamset_name]
            rx_dose = float(self.dosebox.Text)
            nb_fx = int(self.fxbox.Text)
            site = self.site1combo.Text
            ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
            
            #Finalize one or more beamsets
            self.message.Text = "Finalisation du beamset %s en cours" % beamset_name
            result_text = finalize_beamset(beamset_name, rx_dose, nb_fx, site, ptv_name, color="Red")
            if "Impossible" in result_text: #Dose max too low to place PT PRESC
                self.message.Text = result_text
                self.message.ForeColor = Color.Red
                return       
            if self.beamset2combo.Text != "Choisissez beamset":
                beamset_name = self.beamset2combo.Text
                beamset = plan.BeamSets[beamset_name]
                rx_dose = float(self.dosebox2.Text)
                nb_fx = int(self.fxbox2.Text)
                site = self.site1combo.Text         
                ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                self.message.Text = "Finalisation du beamset %s en cours" % beamset_name
                result_text = finalize_beamset(beamset_name, rx_dose, nb_fx, site, ptv_name, color="Green", skip_oars = True)
                if "Impossible" in result_text: #Dose max too low to place PT PRESC
                    self.message.Text = result_text
                    self.message.ForeColor = Color.Red
                    return    
            if self.beamset3combo.Text != "Choisissez beamset":
                beamset_name = self.beamset3combo.Text
                beamset = plan.BeamSets[beamset_name]
                rx_dose = float(self.dosebox3.Text)
                nb_fx = int(self.fxbox3.Text)
                site = self.site1combo.Text     
                ptv_name = beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                self.message.Text = "Finalisation du beamset %s en cours" % beamset_name
                result_text = finalize_beamset(beamset_name, rx_dose, nb_fx, site, ptv_name, color="Skyblue", skip_oars = True)
                if "Impossible" in result_text: #Dose max too low to place PT PRESC
                    self.message.Text = result_text
                    self.message.ForeColor = Color.Red
                    return                    
            if result_text == "PTV en voxels":
                self.message.Text = "PTV doit être en contours (pas en voxels).\nUtiliser l'outil Simplify Contours pour le convertir et reessayer."
                self.message.ForeColor = Color.Red
            else:
                self.message.Text = "Finalisation terminée"
                self.message.ForeColor = Color.Green

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 660)
            
            okButton = Button()
            okButton.Text = "Finaliser"
            okButton.Location = Point(100, 25)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(200,25)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(300, 28)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(okButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
            self.OKbuttonPanel.Controls.Add(self.message)
           
            #Automatically populate beamset selection comboboxes
            self.beamset2combo.Items.Add("Choisissez beamset")
            self.beamset3combo.Items.Add("Choisissez beamset")            
            num_beamsets = 0
            for bs in plan.BeamSets:
                num_beamsets += 1            
                self.beamset1combo.Items.Add(bs.DicomPlanLabel)
                self.beamset2combo.Items.Add(bs.DicomPlanLabel)
                self.beamset3combo.Items.Add(bs.DicomPlanLabel)
            if num_beamsets > 0:
                self.beamset1combo.Text = plan.BeamSets[0].DicomPlanLabel
            if num_beamsets > 1:
                self.beamset2combo.Text = plan.BeamSets[1].DicomPlanLabel
            if num_beamsets > 2:
                self.beamset3combo.Text = plan.BeamSets[2].DicomPlanLabel

    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return  
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
                
    form = FinalisationWindow()
    Application.Run(form)   


def check_rois(site = None):
    patient = lib.get_current_patient()

    if site == "Prostate":
        roi_list = ["RECTUM", "VESSIE", "INTESTINS", "RECTO-SIGMOIDE", "PROSTATE","Bladder","Rectum","Bowel"]
    elif site == "Crâne":
        roi_list = ["MOELLE", "TR CEREBRAL", "OEIL DRT", "OEIL GCHE"]
    elif site == "Poumon":
        roi_list = ["GTV EXPI", "GTV expi", "GTV EXPI A1", "GTV expi A1", "GTV EXPI B1", "GTV expi B1", "MOELLE"]
    elif site == "Foie":            
        roi_list = ["GTV EXPI", "FOIE INSPI", "FOIE EXPI", "MOELLE", "REINS", "OESOPHAGE", "ESTOMAC", "DUODENUM", "COLON", "GRELE"]
    elif site == "Vertebre":            
        roi_list = []
    else:
        return
    
    return roi_list

 
def finalize_beamset(original_beamset_name, rx_dose, nb_fx, site, ptv_name, color, skip_oars = False):
    #Note that I tried to pass the beamset and ptv objects directly into this function, but that seems to cause crashing, so now I pass strings instead.
    patient = lib.get_current_patient()
    plan = lib.get_current_plan()
    
    bs = plan.BeamSets[original_beamset_name]
    ptv = patient.PatientModel.RegionsOfInterest[ptv_name]
    beamset_name = ptv_name.split()[1]
    scan_name = "CT 1" 

    if site == 'Crâne':
        try:
            statistics.stereo_brain_statistics()
        except:
            file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\crane.txt'
            output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + bs.DicomPlanLabel + ',' + 'Collecte de statistiques échouée'
            with open(file_path, 'a') as stat_file:
                stat_file.write(output + '\n')
    elif site == 'Poumon':
        try:
            statistics.stereo_lung_statistics()
        except:
            file_path = r'\\radonc.hmr\Departements\Physiciens\Clinique\IMRT\Statistiques\poumon.txt'
            output = patient.PatientName + ',' + patient.PatientID + ',' + plan.Name + ',' + bs.DicomPlanLabel + ',' + 'Collecte de statistiques échouée'
            with open(file_path, 'a') as stat_file:
                stat_file.write(output + '\n')
                
    #Check to see if PTV is drawn using contours (since prescription point placement will fail if the PTV is in voxel format)
    try:
        temp = patient.PatientModel.StructureSets[scan_name].RoiGeometries[ptv_name].PrimaryShape.Contours[0]
    except:
        return "PTV en voxels"    
        
    #Check to see if prescription dose exists in patient (otherwise it is impossible to place PT PRESC correctly)    
    rx_dose_vol = bs.FractionDose.GetRelativeVolumeAtDoseValues(RoiName=ptv_name, DoseValues=[rx_dose*100/nb_fx])
    if rx_dose_vol[0] == 0: #The volume in BodyRS that receives the prescription dose is 0
        return "Impossible de placer PT PRESC pour beamset " + original_beamset_name + " car \ndose max inférieure à la dose de prescription"
    
    """
    #WARNING: This script uses UI scripting. If the user switches focus to another piece of software during 
    #         execution, the UI commands will not be completed. The script will not give the desired results
    #         and may crash.
    
    # Erase setup beams
    ui = lib.get_current("ui")
    #Select the beamset using the combobox on the top right of RayStation. Note that in plans with only one beamset, this combobox does not exist! So we have to use try.
    try:
        ui.SelectionBar.ComboBox_RadiationSets.ToggleButton.Click()
        ui.SelectionBar.ComboBox_RadiationSets.Popup.ComboBoxItem[original_beamset_name].Select()
        ui.SelectionBar.ComboBox_RadiationSets.ToggleButton.Click()
    except:
        no_big_deal = True        
    ui.MenuItem[2].Button_PlanDesign.Click() #Select Plan Design tab
    try:
        ui.Workspace.TabControl['Beams'].TabItem['Setup Beams'].Select()
        for setup_beam in bs.PatientSetup.SetupBeams:
            ui.Workspace.TabControl['Beams'].Button_Delete.Click()
    except:
        no_big_deal = True    
    """
    
    if site == "Poumon":
        expi_scan = "CT 2" #Used for transfer of contours to expi scan for Mosaiq
    
    if not skip_oars:
        # Rename OAR contours for SuperBridge transfer        
        roi_list = check_rois(site) 
        if site == "Poumon": #Add ITV to transfer list and prepare to copy contours to expi scan
            itv_name = "I" + ptv_name[1:]
            roi_list.append(itv_name)
        for rois in patient.PatientModel.RegionsOfInterest:
            if rois.Name in roi_list:
                rois.Name += "*"
                if site == "Poumon":
                    patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=rois.Name)          
       
    # Rename beamset
    bs.DicomPlanLabel = beamset_name
    
    # Rename isodose ROI and add * to it and PTV
    isodose_roi = patient.PatientModel.RegionsOfInterest["isodose " + beamset_name]       
    if site == "Prostate":
        isodose_roi.Name = "ISO %s %.2fGy*" % (beamset_name, rx_dose*0.95)    
    else:
        isodose_roi.Name = "ISO %s %.2fGy*" % (beamset_name, rx_dose)
    isodose_roi.Name = isodose_roi.Name.replace('.00Gy','Gy')
    ptv.Name += '*'     
    
    # Copy PTV and isodose ROIs to second beamset for patient positioning at treatment room (lung cases only)
    if site == "Poumon":
        patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=ptv.Name)    
        patient.PatientModel.CopyRoiGeometry(SourceExamination=patient.Examinations[scan_name], TargetExamination=patient.Examinations[expi_scan], RoiName=isodose_roi.Name)    
    
    # Add comment for Superbridge transfer (except for prostate cases, since they are not measured with the ArcCheck)
    if site != "Prostate":
        bs.Prescription.Description = "VMAT"

    # Create DSP and PT PRESC
    poi_name = 'PT PRESC ' + beamset_name
    poi.create_poi({'x': 0, 'y': 0, 'z': 0}, poi_name, color=color, examination=patient.Examinations[scan_name])
    bs.CreateDoseSpecificationPoint(Name="DSP", Coordinates={ 'x': 0, 'y': 0, 'z': 0 })
   
    # Move PT PRESC to a point that receives correct dose per fraction and prescribe
    poi.place_prescription_point(target_fraction_dose=rx_dose*100/nb_fx, ptv_name=ptv.Name, poi_name=poi_name, beamset=bs, exam=patient.Examinations[scan_name])
    bs.AddDosePrescriptionToPoi(PoiName=poi_name, DoseValue=rx_dose*100)

    # Move DSP to coordinates of PT PRESC and assign to all beams
    point = poi.get_poi_coordinates(poi_name)
    dsp = [x for x in bs.DoseSpecificationPoints][0]
    dsp.Name = "DSP "+beamset_name
    dsp.Coordinates = point.value

    for beam in bs.Beams:
        beam.SetDoseSpecificationPoint(Name=dsp.Name)
    bs.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=True)  # Dose is recalculated to show beam dose at spec point (otherwise not displayed)            

    return ("You just finalized the beamset named " + bs.DicomPlanLabel)

    
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
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
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
        debug_window('Aucun patient sélectionné')
        return                    
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
        
    form = MainWindow()
    Application.Run(form)   
 
    
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
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "               Beamset: " + beamset.DicomPlanLabel
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
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
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
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "               Beamset: " + beamset.DicomPlanLabel
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
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
    try:
        temp = patient.ModificationInfo.UserName
    except:
        message.message_window('ATTENTION: Le plan a été modifié depuis la dernière sauvegarde.\n\nFermez cette fenêtre pour poursuivre avec la vérification.')
        #return
        
    form = Verif1Window()
    Application.Run(form)   
    
    
   
    
def crane_launcher():

    class CraneLauncher(Form):
        def __init__(self):
            self.Text = "Statistiques"

            self.Width = 700
            self.Height = 740

            self.setupHeaderWindow()
            self.setupMainWindow()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            
            #Automatically populate ROI selection comboboxes
            self.PTV1combo.Items.Add("Choisissez ROI")
            self.PTV2combo.Items.Add("Choisissez ROI")
            self.PTV3combo.Items.Add("Choisissez ROI")         
            for roi in patient.PatientModel.RegionsOfInterest:       
                if 'PTV' in roi.Name.upper():
                    self.PTV1combo.Items.Add(roi.Name)
                    self.PTV2combo.Items.Add(roi.Name)
                    self.PTV3combo.Items.Add(roi.Name)      
                    
            #Determine whether to add dose color table by looking for existing plans
            try:
                existing_plan = patient.TreatmentPlans[0]
                self.isodosecombo.SelectedIndex = self.isodosecombo.FindStringExact('Ne pas créer')
            except:
                self.isodosecombo.SelectedIndex = self.isodosecombo.FindStringExact('Créer')
                
            #Choose planning scan
            try:
                self.scancombo.SelectedIndex = self.scancombo.FindStringExact('CT 1')
            except:
                self.scancombo.Text = 'Sélectionnez'
            
            #Choose isocenter POI
            try:
                self.isocombo.SelectedIndex = self.isocombo.FindStringExact('ISO')
            except:
                self.isocombo.Text = 'Sélectionnez'
                
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 700
            panel.Height = 640
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 700
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
            
            self.toplabel = Label()
            self.toplabel.Text = "PTV                      Dose (Gy)"
            self.toplabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.toplabel.Location = Point(60, 20)
            self.toplabel.AutoSize = True  
                   
            self.PTV1combo = ComboBox()
            self.PTV1combo.Parent = self
            self.PTV1combo.Size = Size(120,40)
            self.PTV1combo.Location = Point(25, offset)
            self.PTV1combo.Text = "Choisissez ROI" 
     
            self.dose1_value = TextBox()
            self.dose1_value.Text = ""
            self.dose1_value.Location = Point(180, offset)
            self.dose1_value.Width = 50              

            self.PTV2combo = ComboBox()
            self.PTV2combo.Parent = self
            self.PTV2combo.Size = Size(120,40)
            self.PTV2combo.Location = Point(25, offset + vert_spacer)
            self.PTV2combo.Text = "Choisissez ROI" 

            self.dose2_value = TextBox()
            self.dose2_value.Text = ""
            self.dose2_value.Location = Point(180, offset + vert_spacer)
            self.dose2_value.Width = 50                                

            self.PTV3combo = ComboBox()
            self.PTV3combo.Parent = self
            self.PTV3combo.Size = Size(120,40)
            self.PTV3combo.Location = Point(25, offset + 2*vert_spacer)
            self.PTV3combo.Text = "Choisissez ROI" 
                      
            self.dose3_value = TextBox()
            self.dose3_value.Text = ""
            self.dose3_value.Location = Point(180, offset + 2*vert_spacer)
            self.dose3_value.Width = 50                   
         
         
            self.fxlabel = Label()
            self.fxlabel.Text = "Nb de fx"
            self.fxlabel.Location = Point(25, offset + 3.5*vert_spacer)
            self.fxlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.fxlabel.AutoSize = True              
            
            self.fxbox = TextBox()
            self.fxbox.Parent = self
            self.fxbox.Size = Size(50,40)
            self.fxbox.Location = Point(150, offset + 3.5*vert_spacer)
            self.fxbox.Text = "1"                 
            
            self.techlabel = Label()
            self.techlabel.Text = "Technique"
            self.techlabel.Location = Point(25, offset + 4.5*vert_spacer)
            self.techlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.techlabel.AutoSize = True              
            
            self.techcombo = ComboBox()
            self.techcombo.Parent = self
            self.techcombo.Size = Size(90,40)
            self.techcombo.Location = Point(150, offset + 4.5*vert_spacer)
            self.techcombo.Text = "VMAT" 
            self.techcombo.Items.Add('VMAT')
            self.techcombo.Items.Add('IMRT')
            self.techcombo.Items.Add('3DC')        
            
            self.sitelabel = Label()
            self.sitelabel.Text = "Nom du site"
            self.sitelabel.Location = Point(25, offset + 5.5*vert_spacer)
            self.sitelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.sitelabel.AutoSize = True              
            
            self.sitebox = TextBox()
            self.sitebox.Parent = self
            self.sitebox.Size = Size(50,40)
            self.sitebox.Location = Point(150, offset + 5.5*vert_spacer)
            self.sitebox.Text = "A1"    
            
            
            self.isolabel = Label()
            self.isolabel.Text = "Isocentre"
            self.isolabel.Location = Point(25, offset + 6.5*vert_spacer)
            self.isolabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.isolabel.AutoSize = True              
            
            self.isocombo = ComboBox()
            self.isocombo.Parent = self
            self.isocombo.Size = Size(90,40)
            self.isocombo.Location = Point(150, offset + 6.5*vert_spacer)
            for poi in patient.PatientModel.PointsOfInterest:
                if 'ISO' in poi.Name:
                    self.isocombo.Items.Add(poi.Name)               
            
            
            self.scanlabel = Label()
            self.scanlabel.Text = "CT de planif"
            self.scanlabel.Location = Point(25, offset + 7.5*vert_spacer)
            self.scanlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.scanlabel.AutoSize = True              
            
            self.scancombo = ComboBox()
            self.scancombo.Parent = self
            self.scancombo.Size = Size(90,40)
            self.scancombo.Location = Point(150, offset + 7.5*vert_spacer)
            for ct in patient.Examinations:
                self.scancombo.Items.Add(ct.Name)         
            
            
            self.machinelabel = Label()
            self.machinelabel.Text = "Appareil"
            self.machinelabel.Location = Point(25, offset + 8.5*vert_spacer)
            self.machinelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.machinelabel.AutoSize = True              
            
            self.machinecombo = ComboBox()
            self.machinecombo.Parent = self
            self.machinecombo.Size = Size(90,40)
            self.machinecombo.Location = Point(150, offset + 8.5*vert_spacer)
            self.machinecombo.Text = "BeamMod"                  
            self.machinecombo.Items.Add('BeamMod')
            self.machinecombo.Items.Add('Infinity')
            

            self.isodoselabel = Label()
            self.isodoselabel.Text = "Dose table"
            self.isodoselabel.Location = Point(25, offset + 9.5*vert_spacer)
            self.isodoselabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.isodoselabel.AutoSize = True              
            
            self.isodosecombo = ComboBox()
            self.isodosecombo.Parent = self
            self.isodosecombo.Size = Size(90,40)
            self.isodosecombo.Location = Point(150, offset + 9.5*vert_spacer)
            self.isodosecombo.Text = "Créer"                  
            self.isodosecombo.Items.Add('Créer')            
            self.isodosecombo.Items.Add('Ne pas créer')            


            self.couchlabel = Label()
            self.couchlabel.Text = "Couch table"
            self.couchlabel.Location = Point(25, offset + 10.5*vert_spacer)
            self.couchlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.couchlabel.AutoSize = True              
            
            self.couchcombo = ComboBox()
            self.couchcombo.Parent = self
            self.couchcombo.Size = Size(90,40)
            self.couchcombo.Location = Point(150, offset + 10.5*vert_spacer)
            self.couchcombo.Text = "Ne pas ajouter"                  
            self.couchcombo.Items.Add('Ne pas ajouter')            
            self.couchcombo.Items.Add('Ajouter')                  

            
            self.message = Label()
            self.message.Text = "Sélectionnez le(s) ROI(s) à traiter (chaque\ncontour distinct devrait être indiqué\nséparément). Seulement les ROIs avec\nPTV dans leurs noms sont disponibles.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nLes plans IMRT/3DC avec plusieurs PTVs\ndistincts auront une optimisation automatique\nde la collimateur. SVP touchez pas à\nl'ordinateur pendant cette optimisation\n(4 à 5 minutes environ)"
            self.message.Location = Point(300, offset)
            self.message.Font = Font("Arial", 11, FontStyle.Italic)
            self.message.AutoSize = True                
            
            self.status = Label()
            self.status.Text = ""
            self.status.Location = Point(25, 600)
            self.status.Font = Font("Arial", 11, FontStyle.Bold)
            self.status.AutoSize = True    
            
            
            evalButton = Button()
            evalButton.Text = "Évaluer les PTVs"
            evalButton.Location = Point(25, offset + 13 * vert_spacer)
            evalButton.Width = 200
            evalButton.Click += self.evalClicked                           
            
            addplanButton = Button()
            addplanButton.Text = "Ajouter plan"
            addplanButton.Location = Point(25, offset + 14 * vert_spacer)
            addplanButton.Width = 200
            addplanButton.Click += self.addplanClicked   

            
            self.MainWindow.Controls.Add(self.toplabel)
            
            self.MainWindow.Controls.Add(self.PTV1combo)
            self.MainWindow.Controls.Add(self.dose1_value)
            self.MainWindow.Controls.Add(self.PTV2combo)
            self.MainWindow.Controls.Add(self.dose2_value)
            self.MainWindow.Controls.Add(self.PTV3combo)
            self.MainWindow.Controls.Add(self.dose3_value)          

            self.MainWindow.Controls.Add(self.fxlabel)
            self.MainWindow.Controls.Add(self.fxbox)   
            
            self.MainWindow.Controls.Add(self.techlabel)          
            self.MainWindow.Controls.Add(self.techcombo)          
         
            self.MainWindow.Controls.Add(self.sitelabel)
            self.MainWindow.Controls.Add(self.sitebox)            

            self.MainWindow.Controls.Add(self.isolabel)
            self.MainWindow.Controls.Add(self.isocombo) 
            
            self.MainWindow.Controls.Add(self.scanlabel)          
            self.MainWindow.Controls.Add(self.scancombo)    
            
            self.MainWindow.Controls.Add(self.machinelabel)          
            self.MainWindow.Controls.Add(self.machinecombo)          

            self.MainWindow.Controls.Add(self.isodoselabel)          
            self.MainWindow.Controls.Add(self.isodosecombo)     

            self.MainWindow.Controls.Add(self.couchlabel)          
            self.MainWindow.Controls.Add(self.couchcombo)             
            
            self.MainWindow.Controls.Add(self.message)            
            self.MainWindow.Controls.Add(self.status)     

            self.MainWindow.Controls.Add(evalButton)
            self.MainWindow.Controls.Add(addplanButton)            

            
        def compile_plan_data(self):            
                               
            self.status.Text = "Compilation des données du plan"      
            
            ptv_names = []
            rx = []            
            error_message = ""
            
            if roi.roi_exists(self.PTV1combo.Text):       
                ptv_names.append(self.PTV1combo.Text)
                try:
                    rx.append(int(float(self.dose1_value.Text) * 100))
                except:
                    error_message = "Dose du PTV 1 illisible"                    

            if roi.roi_exists(self.PTV2combo.Text):       
                ptv_names.append(self.PTV2combo.Text)
                try:
                    rx.append(int(float(self.dose2_value.Text) * 100))
                except:
                    error_message = "Dose du PTV 2 illisible"

            if roi.roi_exists(self.PTV3combo.Text):       
                ptv_names.append(self.PTV3combo.Text)
                try:
                    rx.append(int(float(self.dose3_value.Text) * 100))
                except:
                    error_message = "Dose du PTV 3 illisible"              
            
            if len(ptv_names) == 0:
                error_message = "Aucun PTV sélectionné"
            
            try:
                nb_fx = int(self.fxbox.Text)
            except:
                error_message = "Nb de fractions illisible"
                
            technique = self.techcombo.Text
                    
            if self.couchcombo.Text == 'Ajouter':
                couch = True
            else:
                couch = False                    
                    
            name = self.sitebox.Text + ' ' + technique
            if couch:
                name += ' Couch'            
            try:    
                existing_plan = patient.TreatmentPlans[name]
                error_message = "Un plan avec le nom %s exist déjà, SVP le renommez avant de commencer" % name
            except:
                pass                    
                
            oar_list = crane.crane_stereo_kbp_identify_rois(patient)
            if oar_list[0] == 'ERROR':
                error_message = 'OAR essentiel pas trouvé: ' + oar_list[1]                     

            if error_message != '': #In case of any error, abort and send error message back
                d = []
                return d,error_message
            
            #Compile plan data to send to scripts
            d = dict(patient = patient,
                     site_name = self.sitebox.Text,
                     exam = patient.Examinations[self.scancombo.Text],
                     iso_name = self.isocombo.Text,
                     machine = self.machinecombo.Text,
                     nb_fx = nb_fx,
                     rx = rx,
                     rx_dose = max(rx), #Needed for isodose creation
                     ptv_names = ptv_names,
                     oar_list = oar_list,
                     technique = technique,
                     couch = couch)      
            
            return d,error_message

            
        def evalClicked(self, sender, args):

            self.status.ForeColor = Color.Black
            self.status.Text = "Évaluation en cours, veuillez patienter"        
            
            d,error_message = self.compile_plan_data()
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                 
            
            rx = d['rx']
            ptv_names = d['ptv_names']
            
            #Predict dose to brain (and generate ROIs)
            self.status.ForeColor = Color.Black
            self.status.Text = "Estimation de la dose au cerveau"
            predicted_vol = crane.crane_stereo_kbp_predict_dose(plan_data = d)
            cerv_ptv_vol = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries["CERVEAU-PTV_"+d['site_name']].GetRoiVolume()
            
            #Display predicted results
            self.message.Text = 'Volumes prédits dans le cerveau-PTV:\n   V100%%: %.2fcc\n   V90%%:  %.2fcc\n   V80%%:  %.2fcc\n   V70%%: %.2fcc\n   V60%%:  %.2fcc\n   V50%%:  %.2fcc\n   V40%%:  %.2fcc' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6])
            v10 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1000)
            v12 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1200)
            self.message.Text += '\n\nV10 Cerveau-PTV estimé: %s\nV12 Cerveau-PTV estimé: %s' % (v10,v12)
            
            self.status.Text = "Terminé"
            
            #Use bounding boxes to determine PTV diameters
            small_ptvs = 0
            medium_ptvs = 0
            for ptv in d['ptv_names']:
                bb = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv].GetBoundingBox()
                ptv_vol = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv].GetRoiVolume()
                dia = [abs(bb[0].x-bb[1].x),abs(bb[0].y-bb[1].y),abs(bb[0].z-bb[1].z)]
                self.message.Text += "\n\nCible: %s\n   Vol (cc): %.2f\n   Dimensions: %.2fcm x %.2fcm x %.2fcm" % (ptv,ptv_vol,dia[0],dia[1],dia[2])
                if min(dia)<1:
                    self.message.Text += "\nCe PTV est plus petit que 1cm, consultez la physique"
                elif min(dia)<2:
                    small_ptvs += 1
                elif min(dia)<3:
                    medium_ptvs +=1
                    
            if len(ptv_names) == 1 and small_ptvs == 0:                
                if medium_ptvs == 0:
                    self.message.Text += "\n\nLe VMAT devrait être utilisé pour ce plan"
                    self.techcombo.Text = 'VMAT'
                elif medium_ptvs == 1:
                    self.message.Text += "\n\nComme le PTV est relativement petit, faites une\ncomparaison 3DC/VMAT"
                    self.techcombo.Text = '3DC'
            elif len(ptv_names) == 1 and small_ptvs > 0:
                    self.message.Text += "\n\nLe PTV est trop petit pour un plan VMAT, utilisez le 3DC"
                    self.techcombo.Text = '3DC'
            elif len(ptv_names) > 1:
                if small_ptvs == 0:
                    self.message.Text += "\n\nL'IMRT devrait être utilisé pour ce plan"
                    self.techcombo.Text = 'IMRT'
                else:
                    self.message.Text += "\n\nAu moins un PTV <2cm, faites une comparaison\n3DC/IMRT et consultez la physique"
                    self.techcombo.Text = '3DC'            
            
        def addplanClicked(self, sender, args):
            self.status.ForeColor = Color.Black
            self.status.Text = "Calcul en cours, veuillez patienter"
            
            d,error_message = self.compile_plan_data()
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                  
        
            rx = d['rx']       
            ptv_names = d['ptv_names']
            technique = d['technique']
                        
            #Predict dose to brain (and generate ROIs)
            self.status.ForeColor = Color.Black
            self.status.Text = "Estimation de la dose au cerveau"
            predicted_vol = crane.crane_stereo_kbp_predict_dose(plan_data = d)
            cerv_ptv_vol = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries["CERVEAU-PTV_"+d['site_name']].GetRoiVolume()
            
            #Display predicted results
            self.message.Text = 'Volumes prédits dans le cerveau-PTV:\n   V100%%: %.2fcc\n   V90%%:  %.2fcc\n   V80%%:  %.2fcc\n   V70%%: %.2fcc\n   V60%%:  %.2fcc\n   V50%%:  %.2fcc\n   V40%%:  %.2fcc' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6])
            v10 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1000)
            v12 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1200)
            self.message.Text += '\n\nV10 Cerveau-PTV estimé: %s\nV12 Cerveau-PTV estimé: %s' % (v10,v12)
            
            self.status.Text = "Estimation de la dose max au tronc cerebral"
            tronc_max = crane.crane_stereo_kbp_predict_oar_dose(plan_data = d)    
            
            if patient.BodySite == '':
                patient.BodySite = 'Crâne'  
            
            if self.isodosecombo.Text == "Créer":
                self.status.Text = "Ajout du dose color table"
                crane.crane_stereo_create_isodose_lines(plan_data = d)           
                
            #Create/assign types to POIs and ROIs (only if this is the first plan for the patient)
            try:
                existing_plan = patient.TreatmentPlans[0]
            except:
                self.status.Text = "Gestion des POIs"
                poi.create_iso()
                poi.auto_assign_poi_types()
                
                self.status.Text = "Suppression des overrides de densité"
                for rois in patient.PatientModel.RegionsOfInterest:
                    rois.SetRoiMaterial(Material=None)    
                
                self.status.Text = "Création du contour externe"
                roi.generate_BodyRS_using_threshold()
            
            #Assign proper contour type to all PTVs
            self.status.Text = "Assignation du statut PTV"
            for ptv in ptv_names:
                try:
                    roi.set_roi_type(ptv, 'Ptv', 'Target')
                except:
                    pass #In a perfect world, I would copy the ROI, replace the PTV with the copy in ptv_names and then change its type
            
            #Add plan, beamset and beams
            self.status.Text = "Ajout du plan, beamset et faisceaux"
            if technique == 'VMAT': #Only case where we don't need a 3DC plan at all
                plan,beamset = crane.crane_stereo_kbp_add_VMAT_plan_and_beamset(plan_data = d)
            
            elif technique == 'IMRT' and len(ptv_names) == 1:
                plan,beamset = crane.crane_stereo_kbp_add_IMRT_plan_and_beamset(plan_data = d)
            
            elif technique == 'IMRT' and len(ptv_names) > 1:
                self.status.Text = "Ajout du plan, beamset et faisceaux (touchez pas à l'ordinateur SVP)"
                plan,beamset = crane.crane_stereo_kbp_add_3DC_plan(plan_data = d)
                
                self.status.Text = "Optimisation angles collimateur (touchez pas à l'ordinateur SVP)"
                crane.optimize_collimator_angles()
                
                self.status.Text = "Conversion du plan 3DC > IMRT (touchez pas à l'ordinateur SVP)"
                crane.crane_stereo_convert_3DC_IMRT(plan=plan,beamset=beamset)
            
            elif technique == '3DC':
                self.status.Text = "Ajout du plan, beamset et faisceaux (touchez pas à l'ordinateur SVP)"
                plan,beamset = crane.crane_stereo_kbp_add_3DC_plan(plan_data = d)
                
                if len(ptv_names)>1:
                    self.status.Text = "Optimisation angles collimateur (touchez pas à l'ordinateur SVP)"
                    crane.optimize_collimator_angles()  
                    
            # Add clinical goals (conveniently the same for all types of plan)
            self.status.Text = "Ajout des clinical goals"
            clinical_goals.add_dictionary_cg('Crane Stereo', 15, 1, plan = plan)
            eval.add_clinical_goal("CERVEAU-PTV_"+d['site_name'], 1000, 'AtMost', 'AbsoluteVolumeAtDose', 10, plan=plan)
            eval.add_clinical_goal("CERVEAU-PTV_"+d['site_name'], 1200, 'AtMost', 'AbsoluteVolumeAtDose', 8, plan=plan)
            for i,ptv in enumerate(ptv_names):
                eval.add_clinical_goal(ptv, rx[i], 'AtLeast', 'VolumeAtDose', 99, plan=plan)
                eval.add_clinical_goal(ptv, 1.5 * rx[i], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                #if technique == '3DC':
                #    optim.copy_clinical_goals(old_plan = plan,new_plan = patient.TreatmentPlans[d['site_name']+' 3DC optimised'])                    
                    
            #Add objectives and optimize plan
            if technique == '3DC':
                self.status.Text = "Optimisation du plan 3DC (touchez pas à l'ordinateur SVP)"
                plan,beamset = crane.crane_stereo_kbp_optimize_3DC_plan(plan_data=d,plan=plan,beamset=beamset) 
                obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=False)            
            else:
                self.status.Text = "Ajout des objectifs d'optimisation"
                crane.crane_stereo_kbp_initial_optimization_objectives(plan_data=d,plan=plan,predicted_vol=predicted_vol,tronc_max=tronc_max)
                
                self.status.Text = "Optimization du plan initial"
                plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
                if len(ptv_names) == 1:
                    optim.triple_optimization(plan=plan,beamset=beamset)
                elif len(ptv_names) > 1:
                    optim.optimization_90_30(plan=plan,beamset=beamset)  
                    
                self.status.Text = "Modification du plan"
                if len(ptv_names) == 1:
                    crane.crane_stereo_kbp_modify_plan_single_ptv(plan_data=d,plan=plan,beamset=beamset,predicted_vol=predicted_vol,tronc_max=tronc_max)
                    self.status.Text = "Optimization du plan modifié"
                    optim.triple_optimization(plan=plan,beamset=beamset)
                    self.status.Text = "Scaling couverture à la prescription"
                    obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=False)
                elif len(ptv_names) > 1:     
                    obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=True)
                    self.message.Text += '\n\nV10 obtenu (plan initial): %.2fcc\nV12 obtenu (plan initial): %.2fcc' % (obtained_vol[0]*cerv_ptv_vol,obtained_vol[1]*cerv_ptv_vol)
                    continue_optimization = True
                    best_vol = 100000
                    for i in range(4): #i IS EQUAL TO THE NUMBER OF COMPLETED ITERATIONS!
                        if continue_optimization:
                            self.status.Text = "Modification du plan et réoptimisation (étape %d/4)" % (i+1)
                            continue_optimization = crane.crane_stereo_kbp_modify_plan_multi_ptv(plan_data=d,plan=plan,beamset=beamset) #Evaluates PTV coverage, adjusts and reoptimizes if necessary
                            obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=True)
                            if (obtained_vol[0] + obtained_vol[1]) < best_vol:
                                best_vol = obtained_vol[0] + obtained_vol[1]
                                best_iteration = i
                            #if continue_optimization: #If crane_stereo_kbp_modify_plan_multi_ptv returns False, then the plan hasn't changed since last time and we don't need to print these values again
                            self.message.Text += '\n\nV10 obtenu (après %d révision(s)): %.2fcc\nV12 obtenu (après %d révision(s)): %.2fcc' % (i+1,obtained_vol[0]*cerv_ptv_vol,i+1,obtained_vol[1]*cerv_ptv_vol)                            
                    self.status.Text = "Scaling de la couverture à la prescription"
                    obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=False)
                    
                    #Now we have to check if the final plan is better than the previous plans. If not, we will reoptimize and stop and the correct point.
                    self.status.Text = "Meilleur plan: plan initial avec %d itérations" % best_iteration
                    
                    #if (obtained_vol[0]+obtained_vol[1]*0.9) > best_vol:
                    if (obtained_vol[0]+obtained_vol[1]) > best_vol:
                        self.status.Text = "Retour vers le meilleur plan, veuillez patientez svp"
                        optim.erase_objectives(plan,beamset)
                        plan.PlanOptimizations[beamset.Number-1].ResetOptimization() 
                        crane.crane_stereo_kbp_initial_optimization_objectives(plan_data=d,plan=plan,predicted_vol=predicted_vol,tronc_max=tronc_max)
                        optim.optimization_90_30(plan=plan,beamset=beamset)
                        for i in range(best_iteration+1):
                            self.status.Text = "Modification du plan et réoptimisation (étape %d/%d)" % (i+1,best_iteration+1)
                            continue_optimization = crane.crane_stereo_kbp_modify_plan_multi_ptv(plan_data=d,plan=plan,beamset=beamset)
                        self.status.Text = "Scaling de la couverture à la prescription"
                        obtained_vol,initial_ptv_cov = crane.crane_stereo_kbp_scale_dose(plan_data=d,beamset=beamset,reset_dose=False)                            
            
            
            #Display results of plan
            self.message.Text += '\n\nV10 obtenu: %.2fcc\nV12 obtenu: %.2fcc' % (obtained_vol[0]*cerv_ptv_vol,obtained_vol[1]*cerv_ptv_vol)
            
            #Write results to file (this is put into a try because it will crash if someone has the destination file open when it tries to write to it)
            try:
                crane.crane_kbp_write_results_to_file(plan_data=d,plan=plan,beamset=beamset,predicted_vol=predicted_vol,initial_ptv_cov=initial_ptv_cov,obtained_vol=obtained_vol)
            except:
                pass
            
            self.isodosecombo.Text = 'Ne pas créer'
            self.status.Text = "Terminé avec succès!"
            self.status.ForeColor = Color.Green
    
    
    
    
    
    
    
    
    #Check for common errors while importing patient, plan, beamset and examination
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
        
    form = CraneLauncher()
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
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
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
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
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
            
            
            
            self.renamelabel = Label()
            self.renamelabel.Text = "Renommer les faisceaux"
            self.renamelabel.Location = Point(25, offset + vert_spacer * 3)
            self.renamelabel.Font = Font("Arial", 11, FontStyle.Bold)
            self.renamelabel.AutoSize = True          

            self.renamewarninglabel = Label()
            self.renamewarninglabel.Text = "Pas recommendé pour les plans avec couch de table"
            self.renamewarninglabel.Location = Point(25, offset + vert_spacer * 3.7)
            self.renamewarninglabel.Font = Font("Arial", 10, FontStyle.Italic)
            self.renamewarninglabel.AutoSize = True                  
            
            self.sitelabel = Label()
            self.sitelabel.Text = "Site:"
            self.sitelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.sitelabel.Location = Point(25, offset + vert_spacer * 4.7)
            self.sitelabel.AutoSize = True   
            
            self.sitebox = TextBox()
            self.sitebox.Parent = self
            self.sitebox.Size = Size(60,40)
            self.sitebox.Location = Point(75,offset + vert_spacer * 4.7)
            self.sitebox.Text = "A1"
            
            self.renameButton = Button()
            self.renameButton.Text = "Renommer les faisceaux"
            self.renameButton.Size = Size(150,20)
            self.renameButton.Location = Point(420,offset + vert_spacer * 4.7)
            self.renameButton.Click += self.renameClicked
            
            
            self.MainWindow.Controls.Add(self.NTCPlabel)
            self.MainWindow.Controls.Add(self.roilabel)
            self.MainWindow.Controls.Add(self.diaglabel)            
            self.MainWindow.Controls.Add(self.ROIcombo)
            self.MainWindow.Controls.Add(self.diagcombo)
            self.MainWindow.Controls.Add(self.NTCPButton)
            
            self.MainWindow.Controls.Add(self.renamelabel)
            self.MainWindow.Controls.Add(self.renamewarninglabel)
            self.MainWindow.Controls.Add(self.sitelabel)
            self.MainWindow.Controls.Add(self.sitebox)
            self.MainWindow.Controls.Add(self.renameButton)
            
            
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
            self.ROIcombo.Items.Add("Choisissez ROI")         
            for roi in patient.PatientModel.RegionsOfInterest:       
                self.ROIcombo.Items.Add(roi.Name)
                if roi.Name == 'FOIE EXPI-GTV':
                    self.ROIcombo.Text = roi.Name

                        
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné')
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné')
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé')
        return
        
    form = ToolWindow()
    Application.Run(form)   
  