from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

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


class PermissionsTest(RubberStampTestCase):
    def test_rubberstamp_permissions(self):
        ap_ct = ContentType.objects.get_for_model(AppPermission)
        rubberstamp.autodiscover()
        
        perms = AppPermission.objects.all()
        self.assertEqual(perms.count(), 1)
        
        types = perms.get(codename='manage').content_types.all()
        self.assertTrue(ap_ct in types)
        self.assertEqual(len(types), 1)


__all__ = ('DiscoveryTest', 'PermissionsTest')
