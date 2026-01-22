"""
ASGI CONFIGURATION FILE FOR CODEVOICE
USED BY ASGI SERVERS LIKE DAPHNE FOR ASYNCHRONOUS HANDLING LIKE WEBSOCKETS

"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application('DJANGO_SETTINGS_MODULE','config.settings')

application = get_asgi_application()