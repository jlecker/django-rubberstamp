from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.tests.testapp.models import TestModel
from rubberstamp.exceptions import PermissionLookupError


class AssignTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_user_or_group(self):
        self.assertRaises(TypeError, AppPermission.objects.assign,
            'testapp.use.testapp.testmodel', None)


class AssignUserTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.use', self.user)
        self.assertFalse(AssignedPermission.objects.all().exists())
    
    def test_with_type(self):
        AppPermission.objects.assign('testapp.use.testapp.testmodel', self.user)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=None
        ).exists())
    
    def test_with_object(self):
        AppPermission.objects.assign('testapp.use', self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_with_both(self):
        AppPermission.objects.assign('testapp.use.testapp.testmodel',
            self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_mismatched(self):
        newuser = User.objects.create(username='a')
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.use.testapp.testmodel', self.user, obj=newuser)
        self.assertFalse(AssignedPermission.objects.all().exists())


class AssignGroupTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.group = Group.objects.get(pk=1)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.use', self.group)
        self.assertFalse(AssignedPermission.objects.all().exists())
    
    def test_with_type(self):
        AppPermission.objects.assign('testapp.use.testapp.testmodel', self.group)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=None
        ).exists())
    
    def test_with_object(self):
        AppPermission.objects.assign('testapp.use', self.group, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_with_both(self):
        AppPermission.objects.assign('testapp.use.testapp.testmodel',
            self.group, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_mismatched(self):
        newuser = User.objects.create(username='a')
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.use.testapp.testmodel', self.group, obj=newuser)
        self.assertFalse(AssignedPermission.objects.all().exists())


class AssignTestWithLongDottedCodename(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=3)
    
    def test_no_type_or_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.long.permission.name', self.user)
        self.assertFalse(AssignedPermission.objects.all().exists())
    
    def test_with_type(self):
        AppPermission.objects.assign('testapp.long.permission.name.testapp.testmodel', self.user)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=None
        ).exists())
    
    def test_with_object(self):
        AppPermission.objects.assign('testapp.long.permission.name', self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_with_both(self):
        AppPermission.objects.assign('testapp.long.permission.name.testapp.testmodel',
            self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 1)
        self.assertTrue(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_mismatched(self):
        newuser = User.objects.create(username='a')
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.long.permission.name.testapp.testmodel', self.user, obj=newuser)
        self.assertFalse(AssignedPermission.objects.all().exists())
    
    def test_bad_content_type(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.long.permission.name.noapp.nomodel', self.user)
        self.assertFalse(AssignedPermission.objects.all().exists())
    
    def test_bad_content_type_with_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.assign,
            'testapp.long.permission.name.noapp.nomodel', self.user, obj=self.object)
        self.assertFalse(AssignedPermission.objects.all().exists())


class RemoveUserTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned.json', 'assigned_object.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.remove,
            'testapp.use', self.user)
        self.assertEqual(AssignedPermission.objects.all().count(), 4)
    
    def test_with_type(self):
        AppPermission.objects.remove('testapp.use.testapp.testmodel', self.user)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=None
        ).exists())
    
    def test_with_object(self):
        AppPermission.objects.remove('testapp.use', self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_with_both(self):
        AppPermission.objects.remove('testapp.use.testapp.testmodel',
            self.user, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            user=self.user,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_mismatched(self):
        newuser = User.objects.create(username='a')
        self.assertRaises(PermissionLookupError, AppPermission.objects.remove,
            'testapp.use.testapp.testmodel', self.user, obj=newuser)
        self.assertEqual(AssignedPermission.objects.all().count(), 4)


class RemoveGroupTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json', 'assigned.json', 'assigned_object.json']
    
    def setUp(self):
        self.group = Group.objects.get(pk=1)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertRaises(PermissionLookupError, AppPermission.objects.remove,
            'testapp.have', self.group)
        self.assertEqual(AssignedPermission.objects.all().count(), 4)
    
    def test_with_type(self):
        AppPermission.objects.remove('testapp.have.testapp.testmodel', self.group)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=None
        ).exists())
    
    def test_with_object(self):
        AppPermission.objects.remove('testapp.have', self.group, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_with_both(self):
        AppPermission.objects.remove('testapp.have.testapp.testmodel',
            self.group, obj=self.object)
        self.assertEqual(AssignedPermission.objects.all().count(), 3)
        self.assertFalse(AssignedPermission.objects.filter(
            permission=self.permission,
            group=self.group,
            content_type=self.object_type,
            object_id=self.object.id
        ).exists())        
    
    def test_mismatched(self):
        newuser = User.objects.create(username='a')
        self.assertRaises(PermissionLookupError, AppPermission.objects.remove,
            'testapp.have.testapp.testmodel', self.group, obj=newuser)
        self.assertEqual(AssignedPermission.objects.all().count(), 4)


__all__ = (
    'AssignTest',
    'AssignUserTest',
    'AssignGroupTest',
    'AssignTestWithLongDottedCodename',
    'RemoveUserTest',
    'RemoveGroupTest'
)