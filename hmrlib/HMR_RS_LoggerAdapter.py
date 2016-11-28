from logging import LoggerAdapter
from os import getenv

# To allow importation of module by sphinx-python
try:
    from connect import get_current
except:
    pass


class HMR_RS_LoggerAdapter(LoggerAdapter):

    """
        Imparts contextual information on any RayStation scripting log message.

        - Currently selected patient name
        - Currently selected patient ID
        - Currently selected plan name
        - Currently selected examination
        - Currently selected beamset
        - Currently logged in user (username) from Windows environment variable

        Derives from :py:class:`logging.LoggerAdapter`.

        Args:
            logger (:py:class:`logging.Logger`): the logger to adapt.

        Inheritance diagram:

        .. inheritance-diagram:: hmrlib.HMR_RS_LoggerAdapter.HMR_RS_LoggerAdapter
    """

    def __init__(self, logger):
        super(HMR_RS_LoggerAdapter, self).__init__(logger, None)

    def get_current(self):
        try:
            patient = get_current('Patient')
            self.patient_name = patient.PatientName.replace(' ', '^')
            self.patient_id = patient.PatientID
        except SystemError:
            self.patient_name = '<No patient selected>'
            self.patient_id = '<No patient ID>'
        except NameError:
            # to allow python-sphinx to process this code when not connected
            # to RayStation
            pass

        try:
            plan = get_current('Plan')
            self.plan_name = plan.Name
        except SystemError:
            self.plan_name = '<No plan selected>'
        except NameError:
            # to allow python-sphinx to process this code when not connected
            # to RayStation
            pass

        try:
            beamset = get_current('BeamSet')
            self.beamset_name = beamset.DicomPlanLabel
        except SystemError:
            self.beamset_name = '<No beamset selected>'
        except NameError:
            # to allow python-sphinx to process this code when not connected
            # to RayStation
            pass

        try:
            exam = get_current('Examination')
            self.exam_name = exam.Name
        except SystemError:
            self.exam_name = '<No examination selected>'
        except NameError:
            # to allow python-sphinx to process this code when not connected
            # to RayStation
            pass

        try:
            self.user = getenv('USERNAME')

            self.extra = {
                'user': self.user,
                'patient': self.patient_name,
                'patient_id': self.patient_id,
                'plan': self.plan_name,
                'beamset': self.beamset_name,
                'examination': self.exam_name
            }
        except:
            pass

    def process(self, msg, kwargs):
        self.get_current()
        kwargs['extra'] = self.extra
        # return '[%s - %s (%s) - %s - %s/%s] %s' % (self.user, self.patient_name, self.patient_id, self.exam_name, self.plan_name, self.beamset_name, msg), kwargs
        return msg, kwargs
