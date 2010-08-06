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
        AppPermission.objects.assign('testapp.use_testmodel', self.user, obj=self.object)


__all__ = ('AssignTest',)