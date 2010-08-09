from django.contrib.contenttypes.models import ContentType
from rubberstamp.models import AppPermission, AssignedPermission


class AppPermissionBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    
    def has_perm(self, user, perm, obj=None):
        try:
            (perm, ct) = AppPermission.objects.get_permission_and_content_type(perm, obj)
        except ValueError:
            return False
        
        obj_id = None
        if obj:
            obj_id = obj.id
        
        return AssignedPermission.objects.filter(
            permission=perm,
            user=user,
            content_type=ct,
            object_id=obj_id
        ).exists()
    
    def has_module_perms(self, user, app_label):
        return AssignedPermission.objects.filter(
            permission__app_label=app_label,
            user=user
        ).exists()
    
    def get_all_permissions(self, user, obj=None):
        filters = {'user': user}
        if obj:
            filters['content_type'] = ContentType.objects.get_for_model(obj)
            filters['object_id'] = obj.id
        perm_ids = AssignedPermission.objects.filter(**filters).values_list('permission')
        perms = AppPermission.objects.filter(id__in=perm_ids)
        return set(['%s.%s' % (p.app_label, p.codename) for p in perms])