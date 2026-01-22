"""
WSGI CONFIGURATION FILE FOR CODEVOICE
USED BY STANDARD WSGI SERVERS LIKE GUNICORN FOR SYNCHRONOUS HANDLING

"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
