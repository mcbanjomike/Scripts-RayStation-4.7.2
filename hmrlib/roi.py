# -*- coding: utf-8 -*-
"""
This module contains any functions directly related to ROI operations and queries.
"""
import sys
import os.path
import lib

import logging
from HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

base_logger = logging.getLogger("hmrlib." + os.path.basename(__file__)[:-3])
""" The basic logger object used for logging in hmrlib.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

logger = HMR_RS_LoggerAdapter(base_logger)
""" The basic logger object adapted with an HMR_RS_LoggerAdapter.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

# To allow importation of module by sphinx-python
try:
    from connect import *
    # import ScriptClient
except Exception as e:
    if 'IronPython' in sys.version:
        raise
    else:
        pass


def identify_body():
    """
        Attempts to identify which is the body ROI that should be set as external
        in RayStation.  However, it does not set this ROI as external.

        Returns:
            str: the name of the ROI identified as body. Returns `None` if it could not be identified.
    """
    patient = lib.get_current_patient()
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for r in roi_names:
        if r.upper().replace(' ', '') == 'BODY+TABLE':
            return r
        if r.upper().replace(' ', '') == 'BODY':
            return r
    logger.warning('No ROI named in a standard way for the body could be found.')
    return None


def identify_ptvs2():
    """
    Attempts to identify PTVs.

    Ignores case.  Expects 'PTV' at the beginning of the ROI name, then
    characters which can be represented as a number (the prescription dose).
    """
    patient = lib.get_current_patient()
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    candidates = [x for x in roi_names if (x.replace(' ', '').upper().startswith('PTV') and lib.is_number(x.replace(' ', '').upper()[3:]))]

    if len(candidates) == 0:
        logger.warning('No ROIs could be identified as a PTV.')
        return None

    logger.info('Possible PTVs identified as %s', candidates)
    return candidates


def get_roi(roi_name, examination=None):
    """
    Returns ROI object from an ROI name for the current structure set.

    Args:
        roi_name (str): the name of the ROI to be returned
        examination (RayStation object, optional): the RayStation object representing the examination

    Returns:
        The ROI RayStation object.
    """
    patient = lib.get_current_patient()

    if examination is None:
        exam = lib.get_current_examination()
    else:
        exam = examination

    try:
        roi = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[roi_name]
        if roi.PrimaryShape is None:
            lib.error('ROI %s is not segmented on currently selected examination.  Select correct CT and try again.' % roi_name)
    except Exception as e:
        logger.exception(e)
        raise

    # Could have returned roi.OfRoi, but returning roi lets once access the
    # DicomImportHistory, PrimaryShape and GetCenterOfRoi() and GetRoiVolume()
    # functions.
    #
    # Under roi.OfRoi, we have among others Name, Type, Color, RoiMaterial and
    # several functions.  Launch StateTree to see.
    return roi


def roi_exists(roi_name, examination=None):
    """
        Checks if a ROI exists.

        Args:
            roi_name (str): the name of the ROI to check
            examination (RayStation object, optional): the RayStation object representing the examination

        Returns:
            True if it exists, False if not.
    """

    patient = lib.get_current_patient()

    if examination is None:
        exam = lib.get_current_examination()
    else:
        exam = examination

    try:
        roi = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[roi_name]
    except:
        return False

    if roi.PrimaryShape is None:
        # is not segmented on current examination.
        return False

    return True


def get_roi_approval(roi_name, examination=None):
    """
    Checks if ROI named *roi_name* is approved (in any of the existing beamsets).

    Args:
        roi_name (str): the name of the ROI
        examination (RS examination object, optional): the examination (CT or StructureSet) for which the ROI is defined; if left out the currently selected examination is used.

    Returns:
        True if the ROI is approved, False if not.
    """

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()

    try:
        for beamset_approved_structure_set in patient.PatientModel.StructureSets[examination.Name].ApprovedStructureSets:
            for beamset_approved_rois in beamset_approved_structure_set.ApprovedRoiStructures:
                if beamset_approved_rois.OfRoi.Name == roi_name:
                    logger.info('ROI %s is approved.', roi_name)
                    return True
        logger.info('ROI %s is NOT approved.', roi_name)
        return False
    except Exception as e:
        logger.exception(e)
        raise


def set_ptv(roi_name):
    """
    Sets a given ROI as a PTV (*Type*).  The *OrganType* is set as *Target*.

    Args:
        roi_name (str): the name of the ROI to set as PTV
    """

    if get_roi_approval(roi_name):
        logger.warning('ROI "%s" is approved and therefore cannot be changed.' % roi_name)
        return

    try:
        roi = get_roi(roi_name)
        with CompositeAction('Apply ROI changes'):
            roi.OfRoi.Type = "Ptv"
            roi.OfRoi.OrganData.OrganType = "Target"
            roi.OfRoi.SetRoiMaterial(Material=None)
        logger.info('ROI "%s" set as PTV.', roi_name)
    except Exception as e:
        logger.exception(e)
        raise


def set_external(roi_name):
    """
    Sets a given ROI as external contour.  Any structure outside this ROI will
    be ignored as far as dose calculations are concerned.

    Args:
        roi_name (str): the name of the ROI to set as external
    """

    if get_roi_approval(roi_name):
        logger.warning('ROI "%s" is approved and therefore cannot be changed.' % roi_name)
        return

    try:
        roi = get_roi(roi_name)
        roi.OfRoi.SetAsExternal()
        logger.info('ROI "%s" set as external.', roi_name)
    except Exception as e:
        logger.exception(e)
        raise


def set_roi_type(roi_name, roi_type=None, organ_type=None):
    """
    Sets a ROI to a given type of ROI and/or to a given organ type.

    Args:
        roi_name (str): the name of the ROI
        roi_type (str, optional): the new type of ROI.  Must be one of the supported ROI types in RayStation: *Ptv*, *Gtv*, *TreatedVolume*, *Organ*, etc.
        organ_type (str, optional): the organ type of the ROI. Must be one of the supported ROI organ types in RayStation: *OrganAtRisk*, *Target*, *Other*, etc.
    """

    if get_roi_approval(roi_name):
        logger.warning('ROI "%s" is approved and therefore cannot be changed.' % roi_name)
        return

    patient = lib.get_current_patient()
    try:
        with CompositeAction('Apply ROI changes (' + roi_name + ')'):
            if roi_type:
                patient.PatientModel.RegionsOfInterest[roi_name].Type = roi_type
                logger.info('Type of ROI "%s" set as %s', roi_name, roi_type)
            if organ_type:
                patient.PatientModel.RegionsOfInterest[roi_name].OrganData.OrganType = organ_type
                logger.info('OrganType of ROI "%s" set as %s', roi_name, organ_type)
    except Exception as e:
        logger.exception(e)
        raise


# def set_roi_material(roi_name, material_name):
#     """
#     EXPERIMENTAL
#     """
#     raise NotImplementedError

#     if get_roi_approval(roi_name):
#         logger.warning('ROI "%s" is approved and therefore cannot be changed.' % roi_name)
#         return

#     patient = lib.get_current_patient()

#     print patient.PatientModel.Materials
#     print dir(patient.PatientModel.Materials)
#     for m in patient.PatientModel.Materials:
#         print m, dir(m)

#     mat = patient.PatientModel.RegionsOfInterest['MOELLE'].RoiMaterial.OfMaterial
#     print mat
#     print dir(mat)

#     import ScriptClient

#     print dir(ScriptClient.ScriptObject)

#     print ScriptClient.ScriptObject.GetType(mat)
#     print ScriptClient.ScriptObject.GetHelp(mat)

#     print ScriptClient.ScriptObject.__doc__

#     new_obj = ScriptClient.ScriptObject(ScriptClient.RayScriptService.Instance, patient.PatientModel.RegionsOfInterest['MOELLE'])

#     # try:
#     #     roi = get_roi(roi_name)
#     #     roi.OfRoi.SetRoiMaterial(Material=material_name)
#     #     logger.info('ROI "%s" set as material %s.', material_name)
#     # except Exception as e:
#     #     logger.exception(e)
#     #     raise


def auto_assign_roi_types():
    """
        Attempts to automatically assign correct ROI types.

        This functions makes several assumptions and ignores case in ROI names.

        - Any ROI with a name containing *PTV* or *CTV* or *GTV* or *ITV* with the absence of "-" character is considered a *Target*.  Thus, ROIs named such as *RIBS-PTV* will not be labeled as *Target*.
        - Any ROI with a name starting with *BOLUS* will have its type changed as such.
        - Sets *BODY+Table* (preferably) or *BODY* to external.
        - All other ROIs will be set by default to *Organ* type and *OrganAtRisk* organ type.
    """
    patient = lib.get_current_patient()
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            set_roi_type(name, 'Ptv', 'Target')
        elif 'CTV' in n and '-' not in n:
            set_roi_type(name, 'Ctv', 'Target')
        elif 'GTV' in n and '-' not in n:
            set_roi_type(name, 'Gtv', 'Target')
        elif 'ITV' in n and '-' not in n:
            set_roi_type(name, 'TreatedVolume', 'Target')
        elif n == 'BODY':
            if 'BODY+TABLE' not in [x.replace(' ', '').upper() for x in roi_names]:
                # patient.PatientModel.RegionsOfInterest[name].Type = 'External'
                set_external(name)
                set_roi_type(name, organ_type='Other')
        elif n == 'BODY+TABLE':
            set_external(name)
            set_roi_type(name, organ_type='Other')
        elif n.startswith('BOLUS'):
            set_roi_type(name, 'Bolus', 'Other')
        else:
            set_roi_type(name, 'Organ', 'OrganAtRisk')


def auto_assign_roi_types_v2():
    """
        Attempts to automatically assign correct ROI types.

        This functions makes several assumptions and ignores case in ROI names.

        - Any ROI with a name containing *PTV* or *CTV* or *GTV* or *ITV* with the absence of "-" character is considered a *Target*.  Thus, ROIs named such as *RIBS-PTV* will not be labeled as *Target*.
        - Any ROI with a name starting with *BOLUS* will have its type changed as such.
        - All other ROIs will be set by default to *Organ* type and *OrganAtRisk* organ type.
    """
    patient = lib.get_current_patient()
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    for name in roi_names:
        n = name.replace(' ', '').upper()
        if 'PTV' in n and '-' not in n:
            set_roi_type(name, 'Ptv', 'Target')
        elif 'CTV' in n and '-' not in n:
            set_roi_type(name, 'Ctv', 'Target')
        elif 'GTV' in n and '-' not in n:
            set_roi_type(name, 'Gtv', 'Target')
        elif 'ITV' in n and '-' not in n:
            set_roi_type(name, 'TreatedVolume', 'Target')
        elif n == 'BODY':
            set_roi_type(name, organ_type='Other')
        elif n == 'BODY+TABLE':
            set_roi_type(name, organ_type='Other')
        elif n.startswith('BOLUS'):
            set_roi_type(name, 'Bolus', 'Other')
        else:
            set_roi_type(name, 'Organ', 'OrganAtRisk')


def delete_roi(roi_name):
    """
        Deletes an ROI based on its name.

        Args:
            roi_name (str): the name of the ROI to delete.
    """
    patient = lib.get_current_patient()

    try:
        for r in patient.PatientModel.RegionsOfInterest:
            if r.Name == roi_name:
                r.DeleteRoi()
                logger.info('Deleted ROI %s.', roi_name)
                break
        logger.warning('Could not delete ROI %s (not found).', roi_name)
    except Exception as e:
        logger.exception(e)
        raise e


def get_margin_settings(sup, inf=None, ant=None, post=None, left=None, right=None, margin_type="Expand"):
    """
    Returns the ROI margin settings in the format RayStation uses.

    Args:
        sup (float): the margin in cm in the superior direction
        inf (float, optional): the margin in cm in the inferior direction, equal to sup if unspecified
        ant (float, optional): the margin in cm in the anterior direction, equal to sup if unspecified
        post (float, optional): the margin in cm in the posterior direction, equal to sup if unspecified
        left (float, optional): the margin in cm in the patient left direction, equal to sup if unspecified
        right (float, optional): the margin in cm in the patient right direction, equal to sup if unspecified
        margin_type (str, optional): the type pf margin to use, by default, *Expand*.  Also available : *Contract*.

    Returns:
        dict: the margin settings in the RayStation format
    """
    if inf is None:
        inf = sup
    if ant is None:
        ant = sup
    if post is None:
        post = sup
    if left is None:
        left = sup
    if right is None:
        right = sup
    return dict(Type=margin_type, Superior=sup, Inferior=inf, Anterior=ant, Posterior=post,
                Right=right, Left=left)


def create_expansion(roi_name, sup, inf=None, ant=None, post=None, left=None, right=None, new_name=None):
    """
    Create a new ROI which is the expansion of another existing ROI.

    Args:
        roi_name (str): the source ROI name
        sup (float): the margin in cm in the superior direction
        inf (float, optional): the margin in cm in the inferior direction, equal to sup if unspecified
        ant (float, optional): the margin in cm in the anterior direction, equal to sup if unspecified
        post (float, optional): the margin in cm in the posterior direction, equal to sup if unspecified
        left (float, optional): the margin in cm in the patient left direction, equal to sup if unspecified
        right (float, optional): the margin in cm in the patient right direction, equal to sup if unspecified
        new_name (str, optional): the name of the newly created expanded ROI.  If unspecified, will default to the *<roi_name>+<sup>mm*.

    Returns:
        the ROI RayStation object corresponding to the expanded volume
    """
    if new_name is None:
        new_name = "%s+%dmm" % (roi_name, sup * 10)
    margins = get_margin_settings(sup, inf, ant, post, left, right)
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    source_roi = get_roi(roi_name)
    with CompositeAction('Expand'):
        expanded_roi = patient.PatientModel.CreateRoi(Name=new_name, Type="Organ", TissueName=None, RoiMaterial=None)
        expanded_roi.SetRoiMaterial(Material=source_roi.OfRoi.RoiMaterial)
        expanded_roi.SetMarginExpression(SourceRoiName=roi_name, MarginSettings=margins)
        expanded_roi.UpdateDerivedGeometry(Examination=examination)
    return expanded_roi


def create_ring(roi_name, r2, r1=0, new_name=None):
    """
    Creates a ring ROI around another source ROI.  The ring is specified by two
    distance parameters, :math:`r_1` and :math:`r_2`.  A ring of uniform thickness
    is assumed.

    - By default, :math:`r_1`, the inward distance, is set at 0, which makes the ring ROI inner surface coincide with the source roi surface.
    - The outward distance, :math:`r_2`, must always be specified.  It corresponds to the outward distance from the source ROI surface.  If set at zero, the outer surface of the ring ROI will correspond to the source ROI surface.
    - The sum :math:`r_1 + r_2` therefore gives the ring thickness.

    Args:
        r2 (float): the outward distance in cm
        r1 (float, optional): the inward distance in cm (default 0)
        new_name (str, optional): the name of the newly created ring ROI.  If unspecified, the name will automatically be generated based on *r2* and *r1*.

    Returns:
        the ROI RayStation object corresponding to the new ring ROI
    """
    if r1 < 0 or r2 < 0:
        lib.error('Cannot have a negative distance.')

    if new_name is None:
        if r1 == 0:
            new_name = "%s_ring_%dmm" % (roi_name, r2 * 10)
        else:
            new_name = "%s_ring_%d-%dmm" % (roi_name, r1 * 10, r2 * 10)
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    source_roi = get_roi(roi_name)
    # with CompositeAction('ROI Algebra (%s)' % roi_name):
    #     ring_roi = patient.PatientModel.CreateRoi(Name=new_name, Type="Organ", TissueName=None, RoiMaterial=None)
    #     ring_roi.SetRoiMaterial(Material=source_roi.RoiMaterial)
    #     ring_roi.SetAlgebraExpression(ExpressionA=dict(Operation="Union", SourceRoiNames=[roi_name], MarginSettings=get_margin_settings(r2)),
    #                                   ExpressionB=dict(Operation="Union", SourceRoiNames=[roi_name], MarginSettings=get_margin_settings(r1)),
    #                                   ResultOperation="Subtraction",
    #                                   ResultMarginSettings=get_margin_settings(0))
    #     ring_roi.UpdateDerivedGeometry(Examination=examination)
    with CompositeAction('Create Wall (%s, Image set: %s)' % (roi_name, examination)):
        ring_roi = patient.PatientModel.CreateRoi(Name=new_name, Color="White", Type="Organ", TissueName=None, RoiMaterial=None)
        ring_roi.SetRoiMaterial(Material=source_roi.OfRoi.RoiMaterial)
        ring_roi.SetWallExpression(SourceRoiName=roi_name, OutwardDistance=r2, InwardDistance=r1)
        ring_roi.UpdateDerivedGeometry(Examination=examination)
    return ring_roi


def get_intersecting_volume(roi_name_1, roi_name_2, examination=None):
    """
    Returns the volume of the intersection of two volumes in cc.

    Args:
        roi_name_1 (str): the name of the first ROI
        roi_name_2 (str): the name of the second ROI

    Returns:
        float: The volume in cc of the intersection of the two volumes.  If the volumes are disjoint, returns 0.
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    temp_roi_name = "temp_roi_" + roi_name_1 + "_" + roi_name_2

    with CompositeAction('ROI Algebra (%s, Image set: %s)' % (temp_roi_name, examination.Name)):
        retval_0 = patient.PatientModel.CreateRoi(Name=temp_roi_name, Color="Orange", Type="Organ", TissueName=None, RoiMaterial=None)
        retval_0.CreateAlgebraGeometry(Examination=patient.Examinations[examination.Name], ExpressionA={'Operation': "Union", 'SourceRoiNames': [roi_name_1], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [roi_name_2], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})

    try:
        vol = patient.PatientModel.StructureSets[examination.Name].RoiGeometries[temp_roi_name].GetRoiVolume()
        retval_0.DeleteRoi()
    except SystemError as e:
        if str(e).startswith('There is no geometry set for ROI'):  # disjoint volumes
            retval_0.DeleteRoi()
            return 0.0
        else:
            raise
    except Exception as e:
        print e
        raise

    return vol


def find_most_intersecting_roi(target_roi_name, roi_name_list, examination=None):
    """
    Find, out if a list of ROIs, which one intersects the most, in terms of volume, with a given ROI.

    Args:
        target_roi_name (str): the name of the ROI to test intersection against
        roi_name_list (list of str): the list of names of ROIs out of which to find the most intersecting one
        examination: RayStation examination object (used to determine on which CT the volumes are evaluated)

    Returns:
        str: the name of the ROI that shares the most volume with *target_roi_name*
    """
    if examination is None:
        examination = lib.get_current_examination()

    vol = -1
    return_roi = ''
    for roi_name in roi_name_list:
        test_vol = get_intersecting_volume(roi_name, target_roi_name, examination)
        if test_vol > vol:
            vol = test_vol
            return_roi = roi_name

    return return_roi


def get_roi_volume(roi_name, exam=None):
    """
        Returns the ROI volume in cc. If the ROI has no contours on the selected examination, returns 0.

        Gets the ROI from the currently selected examination.

        Args:
            roi_name (str): the name of the ROI
            exam (RS Examination object): The CT on which the ROI is contoured

        Returns:
            the volume in cc
    """
    if exam is None:
        exam = lib.get_current_examination()
    patient = lib.get_current_patient()

    # volume = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[roi_name].GetRoiVolume()

    try:
        volume = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[roi_name].GetRoiVolume()
    except:
        volume = 0

    return volume


def convert_absolute_volume_to_percentage(roi_name, volume_cc=0.1, examination=None):
    """ Converts an absolute volume to a relative value in percentage
        for ROI with name roi_name.

        Assumes the volume is calculated on the current examination.

        Args:
            roi_name (str): the name of the ROI for which to convert the volume value
            volume_cc (float, optional): the volume value in cc to convert to relative volume (default 0.1 cc)

        Returns:
            float: the volume value relative to the whole ROI volume in %, rounded to two decimal places
    """
    if examination is None:
        examination = lib.get_current_examination()
    volume = get_roi_volume(roi_name, exam=examination)
    cc_percentage = round(100.0 * volume_cc / volume, 2)
    return cc_percentage


def intersect_roi_ptv(roi_name, ptv_name, color="Blue", examination=None, margeptv=0, output_name="PTV"):
    """Creates ROI that is the intersection of the specified ROI and PTV.

    Args:
        roi_name (str): The name of the ROI to use
        ptv_name (str): The name of the PTV to use
        color (str): The color of the resulting ROI
        examination (RS Examination object): The CT on which the source and resulting geometries are contoured
    Returns:
        RS region of interest structure
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    if margeptv == 0:
        newname = "%s dans %s" % (roi_name, output_name)
    else:
        newname = "%s dans %s+%scm" % (roi_name, output_name, margeptv)

    patient.PatientModel.CreateRoi(Name=newname, Color=color, Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[newname].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [ptv_name], 'MarginSettings': {'Type': "Expand", 'Superior': margeptv, 'Inferior': margeptv, 'Anterior': margeptv, 'Posterior': margeptv, 'Right': margeptv, 'Left': margeptv}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [roi_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest[newname].UpdateDerivedGeometry(Examination=examination)

    return patient.PatientModel.RegionsOfInterest[newname]


def subtract_roi_ptv(roi_name, ptv_name, color="Yellow", examination=None, margeptv=0, output_name="PTV"):
    """Creates ROI that is the subtraction of the given PTV from the specified ROI.

    Args:
        roi_name (str): The name of the ROI to use
        ptv_name (str): The name of the PTV to use
        color (str): The color of the resulting ROI
        examination (RS Examination object): The CT on which the source and resulting geometries are contoured
        margeptv (float) : Optional uniform margin around PTV in cm. Default is 0 cm.
    Returns:
        RS region of interest structure
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    if margeptv == 0:
        newname = "%s hors %s" % (roi_name, output_name)
    else:
        newname = "%s hors %s+%scm" % (roi_name, output_name, margeptv)

    patient.PatientModel.CreateRoi(Name=newname, Color=color, Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[newname].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [roi_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [ptv_name], 'MarginSettings': {'Type': "Expand", 'Superior': margeptv, 'Inferior': margeptv, 'Anterior': margeptv, 'Posterior': margeptv, 'Right': margeptv, 'Left': margeptv}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest[newname].UpdateDerivedGeometry(Examination=examination)

    return patient.PatientModel.RegionsOfInterest[newname]



def subtract_rois(big_roi_name, small_roi_name, color="Yellow", examination=None, output_name=None):
    """Creates ROI that is the subtraction of the two ROIs (useful for creating rings from PTV expansions).

    Args:
        big_roi_name (str): The name of the larger ROI
        small_roi_name (str): The name of the smaller ROI
        color (str): The color of the resulting ROI
        examination (RS Examination object): The CT on which the source and resulting geometries are contoured
        output_name (str): The name that the new contour will have
    Returns:
        RS region of interest structure
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    if output_name is None:
        newname = "%s-%s" % (big_roi_name, small_roi_name)
    else:
        newname = output_name

    patient.PatientModel.CreateRoi(Name=newname, Color=color, Type="Organ", TissueName=None, RoiMaterial=None)
    patient.PatientModel.RegionsOfInterest[newname].SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [big_roi_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [small_roi_name], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    patient.PatientModel.RegionsOfInterest[newname].UpdateDerivedGeometry(Examination=examination)

    return patient.PatientModel.RegionsOfInterest[newname]

    
    
def create_expanded_ptv(ptv_name, color="Yellow", examination=None, margeptv=0, output_name=None, operation='Expand'):
    """Creates an expansion of the specified PTV with a uniform margin.
       Note that the maximum margin permitted by RayStation is 5cm, so the operation only continues if the margin <=5cm.

    Args:
        ptv_name (str): The name of the PTV to use
        color (str): The color of the resulting ROI
        examination (RS Examination object): The CT on which the source and resulting geometries are contoured
        margeptv (float) : Uniform margin around PTV in cm. Default is 0.
    Returns:
        RS region of interest structure
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    if output_name is None:
        if operation == 'Expand':
            name = "PTV+%scm" % margeptv
        else:
            name = "PTV-%scm" % margeptv
    else:
        if operation == 'Expand':
            name = output_name + "+%scm" % margeptv
        else:
            name = output_name + "-%scm" % margeptv

    if margeptv <= 5:
        patient.PatientModel.CreateRoi(Name=name, Color=color, Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[name].SetMarginExpression(SourceRoiName=ptv_name, MarginSettings={'Type': operation, 'Superior': margeptv, 'Inferior': margeptv, 'Anterior': margeptv, 'Posterior': margeptv, 'Right': margeptv, 'Left': margeptv})
        patient.PatientModel.RegionsOfInterest[name].UpdateDerivedGeometry(Examination=examination)


def create_expanded_roi(roi_name, color="Yellow", examination=None, marge_lat=0, marge_sup_inf=0, output_name=None, operation='Expand'):
    """Creates an expansion of the specified ROI with a variable margin.
       Note that the maximum margin permitted by RayStation is 5cm, so the operation only continues if the margin <=5cm.

    Args:
        roi_name (str): The name of the ROI to use
        color (str): The color of the resulting ROI
        examination (RS Examination object): The CT on which the source and resulting geometries are contoured
        marge_lat (float) : The margin to use in the LAT and A-P directions. Default is 0.
        marge_sup_inf (float) : The margin to use in the SUP-INF direction. Default is 0.
        operation(str) : Whether to expand or contract the ROI
    Returns:
        RS region of interest structure
    """

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    if output_name is None:
        if operation == 'Expand':
            name = "%s+%scm" % (roi_name, marge_lat)
        else:
            name = "%s-%scm" % (roi_name, marge_lat)
    else:
        name = output_name

    if marge_lat <= 5 and marge_sup_inf <= 5:
        patient.PatientModel.CreateRoi(Name=name, Color=color, Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest[name].SetMarginExpression(SourceRoiName=roi_name, MarginSettings={'Type': operation, 'Superior': marge_sup_inf, 'Inferior': marge_sup_inf, 'Anterior': marge_lat, 'Posterior': marge_lat, 'Right': marge_lat, 'Left': marge_lat})
        patient.PatientModel.RegionsOfInterest[name].UpdateDerivedGeometry(Examination=examination)

def generate_BodyRS_plus_Table(threshold=-750, struct=0, planche_seulement=False):
    """
    This script creates a new external contour named BodyRS, combines it with the table to create BodyRS+Table and then simplifies the resulting
    contour to remove any holes that might prevent optimization from working. This new contours is designated as the external for the patient.
    The script also renames the Pinnacle BODY contour "BODY Pinnacle" and erases any Body+Table contours imported from Pinnacle.

    Note that if a BodyRS+Table contour already exists, another one will not be created and no change will be made to the existing one.

    The script as currently designed will only work if there is ONLY ONE SCAN for the patient.

    ARGS:
    threshold (int) : The lower CT number limit to use when generating the external contour. Default is -750.
    struct (int) : The index of the structure set to use (0 for cases with only one scan, 1 for lung cases)
    """
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()

    # Rename BODY contour to BODY Pinnacle
    if roi_exists("BODY"):
        patient.PatientModel.RegionsOfInterest["BODY"].Name = "BODY Pinnacle"

    # Delete BODY+Table contour
    if roi_exists("Body+Table"):
        patient.PatientModel.RegionsOfInterest['Body+Table'].DeleteRoi()
    if roi_exists("BODY+Table"):
        patient.PatientModel.RegionsOfInterest['BODY+Table'].DeleteRoi()

    # Create new Body contour named BodyRS (in case BODY contains holes which prevent plan optimization)
    if not roi_exists("BodyRS"):
        retval_0 = patient.PatientModel.CreateRoi(Name="BodyRS", Color="Green", Type="Organ", TissueName="", RoiMaterial=None)
        retval_0.CreateExternalGeometry(Examination=examination, ThresholdLevel=threshold)

    if planche_seulement is False:
        # Create BodyRS+Table (unless it exists, in which case it is assumed to be already set as the external contour)
        if not roi_exists("BodyRS+Table"):
            retval_0 = patient.PatientModel.CreateRoi(Name="BodyRS+Table", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
            retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["Table"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BodyRS"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Union", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
            retval_0.UpdateDerivedGeometry(Examination=examination)
            # Set BodyRS+Table as external contour
            patient.PatientModel.RegionsOfInterest['BodyRS+Table'].Type = "External"
            retval_0.SetAsExternal()

    # Remove holes from external contour prior to optimization (not possible in RayStation 4.0)
    if lib.check_version(4.7):
        if planche_seulement is False:
            patient.PatientModel.StructureSets[struct].SimplifyContours(RoiNames=["BodyRS+Table"], RemoveHoles3D=True)
        else:
            patient.PatientModel.StructureSets[struct].SimplifyContours(RoiNames=["BodyRS"], RemoveHoles3D=True)


def generate_BodyRS_using_threshold():
    patient = lib.get_current_patient()
    examination = lib.get_current_examination()
    structure_set = 0

    if not roi_exists("BodyRS"):
        patient.PatientModel.CreateRoi(Name="BodyRS", Color="Green", Type="Organ", TissueName=None, RoiMaterial=None)
        patient.PatientModel.RegionsOfInterest['BodyRS'].GrayLevelThreshold(Examination=patient.Examinations['CT 1'], LowThreshold=-650, HighThreshold=5000, PetUnit="", BoundingBox=None)
        patient.PatientModel.RegionsOfInterest['BodyRS'].Type = "External"
        patient.PatientModel.RegionsOfInterest['BodyRS'].SetAsExternal()
        patient.PatientModel.StructureSets[structure_set].SimplifyContours(RoiNames=["BodyRS"], RemoveHoles3D=True)
