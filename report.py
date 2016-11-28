# -*- coding: utf-8 -*-

"""
Ce module contient les outils pour la vérification des plans.
"""

import hmrlib.lib as lib
import hmrlib.poi as poi
import hmrlib.roi as roi

#Stuff for creating pdf files (from RayStation scripting guideline page 32)
import sys, System
script_path = System.IO.Path.GetDirectoryName(sys.argv[0])
path = script_path.rsplit('\\',1)[0]
sys.path.append(path)
import clr
clr.AddReference("MigraDoc.DocumentObjectModel.dll")
clr.AddReference("MigraDoc.Rendering.dll")
clr.AddReference("PdfSharp.dll")
from MigraDoc.DocumentObjectModel import Document, Colors, Unit, ParagraphAlignment, Orientation
from MigraDoc.DocumentObjectModel.Tables import Table
from MigraDoc.Rendering import PdfDocumentRenderer
from PdfSharp import Pdf
from System.Diagnostics import Process

from connect import *

def create_verif1_report(data):
    
    filename = r'\\radonc.hmr\Departements\Dosimétristes\STEREO FOIE\Calculs NTCP\test.pdf'
    doc = Document()
    
    #Add styles   
    style = doc.Styles["Heading1"]
    style.Font.Size = 20
    style.Font.Bold = True
    style.Font.Name = "Verdana"
    style.ParagraphFormat.Alignment = ParagraphAlignment.Center
    style.ParagraphFormat.SpaceAfter = 20
    
    style = doc.Styles.AddStyle("TableHeader", "Normal");
    style.Font.Name = "Arial"
    style.ParagraphFormat.SpaceAfter = 4
    style.ParagraphFormat.SpaceBefore = 4    
    
    style = doc.Styles.AddStyle("TableText", "Normal");
    style.Font.Name = "Arial"
    style.Font.Size = 8
    style.ParagraphFormat.SpaceAfter = 4
    style.ParagraphFormat.SpaceBefore = 4
    
    #Add a section and set landscape orientation
    sec = doc.AddSection()
    pagesetup = doc.DefaultPageSetup.Clone()
    pagesetup.Orientation = Orientation.Portrait
    sec.PageSetup = pagesetup
    
    #Add a title
    sec.AddParagraph("Vérification initiale de la dosimétrie", "Heading1")    
    
    # Add an image?
    #image = sec.AddImage('//radonc.hmr/Physiciens/Admin/Logo CIUSSS/Logo Ciusss couleur.png')
    #image.Width = "10cm"    
    
    #Add patient information
    presc_text_temp = data['presc_text'].split("à")[0]

    paragraph = sec.AddParagraph("Nom du patient: " + data['patient_name'],"Normal")
    paragraph.AddText("\n\nNuméro du dossier: " + data['patient_number'])
    paragraph.AddText("\n\nPlan: " + data['plan_name'])
    paragraph.AddText("\n\nBeamset: " + data['beamset_name'])
    paragraph.AddText("\n\nPrescription: " + presc_text_temp)
    paragraph.AddText("\n\nPlanifié par: " + data['planned_by_name'])
    paragraph.AddText("\n\nVérifié par: " + data['verified_by_name'])
    
    #Creat a table to hold the statistics
    paragraph = sec.AddParagraph()
    table = Table()
    table.Style = "TableText"
    table.Borders.Width = 0.75
    col = table.AddColumn(Unit.FromCentimeter(3.5))
    col.Format.Alignment = ParagraphAlignment.Left
    col = table.AddColumn(Unit.FromCentimeter(3))
    col.Format.Alignment = ParagraphAlignment.Left
    col = table.AddColumn(Unit.FromCentimeter(11))
    col.Format.Alignment = ParagraphAlignment.Left
            
    #Add header row
    header_row = table.AddRow()
    header_row.Style = "TableHeader"
    header_row.Shading.Color = Colors.LightBlue
    header_row.Cells[0].AddParagraph('ITEM')
    header_row.Cells[1].AddParagraph('VERIFICATION')    
    header_row.Cells[2].AddParagraph('DESCRIPTION')
    
    #Add a row for each verification
    row = table.AddRow()
    row.Cells[0].AddParagraph('Bon scan sélectionné')
    row.Cells[1].AddParagraph(data['check_bonscan'])
    if data['check_bonscan'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red
    row.Cells[2].AddParagraph('-')

    row = table.AddRow()
    row.Cells[0].AddParagraph('Scan')
    row.Cells[1].AddParagraph(data['check_scanOK'])
    if data['check_scanOK'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red
    row.Cells[2].AddParagraph('-')

    row = table.AddRow()
    row.Cells[0].AddParagraph('Contour External et override')
    row.Cells[1].AddParagraph(data['check_ext'])
    if data['check_ext'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red    
    row.Cells[2].AddParagraph(data['ext_text'])
    if data['ext_text'] == 'Script pas roulé':
        row.Cells[2].Shading.Color = Colors.Red      

    row = table.AddRow()
    row.Cells[0].AddParagraph("Position de l'isocentre")
    row.Cells[1].AddParagraph(data['check_isoOK'])
    if data['check_isoOK'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red    
    row.Cells[2].AddParagraph(data['iso_text'])  
    if data['iso_text'] == 'Script pas roulé':
        row.Cells[2].Shading.Color = Colors.Red      
    
    row = table.AddRow()
    row.Cells[0].AddParagraph('Champs')    
    row.Cells[1].AddParagraph(data['check_beams_Rx'])
    if data['check_beams_Rx'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red    
    row.Cells[2].AddParagraph(data['beam_text'])
    if data['beam_text'] == 'Script pas roulé':
        row.Cells[2].Shading.Color = Colors.Red      
    
    row = table.AddRow()
    row.Cells[0].AddParagraph('Prescription')    
    row.Cells[1].AddParagraph(data['check_beams_Rx'])
    if data['check_beams_Rx'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red        
    row.Cells[2].AddParagraph(data['presc_text'])
    if data['presc_text'] == 'Script pas roulé':
        row.Cells[2].Shading.Color = Colors.Red  

    row = table.AddRow()
    row.Cells[0].AddParagraph('Contours')    
    row.Cells[1].AddParagraph(data['check_contours'])
    if data['check_contours'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red        
    row.Cells[2].AddParagraph('-')
    
    row = table.AddRow()
    row.Cells[0].AddParagraph("Paramètres d'optimisation et objectifs")    
    row.Cells[1].AddParagraph(data['check_optimisation'])
    if data['check_optimisation'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red        
    row.Cells[2].AddParagraph(data['opt_text'])
    if data['opt_text'] == 'Script pas roulé':
        row.Cells[2].Shading.Color = Colors.Red      

    row = table.AddRow()
    row.Cells[0].AddParagraph('DVH')        
    row.Cells[1].AddParagraph(data['check_distribution_dose'])
    if data['check_distribution_dose'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red        
    row.Cells[2].AddParagraph('-')
    
    row = table.AddRow()
    row.Cells[0].AddParagraph('Distribution de dose')        
    row.Cells[1].AddParagraph(data['check_distribution_dose'])
    if data['check_distribution_dose'] == 'Pas vérifié':
        row.Cells[1].Shading.Color = Colors.Red       
    row.Cells[2].AddParagraph('-')
    
    #TEST - Format cells (this one works!)
    #for i, row in enumerate(table.Rows):
    #    if i % 2 == 0:
    #        row.Shading.Color = Colors.LightBlue
            
    #This also works
    #for i in range(5):
    #    for j in range (2):
            #if table.Rows[i].Cells[j] == 'Pas vérifié':
            #table.Rows[i].Cells[j].Shading.Color = Colors.Red     
    
    #Add table to the document
    sec.Add(table)
    
    #Render the document, save it to file and display the file
    renderer = PdfDocumentRenderer(True, Pdf.PdfFontEmbedding.Always)
    renderer.Document = doc
    renderer.RenderDocument()
    renderer.PdfDocument.Save(filename)
    process = Process()
    process.StartInfo.FileName = filename
    process.Start()
    process.WaitForExit()


def create_sample_report():
    filename = r'\\radonc.hmr\Departements\Dosimétristes\STEREO FOIE\Calculs NTCP\test.pdf'
    doc = Document()
    
    #Add styles
    style = doc.Styles["Normal"]
    style.Font.Name = "Verdana"
    style.ParagraphFormat.SpaceAfter = 4
    #style.ParagraphFormat.Shading.Color = Colors.SkyBlue
    
    style = doc.Styles["Heading1"]
    style.Font.Size = 20
    style.Font.Bold = True
    style.Font.Name = "Verdana"
    #style.Font.Color = Colors.DeepSkyBlue
    style.ParagraphFormat.Alignment = ParagraphAlignment.Center
    style.ParagraphFormat.SpaceAfter = 10
    
    # Create a new style called TextBox based on style Normal
    style = doc.Styles.AddStyle("TextBox", "Normal");
    style.ParagraphFormat.Alignment = ParagraphAlignment.Justify
    style.ParagraphFormat.Borders.Width = 2.5
    style.ParagraphFormat.Borders.Distance = "3pt"
    style.ParagraphFormat.Shading.Color = Colors.Orange 
        
    #Add a section and set landscape orientation
    sec = doc.AddSection()
    pagesetup = doc.DefaultPageSetup.Clone()
    pagesetup.Orientation = Orientation.Portrait
    sec.PageSetup = pagesetup
    
    #Add a title
    sec.AddParagraph("Première vérification", "Heading1")
    
    #Add patient information
    patient_name = "Bob Smith"
    patient_num = "1979"
    paragraph = sec.AddParagraph("Nom du patient: "+patient_name,"Normal")
    paragraph.AddText("\nNuméro HMR: "+patient_num)
    
    # Add an image?
    image = sec.AddImage(r'\\radonc.hmr\Dosimétristes\halloween2016.jpg')
    image.Width = "10cm"
    
    #Creat a table to hold the statistics
    table = Table()
    table.Borders.Width = 1
    for i in range(5):
        col = table.AddColumn(Unit.FromCentimeter(3))
        if i == 0:
            col.Format.Alignment = ParagraphAlignment.Left
        else:
            col.Format.Alignment = ParagraphAlignment.Right
            
    #Add header row
    header_row = table.AddRow()
    header_row.Shading.Color = Colors.SkyBlue
    header_row.Cells[0].AddParagraph('ROI')
    header_row.Cells[1].AddParagraph('Volume [cc]')    
    header_row.Cells[2].AddParagraph('D99 [cGy]')
    header_row.Cells[3].AddParagraph('Average [cGy]')
    header_row.Cells[4].AddParagraph('D1 [cGy]')
    
    row = table.AddRow()
    row.Cells[0].AddParagraph('How')
    row.Cells[1].AddParagraph('are')
    row.Cells[2].AddParagraph('you')
    row.Cells[3].AddParagraph('doing')
    row.Cells[4].AddParagraph('today?')
    
    #Add table to the document
    sec.Add(table)
    
    #Render the document, save it to file and display the file
    renderer = PdfDocumentRenderer(True, Pdf.PdfFontEmbedding.Always)
    renderer.Document = doc
    renderer.RenderDocument()
    renderer.PdfDocument.Save(filename)
    process = Process()
    process.StartInfo.FileName = filename
    process.Start()
    process.WaitForExit()