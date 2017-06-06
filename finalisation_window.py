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



import verification
import report
import statistics
import message


clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

    
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
        message.message_window('Aucun patient sélectionné')
        return                
    try:
        plan = lib.get_current_plan()
    except:
        message.message_window('Aucun plan sélectionné')
        return  
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
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

