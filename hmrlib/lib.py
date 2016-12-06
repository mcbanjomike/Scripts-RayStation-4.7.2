# -*- coding: utf-8 -*-
"""
This module contains general utility functions and classes to be used with RayStation scripting.

**Only functions and classes not falling in one of these categories should be placed here:**

1.  Plan evaluation (isodose lines, clinical goals, etc.).  See :py:mod:`hmrlib.eval`.
2.  GUI (windows, buttons, etc. to interact with user).  See :py:mod:`hmrlib.gui`.
3.  Plan optimization (objectives, conversion settings, plan calculation, etc.). See :py:mod:`hmrlib.optim`.
4.  POI-related functions  See :py:mod:`hmrlib.poi`.
5.  ROI-related functions.  See :py:mod:`hmrlib.roi`.
6.  Patient QA (QA plan creation, calculation, planar doses).  See :py:mod:`hmrlib.qa`.
"""

import logging
import os.path
import System
import sys
import math
import datetime
from distutils.version import LooseVersion

from HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter
import poi

base_logger = logging.getLogger("hmrlib")
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


class RSScriptWrapper(object):

    """
        Wraps the execution of any script imported in RayStation.
        As convention, every script imported to RayStation should use this
        wrapper object around its code.

        This wrapper has two purposes:

        1.  It logs the start and end of every script launched in RayStation.
        2.  It prevents execution of the code if the script is launched from
            python and not IronPython, the latter we assume is connected to
            RayStation.  This is essential to use the python-sphinx autodoc
            feature, which is not connected to RayStation and therefore will
            produce errors.

        Typical usage for a script imported into RayStation is::

            import setpath
            import hmrlib.hmrlib as hmrlib
            with hmrlib.RSScriptWrapper(__file__):
                script_function_call_1_()
                script_function_call_2_()
                # ...
                script_function_call_n_()

        Args:
            script_name (str): the name, or file name, of the script that will execute.
    """

    def __init__(self, script_name):
        self.name = os.path.basename(script_name)
        self.inRS = 'IronPython' in sys.version

    def __enter__(self):
        if self.inRS:
            self.start = datetime.datetime.now()
            log_script_start(self.name)

    def __exit__(self, ttype, value, traceback):
        if self.inRS:
            log_script_end(self.name, execution_time=datetime.datetime.now() - self.start)
        else:
            # Next line suppresses any exception if running outside RayStation and
            # outside IronPython (i.e. with python and python-sphinx)
            return True


class RSPointArray(object):

    """
    **EXPERIMENTAL**

    Defines an array sequence upon which usual arithmetic operations
    can be performed.

    All elements of the sequence must be of the same type.
    These can be RSPoint objects, and will be handled accordingly.

    The object can be either initialized with a list of object
    or with a single object on its own.

    Args:
        p (list of RSPoint objects or list of dict) : the list of points to form the array
    """

    def __init__(self, p):
        if isinstance(p, list):
            type0 = type(p[0])
            if all(isinstance(x, type0) for x in p):
                self.points = p
                self.type = type0
            else:
                raise ValueError('List of heterogeneous types is not supported.')
        else:
            self.points = [p]
            self.type = type(p)

    def append(self, value):
        if type(value) == self.type:
            self.points.append(value)
        else:
            raise TypeError('Item must be of the same type as already present in the array.')

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        if type(value) == self.type:
            self.points[key] = value
        else:
            raise TypeError('Item must be of the same type as already present in the array.')

    def __delitem__(self, key):
        del self.points[key]

    def __iter__(self):
        return iter(self.points)

    def __reversed__(self):
        return RSPointArray(self.points[::-1])

    def __add__(self, other):
        if isinstance(other, self.__class__):
            if len(self) != len(other):
                raise ValueError('Arrays are not of same length.')
            new_points = []

            for s, o in zip(self.points, other.points):
                new_points.append(s + o)
            return RSPointArray(new_points)
        else:
            return RSPointArray([p + other for p in self.points])

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            if len(self) != len(other):
                raise ValueError('Arrays are not of same length.')
            new_points = []

            for s, o in zip(self.points, other.points):
                new_points.append(s - o)
            return RSPointArray(new_points)
        else:
            return RSPointArray([p - other for p in self.points])

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            raise ValueError('Only multiplying by scalar value is possible.')
        else:
            return RSPointArray([p * other for p in self.points])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, self.__class__):
            raise ValueError('Only dividing by scalar value is possible.')
        else:
            return RSPointArray([p / other for p in self.points])

    def __call__(self):
        if isinstance(self.points[0], RSPoint):
            return [p() for p in self.points]
        return self.points

    def __repr__(self):
        return '%s' % self.points


class RSPoint(object):

    """
    Defines a point that can be added, multiplied, etc. by other points.  The
    use of operators ('+', '-', '*', '/') is supported.

    Addition and substraction are possible both with a scalar value and another
    RSPoint object.  Multiplication and division are only possible with a scalar
    value.

    Can be initialized with three separate coordinates x, y, z
    OR with a single dictionary (point argument) in the RayStation
    format OR with another RSPoint object OR with a RayStation *ExpandoObject*,
    which has x, y and z attributes.

    Args:
        x (float, optional): the x coordinate
        y (float, optional): the y coordinate
        z (float, optional): the z coordinate
        point (dict or RSPoint or any object with x, y, z attributes, optional): the point with which to initialize the coordinates

    Either the x, y, z form may be used, or the point form to initialize the object.

    Attributes:
        x (float): the x coordinate (get/set).
        y (float): the y coordinate (get/set).
        z (float): the z coordinate (get/set).
        value (dict): the value of the point's coordinates stored in a dictionary using the 'x', 'y' and 'z' keys (get/set).  This is the same format as used by RayStation in various places for storing points.
    """

    def __init__(self, x=None, y=None, z=None, point=None):
        # Ensure either creation by specifying the 3 coordinates or a dict
        try:
            assert (point is None or all(v is None for v in [x, y, z]))
        except:
            error('Ambiguous RSPoint instantiation.  Instantiate using three x,y,z coordinates or another point object.')

        if (x is not None) and (y is not None) and (z is not None):
            # Instantiate with 3 coordinates
            self._x, self._y, self._z = float(x), float(y), float(z)
            self._value = {'x': x, 'y': y, 'z': z}
        elif point is not None:
            if isinstance(point, dict):
                # To support instantiating with dict
                self._value = point
            elif isinstance(point, self.__class__):
                # To support instantiating with other RSPoint
                self._value = point._value
            elif hasattr(point, 'x') and hasattr(point, 'y') and hasattr(point, 'z'):
                # To support instantiating with RS ExpandoObject or any object with x,y,z attributes
                self._value = {'x': point.x, 'y': point.y, 'z': point.z}
            else:
                raise TypeError('Could not understand argument "point".')

            self._x, self._y, self._z = self._value['x'], self._value['y'], self._value['z']
        else:
            raise TypeError('All arguments are None.')

    def __getitem__(self, c):
        """
        RSPoint objects can also be used in the same manner as a `dict`, by
        getting an item specified by a key.

        In this case, 'x', 'y' and 'z' keys are available.

        Returns:
            float: the value of the coordinate.
        """
        return self._value[c]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newvalue):
        self._value = newvalue
        self._x, self._y, self._z = newvalue['x'], newvalue['y'], newvalue['z']

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, newvalue):
        self._value = {'x': newvalue, 'y': self._y, 'z': self._z}
        self._x = newvalue

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, newvalue):
        self._value = {'x': self._x, 'y': newvalue, 'z': self._z}
        self._y = newvalue

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, newvalue):
        self._value = {'x': self._x, 'y': self._y, 'z': newvalue}
        self._z = newvalue

    def __round__(self, n):
        self._x = round(self._x, n)
        self._y = round(self._y, n)
        self._z = round(self._z, n)
        self._value = {'x': self._x, 'y': self._y, 'z': self._z}

    def __neg__(self):
        return RSPoint(-self._x, -self._y, -self._z)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return RSPoint(self._x + other._x, self._y + other._y, self._z + other._z)
        else:
            return RSPoint(self._x + other, self._y + other, self._z + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return RSPoint(self._x - other._x, self._y - other._y, self._z - other._z)
        else:
            return RSPoint(self._x - other, self._y - other, self._z - other)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            raise ValueError('Only multiplying by scalar value is possible.')
        else:
            return RSPoint(self._x * other, self._y * other, self._z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, self.__class__):
            raise ValueError('Only dividing by scalar value is possible.')
        else:
            return RSPoint(self._x / other, self._y / other, self._z / other)

    def __repr__(self):
        return "{'x':%.4f, 'y':%.4f, 'z':%.4f}" % (self._value['x'], self._value['y'], self._value['z'])


def error(msg):
    """
        Raise a RayStation SystemError exception with message `msg`, preceded
        by `hmrlib error:`.

        Args:
            msg (str): the message to display in the SystemError exception

        Raises:
            SystemError: will be detected by RayStation and `msg` displayed to the user.
    """
    raise SystemError('hmrlib error: ' + msg)


# VTL
def flush_logger_handlers():
    """
        Calls flush method on all handlers of the base_logger object of hmrlib.
    """
    # logger.handlers is not documented in python documentation,
    # but represents a list of all the logger's handlers.
    # We are looking for the BufferingHandler we added, but a priori we
    # don't know which object in the list it is.  It is this one we need to
    # flush.  However, flushing all handlers (assuming their flush method
    # actually does anything, should not hurt).
    for h in base_logger.handlers:
        try:
            h.flush()
        except Exception as e:
            logger.exception(e)


def log_script_start(script):
    """
        Logs the start of a script.

        Per convention, should ALWAYS be called at the start of a script.
        This is handled by using a RSScriptWrapper object.

        Args:
            script (str): The filename or path of the script that starts.
    """
    logger.info('=' * 80)
    logger.info('Starting script ' + os.path.basename(script))
    logger.info('=' * 80)


def log_script_end(script, execution_time=None):
    """
        Logs the end of a script.

        Per convention, should ALWAYS be called at the end of a script.
        This is handled by using a RSScriptWrapper object.

        Args:
            script (str): The filename or path of the script that ends.
    """
    logger.info('=' * 80)
    logger.info('End of script ' + os.path.basename(script) + ((' [execution time = %s]' % execution_time) if execution_time else ''))
    logger.info('=' * 80)
    flush_logger_handlers()


# VTL
def is_number(s, accept_null=False, reject_signs=True):
    """
        Returns whether `s` can be represented as a number or not.

        By default, rejects strings that contain signs '+', '-'.
        By default, considers ',' a valid decimal separator.

        Args:
            s (str): the string to test
            accept_null (bool, optional): whether or not to accept null string '' as a valid reprentation of a number (or, rather, the absence of any number)
            reject_signs (bool, optional): whether or not to reject sign symbols as a valid part of the string representation of a number

        Returns:
            bool: True is `s` can be represented as a number, False if not.
    """
    if '+' in s or '-' in s:
        return False
    if ',' in s:
        s = s.replace(',', '.')
    if s == '' and accept_null:
        return True
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_version(versionnumber, strict=False):
    """
        Returns True if the latest patient modification's software version
        is greater or equal to the specified version number.

        Args:
            versionnumber (str or float): the version number to compare to
            strict (bool): if True, will check for equality rather than just
                            greater or equal.
    """

    if isinstance(versionnumber, float):
        versionnumber = str(versionnumber)

    # For example: C:\Program Files\RaySearch Laboratories\RayStation 4.7.2\ScriptClient
    version = System.IO.Path.GetDirectoryName(sys.argv[0]).split('RayStation')[-1].split('\\')[0].replace(' ', '')
    logger.debug('Detected software version %s.', version)

    if strict:
        return LooseVersion(version) == LooseVersion(versionnumber)
    else:
        return LooseVersion(version) >= LooseVersion(versionnumber)


def get_current_beamset():
    """
        Returns the currently selected beamset in RayStation.

        If no beamset is selected, a `SystemError` is raised.

        Returns:
            The beamset object.
    """
    try:
        return get_current('BeamSet')
    except SystemError as e:
        logger.exception(e)
        logger.error('Could not get current beamset.  No beamset selected or no beamset exists ?')
        raise


def get_current_plan():
    """
        Returns the currently selected plan in RayStation.

        If no plan is selected, a `SystemError` is raised.

        Returns:
            The plan object.
    """
    try:
        return get_current('Plan')
    except SystemError as e:
        logger.exception(e)
        logger.error('Could not get current plan.  No plan is currently selected ?')
        raise


def get_current_patient():
    """
        Returns the currently selected patient in RayStation.

        If no patient is selected, a `SystemError` is raised.

        Returns:
            The patient object.
    """
    try:
        return get_current('Patient')
    except SystemError as e:
        logger.exception(e)
        logger.error('Could not get current patient.  No patient is currently selected ?')
        raise


def get_current_examination():
    """
        Returns the currently selected examination (e.g. CT) in RayStation.

        If no examination is selected, a `SystemError` is raised.

        Returns:
            The examination object.
    """
    try:
        return get_current('Examination')
    except SystemError as e:
        logger.exception(e)
        logger.error('Could not get current examination.')
        raise


def identify_ptvs_old():
    patient = get_current_patient()
    roi_names = [x.Name for x in patient.PatientModel.RegionsOfInterest]
    ptvs = []
    for rr in roi_names:
        rr = rr.replace(' ', '').upper()
        if rr == 'PTV':
            ptvs.append(rr)
            continue
        if '+' in rr:
            continue
        if rr.startswith('PTV'):
            try:
                float(rr[3:])
                ptvs.append(rr)
                continue
            except ValueError:
                continue


def get_prescription_dose(beamset=None):
    """
    Returns the prescription value for the current beamset.

    Args:
        beamset (object, optional) : the RayStation beamset object

    Returns:
        float: the prescription dose in cGy

    """

    if beamset is None:
        beamset = get_current_beamset()

    try:
        return float(beamset.Prescription.PrimaryDosePrescription.DoseValue)
    except Exception as e:
        logger.exception(e)
        raise


# VTL
def get_fractions(beamset=None):
    """
    Returns the number of fractions for the current beamset.

    Args:
        beamset (object, optional) : the RayStation beamset object

    Returns:
        int: the number of fractions
    """
    if beamset is None:
        beamset = get_current_beamset()

    try:
        return int(beamset.FractionationPattern.NumberOfFractions)
    except Exception as e:
        logger.exception(e)
        raise


# VTL
def point(x, y, z):
    """
        Returns a point in the dictionary form used by RayStation.

        Args:
            x (float): the DICOM x-coordinate
            y (float): the DICOM y-coordinate
            z (float): the DICOM z-coordinate

        Returns:
            dict: a dictionary containing the keys 'x', 'y' and 'z', with the appropriate DICOM coordinates.  This is the format used by RayStation.
    """
    return dict(x=x, y=y, z=z)


def unit_vector(v):
    """
    Returns a unit vector for the vector *v*.

    Args:
        v (RSPoint or RayStation ExpandoObject): a vector

    Returns:
        RSPoint: a unit vector in the direction of *v*
    """
    norm = math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
    return RSPoint(v.x, v.y, v.z) / norm


# VTL
def add_beamset(name, machine_name, fractions, treatment_technique='VMAT', energy=6, modality='Photons', setup_beams=False):
    """
        TODO: implement.
    """
    pass


# VTL
def add_arc(name, iso_poi_name, start, stop, direction, description='', energy=6, collimator=0.0, couch=0.0, exam=None, beamset=None):
    """
    Adds an arc to the current beamset.

    Args:
        name (str): the name of the arc
        iso_poi_name (str): the name of the isocenter POI
        start (float): start angle in degrees of the arc
        stop (float): stop angle in degrees of the arc
        direction (str): one of *CW* or *CCW*
        description (str, optional): the description of the arc (default: none)
        energy (int, optional): the energy in MV of the beam (default: 6)
        collimator (float, optional): the angle in degrees of the collimator angle (default: 0.0)
        couch (float, optional): the angle in degrees of the couch angle (default: 0.0)
        examination (RS object, optional): the examination RayStation object (will get current if none specified)
        beamset (RS object, optional): the beamset RayStation object (will get current if none specified)

    Returns:
        the RayStation arc object
    """
    dir_dict = dict(CW="Clockwise", CCW="Counterclockwise")

    try:
        if beamset is None:
            beamset = get_current_beamset()
        logger.info('Beam Set = %s', beamset)

        if exam is None:
            exam = get_current_examination()
        logger.info('Exam = %s', exam.Name)

        # with CompositeAction('Add beam (%s, Beam Set: %s)' % (name, beam_set.DicomPlanLabel)):
        # Must use RSPoint.value to get dictionary form of the point else cryptic IronPython error...
        beamset.CreateArcBeam(Name=name,
                              Description=description,
                              Isocenter=poi.get_poi_coordinates(iso_poi_name, examination=exam).value,
                              GantryAngle=start,
                              ArcStopGantryAngle=stop,
                              ArcRotationDirection=dir_dict[direction],
                              Energy=6,
                              CollimatorAngle=collimator,
                              CouchAngle=couch,
                              ApertureBlock=None)
        # retval_0.SetBolus(BolusName="")
        # logger.info('Added arc "%s" from %s to %s in direction %s with isocenter %s.  Energy = %s, collimator = %s, couch = %s.' %
        # (name, start, stop, direction, iso_poi_name, energy, collimator, couch))
    except Exception as e:
        logger.exception(e)
        raise

    logger.info('Added arc "%s" from %s to %s in direction %s with isocenter %s.  Energy = %s, collimator = %s, couch = %s.' %
                (name, start, stop, direction, iso_poi_name, energy, collimator, couch))
    # return retval_0


def print_screenshot(printer_name='CutePDF Writer'):
    """
        Grabs a screenshot and prints it on a printer.

        Args:
            printer_name (str, optional) : the name of the printer to print to (default *CutePDF Writer*)
    """
    import clr

    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")
    # clr.AddReference("System.Drawing.Printing")

    from System.Drawing import Bitmap
    from System.Windows.Forms import (
        Screen, PrintDialog
    )
    from System.Drawing.Printing import PrintDocument, PaperSize, PrinterResolution, StandardPrintController

    # Handler for print event sent by PrintDocument object
    def on_print(sender, event):
        # Get screenshot
        bmp = Bitmap(Screen.PrimaryScreen.Bounds.Width, Screen.PrimaryScreen.Bounds.Height, event.Graphics)
        event.Graphics.CopyFromScreen(0, 0, 0, 0, bmp.Size)

    print_doc = PrintDocument()
    # connect handler to print event
    print_doc.PrintPage += on_print

    print_diag = PrintDialog()
    print_diag.Document = print_doc

    print_doc.DocumentName = get_current_patient().PatientName
    print_doc.PrinterSettings.PrinterName = printer_name
    print_doc.OriginAtMargins = True
    print_doc.DefaultPageSettings.Landscape = True

    papersize = PaperSize("custom size", 1667, 2667)
    print_doc.DefaultPageSettings.PaperSize = papersize

    pres = PrinterResolution()
    pres.X = 72
    pres.Y = 72
    print_doc.DefaultPageSettings.PrinterResolution = pres

    # To disable printing status popup which shows on screenshot
    print_doc.PrintController = StandardPrintController()

    # To print withtout dialog
    print_doc.Print()

    # To popup print dialog
    # if print_diag.ShowDialog() == DialogResult.OK:
    #     print_doc.Print()

    
#Simple function to convert user ID into user name    
def get_user_name(user_ID):
    d = dict(hmr0434 = 'Kathleen Ratelle',
             hmr0502 = 'Caroline Duchesne',
             hmr0624 = 'Brigitte Trudeau',
             hmr0853 = 'Anne-Marie Locat',
             hmr1078 = 'Laurent Tantôt',
             hmr1575 = 'Marie Boisvert',
             hmr1627 = 'Patrice Munger',
             hmr2176 = 'Richard Plourde',
             hmr2282 = 'Isabelle Blanchette',
             hmr2605 = 'Étienne Roussin',
             hmr3483 = 'Dominique Martin',
             hmr3992 = 'Geneviève Jarry',
             hmr4182 = 'Julie St-Pierre',
             hmr5552 = 'Matthieu Lemire',
             hmr6320 = 'Maxime Lachance',
             hmr7191 = 'Stéphane Généreux',
             hmr30489 = 'Michael Ayles',
             hmr30507 = 'Christophe Furstoss',
             hmr33707 = 'Rafael Khatchadourian',
             laurie = 'Laurie Archambault',
             vleduc = 'Vincent Leduc')
             #Add other users here as needed

    try:
        return d[user_ID]
    except:
        return "Aucun usager avec ce numéro d'identification"
