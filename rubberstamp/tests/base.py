import os

from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase


class RubberStampTestCase(TestCase):
    def _pre_setup(self):
        self._original_template_dirs = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = list(settings.TEMPLATE_DIRS)
        settings.TEMPLATE_DIRS.append(os.path.join(os.path.dirname(__file__), 'templates'))
        
        self._original_fixture_dirs = settings.FIXTURE_DIRS
        settings.FIXTURE_DIRS = list(settings.FIXTURE_DIRS)
        settings.FIXTURE_DIRS.append(os.path.join(os.path.dirname(__file__), 'fixtures'))
        
        self._original_installed_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS.append('rubberstamp.tests.testapp')
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=0)
        
        self._original_auth_backends = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = list(settings.AUTHENTICATION_BACKENDS)
        settings.AUTHENTICATION_BACKENDS.append('rubberstamp.backends.AppPermissionBackend')
        
        super(TestCase, self)._pre_setup()
    
    def _post_teardown(self):
        super(TestCase, self)._post_teardown()
        settings.AUTHENTICATION_BACKENDS = self._original_auth_backends
        settings.INSTALLED_APPS = self._original_installed_apps
        settings.FIXTURE_DIRS = self._original_fixture_dirs
        settings.TEMPLATE_DIRS = self._original_template_dirs
        loading.cache.loaded = False
