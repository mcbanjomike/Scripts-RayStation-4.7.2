# -*- coding: utf-8 -*-

import hmrlib.lib as lib
import hmrlib.eval as eval
import hmrlib.roi as roi
import hmrlib.optim as optim
import launcher

logger = lib.logger


# Read clinical goal dictionary (defined by GJ)
def read_cg(filepath=r'\\MAGGIE\physicien\dvh_pdf\CRITERES.txt'):
    critere = open(filepath)
    c = {}
    for l in critere:
        if not l.strip(): #If l contains only spaces...
            continue #...move to the next line
        tol = l.split()
        c[tuple(tol[:-4])] = tol[-4:]
    return c

    
# Automatically fill list of clinical goals using the dictionary
def add_dictionary_cg(Site, RX, FX, plan=None):
    """
    Args:
        Site (string)
        RX (float): The total prescribed dose for the plan in Gy
        FX (int): The number of fractions for the plan
        plan: RayStation plan object to which the clinical goals should be added
    It is recommended to erase all clinical goals in the plan before running this script.
    Note that you are allowed to have ROIs with spaces in their names or ROIs with underscores in their names, but NOT BOTH IN THE SAME PATIENT.
    """
    
    if plan is None:
        plan = lib.get_current_plan()
    
    c = read_cg()

    Site = Site.upper().replace(' ', '_')
    RX = str(RX)
    FX = str(FX)
    
    #launcher.debug_window(Site)
    
    #Go through the dictionary line by line, adding clinical goals for each
    for k,v in c.items(): #k is for key, v is for values
        if k[0]==Site and k[1]==RX and k[2]==FX:
            if Site != 'PROSTATE_PACE': #Exception because PACE protocol ROIs have underscores in their names
                roi_name = k[3].replace('_', ' ') #Change underscores to spaces
            else:
                roi_name = k[3]
            type = k[4]
            #ctype, tol1, tol2, unit = c[(Site, RX, FX, roi_name.replace(' ', '_'), type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs
            ctype, tol1, tol2, unit = c[(Site, RX, FX, k[3], type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs            
            if ctype == 'PTV':
                criteria = 'AtLeast'
            elif ctype == 'OAR':
                criteria = 'AtMost'
            if type[0] == "D" and type[-2:] == "cc":  # Criterion of type Dxxcc
                absvol = float(type[1:-2])
                eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, "DoseAtAbsoluteVolume", absvol, plan=plan)
            elif type[0] == "D" and type[-1:] == r'%':  # Criterion of type Dxx%
                relvol = float(type[1:-1])
                eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, "DoseAtVolume", relvol, plan=plan)
            elif type[0] == "V" and type[-2:] == "Gy":  # Criterion of type Vxx
                if 'cc' in unit: # Absolute volume (cc)
                    dose_level = float(type[1:-2])
                    eval.add_clinical_goal(roi_name, dose_level * 100, criteria, 'AbsoluteVolumeAtDose', float(tol2), plan=plan)
                else: # Relative volume (%)
                    dose_level = float(type[1:-2])
                    eval.add_clinical_goal(roi_name, dose_level * 100, criteria, 'VolumeAtDose', float(tol2), plan=plan)
            elif type == "Dmoy":
                eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, 'AverageDose', 0, plan=plan)


# Automatically fill list of clinical goals using the dictionary
def add_dictionary_cg2(Site, RX, FX, plan=None,skip_modptv = False):
    """
    Args:
        Site (string)
        RX (float): The total prescribed dose for the plan in Gy
        FX (int): The number of fractions for the plan
        plan: RayStation plan object to which the clinical goals should be added
    It is recommended to erase all clinical goals in the plan before running this script.
    Note that you are allowed to have ROIs with spaces in their names or ROIs with underscores in their names, but NOT BOTH IN THE SAME PATIENT.
    """
    
    if plan is None:
        plan = lib.get_current_plan()
    
    c = read_cg()

    Site = Site.upper().replace(' ', '_')
    RX = str(RX)
    FX = str(FX)
    
    #launcher.debug_window(Site)
    
    #Go through the dictionary line by line, adding clinical goals for each
    for k,v in c.items(): #k is for key, v is for values
        if k[0]==Site and k[1]==RX and k[2]==FX:
            if Site != 'PROSTATE_PACE': #Exception because PACE protocol ROIs have underscores in their names
                roi_name = k[3].replace('_', ' ') #Change underscores to spaces
            else:
                roi_name = k[3]
            type = k[4]
            #ctype, tol1, tol2, unit = c[(Site, RX, FX, roi_name.replace(' ', '_'), type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs
            ctype, tol1, tol2, unit = c[(Site, RX, FX, k[3], type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs            
            if ctype == 'PTV':
                criteria = 'AtLeast'
            elif ctype == 'OAR':
                criteria = 'AtMost'
            if skip_modptv and roi_name[:6]=='modPTV':
                continue            
            elif type[0] == "D" and type[-2:] == "cc":  # Criterion of type Dxxcc
                absvol = float(type[1:-2])
                eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, "DoseAtAbsoluteVolume", absvol, plan=plan)
            elif type[0] == "D" and type[-1:] == r'%':  # Criterion of type Dxx%
                relvol = float(type[1:-1])
                eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, "DoseAtVolume", relvol, plan=plan)
            elif type[0] == "V" and type[-2:] == "Gy":  # Criterion of type Vxx
                if 'cc' in unit: # Absolute volume (cc)
                    dose_level = float(type[1:-2])
                    eval.add_clinical_goal(roi_name, dose_level * 100, criteria, 'AbsoluteVolumeAtDose', float(tol2), plan=plan)
                else: # Relative volume (%)
                    dose_level = float(type[1:-2])
                    eval.add_clinical_goal(roi_name, dose_level * 100, criteria, 'VolumeAtDose', float(tol2), plan=plan)
            elif type == "Dmoy":
                if roi_name == 'LARYNX':
                    eval.add_clinical_goal(roi_name, 4500, criteria, 'AverageDose', 0, plan=plan)
                elif roi_name == 'OESOPHAGE':
                    eval.add_clinical_goal(roi_name, 4500, criteria, 'AverageDose', 0, plan=plan)
                else:
                    eval.add_clinical_goal(roi_name, float(tol2) * 100, criteria, 'AverageDose', 0, plan=plan)
                   
    
# VTL
def add_cg_brain_stereo(patient_plan=None):
    """
    Ajoute les *clinical goals*, ou critères cliniques, de stéréotaxie de crâne.

    Assume un seul PTV.

    .. rubric::
      PRÉ-REQUIS :

    - PTV nommé avec son niveau de prescription. Ex. : *PTV18*.

    Les prescriptions supportées sont :

    * 15 Gy
    * 18 Gy
    * 20 Gy

    Des avertissements seront affichés à l'écran pour chacun des ROI non
    trouvés par le script.

    Tableau des critères cliniques insérés :

    ===================  ===============  ===========  ========  =========
    ROI                  Type de critère  Comparateur  Valeur 1  Valeur 2
    ===================  ===============  ===========  ========  =========
    PTV<dose>\*          ``Volume@dose``  :math:`\ge`  99 %      <dose> Gy
    PTV<dose>\*\*        ``Volume@dose``  :math:`\ge`  1 cc      <dose> Gy
    BODY\*\*             ``Volume@dose``  :math:`\ge`  1 cc      <dose PTV> Gy
    CERVEAU-PTV          ``Volume@dose``  :math:`\le`  10 cc     12 Gy
    CERVEAU-PTV          ``Volume@dose``  :math:`\le`  15 cc     10 Gy
    CHIASMA              ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    MOELLE               ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    NERF OPT DRT         ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    NERF OPT GCHE        ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    OREILLE D            ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    OREILLE G            ``Dose@Volume``  :math:`\le`  8 Gy      0.1 cc
    COCHLEE              ``Dose@Volume``  :math:`\le`  12 Gy     0.1 cc
    TRONC CEREBRAL       ``Dose@Volume``  :math:`\le`  10 Gy     0.1 cc
    ===================  ===============  ===========  ========  =========

    .. note::
      \*<dose> représente le niveau de prescription en Gy, par exemple *15*.

    .. note::
      \*\*Utilisés seulement pour calculer l'index de conformité.

    .. seealso::
      fonction :py:func:`hmrlib.eval.add_clinical_goal`
    """
    ptvs = roi.identify_ptvs2()

    if len(ptvs) > 1:
        logger.warning('More than one dose level found for PTVs.  PTVs = %s' % ptvs)
        # raise SystemError('More than one dose level found.')

    if patient_plan is None:
        patient_plan = lib.get_current_plan()

    # PTV/GTV
    if 'PTV15' in ptvs:
        # hmrlib.eval.add_clinical_goal('PTV15', 1425, 'AtLeast', 'DoseAtVolume', 100.00, plan=patient_plan)
        eval.add_clinical_goal('PTV15', 1500, 'AtLeast', 'VolumeAtDose', 99, plan=patient_plan)
        eval.add_clinical_goal('PTV15', 1500, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        # eval.add_clinical_goal('BODY', 1500, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        eval.add_clinical_goal('BodyRS', 1500, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        # hmrlib.eval.add_clinical_goal('PTV15', 3000, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

        # hmrlib.eval.add_clinical_goal('GTV', 1500, 'AtLeast', 'DoseAtVolume', 100.00, plan=patient_plan)

    elif 'PTV18' in ptvs:
        # hmrlib.eval.add_clinical_goal('PTV18', 1710, 'AtLeast', 'DoseAtVolume', 100.00, plan=patient_plan)
        eval.add_clinical_goal('PTV18', 1800, 'AtLeast', 'VolumeAtDose', 99, plan=patient_plan)
        eval.add_clinical_goal('PTV18', 1800, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        # eval.add_clinical_goal('BODY', 1800, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        eval.add_clinical_goal('BodyRS', 1800, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        # hmrlib.eval.add_clinical_goal('PTV18', 3600, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

        # hmrlib.eval.add_clinical_goal('GTV', 1800, 'AtLeast', 'DoseAtVolume', 100.00, plan=patient_plan)

    elif 'PTV20' in ptvs:
        eval.add_clinical_goal('PTV20', 2000, 'AtLeast', 'VolumeAtDose', 99, plan=patient_plan)
        eval.add_clinical_goal('PTV20', 2000, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        # eval.add_clinical_goal('BODY', 2000, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)
        eval.add_clinical_goal('BodyRS', 2000, 'AtLeast', 'AbsoluteVolumeAtDose', 1, plan=patient_plan)

    else:
        logger.warning('No PTV with supported dose level found.  Please name PTV with prescription in name (ex. PTV18).')
        logger.warning('Adding brain stereotaxy clinical goals which are not related to PTV.')

    # OAR
    eval.add_clinical_goal('CERVEAU-PTV', 1200, 'AtMost', 'AbsoluteVolumeAtDose', 10, plan=patient_plan)
    eval.add_clinical_goal('CERVEAU-PTV', 1000, 'AtMost', 'AbsoluteVolumeAtDose', 15, plan=patient_plan)

    eval.add_clinical_goal('CHIASMA', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('MOELLE', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('OEIL DRT', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('OEIL GCHE', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('NERF OPT DRT', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('NERF OPT GCHE', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('OREILLE DRT', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('OREILLE GCHE', 800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('COCHLEE', 1200, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('TR CEREBRAL', 1000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)


# VTL
def add_cg_lung_stereo(contralateral_lung=None, patient_plan=None, examination=None):
    """
    Ajoute les *clinical goals*, ou critères cliniques, de stéréotaxie de poumon.

    .. rubric::
      PRÉ-REQUIS :

    - PTV nommé avec son niveau de prescription. Ex. : *PTV48*.

    Si le poumon contralatéral n'est pas spécifié, détecte si le PTV est situé
    dans POUMON D ou POUMON G et ajuste en conséquence.

    Les prescriptions supportées sont :

    * 48 Gy - 4 Fx
    * 54 Gy - 3 Fx
    * 60 Gy - 8 Fx

    Des avertissements seront affichés à l'écran pour chacun des ROI non
    trouvés par le script.

    Args:
        contralateral_lung (str, optional): nom du ROI étant le poumon contralatéral

    .. rubric::
      Tableau des critères pour 48 Gy - 4 Fx :

    =====================  ================  ===========  ===============  =========
    ROI                    Type de critère   Comparateur  Valeur 1         Valeur 2
    =====================  ================  ===========  ===============  =========
    PTV48                  ``Volume@dose``   :math:`\ge`  100 % - 0.1 cc   45.6 Gy
    PTV48                  ``Volume@dose``   :math:`\ge`  95 %             48 Gy
    PTV48                  ``Dose@Volume``   :math:`\le`  80 Gy            0.1 cc
    BR SOUCHE              ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    COEUR                  ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  5 Gy             30 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  10 Gy            15 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  15 Gy            10 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  20 Gy            5 cc
    COMBI PMN-ITV-BR       ``Dose moyenne``  :math:`\le`  5 Gy
    COTES                  ``Dose@Volume``   :math:`\le`  10 Gy            5 cc
    COTES                  ``Dose@Volume``   :math:`\le`  20 Gy            3.6 cc
    COTES                  ``Dose@Volume``   :math:`\le`  30 Gy            1.4 cc
    COTES                  ``Dose@Volume``   :math:`\le`  40 Gy            0.3 cc
    COTES                  ``Dose@Volume``   :math:`\le`  42 Gy            0.1 cc
    COTES                  ``Dose@Volume``   :math:`\le`  48 Gy            0.1 cc
    ESTOMAC                ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    GROS VAISSEAUX         ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    INTESTINS              ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    MOELLE                 ``Dose@Volume``   :math:`\le`  20.2 Gy          0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  11 Gy            0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  30.5 Gy          0.1 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  33.9 Gy          30 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  68.5 Gy          3 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  45.5 Gy          0.2 %
    PEAU                   ``Dose@Volume``   :math:`\le`  27 Gy            0.1 cc
    PLEXUS BRACHIAL        ``Dose@Volume``   :math:`\le`  27 Gy            0.1 cc
    <poumon contralat.>\*  ``Dose@Volume``   :math:`\le`  5 Gy             25 cc
    PRV MOELLE             ``Dose@Volume``   :math:`\le`  22.4 Gy          0.1 cc
    PRV PLEXUS             ``Dose@Volume``   :math:`\le`  30.5 Gy          0.1 cc
    TISSU SAIN A 2cm       ``Dose@Volume``   :math:`\le`  24 Gy            0.1 cc
    TRACHEE                ``Dose@Volume``   :math:`\le`  33.9 Gy          0.1 cc
    =====================  ================  ===========  ===============  =========

    .. rubric::
      Tableau des critères pour 54 Gy - 3 Fx :

    =====================  ================  ===========  ===============  =========
    ROI                    Type de critère   Comparateur  Valeur 1         Valeur 2
    =====================  ================  ===========  ===============  =========
    PTV54                  ``Volume@dose``   :math:`\ge`  100 % - 0.1 cc   51.3 Gy
    PTV54                  ``Volume@dose``   :math:`\ge`  95 %             54 Gy
    PTV54                  ``Dose@Volume``   :math:`\le`  85 Gy            0.1 cc
    BR SOUCHE              ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    COEUR                  ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  5 Gy             20 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  10 Gy            15 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  15 Gy            10 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  20 Gy            5 cc
    COMBI PMN-ITV-BR       ``Dose moyenne``  :math:`\le`  5 Gy
    COTES                  ``Dose@Volume``   :math:`\le`  9.1 Gy           5 cc
    COTES                  ``Dose@Volume``   :math:`\le`  17.9 Gy          3.6 cc
    COTES                  ``Dose@Volume``   :math:`\le`  26.6 Gy          1.4 cc
    COTES                  ``Dose@Volume``   :math:`\le`  35.3 Gy          0.3 cc
    COTES                  ``Dose@Volume``   :math:`\le`  37 Gy            0.1 cc
    COTES                  ``Dose@Volume``   :math:`\le`  54 Gy            0.1 cc
    ESTOMAC                ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    GROS VAISSEAUX         ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    INTESTINS              ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    MOELLE                 ``Dose@Volume``   :math:`\le`  18 Gy            0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  10 Gy            0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  27 Gy            0.1 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  30 Gy            30 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  60 Gy            3 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  40 Gy            0.2 %
    PEAU                   ``Dose@Volume``   :math:`\le`  24 Gy            0.1 cc
    PLEXUS BRACHIAL        ``Dose@Volume``   :math:`\le`  24 Gy            0.1 cc
    <poumon contralat.>\*  ``Dose@Volume``   :math:`\le`  5 Gy             25 cc
    PRV MOELLE             ``Dose@Volume``   :math:`\le`  20 Gy            0.1 cc
    PRV PLEXUS             ``Dose@Volume``   :math:`\le`  27 Gy            0.1 cc
    TISSU SAIN A 2cm       ``Dose@Volume``   :math:`\le`  27 Gy            0.1 cc
    TRACHEE                ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    =====================  ================  ===========  ===============  =========

    .. rubric::
      Tableau des critères pour 60 Gy - 8 Fx :

    =====================  ================  ===========  ===============  =========
    ROI                    Type de critère   Comparateur  Valeur 1         Valeur 2
    =====================  ================  ===========  ===============  =========
    PTV60                  ``Volume@dose``   :math:`\ge`  100 % - 0.1 cc   57 Gy
    PTV60                  ``Volume@dose``   :math:`\ge`  95 %             60 Gy
    PTV60                  ``Dose@Volume``   :math:`\le`  90 Gy            0.1 cc
    BR SOUCHE              ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    COEUR                  ``Dose@Volume``   :math:`\le`  38.5 Gy          15 cc
    COEUR                  ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    COEUR                  ``Dose@Volume``   :math:`\le`  61 Gy            0.1 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  5 Gy             20 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  10 Gy            15 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  15 Gy            10 cc
    COMBI PMN-ITV-BR       ``Dose@Volume``   :math:`\le`  20 Gy            5 cc
    COMBI PMN-ITV-BR       ``Dose moyenne``  :math:`\le`  5 Gy
    COTES                  ``Dose@Volume``   :math:`\le`  12.2 Gy          5 cc
    COTES                  ``Dose@Volume``   :math:`\le`  25.7 Gy          3.6 cc
    COTES                  ``Dose@Volume``   :math:`\le`  39.6 Gy          1.4 cc
    COTES                  ``Dose@Volume``   :math:`\le`  53.6 Gy          0.3 cc
    COTES                  ``Dose@Volume``   :math:`\le`  56.4 Gy          0.1 cc
    COTES                  ``Dose@Volume``   :math:`\le`  60 Gy            0.1 cc
    ESTOMAC                ``Dose@Volume``   :math:`\le`  32.9 Gy          5 cc
    ESTOMAC                ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    ESTOMAC                ``Dose@Volume``   :math:`\le`  61 Gy            0.1 cc
    GROS VAISSEAUX         ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    GROS VAISSEAUX         ``Dose@Volume``   :math:`\le`  48.6 Gy          0.1 cc
    GROS VAISSEAUX         ``Dose@Volume``   :math:`\le`  61 Gy            0.1 cc
    INTESTINS              ``Dose@Volume``   :math:`\le`  32.9 Gy          5 cc
    INTESTINS              ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    INTESTINS              ``Dose@Volume``   :math:`\le`  61 Gy            0.1 cc
    MOELLE                 ``Dose@Volume``   :math:`\le`  25.9 Gy          0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  13.5 Gy          0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  40.3 Gy          0.1 cc
    OESOPHAGE              ``Dose@Volume``   :math:`\le`  61 Gy            0.1 cc
    OESO PAROI OPP         ``Dose@Volume``   :math:`\le`  32.9 Gy          5 cc
    OESO PAROI OPP         ``Dose@Volume``   :math:`\le`  60 Gy            0.1 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  45.1 Gy          30 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  93.8 Gy          3 cc
    PAROI                  ``Dose@Volume``   :math:`\le`  61.3 Gy          0.2 %
    PEAU                   ``Dose@Volume``   :math:`\le`  35.5 Gy          0.1 cc
    PLEXUS BRACHIAL        ``Dose@Volume``   :math:`\le`  35.5 Gy          0.1 cc
    <poumon contralat.>\*  ``Dose@Volume``   :math:`\le`  5 Gy             25 cc
    PRV MOELLE             ``Dose@Volume``   :math:`\le`  29.1 Gy          0.1 cc
    PRV PLEXUS             ``Dose@Volume``   :math:`\le`  40.3 Gy          0.1 cc
    TISSU SAIN A 2cm       ``Dose@Volume``   :math:`\le`  30 Gy            0.1 cc
    TRACHEE                ``Dose@Volume``   :math:`\le`  45.1 Gy          0.1 cc
    =====================  ================  ===========  ===============  =========

    .. note::
      \*<poumon contralat.> représente le nom du ROI du poumon contralatéral, soit *POUMON G* ou *POUMON D*.

    .. seealso::
      fonctions :py:func:`hmrlib.eval.add_clinical_goal`, :py:func:`hmrlib.roi.find_most_intersecting_roi`
    """
    ptvs = roi.identify_ptvs2()

    if len(ptvs) > 1:
        logger.warning('More than one dose level found for PTVs.  PTVs = %s' % ptvs)
        # raise SystemError('More than one dose level found.')

    if examination is None:
        examination = lib.get_current_examination()

    if patient_plan is None:
        patient_plan = lib.get_current_plan()

    if 'PTV48' in ptvs:
        # Compute what is 0.1 cc in percentage of the volume
        ptone_cc_percentage = roi.convert_absolute_volume_to_percentage('PTV48', volume_cc=0.1, examination=examination)

        # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
        eval.add_clinical_goal('PTV48', 4560, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=patient_plan)
        # hmrlib.eval.add_clinical_goal('PTV48', 4560, 'AtLeast', 'AbsoluteVolumeAtDose', hmrlib.get_roi_volume('PTV48') - 0.1, plan=patient_plan)
        eval.add_clinical_goal('PTV48', 4800, 'AtLeast', 'VolumeAtDose', 95, plan=patient_plan)
        eval.add_clinical_goal('PTV48', 8000, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

        eval.add_clinical_goal('BR SOUCHE', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('COEUR', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'VolumeAtDose', 30, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1000, 'AtMost', 'VolumeAtDose', 15, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1500, 'AtMost', 'VolumeAtDose', 10, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 2000, 'AtMost', 'VolumeAtDose', 5, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'AverageDose', 0, plan=patient_plan)

        eval.add_clinical_goal('COTES', 1000, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('COTES', 2000, 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=patient_plan)
        eval.add_clinical_goal('COTES', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=patient_plan)
        eval.add_clinical_goal('COTES', 4000, 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=patient_plan)
        eval.add_clinical_goal('COTES', 4200, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('COTES', 4800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # Si cotes ds PTV

        eval.add_clinical_goal('ESTOMAC', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('GROS VAISSEAUX', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('INTESTINS', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('MOELLE', 2020, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('OESOPHAGE', 1100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('OESOPHAGE', 3050, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # si pres du PTV

        eval.add_clinical_goal('PAROI', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 6850, 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 4550, 'AtMost', 'DoseAtVolume', 0.20, plan=patient_plan)

        eval.add_clinical_goal('PEAU', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PLEXUS BRACHIAL', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV48', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=patient_plan)

        eval.add_clinical_goal('PRV MOELLE', 2240, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PRV PLEXUS', 3050, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TISSU SAIN A 2cm', 2400, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TRACHEE', 3390, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        # eval.add_clinical_goal('r50', 2400, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    elif 'PTV54' in ptvs:
        # Compute what is 0.1 cc in percentage of the volume
        ptone_cc_percentage = roi.convert_absolute_volume_to_percentage('PTV54', volume_cc=0.1, examination=examination)

        # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
        eval.add_clinical_goal('PTV54', 5130, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=patient_plan)
        # hmrlib.eval.add_clinical_goal('PTV54', 5130, 'AtLeast', 'AbsoluteVolumeAtDose', hmrlib.get_roi_volume('PTV54') - 0.1, plan=patient_plan)
        eval.add_clinical_goal('PTV54', 5400, 'AtLeast', 'VolumeAtDose', 95, plan=patient_plan)
        eval.add_clinical_goal('PTV54', 8500, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

        eval.add_clinical_goal('BR SOUCHE', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('COEUR', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'VolumeAtDose', 20, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1000, 'AtMost', 'VolumeAtDose', 15, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1500, 'AtMost', 'VolumeAtDose', 10, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 2000, 'AtMost', 'VolumeAtDose', 5, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'AverageDose', 0, plan=patient_plan)

        eval.add_clinical_goal('COTES', 910, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('COTES', 1790, 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=patient_plan)
        eval.add_clinical_goal('COTES', 2660, 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=patient_plan)
        eval.add_clinical_goal('COTES', 3530, 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=patient_plan)
        eval.add_clinical_goal('COTES', 3700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('COTES', 5400, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # Si cotes ds PTV

        eval.add_clinical_goal('ESTOMAC', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('GROS VAISSEAUX', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('INTESTINS', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('MOELLE', 1800, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('OESOPHAGE', 1000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('OESOPHAGE', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # si pres du PTV

        eval.add_clinical_goal('PAROI', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 4000, 'AtMost', 'DoseAtVolume', 0.20, plan=patient_plan)

        eval.add_clinical_goal('PEAU', 2400, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PLEXUS BRACHIAL', 2400, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV54', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=patient_plan)

        eval.add_clinical_goal('PRV MOELLE', 2000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PRV PLEXUS', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TISSU SAIN A 2cm', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TRACHEE', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        # eval.add_clinical_goal('r50', 2700, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    elif 'PTV60' in ptvs:
        # Compute what is 0.1 cc in percentage of the volume
        ptone_cc_percentage = roi.convert_absolute_volume_to_percentage('PTV60', volume_cc=0.1, examination=examination)

        # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
        eval.add_clinical_goal('PTV60', 5700, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=patient_plan)
        # hmrlib.eval.add_clinical_goal('PTV60', 5700, 'AtLeast', 'AbsoluteVolumeAtDose', hmrlib.get_roi_volume('PTV60') - 0.1, plan=patient_plan)
        eval.add_clinical_goal('PTV60', 6000, 'AtLeast', 'VolumeAtDose', 95, plan=patient_plan)
        eval.add_clinical_goal('PTV60', 9000, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

        eval.add_clinical_goal('BR SOUCHE', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('BR SOUCHE PAROI OPP', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('BR SOUCHE PAROI OPP', 2110, 'AtMost', 'DoseAtAbsoluteVolume', 4.0, plan=patient_plan)

        eval.add_clinical_goal('COEUR', 3850, 'AtMost', 'DoseAtAbsoluteVolume', 15.0, plan=patient_plan)
        eval.add_clinical_goal('COEUR', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('COEUR', 6100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'VolumeAtDose', 20, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1000, 'AtMost', 'VolumeAtDose', 15, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 1500, 'AtMost', 'VolumeAtDose', 10, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 2000, 'AtMost', 'VolumeAtDose', 5, plan=patient_plan)
        eval.add_clinical_goal('COMBI PMN-ITV-BR', 500, 'AtMost', 'AverageDose', 0, plan=patient_plan)

        eval.add_clinical_goal('COTES', 1220, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('COTES', 2570, 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=patient_plan)
        eval.add_clinical_goal('COTES', 3960, 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=patient_plan)
        eval.add_clinical_goal('COTES', 5360, 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=patient_plan)
        eval.add_clinical_goal('COTES', 5640, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('COTES', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # Si cotes ds PTV

        eval.add_clinical_goal('ESTOMAC', 3290, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('ESTOMAC', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('ESTOMAC', 6100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('GROS VAISSEAUX', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('GROS VAISSEAUX', 4860, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('GROS VAISSEAUX', 6100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('INTESTINS', 3290, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('INTESTINS', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('INTESTINS', 6100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('MOELLE', 2590, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('OESOPHAGE', 1350, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('OESOPHAGE', 4030, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
        eval.add_clinical_goal('OESOPHAGE', 6100, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)  # si pres du PTV

        eval.add_clinical_goal('OESO PAROI OPP', 3290, 'AtMost', 'DoseAtAbsoluteVolume', 5.0, plan=patient_plan)
        eval.add_clinical_goal('OESO PAROI OPP', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PAROI', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 9380, 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=patient_plan)
        eval.add_clinical_goal('PAROI', 6130, 'AtMost', 'DoseAtVolume', 0.20, plan=patient_plan)

        eval.add_clinical_goal('PEAU', 3550, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PLEXUS BRACHIAL', 3550, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV60', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=patient_plan)

        eval.add_clinical_goal('PRV MOELLE', 2910, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('PRV PLEXUS', 4030, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TISSU SAIN A 2cm', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        eval.add_clinical_goal('TRACHEE', 4510, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

        # eval.add_clinical_goal('r50', 3000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    else:
        logger.warning('No PTV with supported dose level found.  Please name PTV with prescription in name (ex. PTV48).')


# MA
# This script is no longer used now that prostate CGs are taken from the common dictionary
def add_cg_prostate_A1(patient_plan=None):
    """
    Ajoute les *clinical goals*, ou critères cliniques, pour le plan 1 de prostate en VMAT.

    .. rubric::
      PRÉ-REQUIS :

    - PTV nommé *PTV A1*.
    """

    if patient_plan is None:
        patient_plan = lib.get_current_plan()

    eval.add_clinical_goal('PTV A1', 7600, 'AtLeast', 'VolumeAtDose', 99.5, plan=patient_plan)
    eval.add_clinical_goal('BodyRS', 8800, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=patient_plan)

    eval.add_clinical_goal('INTESTINS', 4500, 'AtMost', 'AbsoluteVolumeAtDose', 65, plan=patient_plan)
    eval.add_clinical_goal('INTESTINS', 4000, 'AtMost', 'AbsoluteVolumeAtDose', 100, plan=patient_plan)
    eval.add_clinical_goal('INTESTINS', 3500, 'AtMost', 'AbsoluteVolumeAtDose', 180, plan=patient_plan)
    eval.add_clinical_goal('INTESTINS', 5000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('RECTUM', 7500, 'AtMost', 'VolumeAtDose', 15, plan=patient_plan)
    eval.add_clinical_goal('RECTUM', 7000, 'AtMost', 'VolumeAtDose', 25, plan=patient_plan)
    eval.add_clinical_goal('RECTUM', 6500, 'AtMost', 'VolumeAtDose', 35, plan=patient_plan)
    eval.add_clinical_goal('RECTUM', 6000, 'AtMost', 'VolumeAtDose', 50, plan=patient_plan)
    eval.add_clinical_goal('RECTUM', 7500, 'AtMost', 'DoseAtVolume', 15, plan=patient_plan)
    eval.add_clinical_goal('RECTUM', 8000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('TETE FEMORALE DRT', 5200, 'AtMost', 'VolumeAtDose', 10, plan=patient_plan)
    eval.add_clinical_goal('TETE FEMORALE DRT', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)
    eval.add_clinical_goal('TETE FEMORALE GCHE', 5200, 'AtMost', 'VolumeAtDose', 10, plan=patient_plan)
    eval.add_clinical_goal('TETE FEMORALE GCHE', 6000, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    eval.add_clinical_goal('VESSIE', 8000, 'AtMost', 'VolumeAtDose', 15, plan=patient_plan)
    eval.add_clinical_goal('VESSIE', 7500, 'AtMost', 'VolumeAtDose', 25, plan=patient_plan)
    eval.add_clinical_goal('VESSIE', 7000, 'AtMost', 'VolumeAtDose', 35, plan=patient_plan)
    eval.add_clinical_goal('VESSIE', 6500, 'AtMost', 'VolumeAtDose', 50, plan=patient_plan)
    eval.add_clinical_goal('VESSIE', 8200, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=patient_plan)

    
def smart_cg_lung_stereo(plan=None, examination=None, nb_fx=None, rx_dose=None, ptv=None, beamset=None):
    """
    This function adds both clinical goals and optimization objectives for SBRT lung cases. In many cases, the proximity
    of an OAR to the PTV is evaluated to determine which objective/clinical goal is used and to which ROI it is applied.
    
    args:
        plan: RayStation plan object
        examination: RayStation examination object
        nb_fx: (int) The number of fractions in the plan
        rx_dose: (int) The prescription dose in cGy
        ptv: RayStation ROI object for the PTV
    """
    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()
    if beamset is None:
        beamset = lib.get_current_beamset()

    if beamset.DicomPlanLabel == 'B1':
        plan_name = 'B1'
        roi_string = ' B1'
        output_name = 'PTV B1'
    else:
        plan_name = 'A1'
        roi_string = ''
        output_name = 'PTV'
        
    # Set PTV name and prescription type
    if nb_fx == 3: #54Gy-3fx
        Rx = 0
    elif nb_fx == 4: #48Gy-4fx or 56Gy-4fx
        Rx = 1
    elif nb_fx == 8 or nb_fx == 15: #60Gy-8fx AND ALSO LUSTRE 60-15 BECAUSE I DON'T KNOW WHAT ELSE TO DO WITH THOSE YET
        Rx = 2
    elif nb_fx == 5: #60Gy-5fx
        Rx = 3

    # Determine PlanOptimization number to use (so that objectives are added to the correct beamset)
    plan_opt = beamset.Number-1
        
    # Objectives for target coverage and rings
    optim.add_mindose_objective(ptv.Name, rx_dose, weight=50, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective(ptv.Name, rx_dose*1.5, weight=1, plan=plan, plan_opt=plan_opt)

    optim.add_maxdose_objective('RING_1'+roi_string, rx_dose*1.01, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective('RING_2'+roi_string, rx_dose*0.87, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective('RING_3'+roi_string, rx_dose*0.59, plan=plan, plan_opt=plan_opt)

    # Clinical Goals
    # Compute what is 0.1 cc in percentage of the volume
    ptone_cc_percentage = roi.convert_absolute_volume_to_percentage(ptv.Name, volume_cc=0.1, examination=examination)
    # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
    eval.add_clinical_goal(ptv.Name, rx_dose*0.95, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=plan)
    eval.add_clinical_goal(ptv.Name, rx_dose, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(ptv.Name, rx_dose*1.5, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)


    # Objectives and Clinical Goals for OARs, chosen based on proximity to the PTV
    # First step is to determine whether the OAR is within 2cm/5mm of the PTV and create corresponding optimization ROIs
    roi_list = ['BR SOUCHE','COEUR','COTES','ESTOMAC','GROS VAISSEAUX','INTESTINS','OESOPHAGE','PAROI','TRACHEE','PLEXUS BRACHIAL','PRV PLEXUS','MOELLE','PRV MOELLE','PAROI OPP OESO','PAROI OPP BRONCHE','PAROI OPP TRACHEE']
    color_list = ['Red','Blue','Yellow','Green','Orange','skyblue','khaki','teal','steelblue','olive','tomato','brown','purple','pink','slateblue','yellowgreen','white']
    for i, roi_name in enumerate(roi_list):
        if roi.roi_exists(roi_name, examination):
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color=color_list[i], examination=examination, margeptv=2, output_name=output_name)
            Vol2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)
            if Vol2cm == 0:
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()
            else:
                dans5mm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color=color_list[i], examination=examination, margeptv=0.5, output_name=output_name)
                Vol5mm = roi.get_roi_volume(dans5mm.Name, exam=examination)
                if Vol5mm == 0:
                    patient.PatientModel.RegionsOfInterest[dans5mm.Name].DeleteRoi()
    # For some ROIs, determine if there is a volume inside the PTV for clinical goals
    roi_list = ['BR SOUCHES','COEUR','COTES','ESTOMAC','GROS VAISSEAUX','INTESTINS','OESOPHAGE']
    for i, roi_name in enumerate(roi_list):
        if roi.roi_exists(roi_name, examination):
            dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color=color_list[i], examination=examination, margeptv=0, output_name=output_name)
            Vol = roi.get_roi_volume(dans.Name, exam=examination)
            if Vol == 0:
                patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()    
    
    
    # BR SOUCHE
    if roi.roi_exists("BR SOUCHE", examination):
        roi_name = "BR SOUCHE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            # CG for ROI in PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            # objective on roi_name dans PTV + 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            # Create ROI hors PTV (potentially useful for optimization)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            # CG for ROI outside of PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),examination): # OAR outside of PTV, but within 5mm
                # objective on roi_name dans PTV + 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),examination): # OAR outside of PTV, but within 2cm
                # objective on roi_name dans PTV + 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                # objective on roi_name
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        
    # COEUR
    if roi.roi_exists("COEUR", examination):
        roi_name = "COEUR"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3850, 3200]  # 15cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),examination): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),examination): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # COTES
    if roi.roi_exists("COTES", examination):
        roi_name = "COTES"
        dose_level1 = [3700, 4200, 5640, 4630]  # 0.1cc hors PTV
        dose_level2 = [3530, 4000, 5360, 4400]  # 0.3cc hors PTV
        dose_level3 = [2660, 3000, 3960, 3290]  # 1.4cc hors PTV
        dose_level4 = [1790, 2000, 2570, 2180]  # 3.6cc hors PTV
        dose_level5 = [910, 1000, 1220, 1070]  # 5cc hors PTV
        dose_level6 = [5400, 4800, 6000, 6000]  # 0.1cc dans PTV - REPLACED BY rx_dose

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination, output_name=output_name)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            eval.add_clinical_goal(roi_name, rx_dose, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            # CG for ROI outside of PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),examination): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),examination): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # ESTOMAC
    if roi.roi_exists("ESTOMAC", examination):
        roi_name = "ESTOMAC"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 5cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # GROS VAISSEAUX
    if roi.roi_exists("GROS VAISSEAUX", examination):
        roi_name = "GROS VAISSEAUX"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 4860, 4010]  # 10cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 10, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # INTESTINS
    if roi.roi_exists("INTESTINS", examination):
        roi_name = "INTESTINS"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 5cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # OESOPHAGE
    if roi.roi_exists("OESOPHAGE", examination):
        roi_name = "OESOPHAGE"
        dose_level1 = [1000, 1100, 1350, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3050, 4030, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),examination): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR within 2cm of PTV
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level2[Rx], plan=plan, plan_opt=plan_opt)
        else: # OAR >2cm from PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)
                                    
    # MOELLE
    if roi.roi_exists("MOELLE", examination):
        roi_name = "MOELLE"
        dose_level1 = [1800, 2020, 2590, 2620]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PRV MOELLE
    if roi.roi_exists("PRV MOELLE", examination):
        roi_name = "PRV MOELLE"
        dose_level1 = [2000, 2240, 2910, 2930]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # Paroi oesophagienne opposée
    if roi.roi_exists("OESO PAROI OPP", examination):
        roi_name = "OESO PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 3290, 2750]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            
    # Paroi trachée/bronches opposées
    if roi.roi_exists("BR SOUCHE PAROI OPP", examination):
        roi_name = "BR SOUCHE PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 2110, 1800]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 4, plan=plan)        

    # PAROI
    if roi.roi_exists("PAROI", examination):
        roi_name = "PAROI"
        dose_level1 = [6000, 6850, 9380, 7590]  # 3cc hors PTV
        dose_level2 = [3000, 3390, 4510, 3730]  # 30cc dans PTV
        dose_level3 = [4000, 4550, 6130, 5010]  # 0.2% dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, output_name=output_name)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, output_name=output_name)
            eval.add_clinical_goal(hors.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

    # PEAU
    if roi.roi_exists("PEAU", examination):
        roi_name = "PEAU"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PLEXUS BRACHIAL
    if roi.roi_exists("PLEXUS BRACHIAL", examination):
        roi_name = "PLEXUS BRACHIAL"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PRV PLEXUS
    if roi.roi_exists("PRV PLEXUS", examination):
        roi_name = "PRV PLEXUS"
        dose_level1 = [2700, 3050, 4030, 3340]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # COMBI PMN-ITV-BR
    if plan_name == 'A1':
        roi_name = 'COMBI PMN-ITV-BR'
    elif plan_name == 'B1':
        roi_name = 'COMBI PMN-2ITVs-BR'
    
    if roi.roi_exists(roi_name, examination):
        eval.add_clinical_goal(roi_name, 500, 'AtMost', 'VolumeAtDose', 20, plan=plan)
        eval.add_clinical_goal(roi_name, 1000, 'AtMost', 'VolumeAtDose', 15, plan=plan)
        eval.add_clinical_goal(roi_name, 1500, 'AtMost', 'VolumeAtDose', 10, plan=plan)
        eval.add_clinical_goal(roi_name, 2000, 'AtMost', 'VolumeAtDose', 5, plan=plan)
        eval.add_clinical_goal(roi_name, 500, 'AtMost', 'AverageDose', 0, plan=plan)

    # CONTRALATERAL LUNG - Does this function need me to send it examination??
    if roi.find_most_intersecting_roi(ptv.Name, ['POUMON DRT', 'POUMON GCHE'], examination=examination) == 'POUMON GCHE':
        contralateral_lung = 'POUMON DRT'
    else:
        contralateral_lung = 'POUMON GCHE'

    eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=plan)
    optim.add_maxdose_objective(contralateral_lung, 500, plan=plan, plan_opt=plan_opt)

    # TRACHEE
    if roi.roi_exists("TRACHEE", examination):
        roi_name = "TRACHEE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),examination): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),examination): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # TISSU SAIN A 2cm
    if plan_name == 'A1':
        roi_name = 'TISSU SAIN A 2cm'
    elif plan_name == 'B1':
        roi_name = 'TISSU SAIN A 2cm A1+B1'
        
    if roi.roi_exists(roi_name, examination):
        dose_level1 = [2700, 2400, 3000, 3000]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        
    # PACEMAKER
    if roi.roi_exists("PACEMAKER", examination):
        roi_name = "PACEMAKER"
        eval.add_clinical_goal(roi_name, 200, 'AtMost', 'DoseAtAbsoluteVolume', 0, plan=plan)     
        optim.add_maxdose_objective(roi_name, 100, plan=plan, plan_opt=plan_opt)        


def smart_cg_foie_sbrt(plan=None, examination=None, ptv=None, Rx_dose=None):
    # This script adds both clinical goals and optimization objectives for cases of liver SBRT.
    # For OAR, proximity to the PTV is evaluated and used to choose which goals and objectives to add.
    # In all cases, the number of fractions determines which set of target doses are used.

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()
    if ptv is None and RX_dose is None:
        # Determine PTV name and prescription dose
        roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
        for name in roi_names:
            n = name.replace(' ', '').upper()
            if 'PTV' in n and '-' not in n:
                ptv = patient.PatientModel.RegionsOfInterest[name]
                Rx_dose = float(ptv.Name[3:])
                break
        
        
    # Determine Rx type via number of fractions
    if plan.BeamSets[0].FractionationPattern.NumberOfFractions == 3:
        Rx = 0
    elif plan.BeamSets[0].FractionationPattern.NumberOfFractions == 5:
        Rx = 1

    # Compute what is 0.1 cc in percentage of the volume
    ptone_cc_percentage = roi.convert_absolute_volume_to_percentage(ptv.Name, volume_cc=0.1, examination=examination)
    # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
    eval.add_clinical_goal(ptv.Name, Rx_dose * 95, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=plan)
    eval.add_clinical_goal(ptv.Name, Rx_dose * 100, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(ptv.Name, Rx_dose * 150, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)

    # Add optimization objectives for PTV, PTV-GTV and Rings
    optim.add_mindose_objective(ptv.Name, Rx_dose * 100, weight=10, plan=plan)
    optim.add_maxdose_objective(ptv.Name, Rx_dose * 133.33, plan=plan)

    optim.add_maxdose_objective("PTV-GTV", Rx_dose * 124.44, plan=plan)

    optim.add_maxdose_objective('Ring_1_0mm', Rx_dose * 101, plan=plan)
    optim.add_maxdose_objective('Ring_2_2mm', Rx_dose * 86.67, plan=plan)
    optim.add_maxdose_objective('Ring_3_5mm', Rx_dose * 64, plan=plan)
    optim.add_maxdose_objective('Ring_4_20mm', Rx_dose * 42.22, plan=plan)

    optim.add_dosefalloff_objective('BodyRS', Rx_dose * 101, Rx_dose * 100 / 2, 2, weight=1, plan=plan)

    # MOELLE
    if roi.roi_exists("MOELLE", examination):
        roi_name = "MOELLE"
        dose_level1 = [1800, 2620]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # prv5mmMOELLE
    if roi.roi_exists("prv5mmMOELLE", examination):
        roi_name = "prv5mmMOELLE"
        dose_level1 = [2000, 2930]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # COEUR
    if roi.roi_exists("COEUR", examination):
        roi_name = "COEUR"
        dose_level1 = [3000, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level3 = [0, 3200]  # 15cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination)
            if Rx == 1:  # Only for prescriptions in 5 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 15, 1, plan=plan)

    # OESOPHAGE, ESTOMAC, DUODENUM, GRELE and COLON all use the same logic:
        # If ROI intersects PTV, add clinical goals for ROI dans PTV as well as max 0.1cc > 2cm from PTV. Leave ROI dans PTV and ROI hors PTV+2cm contours for optimization.
            #(max 0.1cc < 2cm is not added because it is unattainable)
        # If ROI within 2cm of PTV, add clinical goal for max 0.1cc < 2cm and max 0.1cc > 2cm. Leave ROI dans PTV+2cm and ROI hors PTV+2cm contours for optimization.
        # If ROI >2cm from PTV, add clinical goal for max 0.1cc > 2cm without leaving any additional contours.

    # OESOPHAGE
    if roi.roi_exists("OESOPHAGE", examination):
        roi_name = "OESOPHAGE"
        dose_level1 = [1000, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # ESTOMAC - Same logic as OESOPHAGE, but with different dose values
    if roi.roi_exists("ESTOMAC", examination):
        roi_name = "ESTOMAC"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # DUODENUM - Exactly the same as OESOPHAGE
    if roi.roi_exists("DUODENUM", examination):
        roi_name = "DUODENUM"
        dose_level1 = [1000, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Brown", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # GRELE - Exactly the same as ESTOMAC
    if roi.roi_exists("GRELE", examination):
        roi_name = "GRELE"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Purple", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Yellow", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # COLON - Exactly the same as ESTOMAC
    if roi.roi_exists("COLON", examination):
        roi_name = "COLON"
        dose_level1 = [2000, 2450]  # 0.1cc >2cm PTV
        dose_level2 = [3000, 3730]  # 0.1cc <=2cm PTV
        dose_level3 = [0, Rx_dose * 105]  # 0.1cc dans PTV
        dose_level4 = [0, 2750]  # 5cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination)
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

            # Check if ROI in PTV+2cm
            dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination, margeptv=2)
            Voldans2cm = roi.get_roi_volume(dans2cm.Name, exam=examination)

            # Result depends on whether ROI overlaps with PTV+2cm
            if Voldans2cm == 0:  # ROI > 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
                patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()

            else:  # ROI <= 2cm from PTV
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level2[Rx] - 200, plan=plan)
                hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
                Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
                if not Volhors2cm == 0:
                    eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                    optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
                else:
                    patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

        else:  # ROI overlaps PTV
            if Rx == 1:  # Only for prescriptions of in 5fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
                optim.add_maxdose_objective(roi_name, dose_level3[Rx] - 200, plan=plan)
                optim.add_maxdvh_objective(roi_name, dose_level3[Rx] - 200, 5, 1, plan=plan)
            # create ROI hors PTV+2cm and add CG if ROI volume non-zero
            hors2cm = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Pink", examination=examination, margeptv=2)
            Volhors2cm = roi.get_roi_volume(hors2cm.Name, exam=examination)
            if not Volhors2cm == 0:
                eval.add_clinical_goal(hors2cm.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                optim.add_maxdose_objective(hors2cm.Name, dose_level1[Rx] - 200, plan=plan)
            else:
                patient.PatientModel.RegionsOfInterest[hors2cm.Name].DeleteRoi()

    # PEAU
    if roi.roi_exists("PEAU", examination):
        roi_name = "PEAU"
        dose_level1 = [2400, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # COTES
    if roi.roi_exists("COTES", examination):
        roi_name = "COTES"
        dose_level1 = [3700, 4630]  # 0.1cc hors PTV
        dose_level2 = [3530, 4400]  # 0.3cc hors PTV
        dose_level3 = [2660, 3290]  # 1.4cc hors PTV
        dose_level4 = [1790, 2180]  # 3.6cc hors PTV
        dose_level5 = [910, 1070]  # 5cc hors PTV
        dose_level6 = [5400, Rx_dose * 100]  # 0.1cc dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="Orange", examination=examination, margeptv=0.2)
        #dans.Name += "+2mm"
        Vol = roi.get_roi_volume(dans.Name, exam=examination)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)
            patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level6[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level6[Rx], plan=plan)
            optim.add_maxeud_objective(hors.Name, dose_level1[Rx] * 0.66, 1, 1, plan=plan)

    # PAROI
    if roi.roi_exists("PAROI", examination):
        roi_name = "PAROI"
        dose_level1 = [6000, 7590]  # 3cc hors PTV
        dose_level2 = [3000, 3730]  # 30cc dans PTV
        dose_level3 = [4000, 5010]  # 0.2% dans PTV

        if not roi.roi_exists("PAROI hors PTV", examination):
            hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv.Name, color="White", examination=examination)

        eval.add_clinical_goal(hors.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
        eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
        eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        optim.add_maxdose_objective(hors.Name, Rx_dose * 100 - 200, plan=plan)

    # Paroi oesophagienne opposée
    if roi.roi_exists("OESO PAROI OPP", examination):
        roi_name = "OESO PAROI OPP"
        if Rx == 1:  # Only for prescriptions in 5 fx
            dose_level1 = [0, Rx_dose * 105]  # 0.1cc
            dose_level2 = [0, 2750]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx] - 200, plan=plan)

    # FOIE EXPI
    if roi.roi_exists("FOIE EXPI", examination):
        roi_name = "FOIE EXPI"
        dose_level1 = [1500, 1810]  # dose moyenne
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)

    # FOIE EXPI-GTV
    if roi.roi_exists("FOIE EXPI-GTV", examination):
        roi_name = "FOIE EXPI-GTV"
        dose_level1 = [1500, 1810]  # dose moyenne
        dose_level2 = [1700, 2100]  # 700cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)
        eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 700, plan=plan)

    # OPT FOIE EXPI
    if roi.roi_exists("OPT FOIE EXPI", examination):
        roi_name = "OPT FOIE EXPI"
        dose_level1 = [1500, 1810]  # dose moyenne
        optim.add_maxeud_objective(roi_name, dose_level1[Rx] - 100, 1, 1, plan=plan)

    # REINS
    if roi.roi_exists("REINS", examination):
        roi_name = "REINS"
        dose_level1 = [1020, 1200]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'AverageDose', 0, plan=plan)
        optim.add_maxeud_objective('REIN DRT', dose_level1[Rx] - 200, 1, 1, plan=plan)
        optim.add_maxeud_objective('REIN GCHE', dose_level1[Rx] - 200, 1, 1, plan=plan)

    # TISSU SAIN A 2cm
    if roi.roi_exists("TISSU SAIN A 2cm", examination):
        roi_name = "TISSU SAIN A 2cm"
        eval.add_clinical_goal(roi_name, Rx_dose * 50, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
              
        
def smart_cg_orl(plan=None, examination=None):
    # This script adds both clinical goals and optimization objectives for ORL cases.
    # For OAR, proximity to the PTV is evaluated and used to choose which goals and objectives to add.
    # In all cases, the number of fractions determines which set of target doses are used.

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()

    # Determine different PTV levels. If PTV56 exists, it is assumed treatment will be in 35 fractions. If PTV54 exists, 33 fx.
    # PTVs are classified as high, mid or low to simplify generation of contours later on. If PTV70 and 66 exist, the high level PTV is their union.
    ptvs = []
    if roi.roi_exists("PTV70"):
        ptvs.append(70)
        highptv = patient.PatientModel.RegionsOfInterest["PTV70"]
    if roi.roi_exists("PTV66"):
        ptvs.append(66)
        # if roi.roi_exists("PTV70"):
        #    highptv = patient.PatientModel.RegionsOfInterest["PTV70+66"]
        # else:
        highptv = patient.PatientModel.RegionsOfInterest["PTV66"]
    if roi.roi_exists("PTV63"):
        ptvs.append(63)
        midptv = patient.PatientModel.RegionsOfInterest["PTV63"]
    if roi.roi_exists("PTV60"):
        ptvs.append(59.4)
        midptv = patient.PatientModel.RegionsOfInterest["PTV60"]
    if roi.roi_exists("PTV56"):
        ptvs.append(56)
        lowptv = patient.PatientModel.RegionsOfInterest["PTV56"]
    if roi.roi_exists("PTV54"):
        ptvs.append(54)
        lowptv = patient.PatientModel.RegionsOfInterest["PTV54"]

    # Add clinical goals for coverage
    eval.add_clinical_goal(("mod" + highptv.Name), ptvs[0] * 100, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(("mod" + highptv.Name), ptvs[0] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    eval.add_clinical_goal(("mod" + midptv.Name), ptvs[1] * 100, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(("mod" + midptv.Name), ptvs[1] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    eval.add_clinical_goal(("mod" + lowptv.Name), ptvs[2] * 100, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(("mod" + lowptv.Name), ptvs[2] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    eval.add_clinical_goal("BodyRS", ptvs[0] * 110, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)

    # Add clinical goals for OAR using common dictionary (defined by GJ)
    c = read_cg()

    Site = 'ORL'
    RX = '70'
    FX = '33'  # OAR criteria are all defined for 70Gy/33 and do not vary for other similar fractionations

    # If a given OAR has more than one criteria, put them all in the same string separated by spaces
    OAR_list = ['MOELLE', 'prv5mmMOELLE', 'TR CEREBRAL', 'prv5mm TRONC', 'MANDIBULE', 'PARO DRT', 'PARO GCHE', 'CAVITE ORALE', 'LARYNX', 'OESOPHAGE', 'CERVEAU', 'OREILLE DRT', 'OREILLE GCHE', 'PL BRACHIAL DRT', 'PL BRACHIAL GCHE', 'OEIL DRT', 'OEIL GCHE', 'N OPT DRT', 'N OPT GCHE', 'prv5mmNOD', 'prv5mmNOG', 'CRISTALLIN DRT', 'CRISTALLIN GCHE', 'CHIASMA', 'prv5mmCHIASMA']
    type_list = ['D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'Dmoy V30Gy', 'Dmoy V30Gy', 'Dmoy', 'D0.1cc Dmoy', 'D0.1cc Dmoy', 'D0.1cc', 'D0.1cc Dmoy', 'D0.1cc Dmoy', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc', 'D0.1cc']

    for i, OAR in enumerate(OAR_list):
        types = type_list[i].split()
        for type in types:
            ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs
            if type[0] == "D" and type[-2:] == "cc":  # Criterion of type Dxxcc
                absvol = float(type[1:-2])
                eval.add_clinical_goal(OAR, float(tol2) * 100, "AtMost", "DoseAtAbsoluteVolume", absvol, plan=plan)
            elif type[0] == "V" and type[-2:] == "Gy":  # Criterion of type VxxGy
                dose_level = float(type[1:-2])
                eval.add_clinical_goal(OAR, dose_level * 100, 'AtMost', 'VolumeAtDose', float(tol2), plan=plan)
            elif type == "Dmoy":
                eval.add_clinical_goal(OAR, float(tol2) * 100, 'AtMost', 'AverageDose', 0, plan=plan)

    # Add optimization objectives for PTVs, Gradients, Rings and TS
    optim.add_mindose_objective(("mod" + highptv.Name), ptvs[0] * 100, weight=25, plan=plan)
    optim.add_maxdose_objective(("mod" + highptv.Name), ptvs[0] * 104, weight=5, plan=plan)
    optim.add_mineud_objective(("mod" + highptv.Name), ptvs[0] * 101.5, 1, 25, plan=plan)

    optim.add_mindose_objective(("OPT" + midptv.Name), ptvs[1] * 100, weight=25, plan=plan)
    optim.add_maxdose_objective(("OPT" + midptv.Name), ptvs[1] * 104, weight=5, plan=plan)
    optim.add_mineud_objective(("OPT" + midptv.Name), ptvs[1] * 101.5, 1, 1, plan=plan)

    optim.add_mindose_objective(("OPT" + lowptv.Name), ptvs[2] * 100, weight=25, plan=plan)
    optim.add_maxdose_objective(("OPT" + lowptv.Name), ptvs[2] * 104, weight=5, plan=plan)
    optim.add_mineud_objective(("OPT" + lowptv.Name), ptvs[2] * 101.5, 1, 1, plan=plan)

    optim.add_mindose_objective(("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1])), ptvs[1] * 100, weight=1, plan=plan)
    optim.add_maxdose_objective(("Gradient" + str(ptvs[0]) + "-" + str(ptvs[1])), ptvs[0] * 101, weight=1, plan=plan)

    optim.add_mindose_objective(("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2])), ptvs[2] * 100, weight=1, plan=plan)
    optim.add_maxdose_objective(("Gradient" + str(ptvs[0]) + "-" + str(ptvs[2])), ptvs[0] * 101, weight=1, plan=plan)

    optim.add_mindose_objective(("Gradient" + str(ptvs[1]) + "-" + str(ptvs[2])), ptvs[2] * 100, weight=1, plan=plan)
    optim.add_maxdose_objective(("Gradient" + str(ptvs[1]) + "-" + str(ptvs[2])), ptvs[1] * 101, weight=1, plan=plan)

    optim.add_maxdose_objective(("Ring" + highptv.Name), ptvs[0] * 101, weight=1, plan=plan)
    optim.add_maxdose_objective(("Ring" + midptv.Name), ptvs[1] * 101, weight=1, plan=plan)
    optim.add_maxdose_objective(("Ring" + lowptv.Name), ptvs[2] * 101, weight=1, plan=plan)

    optim.add_maxdose_objective(("TS " + highptv.Name), ptvs[0] * 90, weight=1, plan=plan)
    optim.add_maxdose_objective(("TS " + midptv.Name), ptvs[1] * 90, weight=1, plan=plan)
    optim.add_maxdose_objective(("TS " + lowptv.Name), ptvs[2] * 95, weight=1, plan=plan)
    optim.add_maxdose_objective("TissusSains", ptvs[2] * 75, weight=1, plan=plan)

    # Add optimization objectives for OARs
    optim.add_maxdose_objective("MOELLE", 4000, weight=1, plan=plan)
    optim.add_maxdose_objective("OPT MOELLE", 4000, weight=1, plan=plan)
    optim.add_maxdose_objective("prv5mmMOELLE", 4400, weight=1, plan=plan)
    optim.add_maxdose_objective("OPT prvMOELLE", 4400, weight=1, plan=plan)

    optim.add_maxdose_objective("TR CEREBRAL", 4600, weight=1, plan=plan)
    optim.add_maxdose_objective("OPT TRONC", 4600, weight=1, plan=plan)
    optim.add_maxdose_objective("prv5mmTRONC", 5000, weight=1, plan=plan)
    optim.add_maxdose_objective("OPT prvTRONC", 5000, weight=1, plan=plan)

    optim.add_maxdose_objective("OPT CERVEAU", 5700, weight=1, plan=plan)

    optim.add_maxeud_objective("OPT PARO DRT", 1400, 1, weight=1, plan=plan)
    optim.add_maxeud_objective("OPT PARO GCHE", 1400, 1, weight=1, plan=plan)

    optim.add_maxdose_objective(("MAND-" + highptv.Name + "-5mm"), 6630, weight=1, plan=plan)
    optim.add_maxdose_objective(("MAND ds " + highptv.Name + "+5mm"), 7150, weight=1, plan=plan)

    optim.add_maxeud_objective("OPT CAVITE ORALE", 3500, 1, weight=1, plan=plan)
    optim.add_maxeud_objective("OPT LARYNX", 4000, 1, weight=1, plan=plan)
    optim.add_maxeud_objective("OPT OESOPHAGE", 1500, 1, weight=1, plan=plan)
    optim.add_maxdose_objective("OPT LEVRES", 3000, weight=1, plan=plan)

    optim.add_maxdose_objective(("PBD ds " + highptv.Name), ptvs[0] * 101.5, weight=1, plan=plan)
    optim.add_maxdose_objective(("PBD ds " + highptv.Name), ptvs[1] * 100, weight=1, plan=plan)
    optim.add_maxdose_objective(("PBG ds " + midptv.Name), ptvs[0] * 101.5, weight=1, plan=plan)
    optim.add_maxdose_objective(("PBG ds " + midptv.Name), ptvs[1] * 100, weight=1, plan=plan)

    optim.add_maxdose_objective("OREILLE DRT", 4800, weight=1, plan=plan)
    optim.add_maxdose_objective("OREILLE GCHE", 4800, weight=1, plan=plan)

    optim.add_maxdose_objective("OEIL DRT", 4800, weight=1, plan=plan)
    optim.add_maxdose_objective("OEIL GCHE", 4800, weight=1, plan=plan)
    optim.add_maxdose_objective("N OPT DRT", 4300, weight=1, plan=plan)
    optim.add_maxdose_objective("N OPT GCHE", 4300, weight=1, plan=plan)
    optim.add_maxdose_objective("prv5mmNOD", 5200, weight=1, plan=plan)
    optim.add_maxdose_objective("prv5mmNOG", 5200, weight=1, plan=plan)

    optim.add_maxdose_objective("CHIASMA", 4800, weight=1, plan=plan)
    optim.add_maxdose_objective("prv5mmCHIASMA", 5600, weight=1, plan=plan)

    optim.add_maxdose_objective("BLOC MOELLE", 4200, weight=5, plan=plan)


def smart_cg_poumon(plan=None, examination=None):
    # This script adds both clinical goals and optimization objectives for non-SBRT lung cases.
    # Prescription dose and number of fractions determines which set of target doses are used.
    # The script should work for any clinically-used combination of one or two PTVs.

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()

    # Determine different PTV levels.
    ptvs = []
    if roi.roi_exists("PTV66"):
        ptvs.append(66)
        ptv1 = patient.PatientModel.RegionsOfInterest["PTV66"]
    if roi.roi_exists("PTV60"):
        ptvs.append(60)
        if roi.roi_exists("PTV66"):
            ptv2 = patient.PatientModel.RegionsOfInterest["PTV60"]
            ptv = patient.PatientModel.RegionsOfInterest["PTV66+60"]
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV60"]
    if roi.roi_exists("PTV55"):
        ptvs.append(55)
        ptv = patient.PatientModel.RegionsOfInterest["PTV55"]
    if roi.roi_exists("PTV50"):
        ptvs.append(50)
        if roi.roi_exists("PTV55"):
            ptv1 = patient.PatientModel.RegionsOfInterest["PTV55"]
            ptv2 = patient.PatientModel.RegionsOfInterest["PTV50"]
            ptv = patient.PatientModel.RegionsOfInterest["PTV55+50"]
        else:
            ptv = patient.PatientModel.RegionsOfInterest["PTV50"]
    if roi.roi_exists("PTV40.05"):
        ptvs.append(40.05)
        ptv = patient.PatientModel.RegionsOfInterest["PTV40.05"]

    # Add clinical goals for coverage
    if len(ptvs) == 1:
        eval.add_clinical_goal(ptv.Name, ptvs[0] * 100, 'AtLeast', 'VolumeAtDose', 98, plan=plan)
        eval.add_clinical_goal(ptv.Name, ptvs[0] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    elif len(ptvs) == 2:
        eval.add_clinical_goal(ptv1.Name, ptvs[0] * 100, 'AtLeast', 'VolumeAtDose', 98, plan=plan)
        eval.add_clinical_goal(ptv1.Name, ptvs[0] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("modPTV" + str(ptvs[1])), ptvs[1] * 100, 'AtLeast', 'VolumeAtDose', 98, plan=plan)
        eval.add_clinical_goal(("modPTV" + str(ptvs[1])), ptvs[1] * 95, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    eval.add_clinical_goal("BodyRS", ptvs[0] * 120, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)

    # Add clinical goals for OAR using common dictionary (defined by GJ)
    c = read_cg()

    Site = 'POUMON'
    if ptvs[0] == 66:  # 66 Gy does not have its own set of clinical goals criteria
        RX = '60'
    else:
        RX = str(ptvs[0])

    FX = str(plan.BeamSets[0].FractionationPattern.NumberOfFractions)

    # Criteria for PMNS-PTV depend on both Rx dose and number of fractions
    if RX == '60' and FX == '30':
        poum_list = 'V5Gy V10Gy V20Gy'
    elif RX == '60' and FX == '24':
        poum_list = 'V4.5Gy V9.1Gy V18.2Gy'
    elif RX == '50' and FX == '20':  # 50/20 is always followed by 10/4, so criteria for 60/24 are used
        RX = "60"
        FX = "24"
        poum_list = 'V4.5Gy V9.1Gy V18.2Gy'
    elif RX == '55' and FX == '20':
        poum_list = 'V4.3Gy V8.7Gy V17.4Gy'
    elif RX == '40.05' and FX == '15':
        poum_list = 'V4.4Gy V8.8Gy V17.6Gy'
    elif RX == '60' and FX == '20':
        poum_list = 'V4.2Gy V8.3Gy V16.7Gy'

    # If a given OAR has more than one criteria, put them all in the same string separated by spaces
    OAR_list = ['MOELLE', 'COMBI PMNS', 'PMNS-PTV', 'COEUR', 'OESOPHAGE', 'COTES', 'PL BRACHIAL']
    type_list = ['D0.1cc', 'Dmoy', poum_list, r'D100% D66% D33%', r'D100% D66% D33%', 'D0.1cc', 'D0.1cc']

    for i, OAR in enumerate(OAR_list):
        types = type_list[i].split()
        for type in types:
            ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), type)]  # Note that all four variables here are strings, must be converted to floats for use in CGs
            if type[0] == "D" and type[-2:] == "cc":  # Criterion of type Dxxcc
                absvol = float(type[1:-2])
                eval.add_clinical_goal(OAR, float(tol2) * 100, "AtMost", "DoseAtAbsoluteVolume", absvol, plan=plan)
            elif type[0] == "D" and type[-1:] == r'%':  # Criterion of type Dxx%
                relvol = float(type[1:-1])
                eval.add_clinical_goal(OAR, float(tol2) * 100, "AtMost", "DoseAtVolume", relvol, plan=plan)
            elif type[0] == "V" and type[-2:] == "Gy":  # Criterion of type VxxGy
                dose_level = float(type[1:-2])
                eval.add_clinical_goal(OAR, dose_level * 100, 'AtMost', 'VolumeAtDose', float(tol2), plan=plan)
            elif type == "Dmoy":
                eval.add_clinical_goal(OAR, float(tol2) * 100, 'AtMost', 'AverageDose', 0, plan=plan)

    # Add optimization objectives for PTVs, Gradients, Rings and TS
    if len(ptvs) == 1:
        optim.add_mindose_objective(ptv.Name, ptvs[0] * 100, weight=25, plan=plan)
        optim.add_maxdose_objective(("CTV" + str(ptvs[0])), ptvs[0] * 118, weight=5, plan=plan)
        optim.add_mineud_objective(ptv.Name, ptvs[0] * 105, 1, 10, plan=plan)
        optim.add_mindose_objective((ptv.Name + "-CTV" + str(ptvs[0])), ptvs[0] * 100, weight=25, plan=plan)
        optim.add_maxdose_objective((ptv.Name + "-CTV" + str(ptvs[0])), ptvs[0] * 115, weight=2, plan=plan)
    elif len(ptvs) == 2:
        optim.add_mindose_objective(ptv1.Name, ptvs[0] * 100, weight=25, plan=plan)
        optim.add_maxdose_objective(ptv1.Name, ptvs[0] * 118, weight=5, plan=plan)
        optim.add_mineud_objective(ptv1.Name, ptvs[0] * 105, 1, 10, plan=plan)
        optim.add_mindose_objective(("modCTV" + str(ptvs[1])), ptvs[1] * 100, weight=25, plan=plan)
        optim.add_maxdose_objective(("modCTV" + str(ptvs[1])), ptvs[1] * 118, weight=5, plan=plan)
        optim.add_mineud_objective(("OPTCTV" + str(ptvs[1])), ptvs[1] * 105, 1, 10, plan=plan)
        optim.add_mindose_objective(("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1])), ptvs[1] * 100, weight=25, plan=plan)
        optim.add_maxdose_objective(("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1])), ptvs[1] * 115, weight=2, plan=plan)
        optim.add_mineud_objective(("OPTPTV" + str(ptvs[1]) + "-CTV" + str(ptvs[1])), ptvs[1] * 105, 1, 10, plan=plan)

    # optim.add_mindose_objective(("Gradient"+str(ptvs[0])+"-"+str(ptvs[1])), ptvs[1]*100, weight=1, plan=plan)
    # optim.add_maxdose_objective(("Gradient"+str(ptvs[0])+"-"+str(ptvs[1])), ptvs[0]*101, weight=1, plan=plan)

    optim.add_maxdose_objective(("Ring1_3mm"), ptvs[0] * 95, weight=1, plan=plan)
    optim.add_maxdose_objective(("Ring2_6mm"), ptvs[0] * 85, weight=1, plan=plan)
    optim.add_maxdose_objective(("Ring3_16mm"), ptvs[0] * 75, weight=1, plan=plan)

    optim.add_maxdose_objective(("TS1_26mm"), ptvs[0] * 70, weight=0.1, plan=plan)
    optim.add_maxdose_objective(("TS2_66mm"), ptvs[0] * 65, weight=0.1, plan=plan)

    # Add optimization objectives for OARs
    OAR = "MOELLE"
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), 'D0.1cc')]
    optim.add_maxdose_objective("MOELLE", (float(tol2) - 5) * 100, weight=25, plan=plan)
    optim.add_maxdose_objective("presMOELLE", (float(tol2) - 5) * 100, weight=10, plan=plan)
    optim.add_maxdose_objective("prv5mmMOELLE", (float(tol2) - 1) * 100, weight=10, plan=plan)
    optim.add_maxdose_objective("BLOC MOELLE", (float(tol2) - 5) * 100, weight=5, plan=plan)

    OAR = "PMNS-PTV"
    w = 0.1
    types = poum_list.split()
    for type in types:  # All 3 are of the type VxxGy
        ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), type)]
        dose_level = float(type[1:-2])
        if tol2 == '30':
            tol2 = '24'
        elif tol2 == '40':
            tol2 = '45'
        optim.add_maxdvh_objective(OAR, float(dose_level) * 100, float(tol2), w, plan=plan)
        w = w * 10.0

    OAR = "COMBI PMNS"
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), 'Dmoy')]
    optim.add_maxeud_objective("COMBI PMNS", (float(tol2) - 0.5) * 100, 1, weight=1, plan=plan)

    OAR = "COEUR"
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D33%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 33, 1, plan=plan)
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D66%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 66, 1, plan=plan)
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D100%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 100, 1, plan=plan)

    OAR = "OESOPHAGE"
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D33%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 33, 1, plan=plan)
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D66%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 66, 1, plan=plan)
    ctype, tol1, tol2, unit = c[(Site, RX, FX, OAR.replace(' ', '_'), r'D100%')]
    optim.add_maxdvh_objective(OAR, float(tol2) * 100, 100, 1, plan=plan)

       
def smart_cg_vertebre(plan=None, examination=None):
    # This script adds both clinical goals and optimization objectives for vertbre SBRT cases.

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()
    if plan is None:
        plan = lib.get_current_plan()

    # Determine different PTV levels.
    ptv = patient.PatientModel.RegionsOfInterest["PTV18"]
    
    # Add clinical goals for OAR using common dictionary (defined by GJ)
    Site = 'Vertebre'
    RX = 18
    FX = 1
    add_dictionary_cg(Site, RX, FX, plan)
     
    # Add optimization objectives for PTV
    if roi.roi_exists("OPTPTV"):
        optim.add_mindose_objective("OPTPTV", 1800, weight=100, plan=plan)
    else:
        optim.add_mindose_objective(ptv.Name, 1800, weight=100, plan=plan)
    
    # Add optimization objectives for Ring and TS
    optim.add_maxdose_objective(("Ring_5mm"), 1830, weight=10, plan=plan)
    
    optim.add_maxdose_objective(("TS1"), 1700, weight=1, plan=plan)
    VolPTV = roi.get_roi_volume(ptv.Name, exam=examination)
    if VolPTV < 70:
        optim.add_dosefalloff_objective('TS1', 1700, 720, 3, weight=1, plan=plan)
    elif VolPTV > 140:
        optim.add_dosefalloff_objective('TS1', 1700, 720, 5, weight=1, plan=plan)
    else:
        optim.add_dosefalloff_objective('TS1', 1700, 720, 4, weight=1, plan=plan)
 
    optim.add_dosefalloff_objective('TS2', 720, 400, 3, weight=1, plan=plan)
 
    # Add optimization objectives for OARs
    if roi.roi_exists("MOELLE PARTIELLE"):
        optim.add_maxdose_objective(("MOELLE PARTIELLE"), 1400, weight=1, plan=plan)
        optim.add_maxdvh_objective("MOELLE PARTIELLE", 1000, 5, 100, plan=plan)
    if roi.roi_exists("QUEUE CHEVAL"):
        VolQueue = roi.get_roi_volume("QUEUE CHEVAL", exam=examination)
        three_cc = int(3.0/VolQueue*100)
        optim.add_maxdose_objective(("QUEUE CHEVAL"), 1600, weight=100, plan=plan)
        optim.add_maxdvh_objective("QUEUE CHEVAL", 1400, three_cc, 10, plan=plan)
    if roi.roi_exists("PLEXUS BRACHIAL"):
        optim.add_maxdose_objective(("PLEXUS BRACHIAL"), 1750, weight=100, plan=plan)
        VolPB = roi.get_roi_volume("PLEXUS BRACHIAL", exam=examination)
        if VolPB > 3:
            three_cc = int(3.0/VolPB*100)
            optim.add_maxdvh_objective("PLEXUS BRACHIAL", 1400, three_cc, 1, plan=plan)
    if roi.roi_exists("PLEXUS SACRAL"):
        optim.add_maxdose_objective(("PLEXUS SACRAL"), 1800, weight=100, plan=plan)
        VolPS = roi.get_roi_volume("PLEXUS SACRAL", exam=examination)
        if VolPS > 5:
            five_cc = int(5.0/VolPS*100)
            optim.add_maxdvh_objective("PLEXUS SACRAL", 1440, five_cc, 1, plan=plan)
    if roi.roi_exists("PLEXUS LOMBAIRE"):
        optim.add_maxdose_objective(("PLEXUS LOMBAIRE"), 1800, weight=100, plan=plan)
        VolPL = roi.get_roi_volume("PLEXUS LOMBAIRE", exam=examination)
        if VolPL > 5:
            five_cc = int(5.0/VolPL*100)
            optim.add_maxdvh_objective("PLEXUS LOMBAIRE", 1440, five_cc, 1, plan=plan)
          
        
def cg_orl(plan_data):
    # This script adds clinical goals for ORL cases from the file also used in Pinnacle script

    patient = plan_data['patient']
    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]
    ptv = plan_data['ptv']
    rx_dose = plan_data['rx_dose']
    exam = plan_data['exam']
    nb_fx = plan_data['nb_fx']

    add_dictionary_cg2('ORL', 70, 33, plan=plan,skip_modptv = True)
    
    
    # Add clinical goals for coverage
    eval.add_clinical_goal(("BodyRS+Table"), rx_dose[0]*1.08, 'AtMost', 'DoseAtAbsoluteVolume', 0, plan=plan)
    if len(ptv)==4:
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[2]), rx_dose[2], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[2]), rx_dose[2]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[3]), rx_dose[3], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[3]), rx_dose[3]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    elif len(ptv)==3:
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[2]), rx_dose[2], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[2]), rx_dose[2]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    elif len(ptv)==2:
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[1]), rx_dose[1]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    elif len(ptv)==1:
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0], 'AtLeast', 'VolumeAtDose', 95, plan=plan)
        eval.add_clinical_goal(("mod" + ptv[0]), rx_dose[0]*95/100, 'AtLeast', 'VolumeAtDose', 99.5, plan=plan)
    
    
    
    
def smart_cg_lung_stereo_v2(plan_data,plan,beamset,index,num_plans):
    """
    This function adds both clinical goals and optimization objectives for SBRT lung cases. In many cases, the proximity
    of an OAR to the PTV is evaluated to determine which objective/clinical goal is used and to which ROI it is applied.
    """
    
    patient = plan_data['patient']
    exam = plan_data['exam']
    site_name = plan_data['site_names'][index]
    ptv_name = plan_data['ptv_names'][index]
    rx_dose = plan_data['rx_dose']
    nb_fx = plan_data['nb_fx']
       
    # Set PTV name and prescription type
    if nb_fx == 3: #54Gy-3fx
        Rx = 0
    elif nb_fx == 4: #48Gy-4fx or 56Gy-4fx
        Rx = 1
    elif nb_fx == 8: #60Gy-8fx
        Rx = 2
    elif nb_fx == 5: #60Gy-5fx
        Rx = 3
        
    output_name = 'PTV ' + site_name

    # Determine PlanOptimization number to use (so that objectives are added to the correct beamset)
    plan_opt = beamset.Number-1
        
    # Objectives for target coverage and rings
    optim.add_mindose_objective(ptv_name, rx_dose, weight=50, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective(ptv_name, rx_dose*1.5, weight=1, plan=plan, plan_opt=plan_opt)

    optim.add_maxdose_objective('RING_1_'+site_name, rx_dose*1.01, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective('RING_2_'+site_name, rx_dose*0.87, plan=plan, plan_opt=plan_opt)
    optim.add_maxdose_objective('RING_3_'+site_name, rx_dose*0.59, plan=plan, plan_opt=plan_opt)
    
    if roi.roi_exists("TS "+site_name,exam):
        optim.add_maxdose_objective("TS "+site_name, rx_dose*0.5, plan=plan, plan_opt=plan_opt)

    # Clinical Goals
    # Compute what is 0.1 cc in percentage of the volume
    ptone_cc_percentage = roi.convert_absolute_volume_to_percentage(ptv_name, volume_cc=0.1, examination=exam)
    # We want to know if 100 % - 0.1 cc of volume is covered by 95 % prescription
    eval.add_clinical_goal(ptv_name, rx_dose*0.95, 'AtLeast', 'VolumeAtDose', 100.00 - ptone_cc_percentage, plan=plan)
    eval.add_clinical_goal(ptv_name, rx_dose, 'AtLeast', 'VolumeAtDose', 95, plan=plan)
    eval.add_clinical_goal(ptv_name, rx_dose*1.5, "AtMost", "DoseAtAbsoluteVolume", 0.1, plan=plan)


    # Objectives and Clinical Goals for OARs, chosen based on proximity to the PTV
    # First step is to determine whether the OAR is within 2cm/5mm of the PTV and create corresponding optimization ROIs
    roi_list = ['BR SOUCHE','COEUR','COTES','ESTOMAC','GROS VAISSEAUX','INTESTINS','OESOPHAGE','PAROI','TRACHEE','PLEXUS BRACHIAL','PRV PLEXUS','MOELLE','PRV MOELLE','PAROI OPP OESO','PAROI OPP BRONCHE','PAROI OPP TRACHEE']
    color_list = ['Red','Blue','Yellow','Green','Orange','skyblue','khaki','teal','steelblue','olive','tomato','brown','purple','pink','slateblue','yellowgreen','white']
    for i, roi_name in enumerate(roi_list):
        if roi.roi_exists(roi_name, exam):
            if not roi.roi_exists(roi_name+" dans "+output_name+"+2cm",exam):
                dans2cm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color=color_list[i], examination=exam, margeptv=2, output_name=output_name)
                Vol2cm = roi.get_roi_volume(dans2cm.Name, exam=exam)
                if Vol2cm == 0:
                    patient.PatientModel.RegionsOfInterest[dans2cm.Name].DeleteRoi()
                else:
                    dans5mm = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color=color_list[i], examination=exam, margeptv=0.5, output_name=output_name)
                    Vol5mm = roi.get_roi_volume(dans5mm.Name, exam=exam)
                    if Vol5mm == 0:
                        patient.PatientModel.RegionsOfInterest[dans5mm.Name].DeleteRoi()
    # For some ROIs, determine if there is a volume inside the PTV for clinical goals
    roi_list = ['BR SOUCHES','COEUR','COTES','ESTOMAC','GROS VAISSEAUX','INTESTINS','OESOPHAGE']
    for i, roi_name in enumerate(roi_list):
        if roi.roi_exists(roi_name, exam):
            if not roi.roi_exists(roi_name+" dans "+output_name,exam):
                dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color=color_list[i], examination=exam, margeptv=0, output_name=output_name)
                Vol = roi.get_roi_volume(dans.Name, exam=exam)
                if Vol == 0:
                    patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()    
        
    
    # BR SOUCHE
    if roi.roi_exists("BR SOUCHE", exam):
        roi_name = "BR SOUCHE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            # CG for ROI in PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            # objective on roi_name dans PTV + 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            # Create ROI hors PTV (potentially useful for optimization)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            # CG for ROI outside of PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),exam): # OAR outside of PTV, but within 5mm
                # objective on roi_name dans PTV + 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),exam): # OAR outside of PTV, but within 2cm
                # objective on roi_name dans PTV + 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                # objective on roi_name
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        
    # COEUR
    if roi.roi_exists("COEUR", exam):
        roi_name = "COEUR"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3850, 3200]  # 15cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 15, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),exam): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),exam): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # COTES
    if roi.roi_exists("COTES", exam):
        roi_name = "COTES"
        dose_level1 = [3700, 4200, 5640, 4630]  # 0.1cc hors PTV
        dose_level2 = [3530, 4000, 5360, 4400]  # 0.3cc hors PTV
        dose_level3 = [2660, 3000, 3960, 3290]  # 1.4cc hors PTV
        dose_level4 = [1790, 2000, 2570, 2180]  # 3.6cc hors PTV
        dose_level5 = [910, 1000, 1220, 1070]  # 5cc hors PTV
        dose_level6 = [5400, 4800, 6000, 6000]  # 0.1cc dans PTV - REPLACED BY rx_dose

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Brown", examination=exam, output_name=output_name)
            else:
                hors = patient.PatientModel.RegionsOfInterest[roi_name+" hors "+output_name]                
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            eval.add_clinical_goal(roi_name, rx_dose, 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            # CG for ROI outside of PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 1.4, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level4[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3.6, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level5[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "+0.5cm"),exam): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "+2cm"),exam): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "+2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # ESTOMAC
    if roi.roi_exists("ESTOMAC", exam):
        roi_name = "ESTOMAC"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 5cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "+0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # GROS VAISSEAUX
    if roi.roi_exists("GROS VAISSEAUX", exam):
        roi_name = "GROS VAISSEAUX"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 4860, 4010]  # 10cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 10, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # INTESTINS
    if roi.roi_exists("INTESTINS", exam):
        roi_name = "INTESTINS"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc hors PTV
        dose_level2 = [0, 0, 6100, 6100]  # 0.1cc dans PTV
        dose_level3 = [0, 0, 3290, 2750]  # 5cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        else:
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
                optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
            else: #OAR > 2cm from PTV
                optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # OESOPHAGE
    if roi.roi_exists("OESOPHAGE", exam):
        roi_name = "OESOPHAGE"
        dose_level1 = [1000, 1100, 1350, 1180]  # 0.1cc >2cm PTV
        dose_level2 = [2700, 3050, 4030, 3340]  # 0.1cc <=2cm PTV
        dose_level3 = [0, 0, 6100, 6100]  # 0.1cc dans PTV

        if roi.roi_exists((roi_name + " dans " + output_name),exam): # OAR overlaps PTV
            if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
                eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), rx_dose, plan=plan, plan_opt=plan_opt)
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            patient.PatientModel.RegionsOfInterest[(roi_name + " dans " + output_name)].DeleteRoi()
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR within 2cm of PTV
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level2[Rx], plan=plan, plan_opt=plan_opt)
        else: # OAR >2cm from PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)
                                    
    # MOELLE
    if roi.roi_exists("MOELLE", exam):
        roi_name = "MOELLE"
        dose_level1 = [1800, 2020, 2590, 2620]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PRV MOELLE
    if roi.roi_exists("PRV MOELLE", exam):
        roi_name = "PRV MOELLE"
        dose_level1 = [2000, 2240, 2910, 2930]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # Paroi oesophagienne opposée
    if roi.roi_exists("OESO PAROI OPP", exam):
        roi_name = "OESO PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 3290, 2750]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 5, plan=plan)
            
    # Paroi trachée/bronches opposées
    if roi.roi_exists("BR SOUCHE PAROI OPP", exam):
        roi_name = "BR SOUCHE PAROI OPP"
        if Rx > 1:  # Only for prescriptions of 60Gy in 5 or 8 fx
            dose_level1 = [0, 0, 6000, 6100]  # 0.1cc
            dose_level2 = [0, 0, 2110, 1800]  # 4cc
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 4, plan=plan)        

    # PAROI
    paroi_name = 'PAROI ' + plan_data['laterality'][index]
    if roi.roi_exists(paroi_name, exam):
        roi_name = paroi_name
        dose_level1 = [6000, 6850, 9380, 7590]  # 3cc hors PTV
        dose_level2 = [3000, 3390, 4510, 3730]  # 30cc dans PTV
        dose_level3 = [4000, 4550, 6130, 5010]  # 0.2% dans PTV

        # Create intersecting volume
        dans = roi.intersect_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Purple", examination=exam, output_name=output_name)
        Vol = roi.get_roi_volume(dans.Name, exam=exam)

        if Vol == 0:  # No overlap between ROI and PTV
            eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(roi_name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        else:  # ROI overlaps PTV
            # Create ROI hors PTV
            if not roi.roi_exists(roi_name+" hors "+output_name,exam):
                hors = roi.subtract_roi_ptv(roi_name=roi_name, ptv_name=ptv_name, color="Yellow", examination=exam, output_name=output_name)
            else:
                hors = patient.PatientModel.RegionsOfInterest[roi_name+" hors "+output_name]
            eval.add_clinical_goal(hors.Name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 3, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level2[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 30, plan=plan)
            eval.add_clinical_goal(hors.Name, dose_level3[Rx], 'AtMost', 'DoseAtVolume', 0.2, plan=plan)
        patient.PatientModel.RegionsOfInterest[dans.Name].DeleteRoi()

    # PEAU
    if roi.roi_exists("PEAU", exam):
        roi_name = "PEAU"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PLEXUS BRACHIAL
    if roi.roi_exists("PLEXUS BRACHIAL", exam):
        roi_name = "PLEXUS BRACHIAL"
        dose_level1 = [2400, 2700, 3550, 2960]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # PRV PLEXUS
    if roi.roi_exists("PRV PLEXUS", exam):
        roi_name = "PRV PLEXUS"
        dose_level1 = [2700, 3050, 4030, 3340]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # COMBI PMN-ITV-BR
    if num_plans == 1:
        roi_name = 'COMBI PMN-ITV-BR_' + site_name
    elif num_plans == 2:
        roi_name = 'COMBI PMN-ITV-BR_' + plan_data['site_names'][0] + '+' + plan_data['site_names'][1]
    
    if roi.roi_exists(roi_name, exam):
        eval.add_clinical_goal(roi_name, 500, 'AtMost', 'VolumeAtDose', 20, plan=plan)
        eval.add_clinical_goal(roi_name, 1000, 'AtMost', 'VolumeAtDose', 15, plan=plan)
        eval.add_clinical_goal(roi_name, 1500, 'AtMost', 'VolumeAtDose', 10, plan=plan)
        eval.add_clinical_goal(roi_name, 2000, 'AtMost', 'VolumeAtDose', 5, plan=plan)
        eval.add_clinical_goal(roi_name, 500, 'AtMost', 'AverageDose', 0, plan=plan)

    # CONTRALATERAL LUNG
    if plan_data['laterality'][index] == 'GCHE':
        contralateral_lung = 'POUMON DRT'
    else:
        contralateral_lung = 'POUMON GCHE'

    eval.add_clinical_goal(contralateral_lung, 500, 'AtMost', 'VolumeAtDose', 25, plan=plan)
    optim.add_maxdose_objective(contralateral_lung, 500, plan=plan, plan_opt=plan_opt)

    # TRACHEE
    if roi.roi_exists("TRACHEE", exam):
        roi_name = "TRACHEE"
        dose_level1 = [3000, 3390, 4510, 3730]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        if roi.roi_exists((roi_name + " dans " + output_name + "0.5cm"),exam): # OAR outside of PTV, but within 5mm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "0.5cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        elif roi.roi_exists((roi_name + " dans " + output_name + "2cm"),exam): # OAR outside of PTV, but within 2cm
            optim.add_maxdose_objective((roi_name + " dans " + output_name + "2cm"), dose_level1[Rx], plan=plan, plan_opt=plan_opt)
        else: #OAR > 2cm from PTV
            optim.add_maxdose_objective(roi_name, dose_level1[Rx], plan=plan, plan_opt=plan_opt)

    # TISSU SAIN A 2cm
    if num_plans == 1:
        roi_name = 'TISSU SAIN A 2cm_' + site_name
    elif num_plans == 2:
        roi_name = 'TISSU SAIN A 2cm_' + plan_data['site_names'][0] + '+' + plan_data['site_names'][1]
 
    if roi.roi_exists(roi_name, exam):
        dose_level1 = [2700, 2400, 3000, 3000]  # 0.1cc
        eval.add_clinical_goal(roi_name, dose_level1[Rx], 'AtMost', 'DoseAtAbsoluteVolume', 0.1, plan=plan)
        
    # PACEMAKER
    if roi.roi_exists("PACEMAKER", exam):
        roi_name = "PACEMAKER"
        eval.add_clinical_goal(roi_name, 200, 'AtMost', 'DoseAtAbsoluteVolume', 0, plan=plan)     
        optim.add_maxdose_objective(roi_name, 100, plan=plan, plan_opt=plan_opt)        

