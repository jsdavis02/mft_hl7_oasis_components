"""
WSGI config for oasis_ui project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import signal
import sys
import traceback
import time

from django.core.wsgi import get_wsgi_application
sys.path.append('/opt/oasis_py_ui')
# adjust the Python version in the line below as needed 
sys.path.append('/bin/python3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oasis_ui.settings')

try:
    application = get_wsgi_application()
except Exception:
    # Error loading applications 
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
        