# -*- coding: utf-8 -*-
"""
This module contains any functions directly related to ROI operations and queries.
"""
import sys
import os.path
import math
import lib
import roi

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


def get_poi(poi_name, examination=None):
    """
    Returns POI object from a POI name.

    Args:
        poi_name (str): the name of the POI
        examination (str, optional): the name of the examination (CT or StructureSet) for which the poi is defined; if left out the currently selected examination is used.

    Returns:
        the RayStation POI object
    """
    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()

    try:
        poi = [x for x in patient.PatientModel.StructureSets[examination.Name].PoiGeometries if x.OfPoi.Name == poi_name][0]

        if abs(poi.Point.x) == sys.float_info.max or abs(poi.Point.x) == sys.float_info.min:
            lib.error('POI %s is not segmented on current examination.  Select correct CT and try again.' % poi_name)

        return poi
    except IndexError as e:
        logger.error('No POI found named %s', poi_name)
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise


def show_poi_coordinates(poi_name):
    """
        In a popup window, shows DICOM coordinates of a specific POI defined for the current patient model in RayStation.

        Args:
            poi_name (str): the name of the POI for which to show the coordinates
    """
    import gui
    # poi = get_poi(poi_name)
    coords = get_poi_coordinates(poi_name)
    msg = 'Les coordonnées DICOM du point "%s" sont : [x = %.2f cm, y = %.2f cm, z = %.2f cm]' % (poi_name, coords.x, coords.y, coords.z)
    gui.show_log_window(msg)


def show_all_poi_coordinates():
    """
        In a popup window, shows DICOM coordinates of all POIs defined to the current patient model.
    """
    import gui
    patient = lib.get_current_patient()
    poi_names = [r.Name for r in patient.PatientModel.PointsOfInterest]
    msg = ''
    for poi_name in poi_names:
        coords = get_poi_coordinates(poi_name)
        msg += 'Les coordonnées DICOM du point "%s" sont : [x = %.2f cm, y = %.2f cm, z = %.2f cm]\n' % (poi_name, coords.x, coords.y, coords.z)
    gui.show_log_window(msg)


def identify_isocenter_poi():
    """ Attempts to identify isocenter POI.

        The expected name of the isocenter POI is either *ISO* or *ISO SCAN*.
        If either of the two is found, it is returned, with priority to *ISO*.
        If not, the shortest string in the name candidates is returned.

        Returns:
            str: Name of most probable isocenter POI if found, `None` if not.
    """
    patient = lib.get_current_patient()
    poi_names = [r.Name for r in patient.PatientModel.PointsOfInterest]
    iso_candidates = [x for x in poi_names if x.upper().startswith('ISO')]

    # No candidates
    if len(iso_candidates) == 0:
        logger.warning('No isocenter POI could be found.')
        return None

    # Multiple candidates
    if len(iso_candidates) > 1:
        for i in sorted(iso_candidates, key=lambda x: len(x)):
            if i.upper() == 'ISO':
                logger.info('Isocenter POI identified as "%s"', i)
                return i
            if i.upper() == 'ISO SCAN':
                logger.info('Isocenter POI identified as "%s"', i)
                return i

        # If all else fails, return shortest string.
        guess = sorted(iso_candidates, key=lambda x: len(x))[0]
        logger.warning('Best isocenter POI candidate is "%s"', guess)
        return guess

    # Case where there is only 1 candidates
    logger.info('Isocenter POI identified as "%s"', iso_candidates[0])
    return iso_candidates[0]


def set_poi_type(poi_name, poi_type='Marker'):
    """
    Sets a POI to a given POI type.

    Args:
        poi_name (str): the name of the POI for which to set the type
        poi_type (str, optional): the type of the POI.  By default, will set to type *Marker*.
    """

    if get_poi_approval(poi_name):
        logger.warning('POI "%s" is approved and therefore cannot be changed.' % poi_name)
        return

    patient = lib.get_current_patient()
    try:
        patient.PatientModel.PointsOfInterest[poi_name].Type = poi_type
        logger.info('Type of POI "%s" set as %s', poi_name, poi_type)
    except Exception as e:
        logger.exception(e)
        raise


def auto_assign_poi_types():
    """
        Attempts to automatically assign correct POI types.

        Assumes localization point has string *SCAN* as part of its name.
        If no POI with *SCAN* in its name ca be found, the isocenter will
        be assumed to be the proper localization point.

        Isocenter is set to the type *isocenter*, save for the case above.

        All other POIs are set to type *marker*.
    """
    patient = lib.get_current_patient()
    poi_names = [p.Name for p in patient.PatientModel.PointsOfInterest]

    iso_name = identify_isocenter_poi()

    set_poi_type(iso_name, 'Isocenter')

    loc_name = [p.Name for p in patient.PatientModel.PointsOfInterest if 'SCAN' in p.Name.upper()]
    if len(loc_name) > 1:
        logger.error('More than one POI found for possible localization points.  Only one POI should exist with "SCAN" in its name.')
        raise SystemError('More than one POI found for possible localization points.  Only one POI should exist with "SCAN" in its name.')
    elif len(loc_name) == 0:
        logger.warning('No localization point could be found.  Using the isocenter point for localization.')
        loc_name = iso_name
        set_poi_type(loc_name, 'LocalizationPoint')
    else:
        loc_name = loc_name[0]
        set_poi_type(loc_name, 'LocalizationPoint')

    done_pois = [iso_name, loc_name]

    for p in poi_names:
        if p not in done_pois:
            set_poi_type(p, 'Marker')


def place_prescription_point(target_fraction_dose, ptv_name, poi_name, beamset=None, exam=None):
    """
    Attempts to place automatically a POI on a target per-fraction isodose line.

    .. rubric::
      PRE-REQUISITES

    - Existence of an identifiable PTV contour.
    - Dose is calculated.

    .. rubric::
      Algorithm description

    - A point on the PTV contour on a slice near the PTV center is found.
    - The dose is evaluated at that point.
    - An approximate unit vector towards the PTV center is calculated from that position.
        + If the evaluated dose is smaller than the prescription dose, the evaluation point is moved a short distance towards the PTV center.
        + If the evaluated dose is greater than the prescription dose, the evaluation point is moved a short distance away from the PTV center.
    - If the prescription dose is overshot by this procedure, the direction of movement is reversed and the move distance halved.
    - This process is repeated until evaluated dose equals the prescription dose to 3 decimal figures or 100 iterations are reached.

    Finally,

    - The specified POI is placed at the found coordinates.

    .. seealso::
      function `hmrlib.hmrlib.auto_place_prescription_point`

    """

    patient = lib.get_current_patient()
    if exam is None:
        exam = lib.get_current_examination()

    if beamset is None:
        beamset = lib.get_current_beamset()

    try:
        # Get PTV center
        ptv_center = lib.RSPoint(point=patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].GetCenterOfRoi())

        # Get slice thickness from CT
        slice_width = abs(exam.Series[0].ImageStack.SlicePositions[1] - exam.Series[0].ImageStack.SlicePositions[0])
        logger.info('CT slice width = %s cm', slice_width)

        initial_point = None
        # Find contour point on a slice close to PTV center
        for c in patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].PrimaryShape.Contours:
            if lib.check_version(4.7):
                if c[0].z < ptv_center.z + slice_width and c[0].z > ptv_center.z - slice_width:
                    initial_point = lib.RSPoint(c[0].x, c[0].y, c[0].z)
                    break
            else:
                if c.ContourData[0].z < ptv_center.z + slice_width and c.ContourData[0].z > ptv_center.z - slice_width:
                    initial_point = lib.RSPoint(c.ContourData[0].x, c.ContourData[0].y, c.ContourData[0].z)
                    break

        if initial_point is None:
            logger.info('Could not find a point on the same slice as the ROi center. Disjoint/noncoplanar PTV?')
            logger.info('Trying with first point in contour shape.')
            c = patient.PatientModel.StructureSets[exam.Name].RoiGeometries[ptv_name].PrimaryShape.Contours[0]
            if lib.check_version(4.7):
                initial_point = lib.RSPoint(c[0].x, c[0].y, c[0].z)
            else:
                initial_point = lib.RSPoint(c.ContourData[0].x, c.ContourData[0].y, c.ContourData[0].z)

        logger.info('Initial point = %s cm', initial_point)

        u = lib.RSPoint(point=lib.unit_vector(ptv_center - initial_point))
        logger.info('Unit vector towards PTV center = %s cm', u)

        # Change unit vector so that we stay on the same transverse slice
        u.z = 0
        logger.info('Approximate unit vector towards PTV center on single CT slice = %s cm', u)

        def move_point(point, direction, target_fraction_dose, initial_dose, step=0.05, iteration=0):
            point = point + step * direction
            dose = beamset.FractionDose.InterpolateDoseInPoint(Point=point.value)
            logger.info('Dose at %s = %.3f cGy', point, dose)
            if round(dose, 3) == round(target_fraction_dose, 3) or iteration > 100:
                # Found a suitable point or reached max iterations
                return point
            elif (initial_dose < target_fraction_dose and dose > target_fraction_dose) or (initial_dose > target_fraction_dose and dose < target_fraction_dose):
                # We overshot the point, so inverse direction and reduce step
                return move_point(point, -direction, target_fraction_dose, dose, step=0.5 * step, iteration=iteration + 1)
            else:
                # Keep going in the same direction with same step
                return move_point(point, direction, target_fraction_dose, dose, step=step, iteration=iteration + 1)

        dose = beamset.FractionDose.InterpolateDoseInPoint(Point=initial_point.value)

        if math.isnan(dose):
            lib.error('No dose value available.  Check if dose is calculated.')

        logger.info('Dose per fraction at initial point = %.3f cGy', dose)

        # Assume dose rises when moving towards center of PTV
        if dose < target_fraction_dose:
            point = move_point(initial_point, u, target_fraction_dose, dose)
        else:
            point = move_point(initial_point, -u, target_fraction_dose, dose)

        logger.info('Final point = %s cm', point)

    except Exception as e:
        logger.exception(e)
        raise

    if get_poi_approval(poi_name):
        logger.warning('POI %s is approved; cannot continue.', poi_name)
        lib.error('POI %s exists and is approved; cannot continue.  Unapprove %s before running script.' % (poi_name, poi_name))

    set_poi_coordinates(poi_name, point, examination=exam)

    return point


def auto_place_prescription_point():
    """
    Attempts to place automatically a POI on the prescription dose isoline near
    the boundaries of the PTV contour.

    .. rubric::
      PRE-REQUISITES

    1. Prescription dose defined for current beamset.
    2. Existence of a dose specification point (requires manual creation).
    3. Existence of an identifiable PTV contour.
    4. Dose is calculated.

    .. rubric::
      Algorithm description

    - A point on the PTV contour on a slice near the PTV center is found.
    - The dose is evaluated at that point.
    - An approximate unit vector towards the PTV center is calculated from that position.
        + If the evaluated dose is smaller than the prescription dose, the evaluation point is moved a short distance towards the PTV center.
        + If the evaluated dose is greater than the prescription dose, the evaluation point is moved a short distance away from the PTV center.
    - If the prescription dose is overshot by this procedure, the direction of movement is reversed and the move distance halved.
    - This process is repeated until evaluated dose equals the prescription dose to 3 decimal figures or 100 iterations are reached.

    Finally,

    - A POI named *PT PRESC* is placed at the final coordinates of the evaluation point.  This POI is created if not already existing.
    - The prescription is changed to prescribe the prescription dose at the final evaluation point, on the prescription dose isoline.  It is thus automatically satisfied.

    .. seealso::
      function `hmrlib.hmrlib.place_prescription_point`

    """
    # patient = lib.get_current_patient()
    # exam = lib.get_current_examination()
    beamset = lib.get_current_beamset()

    # Create PT PRESC if not present
    create_poi({'x': 0, 'y': 0, 'z': 0}, 'PT PRESC')

    ptv_candidates = roi.identify_ptvs2()
    if len(ptv_candidates) > 1:
        logger.warning('More than one possible PTV found: %s.  Trying highest PTV in the list %s.', ptv_candidates, sorted(ptv_candidates, key=lambda x: x[3:], reverse=True)[0])
    elif len(ptv_candidates) == 0:
        logger.error('No PTV could be found.  Aborting.')
        raise SystemError('No PTV could be found.  Aborting.')

    ptv = sorted(ptv_candidates, key=lambda x: x[3:], reverse=True)[0]
    logger.info('PTV identified as %s', ptv)

    try:
        presc_dose = lib.get_prescription_dose()
        logger.info('Presc dose = %.3f cGy', presc_dose)

        fractions = lib.get_fractions()
        logger.info('Fractions = %s', fractions)

        target_dose = presc_dose / float(fractions)
        logger.info('Target dose = %.3f cGy', target_dose)

    except Exception as e:
        logger.exception(e)
        raise

    point = place_prescription_point(target_dose, ptv, 'PT PRESC', beamset=beamset)

    # Set prescription to PT PRESC
    try:
        beamset.AddDosePrescriptionToPoi(PoiName='PT PRESC', DoseValue=presc_dose)
    except Exception as e:
        logger.exception(e)
        raise

    # Update dose specification point
    try:
        dsp = [x for x in beamset.DoseSpecificationPoints][0]
        dsp.Coordinates = point.value
    except IndexError as e:
        logger.error('You must create a dose specification point manually before executing this script.')
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise

    # Set beam dose specification points
    # Doesn't really update point coordinates for some reason.
    # Leaving to the user to do manually.
    # for b in beamset.Beams:
    #     b.SetDoseSpecificationPoint(Name=dsp.Name)


def create_poi(point, name, color='Green', poi_type='Marker', examination=None):
    """
    Creates a new POI.

    Args:
        point (dict or RSPoint): the (x, y, z) DICOM coordinates of the new point
        name (str): the name of the new POI
        color (str, optional): the color of the new POI (default: *Green*)
        poi_type (str, optional): the type of the new POI (default: *Marker*)

    Returns:
        the RayStation POI object corresponding to the newly created POI
    """

    # Must used dictionary representation of the point if an RSPoint
    if isinstance(point, lib.RSPoint):
        point = point.value

    patient = lib.get_current_patient()
    if examination is None:
        examination = lib.get_current_examination()

    try:
        poi = patient.PatientModel.CreatePoi(Examination=examination, Point=point, Volume=0, Name=name, Color=color, Type=poi_type)
        return poi
    except SystemError as e:
        if str(e) == 'Name not unique':
            logger.warning('A POI named %s already exists.' % name)
    except Exception as e:
        logger.exception(e)
        raise


def poi_exists(poi_name, examination=None):
    """
        Checks if a POI exists.

    Args:
        poi_name (str): the name of the POI
        examination (str, optional): the name of the examination (CT or StructureSet) for which the poi is defined; if left out the currently selected examination is used.

    Returns:
        True if it exists, False if not.

    """
    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()

    try:
        poi = [x for x in patient.PatientModel.StructureSets[examination.Name].PoiGeometries if x.OfPoi.Name == poi_name][0]
    except:
        return False

    if abs(poi.Point.x) == sys.float_info.max or abs(poi.Point.x) == sys.float_info.min:
        # Not segmented
        return False

    return True


def get_poi_approval(poi_name, examination=None):
    """
    Checks if POI named *poi_name* is approved (in any of the existing beamsets).

    TODO: handle the case where no beamsets or no plans exists, implying that
    the structures cannot be approved ?

    Args:
        poi_name (str): the name of the POI
        examination (str, optional): the name of the examination (CT or StructureSet) for which the poi is defined; if left out the currently selected examination is used.

    Returns:
        True if the POI is approved, False if not.
    """

    patient = lib.get_current_patient()

    if examination is None:
        examination = lib.get_current_examination()

    # print 'before'

    try:
        for beamset_approved_structure_set in patient.PatientModel.StructureSets[examination.Name].ApprovedStructureSets:
            for beamset_approved_pois in beamset_approved_structure_set.ApprovedPoiStructures:
                if beamset_approved_pois.OfPoi.Name == poi_name:
                    # print 'after True'
                    logger.info('POI %s is approved.', poi_name)
                    return True
        # print 'after False'
        logger.info('POI %s is NOT approved.', poi_name)
        return False
    except Exception as e:
        logger.exception(e)
        raise


def get_poi_coordinates(poi_name, examination=None):
    """
        Returns coordinates of POI poi_name in DICOM coordinate system.

        Args:
            poi_name (str): the name of the POI for which to get the coordinates
            examination (str, optional): the name of the examination (CT or StructureSet) for which the poi is defined; if left out the currently selected examination is used.

        Returns:
            RSPoint: the POI's DICOM coordinates in a RSPoint object
    """
    poi = get_poi(poi_name, examination)
    logger.info('POI %s: (x, y, z) = (%s, %s, %s)', poi_name, poi.Point.x, poi.Point.y, poi.Point.z)
    # poi.Point is a RayStation ExpandoObject

    return lib.RSPoint(point=poi.Point)
    # return dict(x=poi.Point.x, y=poi.Point.y, z=poi.Point.z)


def set_poi_coordinates(poi_name, point, examination=None):
    """
        Sets POI DICOM coordinates for POI poi_name to those specified in point.

        Args:
            point (RSPoint or RayStation ExpandoObject): the new DICOM coordinates of the point
    """
    if examination is None:
        examination = lib.get_current_examination()

    poi = get_poi(poi_name, examination=examination)

    # Need to check if POI is approved.  If it it, setting the coordinates
    # will crash RayStation.
    if get_poi_approval(poi_name):
        logger.warning('POI "%s" is approved and therefore cannot be changed.' % poi_name)
        return

    try:
        # ====================================================================
        # For some reason this doesn't update point coords !!
        # but also doesn't produce an error.
        # poi.Point.x = point.x
        # poi.Point.y = point.y
        # poi.Point.z = point.z
        # ====================================================================

        # ... but this does update the coordinates, also silently.
        poi.Point = {'x': point.x, 'y': point.y, 'z': point.z}
        logger.info('Set coordinates of POI "%s" to %s.', poi_name, point)
    except Exception as e:
        logger.exception(e)
        raise


def create_iso(exam=None):
    """
    Checks to see if a point named ISO exists. If not, the script creates a copy of REF SCAN to serve as the isocenter.

    Args:
        exam : RayStation examination object
    """
    if exam is None:
        exam = lib.get_current_examination()
    if not poi_exists("ISO", exam):
        if poi_exists("REF SCAN", exam):
            REF_SCAN_coords = get_poi_coordinates('REF SCAN', exam)
            create_poi(REF_SCAN_coords, 'ISO', 'Blue', 'Isocenter', exam)


def erase_pois_not_in_list(poi_list=None):

    patient = lib.get_current_patient()

    if poi_list is None:
        poi_list = ['ISO', 'REF SCAN']
    for poi in patient.PatientModel.PointsOfInterest:
        if not poi.Name.upper() in poi_list:
            poi.DeleteRoi()
