# -*- coding: utf-8 -*-

"""
Ce module contient la configuration des faisceaux utilisée en clinique pour
les multiples sites cliniques planifiés dans RayStation à HMR.

Une fonction devrait être créée pour chaque site qui ajoute les fasceaux
nécessaires.
"""

import hmrlib.lib as lib
import hmrlib.poi as poi
import hmrlib.roi as roi

logger = lib.logger


def add_beams_brain_stereo(beamset=None, site_name='A1'):
    """
        Ajoute les arcs utilisés pour la stéréo de crâne.

        Par défaut, ajoutes des arcs allant de :

        - 181 à 180 degrés en CW avec collimateur de 5 degrés
        - 180 à 181 degrés en CCW avec collimateur de 355 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.

        .. seealso::
          fonction :py:func:`hmrlib.lib.add_arc`
    """
    if beamset is None:
        beamset = lib.get_current_beamset()

    iso = poi.identify_isocenter_poi()
    lib.add_arc((site_name+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
    lib.add_arc((site_name+'.2'), iso, 181, 180, 'CW', description='ARC 181-180', collimator=355, beamset=beamset)


def add_beams_brain_stereo_kbp(beamset=None, site_name='KBP1'):
    """
        Ajoute les arcs utilisés pour la stéréo de crâne.

        Par défaut, ajoutes des arcs allant de :

        - 181 à 180 degrés en CW avec collimateur de 5 degrés
        - 180 à 181 degrés en CCW avec collimateur de 355 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.

        .. seealso::
          fonction :py:func:`hmrlib.lib.add_arc`
    """
    if beamset is None:
        beamset = lib.get_current_beamset()

    iso = poi.identify_isocenter_poi()
    lib.add_arc((site_name+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=2, beamset=beamset)


    
def add_beams_brain_static(beamset=None,site_name='A1',iso_name='ISO', exam=None, nb_beams = 13):    
    """
        Ajoute les faisceaux utilisés pour la stéréo de crâne et les plans 3DC.

        Par défaut, ajoutes 13 faisceaux avec des angles de gantry et de collimateur variés
    """
    if nb_beams == 13:
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".1", Description="OPG 166", GantryAngle=166, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".2", Description="OPG 138", GantryAngle=138, CouchAngle=0, CollimatorAngle=15, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".3", Description="OPG 111", GantryAngle=111, CouchAngle=0, CollimatorAngle=30, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".4", Description="OAG 83", GantryAngle=83, CouchAngle=0, CollimatorAngle=45, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".5", Description="OAG 55", GantryAngle=55, CouchAngle=0, CollimatorAngle=60, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".6", Description="OAG 28", GantryAngle=28, CouchAngle=0, CollimatorAngle=75, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".7", Description="OPD 194", GantryAngle=194, CouchAngle=0, CollimatorAngle=90, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".8", Description="OPD 222", GantryAngle=222, CouchAngle=0, CollimatorAngle=105, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".9", Description="OPD 249", GantryAngle=249, CouchAngle=0, CollimatorAngle=120, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".10", Description="OAD 277", GantryAngle=277, CouchAngle=0, CollimatorAngle=135, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".11", Description="OAD 305", GantryAngle=305, CouchAngle=0, CollimatorAngle=150, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".12", Description="OAD 332", GantryAngle=332, CouchAngle=0, CollimatorAngle=165, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".13", Description="ANT 0", GantryAngle=0, CouchAngle=0, CollimatorAngle=180, ApertureBlock=None)
    elif nb_beams == 9:
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".1", Description="OPG 160", GantryAngle=160, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".2", Description="OPG 120", GantryAngle=120, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".3", Description="OAG 80", GantryAngle=80, CouchAngle=0, CollimatorAngle=40, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".4", Description="OAG 40", GantryAngle=40, CouchAngle=0, CollimatorAngle=60, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".5", Description="OPD 200", GantryAngle=200, CouchAngle=0, CollimatorAngle=80, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".6", Description="OPD 240", GantryAngle=240, CouchAngle=0, CollimatorAngle=100, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".7", Description="OAD 280", GantryAngle=280, CouchAngle=0, CollimatorAngle=120, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".8", Description="OAD 320", GantryAngle=320, CouchAngle=0, CollimatorAngle=140, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates(iso_name, examination=exam).value, Name=site_name+".9", Description="ANT", GantryAngle=0, CouchAngle=0, CollimatorAngle=160, ApertureBlock=None)
       
    

def add_beams_lung_stereo(contralateral_lung=None, beamset=None, examination=None, ptv_name=None, two_arcs=False):
    """
        Ajoute les arcs utilisés en stéréo de poumon.

        Détecte s'il s'agit d'un poumon droit ou gauche si le poumon
        contralatéral n'est pas spécifié.

        Par défaut, des arcs allant de :

        - 181 à 30 degrés en CW, puis de 30 à 181 degrés en CCW pour les traitements du poumon droit;
        - 330 à 180 degrés en CW, puis de 180 à 330 degrés en CCW pour les traitements du poumon gauche;

        seront ajoutés, avec un collimateur de 5 et 355 degrés pour l'arc CW et CCW, respectivement.

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.
        - ROI poumons nommés *POUMON G* et *POUMON D*
        - ROI PTV nommé selon la convention habituelle *PTV<niveau de dose en Gy>*

        Args:
            contralateral_lung (str, optional): le nom du ROI du poumon contralatéral : *POUMON G* ou *POUMON D*.
            beamset: objet beamset de RayStation
            examination: object examination de RayStation

        .. seealso::
          fonctions :py:func:`hmrlib.lib.add_arc`, :py:func:`hmrlib.roi.identify_ptvs2`, :py:func:`hmrlib.roi.find_most_intersecting_roi`
    """
    
    patient = lib.get_current_patient()
    iso = poi.identify_isocenter_poi()

    #Ajouté par MA pour permettre le fonctionnement du méga-script poumons
    if beamset is None:
        beamset = lib.get_current_beamset()
    if examination is None:
        examination = lib.get_current_examination()

    if contralateral_lung is None:
        #ptvs = roi.identify_ptvs2()
        if roi.find_most_intersecting_roi(ptv_name, ['POUMON DRT', 'POUMON GCHE'], examination=examination) == 'POUMON DRT':
            contralateral_lung = 'POUMON GCHE'
        else:
            contralateral_lung = 'POUMON DRT'

    if beamset.DicomPlanLabel == 'B1':
        beam_name = 'B1.1'
        beam_name_2 = 'B1.2'
        if poi.poi_exists("ISO B1", examination=examination):
            iso = "ISO B1"
    else:
        beam_name = 'A1.1'
        beam_name_2 = 'A1.2'                  
                  
    if contralateral_lung == 'POUMON GCHE':
        # Poumon D treated
        lib.add_arc(beam_name, iso, 30, 181, 'CCW', description='ARC 30-181', collimator=5, beamset=beamset, exam=examination)
        if two_arcs:
            lib.add_arc(beam_name_2, iso, 181, 30, 'CW', description='ARC 181-30', collimator=355, beamset=beamset, exam=examination)
    elif contralateral_lung == 'POUMON DRT':
        # Poumon G treated
        lib.add_arc(beam_name, iso, 180, 330, 'CCW', description='ARC 180-330', collimator=5, beamset=beamset, exam=examination)
        if two_arcs:
            lib.add_arc(beam_name_2, iso, 330, 180, 'CW', description='ARC 330-180', collimator=355, beamset=beamset, exam=examination)        
    else:
        lib.error('Contralateral lung ROI name not recognized.')  

        
#Modified script that opens arcs up a little bit compared to clinical script
def add_beams_lung_stereo_test(laterality=None, beamset=None, examination=None, two_arcs=False):
    
    patient = lib.get_current_patient()
    iso = poi.identify_isocenter_poi()

    #Ajouté par MA pour permettre le fonctionnement du méga-script poumons
    if beamset is None:
        beamset = lib.get_current_beamset()
    if examination is None:
        examination = lib.get_current_examination()

    if beamset.DicomPlanLabel == 'B1':
        beam_name = 'B1.1'
        beam_name_2 = 'B1.2'
        if poi.poi_exists("ISO B1", examination=examination):
            iso = "ISO B1"
    else:
        beam_name = 'A1.1'
        beam_name_2 = 'A1.2'                  
                  
    if laterality == 'DRT':
        lib.add_arc(beam_name, iso, 40, 181, 'CCW', description='ARC 30-181', collimator=5, beamset=beamset, exam=examination)
        if two_arcs:
            lib.add_arc(beam_name_2, iso, 181, 40, 'CW', description='ARC 181-30', collimator=355, beamset=beamset, exam=examination)
    elif laterality == 'GCHE':
        lib.add_arc(beam_name, iso, 180, 320, 'CCW', description='ARC 180-330', collimator=5, beamset=beamset, exam=examination)
        if two_arcs:
            lib.add_arc(beam_name_2, iso, 320, 180, 'CW', description='ARC 330-180', collimator=355, beamset=beamset, exam=examination)        


          
        
        
def add_beams_imrt_lung_stereo(contralateral_lung=None, beamset=None, examination=None, ptv_name=None, two_arcs=False):
    """
        Ajoute les champs IMRT utilisés en stéréo de poumon.

        Détecte s'il s'agit d'un poumon droit ou gauche si le poumon
        contralatéral n'est pas spécifié.

        Par défaut, des champs allant de :

        - 7 champs couvrant 181 a 30 pour les traitements du poumon droit;
        - 7 champs couvrant 30 a 180  pour les traitements du poumon gauche;

        seront ajoutés, avec un collimateur de 0 et 80 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.
        - ROI poumons nommés *POUMON G* et *POUMON D*
        - ROI PTV nommé selon la convention habituelle *PTV<niveau de dose en Gy>*

        Args:
            contralateral_lung (str, optional): le nom du ROI du poumon contralatéral : *POUMON G* ou *POUMON D*.
            beamset: objet beamset de RayStation
            examination: object examination de RayStation

        .. seealso::
          fonctions :py:func:`hmrlib.lib.add_arc`, :py:func:`hmrlib.roi.identify_ptvs2`, :py:func:`hmrlib.roi.find_most_intersecting_roi`
    """
    
    patient = lib.get_current_patient()
    iso = poi.identify_isocenter_poi()

    #Ajouté par MA pour permettre le fonctionnement du méga-script poumons
    if beamset is None:
        beamset = lib.get_current_beamset()
    if examination is None:
        examination = lib.get_current_examination()

    if contralateral_lung is None:
        #ptvs = roi.identify_ptvs2()
        if roi.find_most_intersecting_roi(ptv_name, ['POUMON DRT', 'POUMON GCHE'], examination=examination) == 'POUMON DRT':
            contralateral_lung = 'POUMON GCHE'
        else:
            contralateral_lung = 'POUMON DRT'

    if beamset.DicomPlanLabel == 'A1':
        beam_name = 'A1.1'
        beam_name_2 = 'A1.2'
    elif beamset.DicomPlanLabel == 'B1':
        beam_name = 'B1.1'
        beam_name_2 = 'B1.2'
        if poi.poi_exists("ISO B1", examination=examination):
            iso = "ISO B1"
                  
    if contralateral_lung == 'POUMON GCHE':
        # Poumon D treated
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".1", Description="OAD 30", GantryAngle=30, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".2", Description="OAG 355", GantryAngle=355, CouchAngle=0, CollimatorAngle=15, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".3", Description="OAG 320", GantryAngle=320, CouchAngle=0, CollimatorAngle=30, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".4", Description="OAG 285", GantryAngle=285, CouchAngle=0, CollimatorAngle=45, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".5", Description="OPG 250", GantryAngle=250, CouchAngle=0, CollimatorAngle=60, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".6", Description="OPG 215", GantryAngle=215, CouchAngle=0, CollimatorAngle=75, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".7", Description="POST 181", GantryAngle=181, CouchAngle=0, CollimatorAngle=90, ApertureBlock=None)
    elif contralateral_lung == 'POUMON DRT':
        # Poumon G treated
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".1", Description="POST 180", GantryAngle=180, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".2", Description="OPD 145", GantryAngle=145, CouchAngle=0, CollimatorAngle=15, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".3", Description="OPD 110", GantryAngle=110, CouchAngle=0, CollimatorAngle=30, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".4", Description="OAD 75", GantryAngle=75, CouchAngle=0, CollimatorAngle=45, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".5", Description="OAD 40", GantryAngle=40, CouchAngle=0, CollimatorAngle=60, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".6", Description="OAD 5", GantryAngle=5, CouchAngle=0, CollimatorAngle=75, ApertureBlock=None)
        beamset.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter=poi.get_poi_coordinates('ISO', examination=examination).value, Name=beamset.DicomPlanLabel+".7", Description="OAG 330", GantryAngle=330, CouchAngle=0, CollimatorAngle=90, ApertureBlock=None)
    else:
        lib.error('Contralateral lung ROI name not recognized.')  
        
# Ajouté par MA	
def add_beams_prostate_A1(beamset, site_name='A1'):
    """
		Ajoute l'arc utilisé pour le plan A1 d'un prostate VMAT

        Par défaut, ajoutes un arc allant de :
        - 181 à 180 degrés en CW avec collimateur de 5 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.

        Args:
            beamset (objet) : un object beamset de RayStation associé au plan A1

        .. seealso::
          fonction :py:func:`hmrlib.lib.add_arc`
    """   

    iso = poi.identify_isocenter_poi()
    lib.add_arc((site_name+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
    
    
# Ajouté par MA	
def add_beams_prostate_A2(beamset):
   
    """
		Ajoute l'arc utilisé pour le plan A1 d'un prostate VMAT

        Par défaut, ajoutes un arc allant de :
        - 181 à 180 degrés en CW avec collimateur de 5 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.

        Args:
            beamset (objet) : un object beamset de RayStation associé au plan A2

        .. seealso::
          fonction :py:func:`hmrlib.lib.add_arc`
    """   

    iso = poi.identify_isocenter_poi()
    lib.add_arc('A2.1', iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
    
    
    
def add_beams_vertebre_stereo(beamset=None, site_name='A1'):
    """
        Ajoute les arcs utilisés pour la stéréo de vertebre.

        Par défaut, ajoutes des arcs allant de :

        - 181 à 180 degrés en CW avec collimateur de 5 degrés
        - 180 à 181 degrés en CCW avec collimateur de 90 degrés

        .. rubric::
          PRÉ-REQUIS :

        - Isocentre nommé *ISO SCAN* ou *ISO*.

        .. seealso::
          fonction :py:func:`hmrlib.lib.add_arc`
    """
    if beamset is None:
        beamset = lib.get_current_beamset()
    
    iso = poi.identify_isocenter_poi()
    lib.add_arc((site_name+'.1'), iso, 180, 181, 'CCW', description='ARC 180-181', collimator=5, beamset=beamset)
    lib.add_arc((site_name+'.2'), iso, 181, 180, 'CW', description='ARC 181-180', collimator=90, beamset=beamset)
    
    
def ajouter_arc_oppose():
    """
        Ajoute un arc VMAT avec angles gantry, collimateur et sens opposé au faisceau existant.
        Ce script devrait seulement être utilisé pour des beamsets comprenant un seul arc.
        Le script suppose que l'isocentre du plan s'appelle ISO, mais ISO B1 sera utilisé s'il existe et si le premier arc commence par "B"
    """

    plan = lib.get_current_plan()
    beamset = lib.get_current_beamset()
    exam = lib.get_current_examination()
        
    i = 0
    for beam in beamset.Beams:
        i+=1
        
    if i == 1: #This script is only meant to add a second beam when a single beam exists
        new_name = beamset.Beams[0].Name[:-1] + "2"
        if poi.poi_exists("ISO B1") and beamset.Beams[0].Name[0]=='B':
            iso = "ISO B1"
        else:
            iso = "ISO"
        if beamset.Beams[0].ArcRotationDirection == "Clockwise":
            new_sens = "CCW"
        else:
            new_sens = "CW"
        new_description = "ARC %d-%d" % (beamset.Beams[0].ArcStopGantryAngle, beamset.Beams[0].GantryAngle)
        new_colli = 360 - beamset.Beams[0].InitialCollimatorAngle
        lib.add_arc(new_name, iso, beamset.Beams[0].ArcStopGantryAngle, beamset.Beams[0].GantryAngle, new_sens, description=new_description, collimator=new_colli, beamset=beamset, exam=exam)
        
    # Update max delivery time for new beam
    max_time = plan.PlanOptimizations[beamset.Number-1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].ArcConversionPropertiesPerBeam.MaxArcDeliveryTime
    plan.PlanOptimizations[beamset.Number-1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].ArcConversionPropertiesPerBeam.MaxArcDeliveryTime = max_time