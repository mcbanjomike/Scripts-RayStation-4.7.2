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

# To test GUI stuff
import clr
import System.Array

import crane
import verification
import report
import statistics
import message

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)

def crane_launcher():

    class CraneLauncher(Form):
        def __init__(self):
            self.Text = "Statistiques"

            self.Width = 700
            self.Height = 900

            self.setupHeaderWindow()
            self.setupMainWindow()

            self.Controls.Add(self.HeaderWindow)
            self.Controls.Add(self.MainWindow)
            
            #Automatically populate ROI selection comboboxes
            self.PTV1combo.Items.Add("Choisissez ROI")
            self.PTV2combo.Items.Add("Choisissez ROI")
            self.PTV3combo.Items.Add("Choisissez ROI")    
            self.OAR1combo.Items.Add("Choisissez OAR")
            self.OAR2combo.Items.Add("Choisissez OAR")
            self.OAR3combo.Items.Add("Choisissez OAR")
            for roi in patient.PatientModel.RegionsOfInterest:       
                if 'PTV' in roi.Name.upper():
                    self.PTV1combo.Items.Add(roi.Name)
                    self.PTV2combo.Items.Add(roi.Name)
                    self.PTV3combo.Items.Add(roi.Name)      
                if 'PTV' not in roi.Name.upper():
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
                self.isocombo.Items.Add(poi.Name)   
                if poi.Name == 'REF SCAN':
                    self.isocombo.Text = 'REF SCAN'
            
            
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
                if ct.Name == 'CT 1':
                    self.scancombo.Text = 'CT 1'
            
            
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
            #self.couchcombo.Items.Add('Ajouter')                  

            
            self.message = Label()
            self.message.Text = "Sélectionnez le(s) ROI(s) à traiter (chaque\ncontour distinct devrait être indiqué\nséparément). Seulement les ROIs avec\nPTV dans leurs noms sont disponibles.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nLes plans IMRT/3DC avec plusieurs PTVs\ndistincts auront une optimisation automatique\ndu collimateur. SVP ne touchez pas à\nl'ordinateur pendant cette optimisation\n(4 à 5 minutes environ)"
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

            
            evalButton = Button()
            evalButton.Text = "Évaluer les PTVs"
            evalButton.Location = Point(25, offset + 18 * vert_spacer)
            evalButton.Width = 200
            evalButton.Click += self.evalClicked                           
            
            addplanButton = Button()
            addplanButton.Text = "Ajouter plan"
            addplanButton.Location = Point(25, offset + 19 * vert_spacer)
            addplanButton.Width = 200
            addplanButton.Click += self.addplanClicked   


            self.stepcombo = ComboBox()
            self.stepcombo.Parent = self
            self.stepcombo.Size = Size(250,40)
            self.stepcombo.Location = Point(25, offset + 20 * vert_spacer)
            self.stepcombo.Text = "Rouler le script au complet"                  
            self.stepcombo.Items.Add('Rouler le script au complet')            
            self.stepcombo.Items.Add('Multi-PTV: Arrêtez avant optimization collimateur')            
            self.stepcombo.Items.Add('Multi-PTV: Reprendre après optimization collimateur')                   
            
            
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
            
            self.MainWindow.Controls.Add(self.stepcombo) 

            
        def compile_plan_data(self):            
                               
            self.status.Text = "Compilation des données du plan"      
            
            ptv_names = []
            rx = []  
            custom_max = []
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
                    
            if self.isocombo.Text == '':
                error_message = "Choisissez un isocentre avant de continuer"

            if self.scancombo.Text == '':
                error_message = "Choisissez un scan avant de continuer"
                
            if self.couchcombo.Text == 'Ajouter':
                couch = True
            else:
                couch = False                    
                                  
            name = self.sitebox.Text + ' ' + technique
            if couch:
                name += ' Couch'    
            if self.stepcombo.Text != "Multi-PTV: Reprendre après optimization collimateur": #We need to skip this step if completing a plan that was started earlier           
                try:    
                    existing_plan = patient.TreatmentPlans[name]
                    error_message = "Un plan avec le nom %s exist déjà, SVP le renommez avant de commencer" % name
                except:
                    pass                    
                
            if self.stepcombo.Text == "Multi-PTV: Arrêtez avant optimization collimateur" or self.stepcombo.Text == "Multi-PTV: Reprendre après optimization collimateur":
                if technique == 'VMAT':
                    error_message = "Le script partiel devrait seulement être utilisé pour les cas d'IMRT et 3DC"
                elif len(ptv_names) == 1:
                    error_message = "Le script partiel devrait seulement être utilisé pour les cas avec plus qu'un PTV"
                
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
                     couch = couch,
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
            self.status.Text = "Compilation des données du plan"
            
            d,error_message = self.compile_plan_data()
            
            if error_message != "": #If an error is noticed, cancel script execution
                self.status.Text = error_message
                self.status.ForeColor = Color.Red
                return                  
        
            rx = d['rx']       
            ptv_names = d['ptv_names']
            technique = d['technique']
            site = d['site_name']
                                            
            #Predict dose to brain (and generate ROIs)
            self.status.Text = "Estimation de la dose au cerveau"
            predicted_vol = crane.crane_stereo_kbp_predict_dose(plan_data = d)
            cerv_ptv_vol = patient.PatientModel.StructureSets[d['exam'].Name].RoiGeometries["CERVEAU-PTV_"+d['site_name']].GetRoiVolume()            
            
            #Display predicted results
            self.message.Text = 'Volumes prédits dans le cerveau-PTV:\n   V100%%: %.2fcc\n   V90%%:  %.2fcc\n   V80%%:  %.2fcc\n   V70%%:  %.2fcc\n   V60%%:  %.2fcc\n   V50%%:  %.2fcc\n   V40%%:  %.2fcc' % (predicted_vol[0],predicted_vol[1],predicted_vol[2],predicted_vol[3],predicted_vol[4],predicted_vol[5],predicted_vol[6])
            v10 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1000)
            v12 = crane.estimate_vx(predicted_vol=predicted_vol,rx_dose=max(rx),dose_level=1200)
            self.message.Text += '\n\nV10 Cerveau-PTV estimé: %s\nV12 Cerveau-PTV estimé: %s' % (v10,v12)
            
            self.status.Text = "Estimation de la dose max au tronc cerebral"
            tronc_max = crane.crane_stereo_kbp_predict_oar_dose(plan_data = d)    
            
            #Check which steps of the script are to be performed
            if self.stepcombo.Text == "Rouler le script au complet":
                add_plan = True
                optimize_collimator_angles = True
                optimize_plan = True               
            elif self.stepcombo.Text == "Multi-PTV: Arrêtez avant optimization collimateur":
                add_plan = True
                optimize_collimator_angles = False
                optimize_plan = False              
            elif self.stepcombo.Text == "Multi-PTV: Reprendre après optimization collimateur":
                add_plan = False
                optimize_collimator_angles = False
                optimize_plan = True            
            
            if add_plan:
                
                if patient.BodySite == '':
                    patient.BodySite = 'Crâne'  
                
                if self.isodosecombo.Text == "Créer":
                    self.status.Text = "Ajout du dose color table"
                    crane.crane_stereo_create_isodose_lines(plan_data = d)           
                    
                #Create/assign types to POIs and ROIs (only if this is the first plan for the patient)
                try:
                    existing_plan = patient.TreatmentPlans[0]
                except:                
                    if d['iso_name'] == 'REF SCAN': #Need to skip this step if planner is intentionally using a different isocenter
                        self.status.Text = "Création de l'isocentre à partir du REF SCAN"
                        poi.create_iso()
                    self.status.Text = "Gestion des POIs"
                    poi.auto_assign_poi_types()
                    
                    self.status.Text = "Suppression des overrides de densité"
                    for rois in patient.PatientModel.RegionsOfInterest:
                        rois.SetRoiMaterial(Material=None)    
                    
                    self.status.Text = "Création du contour externe"
                    roi.generate_BodyRS_using_threshold()
                    
                    #Create TISSU SAINS à 1cm
                    if not roi.roi_exists("TISSU SAIN 1cm "+site):
                        patient.PatientModel.CreateRoi(Name="TISSU SAIN 1cm "+site, Color="Magenta", Type="Organ", TissueName=None, RoiMaterial=None)
                        patient.PatientModel.RegionsOfInterest["TISSU SAIN 1cm "+site].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ['sum_ptvs_'+site], 'MarginSettings': {'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                        patient.PatientModel.RegionsOfInterest["TISSU SAIN 1cm "+site].UpdateDerivedGeometry(Examination=exam)                    
                
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
                    if optimize_collimator_angles:
                        self.status.Text = "Ajout du plan, beamset et faisceaux (touchez pas à l'ordinateur SVP)"
                        plan,beamset = crane.crane_stereo_kbp_add_3DC_plan(plan_data = d)
                        
                        self.status.Text = "Optimisation angles collimateur (touchez pas à l'ordinateur SVP)"
                        crane.optimize_collimator_angles()
                        
                        self.status.Text = "Conversion du plan 3DC > IMRT (touchez pas à l'ordinateur SVP)"
                        crane.crane_stereo_convert_3DC_IMRT(plan=plan,beamset=beamset)
                    
                    else:
                        self.status.Text = "Ajout du plan, beamset et faisceaux"
                        plan,beamset = crane.crane_stereo_kbp_add_IMRT_plan_and_beamset(plan_data = d)
                        self.status.Text = "Prêt pour optimisation manuelle des angles de collimateur"
                        self.status.ForeColor = Color.Green
                        return
                    
                elif technique == '3DC':
                    self.status.Text = "Ajout du plan, beamset et faisceaux (touchez pas à l'ordinateur SVP)"
                    plan,beamset = crane.crane_stereo_kbp_add_3DC_plan(plan_data = d)
                    
                    #if len(ptv_names)>1:
                    if optimize_collimator_angles:
                        self.status.Text = "Optimisation angles collimateur (touchez pas à l'ordinateur SVP)"
                        crane.optimize_collimator_angles()  
                    else:
                        self.status.Text = "Prêt pour optimisation manuelle des angles de collimateur"
                        self.status.ForeColor = Color.Green
                        return

            if add_plan == False:
                plan = lib.get_current_plan()
                beamset = lib.get_current_beamset()
                
            if optimize_plan:
                            
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
        message.message_window('Aucun patient sélectionné')
        return                    
    try:
        exam = lib.get_current_examination()
    except:
        message.message_window('Aucun examination trouvé')
        return
        
    form = CraneLauncher()
    Application.Run(form)   
 
