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
                self.comboBoxRx.Items.Add("66Gy-22")
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
                #Identify the PTV
                if 'PTV15' in roi_names:
                    self.Label2.Text = "PTV15 trouvé"
                    self.comboBoxRx.Items.Add("15Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("15Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "15"
                    #self.Fxbox.Text = "1"
                elif 'PTV18' in roi_names:
                    self.Label2.Text = "PTV18 trouvé"
                    self.comboBoxRx.Items.Add("18Gy-1")
                    self.comboBoxRx.SelectedIndex = self.comboBoxRx.FindStringExact("18Gy-1")
                    self.techniquecombo.Items.Add("IMRT")                    
                    #self.dosebox.Text = "18"
                    #self.Fxbox.Text = "1"
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
                    opt_plan.PlanOptimizations[0].RunOptimization()                     
                    self.Status.Text = "Auto-optimization en cours (Ajustement des objectifs)"                        
                    prostate.fit_obj_prostate(plan=opt_plan, beamset = opt_plan.BeamSets[0])
                    opt_plan.PlanOptimizations[0].AutoScaleToPrescription = False
                    opt_plan.PlanOptimizations[0].ResetOptimization()
                    self.Status.Text = "Auto-optimization en cours (1er opt après fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()
                    self.Status.Text = "Auto-optimization en cours (2er opt après fit)"
                    opt_plan.PlanOptimizations[0].RunOptimization()                   
                    
                self.Status.Text = "Script terminé! Cliquez sur Cancel pour sortir."
                self.Status.ForeColor = Color.Green      
                
 
            elif self.sitecombo.Text == 'Crâne' or self.sitecombo.Text == 'Crâne 2 niveaux':
                if rx_dose == 1500:
                    ptv = patient.PatientModel.RegionsOfInterest["PTV15"]
                    if self.sitecombo.Text == 'Crâne 2 niveaux':
                        ptv_low = patient.PatientModel.RegionsOfInterest["PTV12"]
                    else:
                        ptv_low = None
                        rx_dose_low = None
                elif rx_dose == 1800:  
                    ptv = patient.PatientModel.RegionsOfInterest["PTV18"]
                    if self.sitecombo.Text == 'Crâne 2 niveaux':
                        ptv_low = patient.PatientModel.RegionsOfInterest["PTV15"]
                    else:
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
                clinical_goals.add_dictionary_cg('Crane Stereo', rx_dose/100, 1, plan = patient.TreatmentPlans[d['plan_name']])
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
   
   
def verify_parameters():

    class VerificationWindow(Form):
        def __init__(self):
            self.Text = "Vérification des paramètres"

            self.Width = 900
            self.Height = 900

            self.setupVerifPanel()
            self.setupButtonPanel()

            self.Controls.Add(self.VerifPanel)
            self.Controls.Add(self.ButtonPanel)
            
        def bigPanel(self, x, y):
            panel = Panel()
            panel.Width = 900
            panel.Height = 800 #Overflows onto the ButtonPanel, but it actually looks better that way
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel
            
        def smallPanel(self, x, y):
            panel = Panel()
            panel.Width = 900
            panel.Height = 130
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel
            
        # eventhandler - THIS DOES NOT WORK CORRECTLY FOR NOW, it seems to take the wrong index from the combobox (ie, it verifies the old plan, not the new one)
        #def comboBox_changed(self, sender, args):
            #beamset = plan.BeamSets[self.beamset_comboBox.Text]
            #self.okClicked(sender, args)
            
        def setupVerifPanel(self):
            self.VerifPanel = self.bigPanel(0, 0)

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name + "                       BeamSet: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True
            
            self.Header1 = Label()
            self.Header1.Text = "ROIs et POIs"
            self.Header1.Location = Point(30, 60)
            self.Header1.Font = Font("Arial", 10, FontStyle.Bold)
            self.Header1.AutoSize = True

            self.Text1a = Label()
            self.Text1a.Text = "Nom du contour External: "
            self.Text1a.Location = Point(self.Header1.Left + 10, self.Header1.Top + 20)
            self.Text1a.AutoSize = True
            self.Text1a.Font = Font("Arial", 10)

            self.Text1b = Label()
            self.Text1b.Text = "ROIs avec override de matériel:"
            self.Text1b.Location = Point(self.Text1a.Left, self.Text1a.Top + 20)
            self.Text1b.AutoSize = True
            self.Text1b.Font = Font("Arial", 10)

            self.Text1c = Label()
            self.Text1c.Text = "POIs isocentre/localisation:"
            self.Text1c.Location = Point(self.Text1b.Left, self.Text1b.Top + 20)
            self.Text1c.AutoSize = True
            self.Text1c.Font = Font("Arial", 10)            
            
            self.Text1d = Label()
            self.Text1d.Text = "Tableau de densité: "
            self.Text1d.Location = Point(self.Text1c.Left, self.Text1c.Top + 20)
            self.Text1d.AutoSize = True
            self.Text1d.Font = Font("Arial", 10)                 
                          
            
            self.Header2 = Label()
            self.Header2.Text = "Détails du beamset"
            self.Header2.Location = Point(self.Header1.Left, self.Text1d.Top + 40)
            self.Header2.Font = Font("Arial", 10, FontStyle.Bold)
            self.Header2.AutoSize = True

            self.Text2a = Label()
            self.Text2a.Text = "Prescription: "
            self.Text2a.Location = Point(self.Header2.Left + 10, self.Header2.Top + 20)
            self.Text2a.AutoSize = True
            self.Text2a.Font = Font("Arial", 10)

            self.Text2b = Label()
            self.Text2b.Text = "Résolution dose grid: "
            self.Text2b.Location = Point(self.Text2a.Left, self.Text2a.Top + 20)
            self.Text2b.AutoSize = True
            self.Text2b.Font = Font("Arial", 10)

            self.Text2c = Label()
            self.Text2c.Text = "Coordonnées iso: "
            self.Text2c.Location = Point(self.Text2b.Left, self.Text2b.Top + 20)
            self.Text2c.AutoSize = True
            self.Text2c.Font = Font("Arial", 10)                   

            self.Text2d = Label()
            self.Text2d.Text = "Coordonnées faisceaux: "
            self.Text2d.Location = Point(self.Text2c.Left, self.Text2c.Top + 20)
            self.Text2d.AutoSize = True
            self.Text2d.Font = Font("Arial", 10)        
            
            self.Text2f = Label()
            self.Text2f.Text = "Dose Specification Points: "
            self.Text2f.Location = Point(self.Text2d.Left, self.Text2d.Top + 20)
            self.Text2f.AutoSize = True
            self.Text2f.Font = Font("Arial", 10)      

            self.Text2g = Label()
            self.Text2g.Text = "Algorithme de calcul: "
            self.Text2g.Location = Point(self.Text2f.Left, self.Text2f.Top + 20)
            self.Text2g.AutoSize = True
            self.Text2g.Font = Font("Arial", 10)                 

            self.Text2h = Label()
            self.Text2h.Text = "CT de planification: "
            self.Text2h.Location = Point(self.Text2g.Left, self.Text2g.Top + 20)
            self.Text2h.AutoSize = True
            self.Text2h.Font = Font("Arial", 10)       
            
            self.Header4 = Label()
            self.Header4.Text = "Faisceaux"
            self.Header4.Location = Point(self.Header2.Left, self.Text2h.Top + 40)
            self.Header4.Font = Font("Arial", 10, FontStyle.Bold)
            self.Header4.AutoSize = True            
            
            self.Text2e = Label()
            self.Text2e.Text = "Nom / Description / Énergie / Gantry / Sens / Colli / Couch / Segments / UMs / Temps "
            self.Text2e.Location = Point(self.Text2d.Left, self.Header4.Top + 20)
            self.Text2e.AutoSize = True
            self.Text2e.Font = Font("Arial", 10)     
            
            self.Header3 = Label()
            self.Header3.Text = "Optimisation"
            self.Header3.Location = Point(self.Header2.Left, self.Text2e.Top + 40)
            self.Header3.Font = Font("Arial", 10, FontStyle.Bold)
            self.Header3.AutoSize = True

            self.Text3a = Label()
            self.Text3a.Text = "Optimization Settings: "
            self.Text3a.Location = Point(self.Header3.Left + 10, self.Header3.Top + 20)
            self.Text3a.AutoSize = True
            self.Text3a.Font = Font("Arial", 10)

            self.Text3b = Label()
            self.Text3b.Text = "Constrain Leaf Motion: "
            self.Text3b.Location = Point(self.Text3a.Left, self.Text3a.Top + 20)
            self.Text3b.AutoSize = True
            self.Text3b.Font = Font("Arial", 10)

            self.Text3c = Label()
            self.Text3c.Text = "Calculate Intermediate Dose / Calculate Final Dose: "
            self.Text3c.Location = Point(self.Text3b.Left, self.Text3b.Top + 20)
            self.Text3c.AutoSize = True
            self.Text3c.Font = Font("Arial", 10)                   

            self.Text3d = Label()
            self.Text3d.Text = "Gantry Spacing / Max Delivery Time: "
            self.Text3d.Location = Point(self.Text3c.Left, self.Text3c.Top + 20)
            self.Text3d.AutoSize = True
            self.Text3d.Font = Font("Arial", 10)     

            self.Text3e = Label()
            self.Text3e.Text = "Beam Optimization Settings: "
            self.Text3e.Location = Point(self.Text3d.Left, self.Text3d.Top + 20)
            self.Text3e.AutoSize = True
            self.Text3e.Font = Font("Arial", 10)             
            
            self.Text3f = Label()
            self.Text3f.Text = "Première/dernière paires de lames: "
            self.Text3f.Location = Point(self.Text3e.Left, self.Text3e.Top + 20)
            self.Text3f.AutoSize = True
            self.Text3f.Font = Font("Arial", 10)     
            
            
            self.avertissement = Label()
            self.avertissement.Text = ""
            self.avertissement.Location = Point(self.Text3f.Left, self.Text3f.Top + 40)
            self.avertissement.AutoSize = True
            self.avertissement.Font = Font("Arial", 10, FontStyle.Bold)  
            self.avertissement.ForeColor = Color.Red            
            
            
            self.VerifPanel.Controls.Add(self.PatientIDHeader)
            self.VerifPanel.Controls.Add(self.Header1)
            self.VerifPanel.Controls.Add(self.Text1a)
            self.VerifPanel.Controls.Add(self.Text1b)
            self.VerifPanel.Controls.Add(self.Text1c)
            self.VerifPanel.Controls.Add(self.Text1d)            
            self.VerifPanel.Controls.Add(self.Header2)
            self.VerifPanel.Controls.Add(self.Text2a)
            self.VerifPanel.Controls.Add(self.Text2b)
            self.VerifPanel.Controls.Add(self.Text2c)
            self.VerifPanel.Controls.Add(self.Text2d)
            self.VerifPanel.Controls.Add(self.Text2f)
            self.VerifPanel.Controls.Add(self.Text2g)            
            self.VerifPanel.Controls.Add(self.Text2h)              
            self.VerifPanel.Controls.Add(self.Header4) # Out of order, sorry
            self.VerifPanel.Controls.Add(self.Text2e)  # Maybe not VERY sorry, though
            self.VerifPanel.Controls.Add(self.Header3)
            self.VerifPanel.Controls.Add(self.Text3a)
            self.VerifPanel.Controls.Add(self.Text3b)
            self.VerifPanel.Controls.Add(self.Text3c)
            self.VerifPanel.Controls.Add(self.Text3d)
            self.VerifPanel.Controls.Add(self.Text3e)
            self.VerifPanel.Controls.Add(self.Text3f)
            self.VerifPanel.Controls.Add(self.avertissement)

        # eventhandler
        #def comboBox_changed(self, sender, args):
            #beamset = plan.BeamSets[self.beamset_comboBox.Text]
            #okButton.PerformClick()
            #self.okClicked()
                   
        def okClicked(self, sender, args):
            beamset = plan.BeamSets[self.beamset_comboBox.Text]
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') + "                       Plan: " + plan.Name + "                       BeamSet: " + beamset.DicomPlanLabel
         
            warning_text = ""
            coords = None
            loc_coords = None
            beam_iso_poi = None

            # External contour and material overrides
            override_roi = []
            external_roi = "Aucun trouvé"
            for roi in patient.PatientModel.StructureSets[exam.Name].RoiGeometries:
                if roi.OfRoi.Type == "External":
                    external_roi = roi.OfRoi.Name
                try:
                    override_material = roi.OfRoi.RoiMaterial.OfMaterial.Name
                    override_roi.append((roi.OfRoi.Name + " (" + override_material + ")"))
                except:
                    continue
            if len(override_roi) > 0:
                self.Text1b.Text = "ROIs avec override de matériel: "                
                for item in override_roi:
                    self.Text1b.Text += item + "  "
            else:
                self.Text1b.Text = "ROIs avec override de matériel: Aucun"      
            self.Text1a.Text = "Nom du contour External: " + external_roi
            
            if external_roi == "Aucun trouvé":
                warning_text += "AVERTISSEMENT: Aucun ROI external défini\n"
            
            # Isocenter and localization point
            try:
                loc_point_name = beamset.PatientSetup.LocalizationPoiGeometrySource.LocalizationPoiGeometry.OfPoi.Name
                loc_coords = poi.get_poi_coordinates(loc_point_name,exam)
            except:
                loc_point_name = "Aucun point de localisation trouvé"
                warning_text += "AVERTISSEMENT: Aucun point de localisation défini\n"
            
            num_iso = 0
            if poi.poi_exists("ISOCENTRE", exam):
                iso_point_name = "ISOCENTRE"
                num_iso +=1                    
            if poi.poi_exists("ISO", exam):
                iso_point_name = "ISO"
                num_iso +=1                
            if poi.poi_exists("ISO SCAN", exam):
                iso_point_name = "ISO SCAN"
                num_iso +=1                
            if poi.poi_exists("ISO B1", exam):
                iso_point_name = "ISO B1"
                num_iso +=1
             
            if num_iso == 0:
                iso_point_name = "Aucun point trouvé pour l'isocentre"
                warning_text += "AVERTISSEMENT: Aucun point trouvé pour l'isocentre\n"
                 
            elif num_iso > 1:
                iso_point_name = "Plus qu'un candidat trouvé"            
                warning_text += "AVERTISSEMENT: Plus qu'un point isocentre trouvé, vérifiez attentivement les coordonées des faiceaux\n"
            elif num_iso == 1:            
                coords = poi.get_poi_coordinates(iso_point_name,exam) 
            
            self.Text1c.Text = "POIs isocentre/localisation: " + iso_point_name + " / " + loc_point_name                
                   
            #Check to find shift from reference point to isocenter
            if loc_coords != None and coords != None:
                if iso_point_name != loc_point_name:
                    if (loc_coords.x-coords.x ==0 ) and (loc_coords.y-coords.y == 0) and (loc_coords.z-coords.z == 0):
                        self.Text1c.Text += " (mêmes coordonnées)"
                    else:
                        self.Text1c.Text += " (Shift de %.2fcm en x, %.2fcm en y et %.2fcm en z)" % (loc_coords.x-coords.x, loc_coords.z-coords.z, coords.y-loc_coords.y)
            
            # CT-to-density table(s)
            table_mismatch = False
            for i,CT in enumerate(patient.Examinations):
                if i > 0:
                    if table != CT.EquipmentInfo.ImagingSystemReference.ImagingSystemName:
                        table_mismatch = True
                table = CT.EquipmentInfo.ImagingSystemReference.ImagingSystemName
            if table_mismatch:
                warning_text += "AVERTISSEMENT: Tableau de densité pas pareil pour tous les CTs\n"                 
                self.Text1d.Text = "Tableau de densité: Pas pareil pour tous les CTs"
            else:
                self.Text1d.Text = "Tableau de densité: " + table
            if table != "HOST-7403" and table != "HOST-7228":
                warning_text += "AVERTISSEMENT: Tableau de densité n'est pas HOST-7228 ni HOST-7403\n"              

            # Prescription
            # Check if beamset dose is dependent
            try:
                bkgdose_name = plan.PlanOptimizations[beamset.Number-1].BackgroundDose.ForBeamSet.DicomPlanLabel
            except:
                bkgdose_name = "None"
            # Determine prescription dose, fractions and target
            try:
                presc_text = str((beamset.Prescription.PrimaryDosePrescription.DoseValue)/100.0) + "Gy"
                presc_text += " en %dfx " % beamset.FractionationPattern.NumberOfFractions
                # Display prescription type and dose
                if beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtPoint':
                    presc_text += "au point " + beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                elif beamset.Prescription.PrimaryDosePrescription.PrescriptionType == 'DoseAtVolume':
                    presc_text += "à " + str(beamset.Prescription.PrimaryDosePrescription.DoseVolume) + r'% du volume du ' + beamset.Prescription.PrimaryDosePrescription.OnStructure.Name
                if bkgdose_name != "None":
                    presc_text += " (dépendente sur beamset " + bkgdose_name + ")"
                presc_text = presc_text.replace(".0Gy","Gy")
                presc_text = presc_text.replace(".0%","%")
            except:
                presc_text = "Prescription non définie"
                warning_text += "AVERTISSEMENT: Prescription non définie\n"
            self.Text2a.Text = "Prescription: " + presc_text          

            # Dose grid resolution
            self.Text2b.Text = "Résolution dose grid: %.2fcm x %.2fcm x %.2fcm" % (beamset.FractionDose.InDoseGrid.VoxelSize.x,beamset.FractionDose.InDoseGrid.VoxelSize.y,beamset.FractionDose.InDoseGrid.VoxelSize.z)
            if beamset.FractionDose.InDoseGrid.VoxelSize.x != 0.2 or beamset.FractionDose.InDoseGrid.VoxelSize.y != 0.2 or beamset.FractionDose.InDoseGrid.VoxelSize.z != 0.2:
                warning_text += "AVERTISSEMENT: Résolution dose grid n'est pas 0.2cm x 0.2cm x 0.2cm\n"
            #self.Text2b.Text = (str(dir(beamset.FractionDose.InDoseGrid.VoxelSize)))
            
            # Find isocenter point and coordinates
            if num_iso == 1:
                self.Text2c.Text = "Coordonnées point %s:  (%.2f, %.2f, %.2f)" % (iso_point_name, coords.x, coords.z, coords.y*-1)
            elif num_iso == 0:
                self.Text2c.Text = "Coordonnées POI isocentre: Aucun point trouvé pour l'isocentre"
            elif num_iso > 1:
                self.Text2c.Text = "Coordonnées POI isocentre: Plus qu'un point isocentre trouvé, impossible d'afficher coordonnées"            

            # Beam isocenters
            self.Text2d.Text = "Coordonnées faisceaux: "
            mismatch = False
            try:              
                for i, beam in enumerate(beamset.Beams): #Verify that coordinates are the same for all beams
                    if i > 0:
                        old_iso_poi = beam_iso_poi
                    beam_iso_poi = [x for x in beam.PatientToBeamMapping.IsocenterPoint]
                    if i>0:
                        if abs(beam_iso_poi[0].Value - old_iso_poi[0].Value) > 0.005 or abs(beam_iso_poi[1].Value - old_iso_poi[1].Value) > 0.005 or abs(beam_iso_poi[2].Value - old_iso_poi[2].Value) > 0.005:
                            self.Text2d.Text = "Coordonnées faisceaux: Coordonnées différentes pour faisceaux " + beamset.Beams[i-1].Name + " et " + beam.Name + "!"
                            warning_text += "AVERTISSEMENT: Coordonnées isocentres pas pareils pour tous les faisceaux\n"
                            mismatch = True
                            break
                if not mismatch:
                    self.Text2d.Text += " (%.2f, %.2f, %.2f)" % (beam_iso_poi[0].Value, beam_iso_poi[2].Value, beam_iso_poi[1].Value*-1)
            except:
                self.Text2d.Text += "Coordonnées pas trouvés"
                warning_text += "AVERTISSEMENT: Coordonnées isocentres faisceaux pas trouvées\n"
                
            # Verify if beams are centered on isocenter point
            if beam_iso_poi != None and coords != None:
                iso_shift_x = coords.x - beam_iso_poi[0].Value
                iso_shift_y = coords.y - beam_iso_poi[1].Value
                iso_shift_z = coords.z - beam_iso_poi[2].Value
                if abs(iso_shift_x) > 0.005 or abs(iso_shift_y) > 0.005 or abs(iso_shift_z) > 0.005:
                    warning_text += "AVERTISSEMENT: Écart entre les coordonnés des faisceaux et le point " + iso_point_name + "\n"
                    warning_text += "                                 Shift de %.2fcm en x, %.2fcm en y et %.2fcm en z\n" % (-1*iso_shift_x, -1*iso_shift_z, iso_shift_y)

            # Dose to Dose Specification Points
            self.Text2f.Text = "Dose Specification Points: "
            dsps = True
            try:
                dsp_name = beamset.DoseSpecificationPoints[0].Name
            except:
                dsps = False
                self.Text2f.Text += "Aucun Dose Specification Point trouvé \n"  
            if dsps:
                for dsp in beamset.DoseSpecificationPoints:
                    dsp_temp = lib.RSPoint(dsp.Coordinates.x, dsp.Coordinates.y, dsp.Coordinates.z)
                    dsp_dose = beamset.FractionDose.InterpolateDoseInPoint(Point=dsp_temp.value)
                    self.Text2f.Text += "%s (%.2fGy par fraction) / " % (dsp.Name, dsp_dose/100.0)
                self.Text2f.Text = self.Text2f.Text[:-2]
                
            # Dose calculation engine
            try:
                dose_algorithm = beamset.FractionDose.DoseValues.AlgorithmProperties.DoseAlgorithm
            except:
                dose_algorithm = "Dose pas calculée"
            self.Text2g.Text = "Algorithme de calcul: " + dose_algorithm
            if dose_algorithm != "CCDose":
                warning_text += "AVERTISSEMENT: La dose n'est pas calculée en collapsed cone\n"              
                
            # Planning CT name
            self.Text2h.Text = "CT de planification: " + beamset.FractionDose.OnDensity.FromExamination.Name                
                    
            #Beam details
            header3_vert = 40
            self.Text2e.Text = "Nom   /    Description    /    Machine   / Énergie /   Gantry   /  Sens  /   Colli   /  Couch  / Segments /   UMs   /     DSP     "
            beams = True
            try:
                beam_name = beamset.Beams[0].Name
            except:
                beams = False
                self.Text2e.Text = "Aucun faisceau trouvé"
                warning_text += "AVERTISSEMENT: Aucun faisceau trouvé\n"
            if beams:
                for i,beam in enumerate(beamset.Beams):
                    header3_vert += 15
                    self.Text2e.Text += "\n" + beam.Name + "    /   " + beam.Description + "   /  " + beam.MachineReference.MachineName + "  / "
                    try: #Checks whether beam has a stop angle (for arcs)
                        stop_angle = beam.ArcStopGantryAngle
                        self.Text2e.Text += "    %d      /  %d-%d   /  " % (beam.MachineReference.Energy, beam.GantryAngle, beam.ArcStopGantryAngle)
                    except:
                        self.Text2e.Text += "    %d      /  %d   /  " % (beam.MachineReference.Energy, beam.GantryAngle)
                    if beam.ArcRotationDirection == "Clockwise":
                        self.Text2e.Text += " CW  "
                    elif beam.ArcRotationDirection == "CounterClockwise":
                        self.Text2e.Text += " CCW "
                    else:
                        self.Text2e.Text += "Statique"
                    self.Text2e.Text += " /     %d     /      %d     " % (beam.InitialCollimatorAngle, beam.CouchAngle)

                    # Get number of segments per beam - THIS IS EXTREMELY INELEGANT
                    num_seg = -1
                    try:
                        for segment in beam.Segments:
                            if segment.SegmentNumber > num_seg:
                                num_seg = segment.SegmentNumber
                    except:
                        num_seg = -1
                    if num_seg > -1:
                        self.Text2e.Text += " /        " + str(num_seg+1)
                    else:
                        self.Text2e.Text += " / Aucun"
                    self.Text2e.Text += "      /  %.1f" % beam.BeamMU
                    #Name of associated DSP
                    try:
                        dsp_name = beamset.FractionDose.BeamDoses[i].IsocenterOverride.Name
                    except:
                        dsp_name = "Isocenter"
                    self.Text2e.Text += "  /   %s" % dsp_name
                
            #Bump next header down depending on number of beams found
            self.Header3.Location = Point(self.Header2.Left, self.Text2e.Top + header3_vert)
            self.Text3a.Location = Point(self.Header3.Left + 10, self.Header3.Top + 20)
            self.Text3b.Location = Point(self.Text3a.Left, self.Text3a.Top + 20)
            self.Text3c.Location = Point(self.Text3b.Left, self.Text3b.Top + 20)
            self.Text3d.Location = Point(self.Text3c.Left, self.Text3c.Top + 20)
            self.Text3e.Location = Point(self.Text3d.Left, self.Text3d.Top + 20)
            self.Text3f.Location = Point(self.Text3e.Left, self.Text3e.Top + 20)
            self.avertissement.Location = Point(self.Text3f.Left, self.Text3f.Top + 40)

            # Optimization parameters
            self.Text3a.Text = "Optimization Settings: "
            opt = plan.PlanOptimizations[beamset.Number-1]
            self.Text3a.Text += "%d iterations / %d avant la conversion" % (opt.OptimizationParameters.Algorithm.MaxNumberOfIterations, opt.OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase)
            self.Text3a.Text += ", Stopping Tolerance " + str(opt.OptimizationParameters.Algorithm.OptimalityTolerance)
            
            self.Text3b.Text = "Constrain Leaf Motion: "
            if beamset.DeliveryTechnique == "Arc":
                if opt.OptimizationParameters.SegmentConversion.ArcConversionProperties.UseMaxLeafTravelDistancePerDegree == True:
                    self.Text3b.Text += "%.1fcm/deg" % opt.OptimizationParameters.SegmentConversion.ArcConversionProperties.MaxLeafTravelDistancePerDegree
                else:
                    self.Text3b.Text += "pas coché"
                    warning_text += "AVERTISSEMENT: Constrain Leaf Motion n'est pas coché\n"
            else:
                self.Text3b.Text += "non-applicable au cas d'IMRT ou 3DC"
                
            self.Text3c.Text = "Compute Intermediate Dose / Compute Final Dose: "
            if opt.OptimizationParameters.DoseCalculation.ComputeIntermediateDose == True:
                self.Text3c.Text += "oui / "
            else:
                self.Text3c.Text += "non / "
            if opt.OptimizationParameters.DoseCalculation.ComputeFinalDose == True:
                self.Text3c.Text += "oui"
            else:
                self.Text3c.Text += "non"
                
            #Beam optimization parameters         
            time_mismatch = False
            spacing_mismatch = False
            opt_types_mismatch = False            
            
            if beamset.DeliveryTechnique == "Arc":
                self.Text3d.Text = "Gantry Spacing / Max Delivery Time: "
                
                old_time = 0
                new_time = 0
                old_spacing = 0
                new_spacing = 0
                old_opt_types = ""
                new_opt_types = ""              
                
                for ts in opt.OptimizationParameters.TreatmentSetupSettings:
                    for i, beam_setting in enumerate(ts.BeamSettings):
                        new_spacing = beam_setting.ArcConversionPropertiesPerBeam.FinalArcGantrySpacing
                        new_time = beam_setting.ArcConversionPropertiesPerBeam.MaxArcDeliveryTime
                        new_opt_types = ""
                        for opt_type in beam_setting.OptimizationTypes:
                            new_opt_types += opt_type
                        if i > 0:
                            if old_spacing != new_spacing:
                                spacing_mismatch = True
                            if old_time != new_time:
                                time_mismatch = True
                            if old_opt_types != new_opt_types:
                                opt_types_mismatch = True
                        old_spacing = new_spacing
                        old_time = new_time
                        old_opt_types = new_opt_types
                if spacing_mismatch:
                    self.Text3d.Text += "pas pareil pour tous les faisceaux / "
                else:
                    self.Text3d.Text += "%d degrés / " % new_spacing
                if time_mismatch:
                    self.Text3d.Text += "pas pareil pour tous les faisceaux"
                else:
                    self.Text3d.Text += "%ds" % new_time               
                
            else: #For IMRT and 3DC
                self.Text3d.Text = "Gantry Spacing / Max Delivery Time: non-applicable au cas d'IMRT ou 3DC"      

                old_opt_types = ""
                new_opt_types = ""
                
                for ts in opt.OptimizationParameters.TreatmentSetupSettings:
                    for i, beam_setting in enumerate(ts.BeamSettings):
                        new_opt_types = ""
                        for opt_type in beam_setting.OptimizationTypes:
                            new_opt_types += opt_type
                        if i > 0 and old_opt_types != new_opt_types:
                            opt_types_mismatch = True
                        old_opt_types = new_opt_types

            self.Text3e.Text = "Optimize Segment Shapes / Segment MU: "
            if opt_types_mismatch:
                self.Text3e.Text += "pas pareil pour tous les faisceaux"
            else:
                if new_opt_types == "SegmentOptSegmentMU" or new_opt_types == "SegmentMUSegmentOpt":
                    self.Text3e.Text += "oui / oui"
                elif new_opt_types == "SegmentOpt":
                    self.Text3e.Text += "oui / non"
                elif new_opt_types == "SegmentMU":
                    self.Text3e.Text += "non / oui"
                elif new_opt_types == "":
                    self.Text3e.Text += "non / non"
                    
            if time_mismatch or spacing_mismatch or opt_types_mismatch:
                warning_text += "AVERTISSEMENT: Beam Optimization Parameters pas pareils pour tous les faisceaux\n"            
                    
            # Check to see if first/last leaf pairs used
            self.Text3f.Text = "Première/dernière paires de lames: "
            first_leaf_open = False
            last_leaf_open = False

            machine_type = None
            try:
                machine_type = beamset.Beams[0].MachineReference.MachineName
            except:
                self.Text3f.Text += "Aucun faisceau trouvé"

            for beam in beamset.Beams:
                try:
                    temp = beam.Segments[0].CollimatorAngle #Just to see if there are segments defined for the beam
                    first_leaf_open = False
                    last_leaf_open = False
                    for seg in beam.Segments:
                        if first_leaf_open == False: #Stop checking if a segment is found where leaves are open
                            if machine_type == "BeamMod":
                                if seg.LeafPositions[0][0] != seg.LeafPositions[1][0]:
                                    first_leaf_open = True
                                    first_leaf_open_seg = seg.SegmentNumber
                        if last_leaf_open == False:
                            if machine_type == "BeamMod":
                                if seg.LeafPositions[0][39] != seg.LeafPositions[1][39]:
                                    last_leaf_open = True
                                    last_leaf_open_seg = seg.SegmentNumber
                    if machine_type != 'BeamMod': 
                        self.Text3f.Text += "vérification seulement possible sur Beam Modulator / "
                    elif first_leaf_open and last_leaf_open:
                        self.Text3f.Text += "%s: première et dernère paire de lames ouvertes (segments %d et %d)" % (beam.Name, first_leaf_open_seg+1, last_leaf_open_seg+1)
                        warning_text += "AVERTISSEMENT: Première et dernière paires de lames ouvertes, PTV potentiellement trop large pour collimateur\n"
                    elif first_leaf_open and not last_leaf_open:
                        self.Text3f.Text += "%s: première paire de lames ouvertes (segment %d) / " % (beam.Name, first_leaf_open_seg+1)
                        warning_text += "AVERTISSEMENT: Première paire de lames ouvertes dans %s, il est peut-être nécessaire de déplacer l'isocentre\n" % beam.Name
                    elif not first_leaf_open and last_leaf_open:
                        self.Text3f.Text += "%s: dernière paire de lames ouvertes (segment %d) / " % (beam.Name, last_leaf_open_seg+1)
                        warning_text += "AVERTISSEMENT: Dernière paire de lames ouvertes dans %s, il est peut-être nécessaire de déplacer l'isocentre\n" % beam.Name
                    elif not first_leaf_open and not last_leaf_open:
                        self.Text3f.Text += beam.Name + ": fermées / "
                except:
                    self.Text3f.Text += beam.Name + " n'a pas de segments valides / "
            if self.Text3f.Text[-3:] == " / ":
                self.Text3f.Text = self.Text3f.Text[:-3]
  
            # Print warning messages
            self.avertissement.Text = warning_text    
           
            
              
            
        def cancelClicked(self, sender, args):
            self.Close()
             
        def setupButtonPanel(self):
            self.ButtonPanel = self.smallPanel(0, 770)

            okButton = Button()
            okButton.Text = "Vérifier"
            okButton.Location = Point(200, 50)
            self.AcceptButton = okButton
            okButton.Click += self.okClicked
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(okButton.Left + okButton.Width + 10, okButton.Top)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked

            self.ButtonPanel.Controls.Add(okButton)
            self.ButtonPanel.Controls.Add(cancelButton)

            self.beamset_comboBox = ComboBox()
            self.beamset_comboBox.Parent = self
            self.beamset_comboBox.Size = Size(160,40)
            self.beamset_comboBox.Location = Point(25, 821)
            self.beamset_comboBox.Text = beamset.DicomPlanLabel
            #self.beamset_comboBox.SelectionChangeCommitted += self.comboBox_changed    #I might need to comment this out again, it's working backwards      
            for bs in plan.BeamSets:
                self.beamset_comboBox.Items.Add(bs.DicomPlanLabel)
 
            okButton.PerformClick() # This automatically clicks OK, running a verification on the default (current) beamset
    
    #Check if Malik is running the script (for custom insult)
    if os.getenv('USERNAME') == 'hmr30968':
        custom_error = ", espèce de hipster"
    elif os.getenv('USERNAME') == 'hmr30489':
        custom_error = ", chef"
    else:
        custom_error = ""
    
    
    #Check for common errors while importing patient, plan, beamset and examination
    try:
        patient = lib.get_current_patient()
    except:
        debug_window('Aucun patient sélectionné'+custom_error)
        return                
    try:
        plan = lib.get_current_plan()
    except:
        debug_window('Aucun plan sélectionné'+custom_error)
        return
    try:
        beamset = lib.get_current_beamset()
    except:
        debug_window('Aucun beamset sélectionné'+custom_error)
        return        
    try:
        exam = lib.get_current_examination()
    except:
        debug_window('Aucun examination trouvé'+custom_error)
        return
    
    #Beamset numbering usually starts at 1, but in some cases it starts at 0 - this causes problems when verifying Plan Optimization parameters
    if beamset.Number == 0:
        debug_window('Warning: unusually-numbered beamset. Please verify plan without the script')
        return
    """
    if beamset.DeliveryTechnique == "SMLC":
        debug_window('Warning: SMLC plan detected. Verification script currently only supports VMAT plans.')
        return
    """
    form = VerificationWindow()
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
            self.doselabel.Text = "Dose (Gy) "
            self.doselabel.Location = Point(240, 20)
            self.doselabel.Font = Font("Arial", 9)
            self.doselabel.AutoSize = True              
            
            self.fxlabel = Label()
            self.fxlabel.Text = "Nb de fx "
            self.fxlabel.Location = Point(320, 20)
            self.fxlabel.Font = Font("Arial", 9)
            self.fxlabel.AutoSize = True                 

            self.dose_value = TextBox()
            self.dose_value.Text = "- - -"
            self.dose_value.Location = Point(240, offset)
            self.dose_value.Width = 40              

            self.fx_value = TextBox()
            self.fx_value.Text = "- - -"
            self.fx_value.Location = Point(320, offset)
            self.fx_value.Width = 40                      
                        
            CreatePlanButton = Button()
            CreatePlanButton.Text = "Créér plan"
            CreatePlanButton.Location = Point(440, offset - 2)
            CreatePlanButton.Width = 120 
            CreatePlanButton.Click += self.CreatePlanButtonClicked     

            self.plan_warning = Label()
            self.plan_warning.Text = "Pré-réquis: PTV15 ou PTV18, CERVEAU, ISO ou REF SCAN"
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
            self.MainWindow.Controls.Add(self.PTVcombo)
            self.MainWindow.Controls.Add(self.dose_value)
            self.MainWindow.Controls.Add(self.fx_value)            
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
            nb_fx = self.fx_value.Text
            self.plan_warning.Text = "Ne touchez pas à RayStation pendant l'execution du script!"
            self.message.Text = "Création du plan en cours"
            crane.plan_crane_3DC(site_name='A1', presc_dose=presc_dose, nb_fx=nb_fx, isodose_creation = isodose_creation, opt_collimator_angles = opt_collimator_angles)
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
            else:
                self.plan_warning.Text = "Le PTV doit s'appeler PTV15 ou PTV18"                 
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
                if roi.Name in ['PTV15','PTV18']:
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
            self.Text = "Première vérification"

            self.Width = 535
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
                     planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
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
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 800
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') #+ "                  Plan: " + plan.Name + "                  Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 35
            offset = 20   
            
            self.label_bonscan = Label()
            self.label_bonscan.Text = "Le bon scan est utilisé pour la planification"
            self.label_bonscan.Location = Point(25, offset)
            self.label_bonscan.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_bonscan.AutoSize = True              
            
            self.check_bonscan = CheckBox()
            self.check_bonscan.Location = Point(480, offset)
            self.check_bonscan.Width = 30
            self.check_bonscan.Checked = False        

            
       
            self.label_scanOK = Label()
            self.label_scanOK.Text = "Scan OK (artéfactes, étendu du scan, objets sur la table)"
            self.label_scanOK.Location = Point(25, offset + vert_spacer)
            self.label_scanOK.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_scanOK.AutoSize = True              
            
            self.check_scanOK = CheckBox()
            self.check_scanOK.Location = Point(480, offset + vert_spacer)
            self.check_scanOK.Width = 30
            self.check_scanOK.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External'"
            button_ext.Font = Font("Arial", 11, FontStyle.Bold)
            button_ext.Location = Point(25, offset + vert_spacer*2)
            button_ext.Width = 410 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(480, offset + vert_spacer*2)
            self.check_ext.Width = 30
            self.check_ext.Checked = False   
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre"
            button_isoOK.Font = Font("Arial", 11, FontStyle.Bold)
            button_isoOK.Location = Point(25, offset + vert_spacer*3)
            button_isoOK.Width = 410 
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(480, offset + vert_spacer*3)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False              
           

           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 11, FontStyle.Bold)
            button_beams_Rx.Location = Point(25, offset + vert_spacer*4)
            button_beams_Rx.Width = 410 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(480, offset + vert_spacer*4)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              
         
         
         
            self.label_contours = Label()
            self.label_contours.Text = "Les contours sont corrects"
            self.label_contours.Location = Point(25, offset + vert_spacer*5)
            self.label_contours.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_contours.AutoSize = True              
            
            self.check_contours = CheckBox()
            self.check_contours.Location = Point(480, offset + vert_spacer*5)
            self.check_contours.Width = 30
            self.check_contours.Checked = False              

            
            
            button_optimisation = Button()
            button_optimisation.Text = "Objectifs et paramètres d'optimisation"
            button_optimisation.Font = Font("Arial", 11, FontStyle.Bold)
            #button_optimisation.TextAlign = HorizontalAlignment.Center
            button_optimisation.Location = Point(25, offset + vert_spacer*6)
            button_optimisation.Width = 410 
            button_optimisation.Click += self.button_opt_Clicked          
            
            self.check_optimisation = CheckBox()
            self.check_optimisation.Location = Point(480, offset + vert_spacer*6)
            self.check_optimisation.Width = 30
            self.check_optimisation.Checked = False                  


            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(25, offset + vert_spacer*7)
            self.label_distribution_dose.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(480, offset + vert_spacer*7)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         


            self.label_results_header = Label()
            self.label_results_header.Text = ""
            self.label_results_header.Location = Point(25, offset + vert_spacer*9)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = ""
            self.label_results.Location = Point(25, offset + vert_spacer*10)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = ""
            self.label_reminder.Location = Point(25, offset + vert_spacer*11)
            self.label_reminder.Font = Font("Arial", 11, FontStyle.Bold)
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
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
            self.label_reminder.Text = "Rappel:\nVérifiez que la table (ou la planche ORL) est comprise dans\nle contour External avant de procéder à la prochaine étape"
            self.message.Text = ""

        def button_isoOK_Clicked(self, sender, args):
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            #self.label_results.Text = d['presc_text']
            #d['iso_text'] = a #+ "\n" + b + "\n" + c + "\n\n" + d
            #self.label_results.Text = d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 110)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
            self.label_reminder.Text = ""
            self.label_results.Text = ""
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification de la prescription en cours"
            self.d['presc_text'] = verification.verify_prescription()
            self.label_results.Text = self.d['presc_text']
            self.message.Text = "Vérification des faisceaux en cours"
            a,b,c,d,e = verification.verify_beams()   #d and e are not needed for a first verification (machine type and energy)
            self.d['beam_text'] = a + "\n\n" + c  
            self.label_results.Text += "\n\nFaisceaux:\n" + self.d['beam_text']
            #self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 80 + 15*b)
            self.message.Text = ""

        def button_opt_Clicked(self, sender, args):       
            self.label_results_header.Text = "Résultats"
            self.message.Text = "Vérification des paramètres d'optimisation"              
            a,b,c,d = verification.verify_opt_parameters()
            self.d['opt_text']  = a + "\n" + b + "\n" + d + "\n" + c   
            self.label_results.Text = self.d['opt_text']
            #d['opt_text'] = a + "\n" + b + "\n" + d + "\n" + c
            #self.label_results.Text = d['opt_text'] 
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 90)
            self.label_reminder.Text = "Rappel:\nVérifier tout les objectifs d'optimisation avant de\nprocéder à la prochaine étape"
            self.message.Text = ""            
            
        def cancelClicked(self, sender, args):
            self.Close()          
            
            
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
            self.OKbuttonPanel = self.miniPanel(0, 900)
            
            printButton = Button()
            printButton.Text = "Imprimer"
            printButton.Location = Point(25, 10)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(110,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(200, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(printButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
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
        debug_window('Sauvegarder le plan avant de rouler la vérification')
        return        
              
    form = Verif1Window()
    Application.Run(form)   
     
   
def verification_finale():

    class Verif1Window(Form):
        def __init__(self):
            self.Text = "Vérification finale"

            self.Width = 535
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
                     planned_by_name = lib.get_user_name(patient.ModificationInfo.UserName.Split('\\')[1]),
                     verified_by_name = lib.get_user_name(os.getenv('USERNAME')),
                     ext_text = "Script pas roulé",
                     grid_text = "Script pas roulé",
                     DSP_text = "Script pas roulé",
                     iso_text = "Script pas roulé",
                     beam_text = "Script pas roulé",
                     presc_text = "Script pas roulé",
                     segments_text = "Script pas roulé",
                     check_scanOK = "Pas vérifié",
                     check_ext = "Pas vérifié",
                     check_isoOK = "Pas vérifié",
                     check_grid = "Pas vérifié",                     
                     check_beams_Rx = "Pas vérifié",
                     check_segments = "Pas vérifié",
                     check_distribution_dose = "Pas vérifié",
                     check_DSP = "Pas vérifié")
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 800
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 535
            panel.Height = 60
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupHeaderWindow(self):
            self.HeaderWindow = self.miniPanel(0, 0)     

            self.PatientIDHeader = Label()
            self.PatientIDHeader.Text = "Patient: " + patient.PatientName.replace('^', ', ') #+ "                  Plan: " + plan.Name + "                  Beamset: " + beamset.DicomPlanLabel
            self.PatientIDHeader.Location = Point(25, 25)
            self.PatientIDHeader.Font = Font("Arial", 12, FontStyle.Bold)
            self.PatientIDHeader.AutoSize = True          

            self.HeaderWindow.Controls.Add(self.PatientIDHeader)
            
        def setupMainWindow(self):
            self.MainWindow = self.Panel(0, 60)
            
            vert_spacer = 35
            offset = 20   

            
            self.label_scanOK = Label()
            self.label_scanOK.Text = "Scan OK (étendu du scan)"
            self.label_scanOK.Location = Point(25, offset)
            self.label_scanOK.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_scanOK.AutoSize = True              
            
            self.check_scanOK = CheckBox()
            self.check_scanOK.Location = Point(480, offset)
            self.check_scanOK.Width = 30
            self.check_scanOK.Checked = False   

            
            
            button_ext = Button()
            button_ext.Text = "Contour 'External' et overrides"
            button_ext.Font = Font("Arial", 11, FontStyle.Bold)
            button_ext.Location = Point(25, offset + vert_spacer)
            button_ext.Width = 410 
            button_ext.Click += self.button_ext_Clicked                 
            
            self.check_ext = CheckBox()
            self.check_ext.Location = Point(480, offset + vert_spacer)
            self.check_ext.Width = 30
            self.check_ext.Checked = False   
           
           
           
            button_isoOK = Button()
            button_isoOK.Text = "Position de l'isocentre et point de localisation"
            button_isoOK.Font = Font("Arial", 11, FontStyle.Bold)
            button_isoOK.Location = Point(25, offset + vert_spacer*2)
            button_isoOK.Width = 410 
            button_isoOK.Click += self.button_isoOK_Clicked     

            self.check_isoOK = CheckBox()
            self.check_isoOK.Location = Point(480, offset + vert_spacer*2)
            self.check_isoOK.Width = 30
            self.check_isoOK.Checked = False              
           

           
            button_grid = Button()
            button_grid.Text = "La grille de dose est correcte"
            button_grid.Font = Font("Arial", 11, FontStyle.Bold)
            button_grid.Location = Point(25, offset + vert_spacer*3)
            button_grid.Width = 410 
            button_grid.Click += self.button_grid_Clicked              
                    
            self.check_grid = CheckBox()
            self.check_grid.Location = Point(480, offset + vert_spacer*3)
            self.check_grid.Width = 30
            self.check_grid.Checked = False              

            
           
            button_beams_Rx = Button()
            button_beams_Rx.Text = "Faisceaux et prescription"
            button_beams_Rx.Font = Font("Arial", 11, FontStyle.Bold)
            button_beams_Rx.Location = Point(25, offset + vert_spacer*4)
            button_beams_Rx.Width = 410 
            button_beams_Rx.Click += self.button_beams_Clicked          
            
            self.check_beams_Rx = CheckBox()
            self.check_beams_Rx.Location = Point(480, offset + vert_spacer*4)
            self.check_beams_Rx.Width = 30
            self.check_beams_Rx.Checked = False              
         
         
         
            button_segments = Button()
            button_segments.Text = "Les segments sont corrects/flashé au besoin"
            button_segments.Font = Font("Arial", 11, FontStyle.Bold)
            button_segments.Location = Point(25, offset + vert_spacer*5)
            button_segments.Width = 410 
            button_segments.Click += self.button_segments_Clicked                        
            
            self.check_segments = CheckBox()
            self.check_segments.Location = Point(480, offset + vert_spacer*5)
            self.check_segments.Width = 30
            self.check_segments.Checked = False                      


            
            self.label_distribution_dose = Label()
            self.label_distribution_dose.Text = "Distribution de dose et clinical goals"
            self.label_distribution_dose.Location = Point(25, offset + vert_spacer*6)
            self.label_distribution_dose.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_distribution_dose.AutoSize = True              
            
            self.check_distribution_dose = CheckBox()
            self.check_distribution_dose.Location = Point(480, offset + vert_spacer*6)
            self.check_distribution_dose.Width = 30
            self.check_distribution_dose.Checked = False         

            
            
            self.label_DSP = Label()
            self.label_DSP.Text = "Notez le HT et les DSP"
            self.label_DSP.Location = Point(25, offset + vert_spacer*7)
            self.label_DSP.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_DSP.AutoSize = True              
            
            self.check_DSP = CheckBox()
            self.check_DSP.Location = Point(480, offset + vert_spacer*7)
            self.check_DSP.Width = 30
            self.check_DSP.Checked = False        
            
            
            
            self.label_results_header = Label()
            self.label_results_header.Text = ""
            self.label_results_header.Location = Point(25, offset + vert_spacer*9)
            self.label_results_header.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_results_header.AutoSize = True     
            
            self.label_results = Label()
            self.label_results.Text = ""
            self.label_results.Location = Point(25, offset + vert_spacer*10)
            self.label_results.Font = Font("Arial", 10,)
            self.label_results.AutoSize = True             

            self.label_reminder = Label()
            self.label_reminder.Text = ""
            self.label_reminder.Location = Point(25, offset + vert_spacer*11)
            self.label_reminder.Font = Font("Arial", 11, FontStyle.Bold)
            self.label_reminder.ForeColor = Color.Red
            self.label_reminder.AutoSize = True                 
            
            
           
            self.MainWindow.Controls.Add(self.label_scanOK)
            self.MainWindow.Controls.Add(self.check_scanOK)  
            
            self.MainWindow.Controls.Add(button_ext)  
            self.MainWindow.Controls.Add(self.check_ext)            
            
            self.MainWindow.Controls.Add(button_isoOK)   
            self.MainWindow.Controls.Add(self.check_isoOK)     
            
            self.MainWindow.Controls.Add(button_grid)
            self.MainWindow.Controls.Add(self.check_grid)              
            
            self.MainWindow.Controls.Add(button_beams_Rx)            
            self.MainWindow.Controls.Add(self.check_beams_Rx)
                      
            self.MainWindow.Controls.Add(button_segments)
            self.MainWindow.Controls.Add(self.check_segments)               
            
            self.MainWindow.Controls.Add(self.label_distribution_dose)
            self.MainWindow.Controls.Add(self.check_distribution_dose)            

            self.MainWindow.Controls.Add(self.label_DSP)
            self.MainWindow.Controls.Add(self.check_DSP)               
            
            self.MainWindow.Controls.Add(self.label_results_header)
            self.MainWindow.Controls.Add(self.label_results)
            self.MainWindow.Controls.Add(self.label_reminder)            
                        
            
        def button_ext_Clicked(self, sender, args):  
            self.message.ForeColor = Color.Black        
            self.message.Text = "Vérification du contour External en cours"
            self.d['ext_text'] = verification.verify_external_and_overrides()
            self.label_results_header.Text = "Résultats"
            self.label_results.Text = self.d['ext_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 50)
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
            self.message.ForeColor = Color.Black
            self.message.Text = "Vérification de l'isocentre"
            a,b,c,d = verification.verify_isocenter()
            self.label_results_header.Text = "Résultats"
            self.d['iso_text'] = a + "\n" + b + "\n" + c + "\n\n" + d
            self.label_results.Text = self.d['iso_text']
            self.label_reminder.Location = Point(self.label_results.Left, self.label_results.Top + 110)
            self.label_reminder.Text = "Rappel:\nVérifiez le placement de l'isocentre en mode BEV avant de\nprocéder à la prochaine étape"
            self.message.Text = ""
            
        def button_beams_Clicked(self, sender, args):       
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
            self.label_reminder.Text = "Rappel:\nS'il y a un prothèse, un pacemaker ou un membre qui dépasse le\nFOV du scan, vérifiez que les angles de gantry sont bien choisis"
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
            
        def cancelClicked(self, sender, args):
            self.Close()          
            
            
        def printClicked(self, sender, args):     

            #Verify that all boxes have been checked
            warning = False
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
            if self.check_DSP.Checked:
                self.d['check_DSP'] = 'OK'
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
            printButton.Location = Point(25, 10)
            #self.AcceptButton = okButton
            printButton.Click += self.printClicked            
            
            cancelButton = Button()
            cancelButton.Text = "Annuler"
            cancelButton.Location = Point(110,10)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked
            
            self.message = Label()
            self.message.Text = ""
            self.message.Location = Point(200, 13)
            self.message.Font = Font("Arial", 11, FontStyle.Bold)
            self.message.AutoSize = True      
            
            self.OKbuttonPanel.Controls.Add(printButton)
            self.OKbuttonPanel.Controls.Add(cancelButton)
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
        debug_window('Sauvegarder le plan avant de rouler la vérification')
        return
        
    form = Verif1Window()
    Application.Run(form)   
    
