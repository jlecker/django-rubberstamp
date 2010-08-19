from django.db.models import Q

def get_perm_q_for_user(user):
    if user.is_anonymous():
        # anonymous users have no perms
        return Q(pk=None)
    return Q(user=user) | Q(group__in=user.groups.all())