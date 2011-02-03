from django.db.models import Q
from django.db.models.loading import get_model


def get_perm_q_for_user(user):
    """
    Returns a Q object for the given user, to be used as a filter on
    `AppPermission`, which will return permissions that this user possesses
    directly and through group membership.
    """
    
    if user.is_anonymous():
        # anonymous users have no perms
        return Q(pk=None)
    return Q(user=user) | Q(group__in=user.groups.all())


def get_permission_targets(permission, user):
    """
    Given a (long) permission string and a user, returns a QuerySet of
    objects for which that user has that permission.
    """
    
    (perm, ct) = get_model('rubberstamp', 'apppermission').objects.get_permission_and_content_type(permission)
    
    q = Q(
            permission=perm,
            content_type=ct,
            object_id__isnull=False
        ) & get_perm_q_for_user(user)
    
    obj_ids = get_model('rubberstamp', 'assignedpermission').objects.filter(q).values('object_id')
    return ct.model_class().objects.filter(pk__in=obj_ids)


def get_app_list(user):
    AssignedPermission = get_model('rubberstamp', 'assignedpermission')
    return AssignedPermission.objects.filter(get_perm_q_for_user(user)) \
        .values_list('permission__app_label', flat=True).distinct()
