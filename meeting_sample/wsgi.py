"""
WSGI config for meeting_sample project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_sample.settings')

application = get_wsgi_application()

from delay_task.views import start_delay_task

start_delay_task()
