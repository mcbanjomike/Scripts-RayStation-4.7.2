import sys
import os.path
import setpath
import hmrlib.lib as lib

import clr
import System.Array

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Drawing import Color, Font, FontStyle, Point, Size
from System.Windows.Forms import (Application, BorderStyle, Button, CheckBox, Form, Label, Panel, RadioButton, ComboBox, TextBox)


def message_window(input = "Everything's fine"):

    class DebugWindow(Form):
        def __init__(self):
            self.Text = "Message"

            self.Width = 750
            self.Height = 750

            self.setupMessageWindow()
            self.setupOKButtons()

            self.Controls.Add(self.MessageWindow)
            self.Controls.Add(self.OKbuttonPanel)
            
        def bigPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 600
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel

        def miniPanel(self, x, y):
            panel = Panel()
            panel.Width = 750
            panel.Height = 150
            panel.Location = Point(x, y)
            panel.BorderStyle = BorderStyle.None
            return panel                           
            
        def setupMessageWindow(self):
            self.MessageWindow = self.bigPanel(0, 0)

            self.Label1 = Label()
            self.Label1.Text = input
            self.Label1.Location = Point(25, 25)
            self.Label1.Font = Font("Arial", 10)
            self.Label1.AutoSize = True
            
            self.MessageWindow.Controls.Add(self.Label1)

        def cancelClicked(self, sender, args):
            self.Close()

        def setupOKButtons(self):
            self.OKbuttonPanel = self.miniPanel(0, 600)
            
            cancelButton = Button()
            cancelButton.Text = "Cancel"
            cancelButton.Location = Point(25,25)
            self.CancelButton = cancelButton
            cancelButton.Click += self.cancelClicked

            self.OKbuttonPanel.Controls.Add(cancelButton)


    form = DebugWindow()
    Application.Run(form)   