import os
import wpf

from System.Windows import Application, Window

thisdir = os.path.dirname(os.path.abspath(__file__))

def dialog():
    class MyWindow(Window):
        def __init__(self, vars):
            wpf.LoadComponent(self, thisdir+'/wpf_test.xaml')
        def OnClosing(self, event):
            vars[0] = self.tb1.Text
            vars[1] = self.tb2.Text
    vars = [None, None]
    Application().Run(MyWindow(vars))
    return tuple(vars)

if __name__ == '__main__':
    t1, t2 = dialog()
    print t1, t2
