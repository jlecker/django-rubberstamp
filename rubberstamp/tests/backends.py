from django.contrib.auth.models import User
from rubberstamp.tests.base import RubberStampTestCase

from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.tests.testapp.models import TestModel


class BackendTestNoneAssigned(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertFalse(self.user.has_perm('testapp.use'))
    
    def test_with_type(self):
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel'))
    
    def test_with_object(self):
        self.assertFalse(self.user.has_perm('testapp.use', obj=self.object))
    
    def test_with_both(self):
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.object))
    
    def test_with_both_mismatched(self):
        self.assertFalse(self.user.has_perm('testapp.use.auth.user', obj=self.object))
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.user))
    
    def test_has_module_perms(self):
        self.assertFalse(self.user.has_module_perms('testapp'))
    
    def test_get_all(self):
        self.assertEqual(len(self.user.get_all_permissions()), 0)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.object)), 0)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.user)), 0)


class BackendTestTypeAssigned(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertFalse(self.user.has_perm('testapp.use'))
    
    def test_with_type(self):
        self.assertTrue(self.user.has_perm('testapp.use.testapp.testmodel'))
    
    def test_with_object(self):
        self.assertFalse(self.user.has_perm('testapp.use', obj=self.object))
    
    def test_with_both(self):
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.object))
    
    def test_with_both_mismatched(self):
        self.assertFalse(self.user.has_perm('testapp.use.auth.user', obj=self.object))
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.user))
    
    def test_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms('testapp'))
    
    def test_get_all(self):
        self.assertEqual(len(self.user.get_all_permissions()), 1)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.object)), 0)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.user)), 0)


class BackendTestObjectAssigned(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned_object.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertFalse(self.user.has_perm('testapp.use'))
    
    def test_with_type(self):
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel'))
    
    def test_with_object(self):
        self.assertTrue(self.user.has_perm('testapp.use', obj=self.object))
    
    def test_with_both(self):
        self.assertTrue(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.object))
    
    def test_with_both_mismatched(self):
        self.assertFalse(self.user.has_perm('testapp.use.auth.user', obj=self.object))
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.user))
    
    def test_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms('testapp'))
    
    def test_get_all(self):
        self.assertEqual(len(self.user.get_all_permissions()), 1)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.object)), 1)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.user)), 0)


class BackendTestBothAssigned(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned.json', 'assigned_object.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertFalse(self.user.has_perm('testapp.use'))
    
    def test_with_type(self):
        self.assertTrue(self.user.has_perm('testapp.use.testapp.testmodel'))
    
    def test_with_object(self):
        self.assertTrue(self.user.has_perm('testapp.use', obj=self.object))
    
    def test_with_both(self):
        self.assertTrue(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.object))
    
    def test_with_both_mismatched(self):
        self.assertFalse(self.user.has_perm('testapp.use.auth.user', obj=self.object))
        self.assertFalse(self.user.has_perm('testapp.use.testapp.testmodel', obj=self.user))
    
    def test_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms('testapp'))
    
    def test_get_all(self):
        self.assertEqual(len(self.user.get_all_permissions()), 1)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.object)), 1)
        self.assertEqual(len(self.user.get_all_permissions(obj=self.user)), 0)


__all__ = (
    'BackendTestNoneAssigned',
    'BackendTestTypeAssigned',
    'BackendTestObjectAssigned',
    'BackendTestBothAssigned',
)