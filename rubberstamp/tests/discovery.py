from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission
import rubberstamp

class DiscoveryTest(RubberStampTestCase):
    def test_discover_permissions(self):
        self.assertRaises(AppPermission.DoesNotExist,
            AppPermission.objects.get, app_label='testapp', codename='use_testmodel')
        rubberstamp.autodiscover()
        AppPermission.objects.get(app_label='testapp', codename='use_testmodel')


__all__ = ('DiscoveryTest',)