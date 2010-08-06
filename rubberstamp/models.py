from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey


class AppPermissionManager(models.Manager):
    def assign(self, permission, user, obj=None):
        perm_ct = None
        bits = permission.split('.')
        if len(bits) >= 4:
            (app_label, codename, ct_app, ct_model) = \
                (bits[0], '.'.join(bits[1:-2]), bits[-2], bits[-1])
            perm_ct = ContentType.objects.get(app_label=ct_app, model=ct_model)
        else:
            (app_label, codename) = (bits[0], '.'.join(bits[1:]))
        
        obj_ct = None
        obj_id = None
        if obj:
            obj_ct = ContentType.objects.get_for_model(obj)
            obj_id = obj.id
        
        content_type = perm_ct or obj_ct
        if not (perm_ct or obj_ct):
            raise ValueError('ContentType must be given in permission, or object must be passed.')
        if perm_ct and obj_ct and perm_ct != obj_ct:
            raise ValueError('ContentType in permission and passed object mismatched.')
        
        perm = self.get(
            app_label=app_label,
            content_types=content_type,
            codename=codename
        )
        return AssignedPermission.objects.get_or_create(
            permission=perm,
            user=user,
            content_type=content_type,
            object_id=obj_id
        )


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


class AssignedPermission(models.Model):
    permission = models.ForeignKey(AppPermission)
    user = models.ForeignKey(User)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    object = GenericForeignKey()