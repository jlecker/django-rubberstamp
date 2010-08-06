from django.contrib.auth.models import User

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission
from rubberstamp.tests.testapp.models import TestModel


class AssignTest(RubberStampTestCase):
    fixtures = ['users.json', 'objects.json', 'permissions.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.object = TestModel.objects.get(pk=1)
    
    def test_assign_via_manager(self):
        # with type in perm, with object
        AppPermission.objects.assign('testapp.use.testapp.testmodel', self.user, obj=self.object)
        
        # no type in perm, with object
        AppPermission.objects.assign('testapp.use', self.user, obj=self.object)
        
        # with type in perm, no object
        AppPermission.objects.assign('testapp.use.testapp.testmodel', self.user)
        
        # no type in perm, no object
        self.assertRaises(ValueError, AppPermission.objects.assign, 'testapp.use', self.user)
        
        # with type in perm, with object, mismatched
        newuser = User.objects.create(username='a')
        self.assertRaises(ValueError, AppPermission.objects.assign, 'testapp.use.testapp.testmodel', self.user, obj=newuser)


__all__ = ('AssignTest',)