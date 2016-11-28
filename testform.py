#!/usr/bin/ipy

import sys
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Application, Form, ToolBar
from System.Windows.Forms import ToolBarButton, ControlStyles, ColorDialog
from System.Windows.Forms import DialogResult
from System.Drawing import Size, Color, SolidBrush, Rectangle

RECT_WIDTH  = 100
RECT_HEIGHT = 100

class IForm(Form):

    def __init__(self):
        self.Text = "ColorDialog"

        self.color = Color.Blue

        toolbar = ToolBar()
        toolbar.Parent = self
        openb = ToolBarButton()

        toolbar.Buttons.Add(openb)
        toolbar.ButtonClick += self.OnClicked

        self.LocateRect()

        self.SetStyle(ControlStyles.ResizeRedraw, True)
        self.Paint += self.OnPaint
 
        self.CenterToScreen()
    
    
    def OnPaint(self, event):
        g = event.Graphics
        self.LocateRect()
        brush = SolidBrush(self.color)
        g.FillRectangle(brush, self.r)
    

    def OnClicked(self, sender, events):
        dialog = ColorDialog()

        if (dialog.ShowDialog(self) == DialogResult.OK):
            self.color = dialog.Color
            print self.color
            self.Invalidate()
       
    def LocateRect(self):
        x = (self.ClientSize.Width - RECT_WIDTH) / 2
        y = (self.ClientSize.Height - RECT_HEIGHT) / 2
        self.r = Rectangle(x, y, RECT_WIDTH, RECT_HEIGHT)
    
    
Application.Run(IForm())

