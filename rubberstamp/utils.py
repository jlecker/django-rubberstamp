from django.db.models import Q

def get_perm_q_for_user(user):
    """
    Returns a Q object for the given user, to be used as a filter on
    `AppPermission`, which will return permission that this user possesses
    directly and through group membership.
    """
    
    if user.is_anonymous():
        # anonymous users have no perms
        return Q(pk=None)
    return Q(user=user) | Q(group__in=user.groups.all())
