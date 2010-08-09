from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.tests.testapp.models import TestModel


class AssignTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
        self.object_type = ContentType.objects.get_for_model(self.object)
        self.permission = AppPermission.objects.get(pk=1)
    
    def test_no_type_or_object(self):
        self.assertRaises(ValueError, AppPermission.objects.assign,
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
        self.assertRaises(ValueError, AppPermission.objects.assign,
            'testapp.use.testapp.testmodel', self.user, obj=newuser)
        self.assertFalse(AssignedPermission.objects.all().exists())


__all__ = ('AssignTest',)