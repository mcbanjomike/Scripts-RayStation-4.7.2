import os, sys, System

#ipyInstallPath = System.IO.Path.GetDirectoryName(System.Environment.GetCommandLineArgs()[0])
scriptInstallPath = System.IO.Path.GetDirectoryName(sys.argv[0])
os.chdir(scriptInstallPath)

#ironpython = r'\"' + ipyInstallPath + r'\ipy.exe\"'
#ironpythonargs = '-X:TabCompletion -X:ColorfulConsole -X:AutoIndent'

#setenv1 = 'set IRONPYTHONSTARTUP=console_startup.py'
#setenv2 = 'set RAYSTATION_PID="{0}"'.format(sys.argv[1])

#title = 'RayStation Command Console'

#consolecmd = 'Tools\Console2\Console.exe -w "{0}" -r "/k {1} & {2} & ({3} {4})"'.format(title, setenv1, setenv2, ironpython, ironpythonargs)
#os.system(consolecmd)


import subprocess

pid = subprocess.Popen('Tools\Console2\Console.exe').pid










