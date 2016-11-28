# -*- coding: utf-8 -*-
"""
This module contains anything related to GUI windows.

All .xaml files specifying the layout, widgets, etc. of the windows should be placed under the sub-directory ./gui.
"""

import os
import os.path

from lib import *

import logging
from HMR_RS_LoggerAdapter import HMR_RS_LoggerAdapter

base_logger = logging.getLogger("hmrlib." + os.path.basename(__file__)[:-3])
""" The basic logger object used for logging in hmrlib.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

logger = HMR_RS_LoggerAdapter(base_logger)
""" The basic logger object adapted with an HMR_RS_LoggerAdapter.
It was loaded in memory by python-sphinx, which is why you see the object's address!"""

try:
    import wpf
    from System.Windows import Application, Window
except:
    pass

thisdir = os.path.dirname(os.path.abspath(__file__))
gui_path = thisdir + '/gui/'


def show_log_window(log):
    class MyWindow(Window):

        def __init__(self, log):
            wpf.LoadComponent(self, gui_path + 'log_window.xaml')
            self.logbox.Text = log

        def OnClosing(self, event):
            self.Topmost = False

    MyWindow.Topmost = True
    Application().Run(MyWindow(log))
    MyWindow.Topmost = True

if __name__ == '__main__':
    show_log_window('Ceci est un test.')


def yes_no_dialog(msg):
    """
        **TO BE IMPLEMENTED**

        Pops up a yes/no dialog with msg displayed as message.

        Args:
            msg (str): the message to display in the popup

        Returns:
            bool: True for yes, False for no
    """
    raise NotImplementedError
