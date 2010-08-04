import os

from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase


class RubberStampTestCase(TestCase):
    def _pre_setup(self):
        self._original_installed_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS.append('rubberstamp.tests.testapp')
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=0)
        
        super(TestCase, self)._pre_setup()
    
    def _post_teardown(self):
        super(TestCase, self)._post_teardown()
        settings.GEYSER_PUBLISHABLES = self._original_geyser
        settings.INSTALLED_APPS = self._original_installed_apps
        loading.cache.loaded = False