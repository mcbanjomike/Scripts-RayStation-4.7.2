#-*- coding: utf-8 -*-
"""
    Appends location of RayStation scripts to the system path.

    - Departements/Physiciens/TPS/RayStation/Scripts.<username> is used for testing/development.
    - Departements/Physiciens/TPS/RayStation/Scripts is used for the production clinical database.

    Therefore, the code of this file is not the same for development and production environments.
"""

import sys
import os

if os.path.isdir('//radonc.hmr/Departements/Physiciens/TPS/RayStation/Scripts.%s' % os.getenv('USERNAME')):
    sys.path.append('//radonc.hmr/Departements/Physiciens/TPS/RayStation/Scripts.%s' % os.getenv('USERNAME'))
else:
    sys.path.append('//radonc.hmr/Departements/Physiciens/TPS/RayStation/Scripts')

print 'Path = %s' % sys.path