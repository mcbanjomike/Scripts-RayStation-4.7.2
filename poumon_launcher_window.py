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

#GUI stuff
import clr
import System.Array

import poumon
import crane #for the custom max dose function
import verification
import report
import statistics
import message

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

def poumon_launcher():

    class PoumonLauncher(Form):
        def __init__(self):
            self.Text = "Plan de poumon VMAT"

            self.Width = 700
            self.Height = 900

            self.setupHeaderWindow()
            self.setupMainWindow()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            
            #Automatically populate ROI selection comboboxes
            self.PTV1combo.Items.Add("Choisissez")
            self.PTV2combo.Items.Add("Choisissez")  
            self.ITV1combo.Items.Add("Choisissez")
            self.ITV2combo.Items.Add("Choisissez")              
            self.OAR1combo.Items.Add("Choisissez OAR")
            self.OAR2combo.Items.Add("Choisissez OAR")
            self.OAR3combo.Items.Add("Choisissez OAR")
            for roi in patient.PatientModel.RegionsOfInterest:       
                if 'PTV' in roi.Name.upper():
                    self.PTV1combo.Items.Add(roi.Name)
                    self.PTV2combo.Items.Add(roi.Name)  
                elif 'ITV' in roi.Name.upper():
                    self.ITV1combo.Items.Add(roi.Name)
                    self.ITV2combo.Items.Add(roi.Name)               
                else:
                    self.OAR1combo.Items.Add(roi.Name)
                    self.OAR2combo.Items.Add(roi.Name)
                    self.OAR3combo.Items.Add(roi.Name)
                    
            #Determine whether to add dose color table by looking for existing plans
            try:
                existing_plan = patient.TreatmentPlans[0]
                self.isodosecombo.SelectedIndex = self.isodosecombo.FindStringExact('Ne pas créer')
            except:
                self.isodosecombo.SelectedIndex = self.isodosecombo.FindStringExact('Créer')
                
            
        def Panel(self, x, y):
            panel = Panel()
            panel.Width = 700
            panel.Height = 800
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
            offset = 20   
            
            #self.toplabel = Label()
            #self.toplabel.Text = "PTV           ITV         Isocentre      Site"
            #self.toplabel.Font = Font("Arial", 10, FontStyle.Bold)
            #self.toplabel.Location = Point(30, 20)
            #self.toplabel.AutoSize = True  

            self.PTVlabel = Label()
            self.PTVlabel.Text = "PTV"
            self.PTVlabel.Location = Point(25, offset)
            self.PTVlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.PTVlabel.AutoSize = True    
            
            self.PTV1combo = ComboBox()
            self.PTV1combo.Parent = self
            self.PTV1combo.Size = Size(80,40)
            self.PTV1combo.Location = Point(80, offset)
            self.PTV1combo.Text = "Choisissez" 
            self.PTV1combo.TextChanged += self.PTV1selectionChanged

            self.PTV2combo = ComboBox()
            self.PTV2combo.Parent = self
            self.PTV2combo.Size = Size(80,40)
            self.PTV2combo.Location = Point(170, offset)
            self.PTV2combo.Text = "Choisissez"             
            

            
            self.ITVlabel = Label()
            self.ITVlabel.Text = "ITV"
            self.ITVlabel.Location = Point(25, offset + vert_spacer)
            self.ITVlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.ITVlabel.AutoSize = True               
            
            self.ITV1combo = ComboBox()
            self.ITV1combo.Parent = self
            self.ITV1combo.Size = Size(80,40)
            self.ITV1combo.Location = Point(80, offset + vert_spacer)
            self.ITV1combo.Text = "Choisissez" 
            
            self.ITV2combo = ComboBox()
            self.ITV2combo.Parent = self
            self.ITV2combo.Size = Size(80,40)
            self.ITV2combo.Location = Point(170, offset + vert_spacer)
            self.ITV2combo.Text = "Choisissez"               
            
            
            
            self.isolabel = Label()
            self.isolabel.Text = "Iso"
            self.isolabel.Location = Point(25, offset + 2*vert_spacer)
            self.isolabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.isolabel.AutoSize = True               
            
            self.isocombo = ComboBox()
            self.isocombo.Parent = self
            self.isocombo.Size = Size(80,40)
            self.isocombo.Location = Point(80, offset + 2*vert_spacer)
            for poi in patient.PatientModel.PointsOfInterest:
                self.isocombo.Items.Add(poi.Name)
                if poi.Name == 'ISO':
                    self.isocombo.Text = 'ISO'
                elif self.isocombo.Text != 'ISO' and poi.Name == 'REF SCAN':
                    self.isocombo.Text = 'REF SCAN'            
                    
            self.isocombo2 = ComboBox()
            self.isocombo2.Parent = self
            self.isocombo2.Size = Size(80,40)
            self.isocombo2.Location = Point(170, offset + 2*vert_spacer)
            for poi in patient.PatientModel.PointsOfInterest:
                self.isocombo2.Items.Add(poi.Name)
                if poi.Name == 'ISO':
                    self.isocombo2.Text = 'ISO'
                elif self.isocombo2.Text != 'ISO' and poi.Name == 'REF SCAN':
                    self.isocombo2.Text = 'REF SCAN'                          
                    
                    
                    
            self.sitelabel = Label()
            self.sitelabel.Text = "Site"
            self.sitelabel.Location = Point(25, offset + 3*vert_spacer)
            self.sitelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.sitelabel.AutoSize = True                       
                    
            self.sitebox = TextBox()
            self.sitebox.Parent = self
            self.sitebox.Size = Size(80,40)
            self.sitebox.Location = Point(80, offset + 3*vert_spacer)
            self.sitebox.Text = "A1" 
        
            self.sitebox2 = TextBox()
            self.sitebox2.Parent = self
            self.sitebox2.Size = Size(80,40)
            self.sitebox2.Location = Point(170, offset + 3*vert_spacer)
            self.sitebox2.Text = ""                      
            


            self.techlabel = Label()
            self.techlabel.Text = "Tech"
            self.techlabel.Location = Point(25, offset + 4*vert_spacer)
            self.techlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.techlabel.AutoSize = True              
            
            self.techcombo = ComboBox()
            self.techcombo.Parent = self
            self.techcombo.Size = Size(80,40)
            self.techcombo.Location = Point(80, offset + 4*vert_spacer)
            self.techcombo.Text = "VMAT" 
            self.techcombo.Items.Add('VMAT')    
            self.techcombo.Items.Add('IMRT')            
            
            self.techcombo2 = ComboBox()
            self.techcombo2.Parent = self
            self.techcombo2.Size = Size(80,40)
            self.techcombo2.Location = Point(170, offset + 4*vert_spacer)
            self.techcombo2.Text = "VMAT" 
            self.techcombo2.Items.Add('VMAT')    
            self.techcombo2.Items.Add('IMRT')               
         

            self.doselabel = Label()
            self.doselabel.Text = "Dose (Gy)"
            self.doselabel.Location = Point(25, offset + 5.25*vert_spacer)
            self.doselabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.doselabel.AutoSize = True    
         
            self.dose_value = TextBox()
            self.dose_value.Text = ""
            self.dose_value.Location = Point(150, offset + 5.25*vert_spacer)
            self.dose_value.Width = 50 
         
         
            self.fxlabel = Label()
            self.fxlabel.Text = "Nb de fx"
            self.fxlabel.Location = Point(25, offset + 6.25*vert_spacer)
            self.fxlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.fxlabel.AutoSize = True              
            
            self.fxbox = TextBox()
            self.fxbox.Parent = self
            self.fxbox.Size = Size(50,40)
            self.fxbox.Location = Point(150, offset + 6.25*vert_spacer)
            self.fxbox.Text = ""                 

            
            evalButton = Button()
            evalButton.Text = "Évaluer les PTVs"
            evalButton.Location = Point(25, offset + 7.5 * vert_spacer)
            evalButton.Width = 230
            evalButton.Click += self.evalClicked   
            
            
            self.scanlabel = Label()
            self.scanlabel.Text = "CT de planif"
            self.scanlabel.Location = Point(25, offset + 9*vert_spacer)
            self.scanlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.scanlabel.AutoSize = True              
            
            self.scancombo = ComboBox()
            self.scancombo.Parent = self
            self.scancombo.Size = Size(90,40)
            self.scancombo.Location = Point(150, offset + 9*vert_spacer)
            for ct in patient.Examinations:
                self.scancombo.Items.Add(ct.Name)         
                if ct.Name == 'CT 1':
                    self.scancombo.Text = 'CT 1'
            
            
            self.machinelabel = Label()
            self.machinelabel.Text = "Appareil"
            self.machinelabel.Location = Point(25, offset + 10*vert_spacer)
            self.machinelabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.machinelabel.AutoSize = True              
            
            self.machinecombo = ComboBox()
            self.machinecombo.Parent = self
            self.machinecombo.Size = Size(90,40)
            self.machinecombo.Location = Point(150, offset + 10*vert_spacer)
            self.machinecombo.Text = "BeamMod"                  
            self.machinecombo.Items.Add('BeamMod')
            self.machinecombo.Items.Add('Infinity')
            

            self.isodoselabel = Label()
            self.isodoselabel.Text = "Dose table"
            self.isodoselabel.Location = Point(25, offset + 11*vert_spacer)
            self.isodoselabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.isodoselabel.AutoSize = True              
            
            self.isodosecombo = ComboBox()
            self.isodosecombo.Parent = self
            self.isodosecombo.Size = Size(90,40)
            self.isodosecombo.Location = Point(150, offset + 11*vert_spacer)
            self.isodosecombo.Text = "Créer"                  
            self.isodosecombo.Items.Add('Créer')            
            self.isodosecombo.Items.Add('Ne pas créer')            
         

            
            self.message = Label()
            self.message.Text = "Sélectionnez le(s) ROI(s) à traiter. Seulement les ROIs\navec PTV ou ITV dans leurs noms sont disponibles.\n\nSi vous planifiez pour un seul PTV, utilisez la colonne\nde gauche.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSeulement le PTV de gauche sera considéré pour un plan falloff"
            self.message.Location = Point(300, offset)
            self.message.Font = Font("Arial", 11, FontStyle.Italic)
            self.message.AutoSize = True                
            
            self.status = Label()
            self.status.Text = ""
            self.status.Location = Point(25, 760)
            self.status.Font = Font("Arial", 11, FontStyle.Bold)
            self.status.AutoSize = True    
            

            self.OARlabel = Label()
            self.OARlabel.Text = "Max doses custom (Gy)"
            self.OARlabel.Location = Point(25, offset + 13*vert_spacer)
            self.OARlabel.Font = Font("Arial", 10, FontStyle.Bold)
            self.OARlabel.AutoSize = True              
            
            self.OAR1combo = ComboBox()
            self.OAR1combo.Parent = self
            self.OAR1combo.Size = Size(120,40)
            self.OAR1combo.Location = Point(25, offset + 14*vert_spacer)
            self.OAR1combo.Text = "Choisissez OAR"     

            self.OAR1_value = TextBox()
            self.OAR1_value.Text = ""
            self.OAR1_value.Location = Point(160, offset + 14*vert_spacer)
            self.OAR1_value.Width = 50                  
            
            self.OAR2combo = ComboBox()
            self.OAR2combo.Parent = self
            self.OAR2combo.Size = Size(120,40)
            self.OAR2combo.Location = Point(25, offset + 15*vert_spacer)
            self.OAR2combo.Text = "Choisissez OAR"     
            
            self.OAR2_value = TextBox()
            self.OAR2_value.Text = ""
            self.OAR2_value.Location = Point(160, offset + 15*vert_spacer)
            self.OAR2_value.Width = 50                
            
            self.OAR3combo = ComboBox()
            self.OAR3combo.Parent = self
            self.OAR3combo.Size = Size(120,40)
            self.OAR3combo.Location = Point(25, offset + 16*vert_spacer)
            self.OAR3combo.Text = "Choisissez OAR"                 
            
            self.OAR3_value = TextBox()
            self.OAR3_value.Text = ""
            self.OAR3_value.Location = Point(160, offset + 16*vert_spacer)
            self.OAR3_value.Width = 50    


            

            self.stepcombo = ComboBox()
            self.stepcombo.Parent = self
            self.stepcombo.Size = Size(200,40)
            self.stepcombo.Location = Point(25, offset + 19 * vert_spacer)
            self.stepcombo.Text = "1 plan"  
            self.stepcombo.Items.Add('1 plan')        
            self.stepcombo.Items.Add('1 plan (colli 90)')             
            self.stepcombo.Items.Add('2 plans sur 1 isocentre')            
            self.stepcombo.Items.Add('2 plans sur 2 isocentres')                
            
            
            addplanButton = Button()
            addplanButton.Text = "Ajouter plan"
            addplanButton.Location = Point(25, offset + 20 * vert_spacer)
            addplanButton.Width = 200
            addplanButton.Click += self.addplanClicked   

            
            addKBPplanButton = Button()
            addKBPplanButton.Text = "Ajouter plan falloff (TEST)"
            addKBPplanButton.Location = Point(25, offset + 22 * vert_spacer)
            addKBPplanButton.Width = 200
            addKBPplanButton.Click += self.addKBPplanClicked              
            
            
            
            
            #self.MainWindow.Controls.Add(self.toplabel)
            self.MainWindow.Controls.Add(self.PTVlabel)
            self.MainWindow.Controls.Add(self.PTV1combo)
            self.MainWindow.Controls.Add(self.PTV2combo)
            
            self.MainWindow.Controls.Add(self.ITVlabel)
            self.MainWindow.Controls.Add(self.ITV1combo)
            self.MainWindow.Controls.Add(self.ITV2combo)
            
            self.MainWindow.Controls.Add(self.isolabel)
            self.MainWindow.Controls.Add(self.isocombo) 
            self.MainWindow.Controls.Add(self.isocombo2)
            
            self.MainWindow.Controls.Add(self.sitelabel)
            self.MainWindow.Controls.Add(self.sitebox)
            self.MainWindow.Controls.Add(self.sitebox2)
            
            self.MainWindow.Controls.Add(self.techlabel)          
            self.MainWindow.Controls.Add(self.techcombo)    
            self.MainWindow.Controls.Add(self.techcombo2)            

            self.MainWindow.Controls.Add(self.dose_value)
            self.MainWindow.Controls.Add(self.doselabel)
            
            self.MainWindow.Controls.Add(self.fxlabel)
            self.MainWindow.Controls.Add(self.fxbox)             
            
            self.MainWindow.Controls.Add(self.scanlabel)          
            self.MainWindow.Controls.Add(self.scancombo)    
            
            self.MainWindow.Controls.Add(self.machinelabel)          
            self.MainWindow.Controls.Add(self.machinecombo)          

            self.MainWindow.Controls.Add(self.isodoselabel)          
            self.MainWindow.Controls.Add(self.isodosecombo)               
            
            self.MainWindow.Controls.Add(self.OARlabel)
            self.MainWindow.Controls.Add(self.OAR1combo)
            self.MainWindow.Controls.Add(self.OAR1_value)
            self.MainWindow.Controls.Add(self.OAR2combo)
            self.MainWindow.Controls.Add(self.OAR2_value)
            self.MainWindow.Controls.Add(self.OAR3combo)
            self.MainWindow.Controls.Add(self.OAR3_value)
            
            self.MainWindow.Controls.Add(self.message)            
            self.MainWindow.Controls.Add(self.status)     

            self.MainWindow.Controls.Add(evalButton)
            self.MainWindow.Controls.Add(addplanButton)            
            self.MainWindow.Controls.Add(addKBPplanButton) 
            
            self.MainWindow.Controls.Add(self.stepcombo) 
            
            #Label empty contours
            exam_list = []
            for CT in patient.Examinations:
                exam_list.append(CT.Name)            
            
            for contour in patient.PatientModel.RegionsOfInterest:
                VolCT1 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 1"])
                if "CT 2" in exam_list:
                    VolCT2 = roi.get_roi_volume(contour.Name, exam=patient.Examinations["CT 2"])
                else:
                    VolCT2 = 0

                if VolCT1 == 0 and VolCT2 == 0:
                    contour.Name = ("vide_" + contour.Name)            
        

        def PTV1selectionChanged(self, sender, args):            
            if self.PTV1combo.Text == 'PTV48':
                self.dose_value.Text = '48'
                self.fxbox.Text = '4'
                if roi.roi_exists('ITV48'):
                    self.ITV1combo.Text = 'ITV48'
            elif self.PTV1combo.Text == 'PTV54':
                self.dose_value.Text = '54'
                self.fxbox.Text = '3'
                if roi.roi_exists('ITV54'):
                    self.ITV1combo.Text = 'ITV54'
            elif self.PTV1combo.Text == 'PTV56':
                self.dose_value.Text = '56'
                self.fxbox.Text = '4'
                if roi.roi_exists('ITV56'):
                    self.ITV1combo.Text = 'ITV56'            
            elif self.PTV1combo.Text == 'PTV60':
                self.dose_value.Text = '60'
                self.fxbox.Text = ''
                if roi.roi_exists('ITV60'):
                    self.ITV1combo.Text = 'ITV60'
            else:
                self.dose_value.Text = ''
                self.fxbox.Text = ''
                self.ITV1combo.Text = 'Choisissez'                
            
            
        def compile_plan_data(self):            
                               
            self.status.Text = "Compilation des données du plan"      
            
            ptv_names = []
            itv_names = []
            iso_names = []
            site_names = []
            techniques = []
            custom_max = []
            laterality = []
            error_message = ""
            self.message.Text = ""
            
            if roi.roi_exists(self.PTV1combo.Text):       
                ptv_names.append(self.PTV1combo.Text)
                if roi.roi_exists(self.ITV1combo.Text):       
                    itv_names.append(self.ITV1combo.Text)
                else:
                    error_message = "ROI sélectionné pour ITV 1 introuvable"
                try:
                    if roi.find_most_intersecting_roi(self.PTV1combo.Text, ['POUMON DRT', 'POUMON GCHE'], examination=exam) == 'POUMON DRT':
                        laterality.append('DRT')
                    elif roi.find_most_intersecting_roi(self.PTV1combo.Text, ['POUMON DRT', 'POUMON GCHE'], examination=exam) == 'POUMON GCHE':
                        laterality.append('GCHE')
                except:
                    error_message = "Impossible de déterminer la latéralité du cible %s" % self.PTV1combo.Text

            if roi.roi_exists(self.PTV2combo.Text):       
                ptv_names.append(self.PTV2combo.Text)
                if roi.roi_exists(self.ITV2combo.Text):       
                    itv_names.append(self.ITV2combo.Text)
                else:
                    error_message = "ROI sélectionné pour ITV 2 introuvable"   
                try:
                    if roi.find_most_intersecting_roi(self.PTV2combo.Text, ['POUMON DRT', 'POUMON GCHE'], examination=exam) == 'POUMON DRT':
                        laterality.append('DRT')
                    elif roi.find_most_intersecting_roi(self.PTV2combo.Text, ['POUMON DRT', 'POUMON GCHE'], examination=exam) == 'POUMON GCHE':
                        laterality.append('GCHE')
                except:
                    error_message = "Impossible de déterminer la latéralité du cible %s" % self.PTV2combo.Text     
            
            if len(ptv_names) == 0:
                error_message = "Aucun PTV sélectionné"
            
            self.message.Text += "Vérification des PTVs"
            
            try:
                rx_dose = int(float(self.dose_value.Text) * 100)
            except:
                error_message = "Dose de prescription illisible"                   
            
            try:
                nb_fx = int(self.fxbox.Text)
            except:
                error_message = "Nb de fractions illisible"

            self.message.Text += "\nVérification de la prescription"
                
            if self.techcombo.Text == 'IMRT':
                techniques.append('SMLC')
            elif self.techcombo.Text == 'VMAT':
                techniques.append('VMAT')
            if self.techcombo2.Text == 'IMRT':
                techniques.append('SMLC')
            elif self.techcombo2.Text == 'VMAT':
                techniques.append('VMAT')                
                
            self.message.Text += "\nVérification de la technique"
            
            if poi.poi_exists(self.isocombo.Text,exam):
                iso_names.append(self.isocombo.Text)
            else:
                error_message = "Isocentre pas trouvé pour le premier PTV"
            if self.isocombo2.Text != '':
                if poi.poi_exists(self.isocombo2.Text,exam):
                    iso_names.append(self.isocombo2.Text)   
                else:
                    error_message = "Isocentre pas trouvé pour le deuxième PTV"                    
            
            if len(iso_names) == 0:
                error_message = "Choisissez un isocentre avant de continuer"
              
            self.message.Text += "\nVérification des isocentres"
                
            if self.scancombo.Text == '':
                error_message = "Choisissez un scan avant de continuer"        

            self.message.Text += "\nVérification du scan de planification"                
            
            
            if roi.roi_exists(self.OAR1combo.Text):
                try:
                    custom_max.append((self.OAR1combo.Text,float(self.OAR1_value.Text))) #Yes, you need all those parentheses for this to work
                except:
                    error_message = "Impossible de lire custom max dose 1"
            if roi.roi_exists(self.OAR2combo.Text):
                try:
                    custom_max.append((self.OAR2combo.Text,float(self.OAR2_value.Text)))
                except:
                    error_message = "Impossible de lire custom max dose 2"
            if roi.roi_exists(self.OAR3combo.Text):
                try:
                    custom_max.append((self.OAR3combo.Text,float(self.OAR3_value.Text)))
                except:
                    error_message = "Impossible de lire custom max dose 3"         
                

            oar_message = poumon.poumon_verify_oars(exam)
            if oar_message != '':
                error_message = 'OAR essentiel pas trouvé: ' + oar_message      

            self.message.Text += "\nVérification des OARs"
                
            if error_message != '': #In case of any error, abort and send error message back
                d = []
                return d,error_message
            
            
            #Compile plan data to send to scripts
            d = dict(patient = patient,
                     site_names = [self.sitebox.Text,self.sitebox2.Text],
                     exam = patient.Examinations[self.scancombo.Text],
                     iso_names = iso_names,
                     machine = self.machinecombo.Text,
                     nb_fx = nb_fx,
                     rx_dose = rx_dose,
                     ptv_names = ptv_names,
                     itv_names = itv_names,
                     laterality = laterality,
                     #oar_list = oar_list,
                     techniques = techniques,
                     custom_max = custom_max)      
            
            return d,error_message

            
        def evalClicked(self, sender, args):

            self.status.ForeColor = Color.Black
            self.status.Text = "Évaluation en cours, veuillez patienter"                 
            
            d,error_message = self.compile_plan_data()
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                 
            
            ptv_names = d['ptv_names']
            exam = d['exam']
            
            self.message.Text = ""
            
            for ptv in d['ptv_names']:
                bb = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv].GetBoundingBox()
                ptv_vol = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv].GetRoiVolume()
                dia = [abs(bb[0].x-bb[1].x),abs(bb[0].y-bb[1].y),abs(bb[0].z-bb[1].z)]
                self.message.Text += "Cible: %s\n   Vol (cc): %.2f\n   Dimensions: %.2fcm x %.2fcm x %.2fcm\n\n" % (ptv,ptv_vol,dia[0],dia[1],dia[2])
            
            self.message.Text += "\n\n"
            
            #For single PTV, the choice is simple
            if len(ptv_names) == 1:                
                self.message.Text += "Le VMAT devrait être utilisé pour ce plan"
                self.techcombo.Text = 'VMAT'            
            
            #For multiple PTVs... 
            elif len(ptv_names) > 1:       
                self.status.Text = "Évaluation de la distance entre les PTVs"            
                #...start by determining whether the PTVs are in different lungs
                if d['laterality'][0] != d['laterality'][1]:
                    self.message.Text += "Les PTVs ne sont pas dans le même poumon, \n   il faut traiter chacun avec son propre isocentre"
                    self.stepcombo.Text = '2 plans sur 2 isocentres'
                    self.sitebox.Text = "A1" 
                    self.sitebox2.Text = "B1"
                    if not roi.roi_exists("PAROI DRT"):
                        self.message.Text += "\nContour manquant: PAROI DRT"
                    if not roi.roi_exists("PAROI GCHE"):
                        self.message.Text += "\nContour manquant: PAROI GCHE"                        
                
                else:
                    #If they are in the same lung, determine whether the PTVs are close enough to treat with a single isocenter (limited by CBCT field of approx 20cm)            
                    center = poi.get_poi_coordinates(d['iso_names'][0],exam)
                    if not roi.roi_exists("zone_imagerie"):
                        patient.PatientModel.CreateRoi(Name="zone_imagerie", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
                    patient.PatientModel.RegionsOfInterest['zone_imagerie'].CreateCylinderGeometry(Radius=10, Axis={ 'x': 0, 'y': 0, 'z': 1 }, Length=20, Examination=exam, Center={ 'x': center.x, 'y': center.y, 'z': center.z })            
                    intersect1 = roi.subtract_rois(ptv_names[0], "zone_imagerie", color="Yellow", examination=exam, output_name="outside_vol_1")
                    intersect2 = roi.subtract_rois(ptv_names[1], "zone_imagerie", color="Yellow", examination=exam, output_name="outside_vol_2")
                    bb_ptv1 = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv_names[0]].GetBoundingBox()
                    bb_ptv2 = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries[ptv_names[1]].GetBoundingBox()
                    
                    #self.message.Text += "\nVolume de chaque PTV qui sort du cylindre: %.2f, %.2f" % (roi.get_roi_volume("outside_vol_1", exam),roi.get_roi_volume("outside_vol_2", exam))
                    
                    #If they don't fit into the 20cm cylinder, see if a new point will do the trick
                    if roi.get_roi_volume("outside_vol_1", exam) > 0 or roi.get_roi_volume("outside_vol_2", exam) > 0:
                        
                        #Create new isocenter based on the middle of the two PTVs bounding boxes
                        combined_bb_x = sorted([bb_ptv1[0].x,bb_ptv1[1].x,bb_ptv2[0].x,bb_ptv2[1].x])
                        combined_bb_y = sorted([bb_ptv1[0].y,bb_ptv1[1].y,bb_ptv2[0].y,bb_ptv2[1].y])
                        combined_bb_z = sorted([bb_ptv1[0].z,bb_ptv1[1].z,bb_ptv2[0].z,bb_ptv2[1].z])
                        
                        #Find coordinates of bounding box, determine shift relative to isocenter, round shift to nearest cm
                        shift_x = round((combined_bb_x[0]+combined_bb_x[3])/2 - center.x)
                        shift_y = round((combined_bb_y[0]+combined_bb_y[3])/2 - center.y)
                        shift_z = round((combined_bb_z[0]+combined_bb_z[3])/2 - center.z)
                        
                        #new_point_coords = lib.RSPoint((combined_bb_x[0]+combined_bb_x[3])/2,(combined_bb_y[0]+combined_bb_y[3])/2,(combined_bb_z[0]+combined_bb_z[3])/2)
                        new_point_coords = lib.RSPoint(round(center.x + shift_x,2),round(center.y + shift_y,2),round(center.z + shift_z,2))
                        
                        #Round coordinates to make nice displacements and prevents shifts of less than 1 cm
                        if not poi.poi_exists('Iso Auto',exam):
                            new_iso = poi.create_poi(new_point_coords, 'Iso Auto', color='Red', poi_type='Isocenter', examination=exam)
                        self.isocombo.Items.Add('Iso Auto')
                        self.isocombo2.Items.Add('Iso Auto')
                        
                        patient.PatientModel.RegionsOfInterest['zone_imagerie'].CreateCylinderGeometry(Radius=10, Axis={ 'x': 0, 'y': 0, 'z': 1 }, Length=20, Examination=exam, Center={ 'x': new_point_coords.x, 'y': new_point_coords.y, 'z': new_point_coords.z })                                    
                        patient.PatientModel.RegionsOfInterest["outside_vol_1"].DeleteRoi()
                        patient.PatientModel.RegionsOfInterest["outside_vol_2"].DeleteRoi()
                        intersect1 = roi.subtract_rois(ptv_names[0], "zone_imagerie", color="Yellow", examination=exam, output_name="outside_vol_1")
                        intersect2 = roi.subtract_rois(ptv_names[1], "zone_imagerie", color="Yellow", examination=exam, output_name="outside_vol_2")        
                        
                        if roi.get_roi_volume("outside_vol_1", exam) > 0 or roi.get_roi_volume("outside_vol_2", exam) > 0:
                            self.message.Text += "Les PTVs sont trop espacés pour imager ensemble, \n   il faut traiter chacun avec son propre isocentre"
                            if roi.get_roi_volume("outside_vol_1", exam) > 0:
                                self.message.Text += "\n%s sort du la zone d'imagerie" % ptv_names[0]
                            if roi.get_roi_volume("outside_vol_2", exam) > 0:
                                self.message.Text += "\n%s sort du la zone d'imagerie" % ptv_names[1]
                            self.stepcombo.Text = '2 plans sur 2 isocentres'
                            self.sitebox.Text = "A1" 
                            self.sitebox2.Text = "B1" 
                        else:
                            self.message.Text += "Les PTVs sont trop espacés pour traiter avec\n   l'isocentre %s.\nIl est possible de traiter les PTVs en 2 plans\n   avec l'isocentre Iso Auto" % d['iso_names'][0]
                            self.message.Text += "\nShift: %.0fcm en lat, %.0fcm en HT, %.0fcm en longi" % (abs(shift_x),abs(shift_y),abs(shift_z))  
                            self.message.Text += "\nCoordonnés: %.2f,%.2f,%.2f\n\n" % (new_point_coords.x,new_point_coords.y,new_point_coords.z)            
                            self.stepcombo.Text = '2 plans sur 1 isocentre'
                            self.sitebox.Text = "A1" 
                            self.sitebox2.Text = "B1" 
                            self.isocombo.Text = 'Iso Auto'
                            self.isocombo2.Text = 'Iso Auto'
                
                    #If both PTVs are close enough to treat with the same isocenter, determine if single or multiple plans are preferred
                    else:
                        #self.message.Text += "Limites longi du PTV1: %.2f, %.2f" % (bb_ptv1[0].z,bb_ptv1[1].z)
                        #self.message.Text += "\nLimites longi du PTV2: %.2f, %.2f" % (bb_ptv2[0].z,bb_ptv2[1].z)
                        if (bb_ptv1[0].z > bb_ptv2[0].z and bb_ptv1[0].z < bb_ptv2[1].z) or (bb_ptv1[1].z > bb_ptv2[0].z and bb_ptv1[1].z < bb_ptv2[1].z) or (bb_ptv2[0].z > bb_ptv1[0].z and bb_ptv2[0].z < bb_ptv1[1].z) or (bb_ptv2[1].z > bb_ptv1[0].z and bb_ptv2[1].z < bb_ptv1[1].z):
                            self.message.Text += "\nOverlap entre les PTVs"
                            longi_separation = 0                        
                        else:
                            bb_z_coords = [bb_ptv1[0].z,bb_ptv1[1].z,bb_ptv2[0].z,bb_ptv2[1].z]
                            bb_z_coords.sort()
                            longi_separation = bb_z_coords[2] - bb_z_coords[1]
                            self.message.Text += "\nSéparation en longi: %.2f" % (longi_separation)
                        if longi_separation < 0.5:
                            self.message.Text += "\nPlanifiez les deux PTVs ensemble (avec collimateur 90)"
                            self.stepcombo.Text = '1 plan (colli 90)'
                            self.sitebox2.Text = self.sitebox.Text
                            self.isocombo2.Text = self.isocombo.Text
                            self.techcombo2.Text = self.techcombo.Text
                        elif longi_separation < 2:
                            self.message.Text += "\nPlanifiez les deux PTVs ensemble"
                            self.stepcombo.Text = '1 plan'
                            self.sitebox2.Text = self.sitebox.Text
                            self.isocombo2.Text = self.isocombo.Text
                            self.techcombo2.Text = self.techcombo.Text
                        else:
                            self.message.Text += "\nPlanifiez les deux PTVs séparément sur le même isocentre"
                            self.stepcombo.Text = '2 plans sur 1 isocentre'
                            self.sitebox.Text = "A1" 
                            self.sitebox2.Text = "B1" 
                            self.isocombo2.Text = self.isocombo.Text                            
            
            rx_dose = d['rx_dose']
            if self.stepcombo.Text == '1 plan' or self.stepcombo.Text == '1 plan (colli 90)':
                num_plans = 1
            else:
                num_plans = 2
            self.message.Text += "\n\nPresciption: %.2fGy en %d fractions" % (rx_dose/100.0,d['nb_fx'])
            if d['nb_fx'] == 15:
                self.message.Text += "\n%d plan(s) LUSTRE seront ajouté(s)" % (num_plans)
            else:
                self.message.Text += "\n%d plan(s) SBRT seront ajouté(s)" % (num_plans)
            
            if roi.roi_exists("outside_vol_1",exam):
                patient.PatientModel.RegionsOfInterest["outside_vol_1"].DeleteRoi()
                patient.PatientModel.RegionsOfInterest["outside_vol_2"].DeleteRoi()   
            
            self.status.ForeColor = Color.Green
            self.status.Text = "Évaluation complétée" 
   
   
        def addplanClicked(self, sender, args):
        
            self.message.Text = ""        
            self.status.ForeColor = Color.Black                     
            self.status.Text = "Compilation des données du plan"
            
            d,error_message = self.compile_plan_data()                         
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                
            
            rx_dose = d['rx_dose']       
            ptv_names = d['ptv_names']
            itv_names = d['itv_names']
            iso_names = d['iso_names']            
            site_names = d['site_names']            
            techniques = d['techniques']            
            
            if self.stepcombo.Text == '2 plans sur 2 isocentres':
                self.status.Text = "Vérification 2 plans"
                if len(ptv_names) < 2:
                    error_message = "Veuillez choisir un 2e PTV"
                if len(iso_names) < 2:
                    error_message = "Veuillez choisir un isocentre pour chaque PTV"      
                if iso_names[0] == iso_names[1]:
                    error_message = "Les deux PTVs devrait avoir des isocentres différents"  
                if site_names[0] == site_names[1] or site_names[1]=='':
                    error_message = "Chaque PTV a besoin d'un nom de site unique"
                if techniques[1] == '':
                    error_message = "Veuillez choisir une technique pour chaque PTV"    
            elif self.stepcombo.Text == '2 plans sur 1 isocentre':
                if len(ptv_names) < 2:
                    error_message = "Veuillez choisir un 2e PTV"
                if iso_names[0] != iso_names[1]:
                    error_message = "Sélectionnez le même isocentre pour les deux plans"        
                if site_names[0] == site_names[1] or site_names[1]=='':
                    error_message = "Chaque PTV a besoin d'un nom de site unique"            
                if techniques[1] == '':
                    error_message = "Veuillez choisir une technique pour chaque PTV"                      
            
            if d['nb_fx'] == 15:
                suffix = " LUSTRE"
            else:
                suffix = " Rings"
            if len(ptv_names) == 1:
                plan_name = site_names[0] + suffix
            elif len(ptv_names) == 2:
                plan_name = site_names[0] + '+' + site_names[1] + suffix
            
            try:    
                existing_plan = patient.TreatmentPlans[plan_name]
                error_message = "Un plan avec le nom %s exist déjà" % plan_name
            except:
                pass                
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                  
        
            #How many plans we making here?
            if self.stepcombo.Text == '2 plans sur 2 isocentres' or self.stepcombo.Text == '2 plans sur 1 isocentre':
                num_plans = 2
            else:            
                num_plans = 1
                if len(ptv_names)>1:
                    if not roi.roi_exists("sum_ptvs_"+site_names[0]):
                        #If multiple PTVs are selected for a single plan, combine them into one ROI (same for ITVs)
                        self.status.Text = "Combinaison des PTVs"                    
                        patient.PatientModel.CreateRoi(Name="sum_ptvs_"+site_names[0], Color="Red", Type="Organ", TissueName=None, RoiMaterial=None)
                        patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site_names[0]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                        patient.PatientModel.RegionsOfInterest["sum_ptvs_"+site_names[0]].UpdateDerivedGeometry(Examination=d['exam'])
                    if not roi.roi_exists("sum_itvs_"+site_names[0]):                        
                        patient.PatientModel.CreateRoi(Name="sum_itvs_"+site_names[0], Color="128, 128, 192", Type="Organ", TissueName=None, RoiMaterial=None)
                        patient.PatientModel.RegionsOfInterest["sum_itvs_"+site_names[0]].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [itv_names[0]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [itv_names[1]], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                        patient.PatientModel.RegionsOfInterest["sum_itvs_"+site_names[0]].UpdateDerivedGeometry(Examination=d['exam'])         
                    d['ptv_names'][0] = "sum_ptvs_"+site_names[0]
                    d['itv_names'][0] = "sum_itvs_"+site_names[0]
            
            
            #Remove material overrides from all imported ROIs before commencing
            self.status.Text = "Overrides ROIs"
            for rois in patient.PatientModel.RegionsOfInterest:
                rois.SetRoiMaterial(Material=None)
                
            #Copy imaging system to average from expi CT if necessary
            try:
                self.status.Text = "Assignation du tableau CT-to-density"
                temp_plan = patient.TreatmentPlans[0] #If a plan already exists, skip this step (since it isn't necessary and it will invalidate the dose of existing plans)
            except:
                try:
                    patient.Examinations['CT 1'].EquipmentInfo.SetImagingSystemReference(ImagingSystemName=patient.Examinations['CT 2'].EquipmentInfo.ImagingSystemReference.ImagingSystemName)
                except: #For rare cases where there is only one scan
                    pass
  
            fat_r50 = False
            i = 0
            if d['nb_fx'] < 15: #For SBRT plans
                while i < num_plans:
                    self.status.Text = "Plan %d/%d: Création de l'isocentre" % (i+1,num_plans)
                    poumon.poumon_stereo_v2_pois(plan_data=d, index=i)
                    
                    self.status.Text = "Plan %d/%d: Création des ROIs d'optimisation" % (i+1,num_plans)
                    if self.stepcombo.Text == '1 plan (colli 90)':
                        fat_r50 = True
                    poumon.poumon_stereo_v2_rois(plan_data=d, index=i, num_plans=num_plans, fat_r50=fat_r50)                
                    
                    if i == 0:
                        self.status.Text = "Ajout du plan"
                        plan = poumon.poumon_stereo_v2_add_plan(plan_data=d, num_plans=num_plans)
                        
                        self.status.Text = "Reglage du Dose Color Table"
                        poumon.poumon_stereo_v2_create_isodose_lines(plan_data=d)
                        
                    self.status.Text = "Plan %d/%d: Ajout du beamset" % (i+1,num_plans)
                    beamset = poumon.poumon_stereo_v2_add_beamset(plan_data=d, index=i, plan=plan, coverage=95)
                    
                    self.status.Text = "Plan %d/%d: Ajout des faisceaux" % (i+1,num_plans) 
                    if techniques[i] == 'VMAT':
                        if self.stepcombo.Text == '1 plan (colli 90)':
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i, two_arcs=True, colli1=90, colli2=90)
                        elif self.stepcombo.Text == '1 plan' and len(ptv_names)>1:
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i, two_arcs=True)
                        else:
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i)
                    else:
                        beams.add_beams_imrt_lung_stereo_v2(plan_data=d, beamset=beamset, index=i)
                    
                    self.status.Text = "Plan %d/%d: Reglage des paramètres d'optimisation" % (i+1,num_plans)
                    poumon.poumon_stereo_v2_opt_settings(plan_data=d, plan=plan, index=i, plan_type=self.stepcombo.Text)
                    
                    self.status.Text = "Plan %d/%d: Objectifs d'optimisation et Clinical Goals" % (i+1,num_plans)
                    clinical_goals.smart_cg_lung_stereo_v2(plan_data=d, plan=plan, beamset=beamset, index=i, num_plans=num_plans)
                    crane.add_custom_max_doses(custom_max=d['custom_max'], plan=plan, plan_opt=i)
                    
                    self.status.Text = "Plan %d/%d: Optimisation initiale" % (i+1,num_plans)
                    optim.optimization_90_30(plan=plan,beamset=beamset)
                    
                    i += 1
            
            
            elif d['nb_fx'] == 15: #For LUSTRE plans in 15 fractions
                while i < num_plans:
                    self.status.Text = "Plan %d/%d: Création de l'isocentre" % (i+1,num_plans)
                    poumon.poumon_stereo_v2_pois(plan_data=d, index=i)
                    
                    self.status.Text = "Plan %d/%d: Création des ROIs d'optimisation" % (i+1,num_plans)
                    poumon.poumon_lustre_rois(plan_data=d, index=i, num_plans=num_plans)
                    
                    if i == 0:
                        self.status.Text = "Ajout du plan"
                        plan = poumon.poumon_stereo_v2_add_plan(plan_data=d, num_plans=num_plans)
                        
                        self.status.Text = "Reglage du Dose Color Table"
                        poumon.poumon_stereo_v2_create_isodose_lines(plan_data=d)
                        
                    self.status.Text = "Plan %d/%d: Ajout du beamset" % (i+1,num_plans)          
                    beamset = poumon.poumon_stereo_v2_add_beamset(plan_data=d, index=i, plan=plan, coverage=98)
                    
                    self.status.Text = "Plan %d/%d: Ajout des faisceaux" % (i+1,num_plans) 
                    if techniques[i] == 'VMAT':
                        if self.stepcombo.Text == '1 plan (colli 90)':
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i, two_arcs=True, colli1=90, colli2=90)
                        elif self.stepcombo.Text == '1 plan' and len(ptv_names)>1:
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i, two_arcs=True)
                        else:
                            beams.add_arcs_lung_stereo_v2(plan_data=d, beamset=beamset, index=i)
                    else:
                        beams.add_beams_imrt_lung_stereo_v2(plan_data=d, beamset=beamset, index=i)
                    
                    self.status.Text = "Plan %d/%d: Reglage des paramètres d'optimisation" % (i+1,num_plans)
                    poumon.poumon_stereo_v2_opt_settings(plan_data=d, plan=plan, index=i, plan_type=self.stepcombo.Text)                    

                    self.status.Text = "Plan %d/%d: Ajout des Clinical Goals" % (i+1,num_plans)
                    poumon.poumon_lustre_add_clinical_goals(plan_data=d, index=i, plan=plan, num_plans=num_plans)
        
                    self.status.Text = "Plan %d/%d: Optimisation initiale" % (i+1,num_plans)
                    poumon.poumon_lustre_initial_plan(plan_data=d, index=i, plan=plan, beamset=beamset)
                    
                    i += 1
                
                
                #Once both plans have their initial optimisations, copy the plan and modify the beamsets
                #patient.CopyPlan(PlanName=plan.Name, NewPlanName=plan.Name + ' initial')
                
                #Modify the beamsets (must be done before modifying dose grid or we'll lose our dose)
                i = 0
                while i < num_plans:
                    self.status.Text = "Plan %d/%d: Modification du plan" % (i+1,num_plans)
                    poumon.poumon_lustre_modify_plan(plan_data=d, index=i, plan=plan, beamset=plan.BeamSets[i], num_plans=num_plans)
                    crane.add_custom_max_doses(custom_max=d['custom_max'], plan=plan, plan_opt=i)
                
                    i += 1
                
                #Set the dose grid back to 2mm voxels
                grid = plan.GetDoseGrid()
                plan.UpdateDoseGrid(Corner={ 'x': grid.Corner.x, 'y': grid.Corner.y, 'z': grid.Corner.z }, VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 }, NumberOfVoxels={ 'x': grid.NrVoxels.x * 2, 'y': grid.NrVoxels.y * 2, 'z': grid.NrVoxels.z * 2 })
                
                #Optimize modified plans
                i = 0
                while i < num_plans:                   
                    self.status.Text = "Plan %d/%d: Optimisation du plan modifié" % (i+1,num_plans)
                    optim.optimization_90_30_30(plan=plan, beamset=plan.BeamSets[i])
                    
                    i += 1
                    
                    
                    
                    

            self.isodosecombo.Text = 'Ne pas créer'
            self.status.Text = "Terminé avec succès!"
            self.status.ForeColor = Color.Green
         
   
        def addKBPplanClicked(self, sender, args):
            self.message.Text = ""        
            self.status.ForeColor = Color.Black                     
            self.status.Text = "Compilation des données du plan"
            
            d,error_message = self.compile_plan_data()                       
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return    

            plan_name = "Plan Test"
            try:
                existing_plan = patient.TreatmentPlans[plan_name]
                error_message = "Un plan avec le nom %s exist déjà" % plan_name
            except:
                pass                

            #Add categories to plan data dictionary to make it compatible with old kbp scripts (THIS IS SUPER KLUDGY AND SHOULD BE IMPROVED LATER)
            d['site_name'] = d['site_names'][0]
            d['ptv'] = patient.PatientModel.RegionsOfInterest[d['ptv_names'][0]]
            d['site_name'] = d['site_names'][0]
            d['treatment_technique'] = d['techniques'][0]
            
            self.status.Text = "Test: Vérification des OARs"
            oar_list,laterality = poumon.poumon_stereo_kbp_identify_rois(plan_data=d)
            self.status.Text = "Test: Ajout du plan et beamset test"                    
            poumon.poumon_stereo_kbp_add_plan_and_beamset(plan_data=d,laterality=laterality)
            self.status.Text = "Test: Configuration des paramêtres d'optimisation"
            poumon.poumon_stereo_kbp_opt_settings(plan_data=d)
            self.status.Text = "Test: Création et optimisation du plan inital"
            poumon.poumon_stereo_kbp_initial_plan(plan_data=d,oar_list=oar_list,plan_opt=0)
            self.status.Text = "Test: Modification des objectifs d'optimisation"
            poumon.poumon_stereo_kbp_modify_plan(plan_data=d,oar_list=oar_list,plan_opt=0)
            self.status.Text = "Test: Optimisation du plan modifié"
            poumon.poumon_stereo_kbp_iterate_plan(plan_data=d,oar_list=oar_list)
            #self.Status.Text = "Test: Impression des resultats"
            #poumon.poumon_stereo_kbp_evaluate_plan(plan_data=d,oar_list=oar_list)
   
   
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
        
    form = PoumonLauncher()
    Application.Run(form)   
 
