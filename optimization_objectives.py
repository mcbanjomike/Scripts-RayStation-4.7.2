# -*- coding: utf-8 -*-
import hmrlib.lib as lib
import hmrlib.optim as optim
import hmrlib.roi as roi

logger = lib.logger

# from connect import get_current


def add_opt_obj_brain_stereo(patient_plan=None):
    """
    Ajoute les objectifs d'optimisation pour les cas de stéréo de poumon.

    Assume que les PTV sont nommés avec leur niveau de prescription. Ex. : PTV15

    Les prescriptions supportées sont :

    * 15 Gy
    * 18 Gy
    * 20 Gy

    .. rubric::
      Objectifs pour prescription de 15 Gy :

    ===================  ================  ===========  ==========
    ROI                  Type de critère   Poids        Valeur
    ===================  ================  ===========  ==========
    PTV15                ``mindose``       50           15 Gy
    PTV15                ``maxdose``       1            15 Gy
    RING_1_3mm           ``maxdose``       1            15.5 Gy
    RING_2_8mm           ``maxdose``       1            10 Gy
    RING_3_1cm           ``maxdose``       1            7.5 Gy
    ===================  ================  ===========  ==========

    .. rubric::
      Objectifs pour prescription de 18 Gy :

    ===================  ================  ===========  ==========
    ROI                  Type de critère   Poids        Valeur
    ===================  ================  ===========  ==========
    PTV18                ``mindose``       50           18 Gy
    PTV18                ``maxdose``       1            27 Gy
    RING_1_3mm           ``maxdose``       1            18.5 Gy
    RING_2_8mm           ``maxdose``       1            12.5 Gy
    RING_3_1cm           ``maxdose``       1            8.5 Gy
    ===================  ================  ===========  ==========

    .. rubric::
      Objectifs pour prescription de 20 Gy :

    ===================  ================  ===========  ==========
    ROI                  Type de critère   Poids        Valeur
    ===================  ================  ===========  ==========
    PTV20                ``mindose``       50           20 Gy
    PTV20                ``maxdose``       1            30 Gy
    RING_1_3mm           ``maxdose``       1            20.5 Gy
    RING_2_8mm           ``maxdose``       1            14 Gy
    RING_3_1cm           ``maxdose``       1            9.5 Gy
    ===================  ================  ===========  ==========

    .. seealso::
      fonctions :py:func:`hmrlib.optim.add_mindose_objective`, :py:func:`hmrlib.optim.add_maxdose_objective`
    """
    if patient_plan is None:
        patient_plan = lib.get_current_plan()

    ptvs = roi.identify_ptvs2()

    if len(ptvs) > 1:
        logger.warning('More than one dose level found for PTVs.  PTVs = %s', ptvs)
        # raise SystemError('More than one dose level found.')

    if 'PTV15' in ptvs:
        optim.add_mindose_objective('PTV15', 1500, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV15', 2250, plan=patient_plan)

        optim.add_maxdose_objective('RING_1_3mm', 1550, plan=patient_plan)
        optim.add_maxdose_objective('RING_2_8mm', 1000, plan=patient_plan)
        optim.add_maxdose_objective('RING_3_1cm', 750, plan=patient_plan)
        optim.add_maxdose_objective('TISSUS SAINS', 650, plan=patient_plan)

    elif 'PTV18' in ptvs:
        optim.add_mindose_objective('PTV18', 1800, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV18', 2700, plan=patient_plan)

        optim.add_maxdose_objective('RING_1_3mm', 1850, plan=patient_plan)
        optim.add_maxdose_objective('RING_2_8mm', 1250, plan=patient_plan)
        optim.add_maxdose_objective('RING_3_1cm', 850, plan=patient_plan)
        optim.add_maxdose_objective('TISSUS SAINS', 725, plan=patient_plan)
        
    elif 'PTV20' in ptvs:
        optim.add_mindose_objective('PTV20', 2000, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV20', 3000, plan=patient_plan)

        optim.add_maxdose_objective('RING_1_3mm', 2050, plan=patient_plan)
        optim.add_maxdose_objective('RING_2_8mm', 1400, plan=patient_plan)
        optim.add_maxdose_objective('RING_3_1cm', 950, plan=patient_plan)

    else:
        logger.warning('No PTV with supported dose level found.  Please name PTV with prescription in name (ex. PTV18).')


def add_opt_obj_brain_stereo_v2(plan_data):

    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]

    if plan_data['ptv_low'] is None: # 1 dose level
        optim.add_mindose_objective(plan_data['ptv'].Name, plan_data['rx_dose'], weight=50, plan=plan)
        optim.add_maxdose_objective(plan_data['ptv'].Name, plan_data['rx_dose']*1.5, plan=plan)
        optim.add_maxdose_objective('RING_1_3mm', plan_data['rx_dose']*1.03, plan=plan)
        optim.add_maxdose_objective('RING_2_8mm', plan_data['rx_dose']*0.66, plan=plan)
        optim.add_maxdose_objective('RING_3_1cm', plan_data['rx_dose']*0.5, plan=plan)
        optim.add_maxdose_objective('TISSUS SAINS', plan_data['rx_dose']*0.42, plan=plan)
 
        """
        if plan_data['rx_dose'] == 1500:
            optim.add_mindose_objective('PTV15', 1500, weight=50, plan=plan)
            optim.add_maxdose_objective('PTV15', 2250, plan=plan)

            optim.add_maxdose_objective('RING_1_3mm', 1550, plan=plan)
            optim.add_maxdose_objective('RING_2_8mm', 1000, plan=plan)
            optim.add_maxdose_objective('RING_3_1cm', 750, plan=plan)
            optim.add_maxdose_objective('TISSUS SAINS', 650, plan=plan)

        elif plan_data['rx_dose'] == 1800:
            optim.add_mindose_objective('PTV18', 1800, weight=50, plan=plan)
            optim.add_maxdose_objective('PTV18', 2700, plan=plan)

            optim.add_maxdose_objective('RING_1_3mm', 1850, plan=plan)
            optim.add_maxdose_objective('RING_2_8mm', 1250, plan=plan)
            optim.add_maxdose_objective('RING_3_1cm', 850, plan=plan)
            optim.add_maxdose_objective('TISSUS SAINS', 725, plan=plan)
        """    
    
    else:     # 2 dose levels
        optim.add_mindose_objective(plan_data['ptv'].Name, plan_data['rx_dose'], weight=50, plan=plan)
        optim.add_maxdose_objective(plan_data['ptv'].Name, plan_data['rx_dose']*1.5, plan=plan)
        optim.add_mindose_objective(plan_data['ptv_low'].Name, plan_data['rx_dose_low'], weight=50, plan=plan)
        optim.add_maxdose_objective(plan_data['ptv_low'].Name, plan_data['rx_dose_low']*1.5, plan=plan)
        optim.add_maxdose_objective('RING_PTVH_1_3mm', plan_data['rx_dose']*1.03, plan=plan)
        optim.add_maxdose_objective('RING_PTVL_1_3mm', plan_data['rx_dose_low']*1.03, plan=plan)
        optim.add_maxdose_objective('RING_PTVH_2_8mm', plan_data['rx_dose']*0.8, plan=plan)
        optim.add_maxdose_objective('RING_PTVL_2_8mm', plan_data['rx_dose_low']*0.8, plan=plan)
        optim.add_maxdose_objective('RING_PTVH_3_1cm', plan_data['rx_dose']*0.53, plan=plan)
        optim.add_maxdose_objective('RING_PTVL_3_1cm', plan_data['rx_dose_low']*0.53, plan=plan)
       
        
def add_opt_obj_lung_stereo(contralateral_lung=None, patient_plan=None):
    """
    Ajoute les objectifs d'optimisation pour les cas de stéréo de poumon.

    Assume que les PTV sont nommés avec leur niveau de prescription. Ex. : PTV48

    Si le nom du ROI du poumon contralatéral n'est pas spécifié, détecte si le
    PTV est situé dans POUMON D ou POUMON G et ajuste en conséquence.

    Args:
        contralateral_lung (str, optional): nom du ROI du poumon contralatéral

    .. rubric::
      Objectifs pour prescription de 48 Gy - 4 Fx :

    =====================  ================  ===========  ========
    ROI                    Type de critère   Poids        Valeur
    =====================  ================  ===========  ========
    PTV48                  ``mindose``       50           48 Gy
    PTV48                  ``maxdose``       1            72 Gy
    RING_1                 ``maxdose``       1            48.5 Gy
    RING_2                 ``maxdose``       1            42 Gy
    RING_3                 ``maxdose``       1            28 Gy
    PEAU                   ``maxdose``       1            27 Gy
    BR SOUCHE              ``maxdose``       1            33.9 Gy
    COTES                  ``maxdose``       1            48 Gy
    MOELLE                 ``maxdose``       1            18 Gy
    COEUR                  ``maxdose``       1            33.9 Gy
    OESOPHAGE              ``maxdose``       1            11 Gy
    <poumon contralat.>\*  ``maxdose``       1            5 Gy
    PLEXUS BRACHIAL        ``maxdose``       1            27 Gy
    TRACHEE                ``maxdose``       1            33.9 Gy
    PRV MOELLE             ``maxdose``       1            22.4 Gy
    PRV PLEXUS             ``maxdose``       1            30.5 Gy
    =====================  ================  ===========  ========

    .. rubric::
      Objectifs pour prescription de 54 Gy - 3 Fx :

    =====================  ================  ===========  ========
    ROI                    Type de critère   Poids        Valeur
    =====================  ================  ===========  ========
    PTV54                  ``mindose``       50           54 Gy
    PTV54                  ``maxdose``       1            81 Gy
    RING_1                 ``maxdose``       1            54.5 Gy
    RING_2                 ``maxdose``       1            47 Gy
    RING_3                 ``maxdose``       1            32 Gy
    PEAU                   ``maxdose``       1            24 Gy
    BR SOUCHE              ``maxdose``       1            30 Gy
    COTES                  ``maxdose``       1            54 Gy
    MOELLE                 ``maxdose``       1            18 Gy
    COEUR                  ``maxdose``       1            30 Gy
    OESOPHAGE              ``maxdose``       1            10 Gy
    <poumon contralat.>\*  ``maxdose``       1            5 Gy
    PLEXUS BRACHIAL        ``maxdose``       1            24 Gy
    TRACHEE                ``maxdose``       1            30 Gy
    PRV MOELLE             ``maxdose``       1            20 Gy
    PRV PLEXUS             ``maxdose``       1            27 Gy
    =====================  ================  ===========  ========

    .. rubric::
      Objectifs pour prescription de 60 Gy - 8 Fx :

    =====================  ================  ===========  ========
    ROI                    Type de critère   Poids        Valeur
    =====================  ================  ===========  ========
    PTV60                  ``mindose``       50           60 Gy
    PTV60                  ``maxdose``       1            90 Gy
    RING_1                 ``maxdose``       1            60.5 Gy
    RING_2                 ``maxdose``       1            52 Gy
    RING_3                 ``maxdose``       1            35.5 Gy
    PEAU                   ``maxdose``       1            35.5 Gy
    BR SOUCHE              ``maxdose``       1            45.1 Gy
    BR SOUCHE              ``maxdose``       1            61 Gy
    COTES                  ``maxdose``       1            60 Gy
    MOELLE                 ``maxdose``       1            24 Gy
    COEUR                  ``maxdose``       1            45 Gy
    OESOPHAGE              ``maxdose``       1            13.5 Gy
    <poumon contralat.>\*  ``maxdose``       1            5 Gy
    PLEXUS BRACHIAL        ``maxdose``       1            35.5 Gy
    TRACHEE                ``maxdose``       1            45 Gy
    PRV MOELLE             ``maxdose``       1            29.1 Gy
    PRV PLEXUS             ``maxdose``       1            40.3 Gy
    =====================  ================  ===========  ========

    .. note::
      \*<poumon contralat.> représente le nom du ROI du poumon contralatéral, soit *POUMON G* ou *POUMON D*.

    .. seealso::
      fonctions :py:func:`hmrlib.hmrlib.optim.add_mindose_objective`, :py:func:`hmrlib.hmrlib.optim.add_maxdose_objective`
    """

    if patient_plan is None:
        patient_plan = lib.get_current_plan()

    ptvs = roi.identify_ptvs2()

    if len(ptvs) > 1:
        logger.warning('More than one dose level found for PTVs.  PTVs = %s', ptvs)
        # raise SystemError(u"Plus d'un niveau de dose trouvé pour les PTV.")

    if 'PTV48' in ptvs:
        optim.add_mindose_objective('PTV48', 4800, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV48', 7200, plan=patient_plan)

        optim.add_maxdose_objective('RING_1', 4850, plan=patient_plan)
        optim.add_maxdose_objective('RING_2', 4200, plan=patient_plan)
        optim.add_maxdose_objective('RING_3', 2800, plan=patient_plan)

        optim.add_maxdose_objective('PEAU', 2700, plan=patient_plan)
        optim.add_maxdose_objective('BR SOUCHE', 3390, plan=patient_plan)
        optim.add_maxdose_objective('COTES', 4800, plan=patient_plan)
        optim.add_maxdose_objective('MOELLE', 1800, plan=patient_plan)
        optim.add_maxdose_objective('COEUR', 3390, plan=patient_plan)
        optim.add_maxdose_objective('OESOPHAGE', 1100, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV48', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        optim.add_maxdose_objective(contralateral_lung, 500, plan=patient_plan)

        optim.add_maxdose_objective('PLEXUS BRACHIAL', 2700, plan=patient_plan)
        optim.add_maxdose_objective('TRACHEE', 3390, plan=patient_plan)
        optim.add_maxdose_objective('PRV MOELLE', 2240, plan=patient_plan)
        optim.add_maxdose_objective('PRV PLEXUS', 3050, plan=patient_plan)

    elif 'PTV54' in ptvs:
        optim.add_mindose_objective('PTV54', 5400, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV54', 8100, plan=patient_plan)

        optim.add_maxdose_objective('RING_1', 5450, plan=patient_plan)
        optim.add_maxdose_objective('RING_2', 4700, plan=patient_plan)
        optim.add_maxdose_objective('RING_3', 3200, plan=patient_plan)

        optim.add_maxdose_objective('PEAU', 2400, plan=patient_plan)
        optim.add_maxdose_objective('BR SOUCHE', 3000, plan=patient_plan)
        optim.add_maxdose_objective('COTES', 5400, plan=patient_plan)
        optim.add_maxdose_objective('MOELLE', 1800, plan=patient_plan)
        optim.add_maxdose_objective('COEUR', 3000, plan=patient_plan)
        optim.add_maxdose_objective('OESOPHAGE', 1000, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV54', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        optim.add_maxdose_objective(contralateral_lung, 500, plan=patient_plan)

        optim.add_maxdose_objective('PLEXUS BRACHIAL', 2400, plan=patient_plan)
        optim.add_maxdose_objective('TRACHEE', 3000, plan=patient_plan)
        optim.add_maxdose_objective('PRV MOELLE', 2000, plan=patient_plan)
        optim.add_maxdose_objective('PRV PLEXUS', 2700, plan=patient_plan)

    elif 'PTV60' in ptvs:
        optim.add_mindose_objective('PTV60', 6000, weight=50, plan=patient_plan)
        optim.add_maxdose_objective('PTV60', 9000, plan=patient_plan)

        optim.add_maxdose_objective('RING_1', 6050, plan=patient_plan)
        optim.add_maxdose_objective('RING_2', 5200, plan=patient_plan)
        optim.add_maxdose_objective('RING_3', 3550, plan=patient_plan)

        optim.add_maxdose_objective('PEAU', 3550, plan=patient_plan)
        optim.add_maxdose_objective('BR SOUCHE', 4510, plan=patient_plan)
        optim.add_maxdose_objective('BR SOUCHE', 6100, plan=patient_plan)
        optim.add_maxdose_objective('COTES', 6000, plan=patient_plan)
        optim.add_maxdose_objective('MOELLE', 2400, plan=patient_plan)
        optim.add_maxdose_objective('COEUR', 4500, plan=patient_plan)
        optim.add_maxdose_objective('OESOPHAGE', 1350, plan=patient_plan)

        if contralateral_lung is None:
            if roi.find_most_intersecting_roi('PTV60', ['POUMON DRT', 'POUMON GCHE']) == 'POUMON GCHE':
                contralateral_lung = 'POUMON DRT'
            else:
                contralateral_lung = 'POUMON GCHE'

        optim.add_maxdose_objective(contralateral_lung, 500, plan=patient_plan)

        optim.add_maxdose_objective('PLEXUS BRACHIAL', 3550, plan=patient_plan)
        optim.add_maxdose_objective('TRACHEE', 4500, plan=patient_plan)
        optim.add_maxdose_objective('PRV MOELLE', 2910, plan=patient_plan)
        optim.add_maxdose_objective('PRV PLEXUS', 4030, plan=patient_plan)

    else:
        logger.warning('No PTV with supported dose level found.  Please name PTV with prescription in name (ex. PTV48).')


# MA
def add_opt_obj_prostate_A1(plan=None):
    """
    Ajoute les objectifs d'optimisation pour les cas de prostate (plan A1).

    ===================  ================  ===========  =========  =========
    ROI                  Type de critère   Poids        Valeur 1   Valeur 2
    ===================  ================  ===========  =========  =========
    PTV A1               ``mindose``       100          76 Gy
    PTV A1               ``maxdose``       10           83 Gy
    RECTUM               ``maxdvh` `       10           75 Gy      15 %
    RECTUM               ``maxdvh` `       10           70 Gy      25 %
    RECTUM               ``maxdvh` `       1            65 Gy      35 %
    RECTUM               ``maxdvh` `       1            60 Gy      50 %
    RECTUM               ``maxdose``       10           79.5 Gy
    VESSIE               ``maxdose``       1            82 Gy
    BodyRS               ``dosefalloff``   0            76-40 Gy   3 cm
    ===================  ================  ===========  =========  =========

    .. seealso::
      fonctions :py:func:`hmrlib.hmrlib.optim.add_mindose_objective`, :py:func:`hmrlib.hmrlib.optim.add_maxdose_objective`
    """

    if plan is None:
        plan = lib.get_current_plan()
        
    nb_fx = plan.BeamSets[0].FractionationPattern.NumberOfFractions
    
    if nb_fx == 40: #Plan to 80Gy
        optim.add_mindose_objective('PTV A1', 7600, weight=100, plan=plan)
        optim.add_maxdose_objective('PTV A1', 8300, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 7500, 15, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 7000, 25, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 6500, 35, weight=1, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 6000, 50, weight=1, plan=plan)
        optim.add_maxdose_objective('RECTUM+3mm', 7900, weight=10, plan=plan)
        optim.add_maxdose_objective('VESSIE', 8200, weight=1, plan=plan)
        optim.add_dosefalloff_objective('BodyRS', 7600, 4000, 3, weight=0, plan=plan)
    elif nb_fx == 33: #Plan to 66 Gy
        optim.add_mindose_objective('PTV A1', 6270, weight=100, plan=plan)
        optim.add_maxdose_objective('PTV A1', 6850, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 6500, 35, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 6000, 50, weight=10, plan=plan)
        optim.add_maxdose_objective('RECTUM+3mm', 6800, weight=10, plan=plan)
        optim.add_maxdose_objective('VESSIE', 6900, weight=1, plan=plan)
        optim.add_dosefalloff_objective('BodyRS', 6270, 3300, 3, weight=0, plan=plan)
    elif nb_fx == 22: #Plan to 66 Gy at 3Gy per fraction
        optim.add_mindose_objective('PTV A1', 6270, weight=100, plan=plan)
        optim.add_maxdose_objective('PTV A1', 6850, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 5420, 35, weight=10, plan=plan)
        optim.add_maxdvh_objective('RECTUM', 5000, 50, weight=10, plan=plan)
        optim.add_maxdose_objective('RECTUM+3mm', 6500, weight=10, plan=plan)
        optim.add_maxdose_objective('VESSIE', 6900, weight=1, plan=plan)
        optim.add_dosefalloff_objective('BodyRS', 6270, 3300, 3, weight=0, plan=plan)
    elif nb_fx == 20  or nb_fx == 24: #Plan to 60 Gy at 3Gy per fraction (or PACE 62Gy in 20fx)
        if roi.roi_exists('PTV_6200'):
            optim.add_mindose_objective('PTV_6200', 5890, weight=100, plan=plan)
            optim.add_maxdose_objective('PTV_6200', 6450, weight=10, plan=plan)
            optim.add_maxdvh_objective('Rectum', 6000, 5, weight=10, plan=plan)
            optim.add_maxdvh_objective('Rectum', 5600, 25, weight=10, plan=plan)
            optim.add_maxdvh_objective('Rectum', 5200, 30, weight=1, plan=plan)
            optim.add_maxdvh_objective('Rectum', 4800, 50, weight=1, plan=plan)
            optim.add_maxdose_objective('Rectum+3mm', 6100, weight=10, plan=plan)
            optim.add_maxdose_objective('Bladder', 6400, weight=1, plan=plan)
            optim.add_dosefalloff_objective('BodyRS', 5890, 3100, 3, weight=0, plan=plan)
        else:
            optim.add_mindose_objective('PTV A1', 5700, weight=100, plan=plan)
            optim.add_maxdose_objective('PTV A1', 6225, weight=10, plan=plan)
            optim.add_maxdvh_objective('RECTUM', 5700, 15, weight=10, plan=plan)
            optim.add_maxdvh_objective('RECTUM', 5280, 30, weight=10, plan=plan)
            optim.add_maxdvh_objective('RECTUM', 4860, 50, weight=1, plan=plan)
            optim.add_maxdvh_objective('RECTUM', 3240, 70, weight=1, plan=plan)
            optim.add_maxdose_objective('RECTUM+3mm', 6000, weight=10, plan=plan)
            optim.add_maxdose_objective('VESSIE', 6300, weight=1, plan=plan)
            optim.add_dosefalloff_objective('BodyRS', 5700, 3000, 3, weight=0, plan=plan)
        
    elif nb_fx == 39: #PACE 78Gy en 29fx
        optim.add_mindose_objective('PTV_7800', 7410, weight=100, plan=plan)
        optim.add_maxdose_objective('PTV_7800', 8100, weight=10, plan=plan)
        optim.add_maxdvh_objective('Rectum', 7500, 5, weight=10, plan=plan)
        optim.add_maxdvh_objective('Rectum', 7000, 25, weight=10, plan=plan)
        optim.add_maxdvh_objective('Rectum', 6500, 30, weight=1, plan=plan)
        optim.add_maxdvh_objective('Rectum', 6000, 50, weight=1, plan=plan)
        optim.add_maxdose_objective('Rectum+3mm', 7700, weight=10, plan=plan)
        optim.add_maxdose_objective('Bladder', 8000, weight=1, plan=plan)
        optim.add_dosefalloff_objective('BodyRS', 7410, 3900, 3, weight=0, plan=plan)
    elif nb_fx == 5: #PACE 36.25Gy en 5fx
        optim.add_mindose_objective('PTV_3625', 3444, weight=100, plan=plan)
        optim.add_maxdose_objective('PTV_3625', 3760, weight=10, plan=plan)
        optim.add_maxdvh_objective('Rectum', 2500, 20, weight=10, plan=plan)
        optim.add_maxdvh_objective('Rectum', 1810, 50, weight=10, plan=plan)
        optim.add_maxdose_objective('Rectum+3mm', 3575, weight=10, plan=plan)
        optim.add_maxdose_objective('Bladder', 3700, weight=1, plan=plan)
        optim.add_dosefalloff_objective('BodyRS', 3444, 1813, 3, weight=0, plan=plan)        
 
 
def add_opt_obj_orl(plan_data,yeux=False):

    plan = plan_data['patient'].TreatmentPlans[plan_data['plan_name']]
    patient = plan_data['patient']
    rx_dose = plan_data['rx_dose']
    ptv = plan_data['ptv']
    nb_fx = plan_data['nb_fx']
    nb_ptv = len(ptv)
    
    #change the dose from 60 to 59.4 if 33 fractions but just for the objectives and clinical goals
    if 'PTV60' in ptv and nb_fx == 33:
        rx_dose.append(5940)
        rx_dose.remove(6000)
        rx_dose.sort(reverse=True)
    
    if nb_ptv == 4:
        optim.add_mindose_objective('mod'+ptv[0], rx_dose[0], weight=500, plan=plan)
        optim.add_maxdose_objective('mod'+ptv[0], rx_dose[0]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[1], rx_dose[1], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[1], rx_dose[1]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[2], rx_dose[2], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[2], rx_dose[2]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[3], rx_dose[3], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[3], rx_dose[3]*1.05, weight=50, plan=plan)
    elif nb_ptv == 3:
        optim.add_mindose_objective('mod'+ptv[0], rx_dose[0], weight=500, plan=plan)
        optim.add_maxdose_objective('mod'+ptv[0], rx_dose[0]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[1], rx_dose[1], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[1], rx_dose[1]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[2], rx_dose[2], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[2], rx_dose[2]*1.05, weight=50, plan=plan)
    elif nb_ptv == 2:
        optim.add_mindose_objective('mod'+ptv[0], rx_dose[0], weight=500, plan=plan)
        optim.add_maxdose_objective('mod'+ptv[0], rx_dose[0]*1.05, weight=50, plan=plan)
        optim.add_mindose_objective('mod'+ptv[1], rx_dose[1], weight=500, plan=plan)
        optim.add_maxdose_objective('OPT'+ptv[1], rx_dose[1]*1.05, weight=50, plan=plan)
    elif nb_ptv == 1:
        optim.add_mindose_objective('mod'+ptv[0], rx_dose[0], weight=500, plan=plan)
        optim.add_maxdose_objective('mod'+ptv[0], rx_dose[0]*1.05, weight=50, plan=plan)
        
    if rx_dose[0] < 4300:
        optim.add_maxdose_objective('MOELLE', rx_dose[0], plan=plan)
        optim.add_maxdose_objective('prv5mmMOELLE', rx_dose[0], plan=plan)
        optim.add_maxdose_objective('TR CEREBRAL', rx_dose[0], plan=plan)
        optim.add_maxdose_objective('prv5mmTR CEREBRAL', rx_dose[0], plan=plan)
    else:
        optim.add_maxdose_objective('MOELLE', 4300,weight=100, plan=plan)
        optim.add_maxdose_objective('prv5mmMOELLE', 4700,weight=100, plan=plan)
        optim.add_maxdose_objective('TR CEREBRAL', 4800,weight=100, plan=plan)
        optim.add_maxdose_objective('prv5mm TRONC', 5000,weight=100, plan=plan)
        optim.add_maxdose_objective('BLOC MOELLE', 4300,weight=1, plan=plan)
    
    try:
        optim.add_maxdose_objective('OREILLE DRT', 4800,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('OREILLE GCHE', 4800,weight=10, plan=plan)
    except:
        pass
    try:
        if rx_dose[0]> 5700:
            optim.add_maxdose_objective('OPT CERVEAU', 5700,weight=10, plan=plan)
        else:
            optim.add_maxdose_objective('OPT CERVEAU', rx_dose[0]*1.02,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('MAND ds '+ptv[0]+'+5mm', rx_dose[0]*1.02,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('MAND-'+ptv[0]+'-5mm', rx_dose[0]*0.97,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('PBD ds ' + ptv[0], rx_dose[0]*1.02,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('PBG ds ' + ptv[0], rx_dose[0]*1.02,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('PBD ds ' + ptv[1], rx_dose[1]*1.05,weight=10, plan=plan)
    except:
        pass
    try:
        optim.add_maxdose_objective('PBG ds ' + ptv[1], rx_dose[1]*1.05,weight=10, plan=plan)
    except:
        pass
    try:
        vol_paro_drt = patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['OPT PARO DRT'].GetRoiVolume()/patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['PARO DRT'].GetRoiVolume()
        if vol_paro_drt > 0.99:
            vol_paro_drt = 0.5
        dose_paro_drt = round(vol_paro_drt*30*rx_dose[0]/(100),-1)
        optim.add_maxeud_objective('OPT PARO DRT', dose_paro_drt, param_a=1.0, weight=1.0, plan=plan, plan_opt=0)
    except:
        pass
    try:
        vol_paro_gche = patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['OPT PARO GCHE'].GetRoiVolume()/patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['PARO GCHE'].GetRoiVolume()
        if vol_paro_gche > 0.99:
            vol_paro_gche = 0.5
        dose_paro_gche = round(vol_paro_gche*30*rx_dose[0]/(100),-1)
        optim.add_maxeud_objective('OPT PARO GCHE', dose_paro_gche, param_a=1.0, weight=1.0, plan=plan, plan_opt=0)
    except:
        pass
    try:
        vol_cavite = patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['OPT CAVITE ORALE'].GetRoiVolume()/patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['CAVITE ORALE'].GetRoiVolume()
        if vol_cavite > 0.98:
            vol_cavite = 1.6
        dose_vol_cavite = round(((vol_cavite*(-26))+72)*rx_dose[0]/100,-1)
        optim.add_maxeud_objective('OPT CAVITE ORALE', dose_vol_cavite, param_a=1.0, weight=1.0, plan=plan, plan_opt=0)
    except:
        pass
    if roi.roi_exists('OPT LARYNX'):
        optim.add_maxeud_objective('OPT LARYNX', round(0.54*rx_dose[0],-1), param_a=1.0, weight=1.0, plan=plan, plan_opt=0)
    else:
        if roi.roi_exists('LARYNX'):
            optim.add_maxdose_objective('LARYNX', round(rx_dose[0]*1.03,-1),weight=10, plan=plan)
    try:
        vol_oeso = patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['OPT OESOPHAGE'].GetRoiVolume()/patient.PatientModel.StructureSets[plan_data['ct']].RoiGeometries['OESOPHAGE'].GetRoiVolume()
        if vol_oeso > 0.98:
            vol_oeso = 1
        dose_vol_oeso = round(((vol_oeso*(-30))+58)*rx_dose[0]/(100),-1)
        optim.add_maxeud_objective('OPT OESOPHAGE', dose_vol_oeso, param_a=1.0, weight=1.0, plan=plan, plan_opt=0)
    except:
        if roi.roi_exists('OESOPHAGE'):
            optim.add_maxdose_objective('OESOPHAGE', round(rx_dose[0]*1.03,-1),weight=10, plan=plan)

    optim.add_dosefalloff_objective('Ring', rx_dose[0], rx_dose[0]*0.5, distance=3, weight=1, plan=plan, plan_opt=0,adapt_dose_level=True)
    optim.add_dosefalloff_objective('BodyRS+Table', rx_dose[0], rx_dose[0]*0.85, distance=0.3, weight=1, plan=plan, plan_opt=0,adapt_dose_level=True)
    
    if yeux:
        optim.add_maxdose_objective('CHIASMA', 4900,weight=10, plan=plan)
        optim.add_maxdose_objective('prv5mmCHIASMA', 5500,weight=10, plan=plan)
        optim.add_maxdose_objective('OEIL DRT', 4400,weight=10, plan=plan)
        optim.add_maxdose_objective('OEIL GCHE', 4400,weight=10, plan=plan)
        optim.add_maxdose_objective('CRISTALLIN DRT', 600,weight=10, plan=plan)
        optim.add_maxdose_objective('CRISTALLIN GCHE', 600,weight=10, plan=plan)
        optim.add_maxdose_objective('N OPT DRT', 4400,weight=10, plan=plan)
        optim.add_maxdose_objective('N OPT GCHE', 4400,weight=10, plan=plan)
        optim.add_maxdose_objective('prv5mmNOD', 5300,weight=10, plan=plan)
        optim.add_maxdose_objective('prv5mmNOG', 5300,weight=10, plan=plan)        