from django.conf.urls.defaults import *
from django.contrib.auth.decorators import permission_required

from rubberstamp.views import app_list, type_list, object_list, type_perms


manage_perm = 'rubberstamp.manage.rubberstamp.apppermission'

urlpatterns = patterns('',
    (r'^$',
        permission_required(manage_perm)(app_list)),
    (r'^(\w+)\.(\w+)/$',
        permission_required(manage_perm)(type_list)),
    (r'^(\w+)\.(\w+)\.(\w+)\.(\w+)/$',
        permission_required(manage_perm)(type_perms)),
    (r'^(\w+)\.(\w+)\.(\w+)\.(\w+)/objects/$', 
        permission_required(manage_perm)(object_list)),
    (r'^(\w+)\.(\w+)\.(\w+)\.(\w+)/objects/(\d+)/$', 
        permission_required(manage_perm)(type_perms)),
)
