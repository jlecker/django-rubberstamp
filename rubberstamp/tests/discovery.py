from django.contrib.auth.models import User

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission
import rubberstamp
from rubberstamp.tests.testapp.models import TestModel
from rubberstamp.tests.testapp import permissions as p


class DiscoveryTest(RubberStampTestCase):
    def setUp(self):
        self._original_permissions = p.permissions[:]
    
    def tearDown(self):
        p.permissions = self._original_permissions[:]

    def test_autodiscover_for_single_type(self):
        self.assertRaises(AppPermission.DoesNotExist,
            AppPermission.objects.get, app_label='testapp', codename='use')
        p.permissions = [
            ('use', 'Use this object', TestModel),
        ]
        rubberstamp.autodiscover()
        AppPermission.objects.get(app_label='testapp', codename='use')

    def test_autodiscover_for_multiple_types(self):
        self.assertRaises(AppPermission.DoesNotExist,
            AppPermission.objects.get, app_label='testapp', codename='use')
        p.permissions = [
            ('use', 'Use this object', (TestModel, User)),
        ]
        rubberstamp.autodiscover()
        perm = AppPermission.objects.get(app_label='testapp', codename='use')
        self.assertEqual(len(perm.content_types.all()), 2)


__all__ = ('DiscoveryTest',)