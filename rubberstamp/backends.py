from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.utils import get_perm_q_for_user
from rubberstamp.exceptions import PermissionLookupError


class AppPermissionBackend(object):
    """A permission backend to support AppPermission."""
    
    supports_object_permissions = True
    supports_anonymous_user = True
    
    def has_perm(self, user, perm, obj=None):
        try:
            (perm, ct) = AppPermission.objects.get_permission_and_content_type(perm, obj)
        except PermissionLookupError:
            return False
        
        obj_id = None
        if obj:
            obj_id = obj.id
        
        q = Q(
            permission=perm,
            content_type=ct,
            object_id=obj_id
        ) & get_perm_q_for_user(user)
        return AssignedPermission.objects.filter(q).exists()
    
    def has_module_perms(self, user, app_label):
        q = Q(permission__app_label=app_label) & get_perm_q_for_user(user)
        return AssignedPermission.objects.filter(q).exists()
    
    def get_all_permissions(self, user, obj=None):
        q = get_perm_q_for_user(user)
        if obj:
            q = q & Q(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id
            )
        perm_ids = AssignedPermission.objects.filter(q).values_list('permission')
        perms = AppPermission.objects.filter(id__in=perm_ids)
        return set(['%s.%s' % (p.app_label, p.codename) for p in perms])
    
    def authenticate(self, **credentials):
        return None
