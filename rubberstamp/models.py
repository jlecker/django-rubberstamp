from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from rubberstamp.utils import get_perm_q_for_user
from rubberstamp.exceptions import PermissionLookupError


class AppPermissionManager(models.Manager):
    def get_permission_and_content_type(self, permission, obj=None):
        """
        Given a permission string and (optionally) an object, returns a tuple
        of an AppPermission instance and a ContentType instance corresponding
        to that string (and object, if given).
        
        The permission string is given in the dotted form, either
        `'app_label.codename'` or
        `'app_label.codename.target_app.target_model'`.
        
        If the correct AppPermission and ContentType cannot be determined for
        the passed parameters, a `PermissionLookupError` is raised.
        """
        
        perm_ct = None
        bits = permission.split('.')
        app_label = bits.pop(0)
        if len(bits) >= 3:
            # either a ContentType was given, or this is a long codename
            try:
                perm_ct = ContentType.objects.get(
                    app_label=bits[-2], model=bits[-1])
            except ContentType.DoesNotExist:
                codename = '.'.join(bits)
            else:
                codename = '.'.join(bits[:-2])
        else:
            codename = '.'.join(bits)
        
        obj_ct = None
        if obj:
            obj_ct = ContentType.objects.get_for_model(obj)
        
        content_type = perm_ct or obj_ct
        if not (content_type):
            raise PermissionLookupError('ContentType must be given in permission, or object must be passed.')
        if perm_ct and obj_ct and perm_ct != obj_ct:
            raise PermissionLookupError('ContentType in permission and passed object mismatched.')
        
        try:
            return (
                self.get(
                    app_label=app_label,
                    content_types=content_type,
                    codename=codename
                ),
                content_type
            )
        except self.model.DoesNotExist:
            raise PermissionLookupError('AppPermission not found.')
    
    def assign(self, permission, user_or_group, obj=None):
        """
        Assigns the given permission to the given user or group, and returns
        the AssignedPermission instance.
        
        If an object is given, assigns the permission for that object.
        """
        
        (perm, ct) = self.get_permission_and_content_type(permission, obj)
        
        assigned_dict = {
            'permission': perm,
            'content_type': ct,
            'object_id': None
        }
        
        if obj:
            assigned_dict['object_id'] = obj.id

        if isinstance(user_or_group, User):
            assigned_dict['user'] = user_or_group
        elif isinstance(user_or_group, Group):
            assigned_dict['group'] = user_or_group
        else:
            raise TypeError('Permissions must be assigned to a User or Group instance.')
        
        return AssignedPermission.objects.get_or_create(**assigned_dict)
    
    def remove(self, permission, user_or_group, obj=None):
        """
        Removes the given permission from the given user or group, and returns
        the deleted AssignedPermission instance or None if not found.
        
        If an object is given, removes the permission for that object.
        """
        
        (perm, ct) = self.get_permission_and_content_type(permission, obj)
        
        assigned_dict = {
            'permission': perm,
            'content_type': ct,
            'object_id': None
        }
        
        if obj:
            assigned_dict['object_id'] = obj.id

        if isinstance(user_or_group, User):
            assigned_dict['user'] = user_or_group
        elif isinstance(user_or_group, Group):
            assigned_dict['group'] = user_or_group
        else:
            raise TypeError('Permissions can only be removed from a User or Group instance.')
        
        try:
            assigned = AssignedPermission.objects.get(**assigned_dict)
        except AssignedPermission.DoesNotExist:
            return None
        else:
            assigned.delete()
            return assigned
    
    def get_permission_targets(self, permission, user):
        """
        Given a (long) permission string and a user, returns a QuerySet of
        objects for which that user has that permission.
        """
        
        (perm, ct) = self.get_permission_and_content_type(permission)
        
        q = models.Q(
                permission=perm,
                content_type=ct,
                object_id__isnull=False
            ) & get_perm_q_for_user(user)
        
        obj_ids = AssignedPermission.objects.filter(q).values('object_id')
        return ct.model_class().objects.filter(pk__in=obj_ids)
    
    def get_by_natural_key(self, app_label, codename):
        return self.get(app_label=app_label, codename=codename)
        


class AppPermission(models.Model):
    """
    Permission model which allows apps to add permissions for models in other
    apps, keeping track of the permissions added by each app.
    """
    
    app_label = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    content_types = models.ManyToManyField(ContentType)
    
    objects = AppPermissionManager()
    
    class Meta:
        unique_together = ('app_label', 'codename')
    
    def __unicode__(self):
        return '%s.%s' % (self.app_label, self.codename)
    
    def natural_key(self):
        return (self.app_label, self.codename)


class AssignedPermission(models.Model):
    """An AppPermission which has been assigned to a user or group."""
    
    permission = models.ForeignKey(AppPermission)
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
