from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rubberstamp.tests.base import RubberStampTestCase
from rubberstamp.models import AppPermission
from rubberstamp.tests.testapp.models import TestModel


class ViewTest(RubberStampTestCase):
    fixtures = ['users.json', 'view_objects.json', 'view_permissions.json']
    urls = 'rubberstamp.tests.testurls'
    
    def setUp(self):
        self.user = User.objects.get(username='user')
    
    def test_app_list(self):
        xr = self.client.get('/')
        self.assertEqual(xr.status_code, 302)
        
        self.client.login(username='user', password='')
        xr = self.client.get('/')
        self.assertEqual(xr.status_code, 302)
        
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        
        # app perms should be a list of tuples like
        # [('app_label', ['codename', 'codename', ...]), ...]
        ap = r.context['app_perms']
        self.assertEqual(len(ap), 2)
        rp = ap[0]
        self.assertEqual(rp[0], 'rubberstamp')
        self.assertEqual(len(rp[1]), 1)
        self.assertEqual(rp[1][0], 'manage')
        tp = ap[1]
        self.assertEqual(tp[0], 'testapp')
        self.assertEqual(len(tp[1]), 2)
        self.assertTrue(all(c in tp[1] for c in ['use', 'have']))
    
    def test_type_list_for_perm(self):
        xr = self.client.get('/testapp.not/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use/')
        self.assertEqual(xr.status_code, 302)
        
        self.client.login(username='user', password='')
        xr = self.client.get('/testapp.not/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use/')
        self.assertEqual(xr.status_code, 302)
        
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        xr = self.client.get('/testapp.not/')
        self.assertEqual(xr.status_code, 404)
        r = self.client.get('/testapp.use/')
        self.assertEqual(r.status_code, 200)
        
        type_list = r.context['types']
        self.assertEqual(len(type_list), 2)
        tm_ct = ContentType.objects.get(app_label='testapp', model='testmodel')
        self.assertTrue(tm_ct in type_list)
        otm_ct = ContentType.objects.get(app_label='testapp', model='othertestmodel')
        self.assertTrue(otm_ct in type_list)
    
    def test_type_to_user(self):
        xr = self.client.get('/testapp.use.testapp.nomodel/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/')
        self.assertEqual(xr.status_code, 302)
        
        self.client.login(username='user', password='')
        # logged in, but without correct perm
        xr = self.client.get('/testapp.use.testapp.nomodel/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/')
        self.assertEqual(xr.status_code, 302)
        
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        # nonexistent should raise 404
        xr = self.client.get('/testapp.use.testapp.nomodel/')
        self.assertEqual(xr.status_code, 404)
        # model to which this perm doesn't apply should raise 404
        xr = self.client.get('/testapp.use.auth.user/')
        self.assertEqual(xr.status_code, 404)
        r = self.client.get('/testapp.use.testapp.testmodel/')
        self.assertEqual(r.status_code, 200)
        
        assign_form = r.context['assign_form']
        self.assertFalse(assign_form.is_bound)
        self.assertRaises(KeyError, lambda: r.context['objects'])
        
        post_dict = {
            'users': ['4', '5'],
        }
        rp = self.client.post('/testapp.use.testapp.testmodel/', post_dict)
        self.assertEqual(rp.status_code, 200)
        assign_form = rp.context['assign_form']
        self.assertTrue(assign_form.is_valid())
        user4 = User.objects.get(pk=4)
        self.assertTrue(user4.has_perm('testapp.use.testapp.testmodel'))
    
    def test_type_to_group(self):
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        self.client.login(username='user', password='')
        post_dict = {
            'groups': ['1'],
        }
        rp = self.client.post('/testapp.use.testapp.testmodel/', post_dict)
        self.assertEqual(rp.status_code, 200)
        assign_form = rp.context['assign_form']
        self.assertTrue(assign_form.is_valid())
        user4 = User.objects.get(pk=4)
        self.assertFalse(user4.has_perm('testapp.use.testapp.testmodel'))
        group = Group.objects.get(pk=1)
        user4.groups.add(group)
        user4 = User.objects.get(pk=4)
        self.assertTrue(user4.has_perm('testapp.use.testapp.testmodel'))
    
    def test_type_remove(self):
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        self.client.login(username='user', password='')
        user4 = User.objects.get(pk=4)
        AppPermission.objects.assign('testapp.use.testapp.testmodel', user4)
        self.assertTrue(user4.has_perm('testapp.use.testapp.testmodel'))
        rp = self.client.post('/testapp.use.testapp.testmodel/', {})
        self.assertEqual(rp.status_code, 200)
        assign_form = rp.context['assign_form']
        self.assertTrue(assign_form.is_valid())
        user4 = User.objects.get(pk=4)
        self.assertFalse(user4.has_perm('testapp.use.testapp.testmodel'))
        
        user5 = User.objects.get(pk=5)
        group = Group.objects.get(pk=1)
        AppPermission.objects.assign('testapp.use.testapp.testmodel', group)
        user5.groups.add(group)
        self.assertTrue(user5.has_perm('testapp.use.testapp.testmodel'))
        rp = self.client.post('/testapp.use.testapp.testmodel/', {})
        user5 = User.objects.get(pk=5)
        self.assertFalse(user5.has_perm('testapp.use.testapp.testmodel'))
    
    def test_object_list(self):
        xr = self.client.get('/testapp.use.testapp.nomodel/objects/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/')
        self.assertEqual(xr.status_code, 302)
        
        self.client.login(username='user', password='')
        # logged in, but without correct perm
        xr = self.client.get('/testapp.use.testapp.nomodel/objects/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/')
        self.assertEqual(xr.status_code, 302)
        
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        # nonexistent should raise 404
        xr = self.client.get('/testapp.use.testapp.nomodel/objects/')
        self.assertEqual(xr.status_code, 404)
        # model to which this perm doesn't apply should raise 404
        xr = self.client.get('/testapp.use.auth.user/objects/')
        self.assertEqual(xr.status_code, 404)
        r = self.client.get('/testapp.use.testapp.testmodel/objects/')
        self.assertEqual(r.status_code, 200)
        
        objects = r.context['objects']
        self.assertEqual(len(objects), 2)
    
    def test_object_to_user(self):
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/100/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/1/')
        self.assertEqual(xr.status_code, 302)
        
        self.client.login(username='user', password='')
        # logged in, but without correct perm
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/100/')
        self.assertEqual(xr.status_code, 302)
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/1/')
        self.assertEqual(xr.status_code, 302)
        
        AppPermission.objects.assign('rubberstamp.manage.rubberstamp.apppermission', self.user)
        # nonexistent should raise 404
        xr = self.client.get('/testapp.use.testapp.testmodel/objects/100/')
        self.assertEqual(xr.status_code, 404)
        r = self.client.get('/testapp.use.testapp.testmodel/objects/1/')
        self.assertEqual(r.status_code, 200)
        
        assign_form = r.context['assign_form']
        self.assertFalse(assign_form.is_bound)
        self.assertRaises(KeyError, lambda: r.context['objects'])
        
        post_dict = {
            'users': ['4', '5'],
        }
        rp = self.client.post('/testapp.use.testapp.testmodel/objects/1/', post_dict)
        self.assertEqual(rp.status_code, 200)
        assign_form = rp.context['assign_form']
        self.assertTrue(assign_form.is_valid())
        user4 = User.objects.get(pk=4)
        object = TestModel.objects.get(pk=1)
        self.assertTrue(user4.has_perm('testapp.use.testapp.testmodel', obj=object))


__all__ = ('ViewTest',)
