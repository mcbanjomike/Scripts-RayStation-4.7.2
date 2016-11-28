# -*- coding: utf-8 -*-
r"""
Introduction
------------
:py:mod:`hmrlib` is a collection of functions that perform various operations in
RayStation via the scripting interface.

The module is divided into multiple sub-modules:

1.  General functions not falling into a specific category -- :py:mod:`hmrlib.lib`.
2.  Plan evaluation (isodose lines, clinical goals, etc.) -- :py:mod:`hmrlib.eval`.
3.  GUI (windows, buttons, etc. to interact with user) -- :py:mod:`hmrlib.gui`.
4.  Plan optimization (objectives, conversion settings, plan calculation, etc.) -- :py:mod:`hmrlib.optim`.
5.  POI-related functions -- :py:mod:`hmrlib.poi`.
6.  ROI-related functions -- :py:mod:`hmrlib.roi`.
7.  Patient QA (QA plan creation, calculation, planar doses) -- :py:mod:`hmrlib.qa`.

Basics
^^^^^^
In RayStation, scripts made available to the user must be recorded imported
and stored in the RayStation database before they can be used.  This makes
developing and maintaining code difficult, as any change requires that a user
re-imports a script in RayStation (RS).

However, if most of the code is stored in an external file, then we need only
import short scripts to the RS database that call code contained in the
external file.

Indeed, if the :py:mod:`hmrlib` module is imported, then all of its functions will
be available to RS.  It requires only a simple script to be imported that sets
the python path correctly, so that :py:mod:`hmrlib` can be found.  This script
is called :py:mod:`setpath` and is already should be saved in the RayStation
database.

It should also add the correct directory to the system path.  For the production
(clinical) database, it should point to `\\\\radonc.hmr\\Departements\\Physiciens\\TPS\\RayStation\\Scripts`
directory.  For the development environment running in a test database of RayStation, it should point to
`\\\\radonc.hmr\\Departements\\Physiciens\\TPS\\RayStation\\Scripts.dev`.
A mercurial repository is present in both directories and `Scripts` should be
periodically synchronized with `Scripts.dev`, whenever the scripts in the development
location are deemed stable and ready for use.

Logging
^^^^^^^
Whenever :py:mod:`hmrlib` is imported, its `__init__` file is executed.  This sets
up logging.  The standard python library logging module is used.

File handler
''''''''''''
A :py:class:`logging.handlers.RotatingFileHandler` is used to record logs in a file called `hmrlib.log`, in
the base directory of the hmrlib module.

Memory handler
''''''''''''''
A custom class deriving from :py:class:`logging.handlers.MemoryHandler` is used to
commit to memory.  After script execution, any errors and warnings can thus be
displayed in a GUI window.  This happens when the handler's flush method is
called.

Logging adapter
'''''''''''''''
A custom class deriving from :py:class:`logging.LoggerAdapter` is used to impart
contextual information in the logs.  For every event, this adapter allows the
recording of the current user, current selected patient and current selected
plan.  See :py:class:`hmrlib.__init__.HMR_RS_Log_Handler`.
"""

# logging setup start ########################################################
import os
import sys
import logging
import logging.handlers
# from log_io_handler import LogIOHandler
import logstash
import gui

# To allow importation of module by sphinx-python
# try:
#     from HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter
# except Exception as e:
#     if not 'IronPython' in sys.version:
#         pass
#     else:
#         raise

logging.getLogger().setLevel(0)
logger = logging.getLogger("hmrlib")

thisdir = os.path.dirname(os.path.abspath(__file__))

try:
    # create rotating file handler
    handler = logging.handlers.RotatingFileHandler(thisdir + '/../hmrlib.log',
                                                   maxBytes=2000000, backupCount=5)

    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # This formatter uses extra fields passed to the handler from the
    # LoggerAdapter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(user)s - %(patient)s (%(patient_id)s) - %(examination)s - %(plan)s/%(beamset)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except IOError as e:
    # create stream handler instead
    # handler = logging.StreamHandler()
    print str(e)
except Exception as e:
    pass

# logstash handler (kibana 4, elasticsearch 1.5)
try:
    handler = logstash.TCPLogstashHandler(
        '11.1.5.231', (5546 if 'Scripts.' in thisdir else 5545), version=1, message_type='raystation' + ('.dev' if 'Scripts.' in thisdir else ''))
    handler.retryMax = 10.0
    logger.addHandler(handler)
except Exception as e:
    pass


class HMR_RS_Log_Handler(logging.handlers.MemoryHandler):

    """
        Custom log handler deriving from :py:class:`logging.handlers.MemoryHandler`,
        which itself derives from :py:class:`logging.handlers.BufferingHandler`.

        The :py:meth:`logging.handlers.BufferingHandler.emit` method and the
        :py:meth:`logging.handlers.MemoryHandler.flush` method are overridden
        to customize the format of log messages and pop up a window with the
        .NET wpf/xaml interface upon flushing the logger buffer.

        Parameters:
            args : see :py:class:`logging.handlers.MemoryHandler`.

        Inheritance diagram:

        .. inheritance-diagram:: hmrlib.__init__.HMR_RS_Log_Handler
    """

    def emit(self, record):
        super(HMR_RS_Log_Handler, self).emit(record)

        # This will also print log message in RayStation
        # execution details.
        print self.format(record)

    def flush(self):
        formatted_records = [self.format(record) for record in self.buffer]
        log = '\n'.join([record for record in formatted_records])

        if len(formatted_records) > 0:
            print '=' * 80
            print "Messages from script execution log:"
            print
            print log
            print '=' * 80
            # gui.show_log_window(log)

        # Flush buffer
        self.buffer = []

try:
    handler = HMR_RS_Log_Handler(2 * 1024 ** 2)
    handler.setFormatter(formatter)
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)
except Exception as e:
    if 'IronPython' not in sys.version:
        pass
    else:
        raise

logger.setLevel(logging.INFO)

# To allow importation of module by sphinx-python
# try:
#     adapter = HMR_RS_LoggerAdapter(logger)
#     adapter.info('Logging ready.')
# except Exception as e:
#     if not 'IronPython' in sys.version:
#         pass
#     else:
#         raise

# logging setup end ##########################################################
