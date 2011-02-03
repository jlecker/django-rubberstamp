from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission
from rubberstamp.tests.testapp.models import TestModel
from rubberstamp.exceptions import PermissionLookupError
from rubberstamp.utils import get_permission_targets, get_app_list


class GetPermissionTargetsTest(RubberStampTestCase):
    """Tests for ``rubberstamp.utils.get_permission_targets``."""
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned_object.json']
    
    def test_none_assigned(self):
        user = User.objects.get(pk=2)
        self.assertEqual(len(get_permission_targets(
            'testapp.have.testapp.testmodel', user)), 0)
    
    def test_no_content_type(self):
        user = User.objects.get(pk=2)
        self.assertRaises(PermissionLookupError,
            get_permission_targets, 'testapp.use', user)
    
    def test_user_assigned(self):
        user = User.objects.get(pk=2)
        obj = TestModel.objects.get(pk=1)
        lst = get_permission_targets(
            'testapp.use.testapp.testmodel', user)
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], obj)
    
    def test_group_assigned(self):
        grouper = User.objects.get(pk=3)
        self.assertEqual(len(get_permission_targets(
            'testapp.use.testapp.testmodel', grouper)), 0)
        self.assertEqual(len(get_permission_targets(
            'testapp.have.testapp.testmodel', grouper)), 1)


class GetAppsTest(RubberStampTestCase):
    """Tests for ``rubberstamp.utils.get_apps_list``."""
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned_object.json']
    
    def setUp(self):
        tm_ct = ContentType.objects.get(app_label='testapp', model='testmodel')
        self.rs_perm = AppPermission.objects.create(
            app_label='rubberstamp',
            codename='manage'
        )
        self.rs_perm.content_types.add(tm_ct)
    
    def test_one_app(self):
        """A list of one item when user has perm in one app."""
        apps = get_app_list(User.objects.get(pk=2))
        self.assertEqual(len(apps), 1)
        self.assertTrue('testapp' in apps)
    
    def test_no_apps(self):
        apps = get_app_list(User.objects.get(pk=4))
        self.assertEqual(len(apps), 0)
    
    def test_all_apps(self):
        u = User.objects.get(pk=2)
        AppPermission.objects.assign('rubberstamp.manage.testapp.testmodel', u)
        apps = get_app_list(u)
        self.assertEqual(len(apps), 2)
        self.assertTrue(all(a in apps for a in ['testapp', 'rubberstamp']))


__all__ = (
    'GetPermissionTargetsTest',
    'GetAppsTest',
)
