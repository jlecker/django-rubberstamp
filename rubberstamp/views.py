from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.forms import PermissionAssignForm


def app_list(request):
    """
    Returns a list of apps and their permission codenames.
    
    Renders the template ``'rubberstamp/app_list.html'``, with context
    containing ``app_perms``, a list of tuples like::
    
        [('app_label', ['codename', 'codename', ...]), ...]
    """
    
    app_codes = AppPermission.objects.order_by('app_label', 'codename') \
        .values_list('app_label', 'codename')
    on_app = None
    app_perms = []
    for (app, code) in app_codes:
        if app != on_app:
            on_app = app
            app_perms.append((app, [])) # add app and empty perm list
        app_perms[-1][1].append(code) # add this code to the current app's list
    
    # app perms should be a list of tuples like
    # [('app_label', ['codename', 'codename', ...]), ...]
    return render_to_response(
        'rubberstamp/app_list.html',
        {'app_perms': app_perms},
        RequestContext(request)
    )


def type_list(request, app_label, codename):
    """
    Given an app label and permission codename, returns a list of types to
    which that permission can apply.
    
    Renders the template ``'rubberstamp/type_list.html'``, with context
    containing ``types``, a list of `ContentType` objects.
    """
    
    perm = get_object_or_404(
        AppPermission, app_label=app_label, codename=codename)
    return render_to_response(
        'rubberstamp/type_list.html',
        {'types': perm.content_types.all()},
        RequestContext(request)
    )


def object_list(request, app, code, target_app, target_model):
    """
    Given an app label and permission codename, as well as a "target" app label
    and model name, returns a list of objects of the target type to which the
    permission can apply.
    
    Renders the template ``'rubberstamp/object_list.html'``, with context
    containing ``objects``, a list of instances of the appropriate type.
    """
    
    target_ct = get_object_or_404(
        ContentType, app_label=target_app, model=target_model)
    perm = get_object_or_404(AppPermission,
        app_label=app, codename=code, content_types=target_ct)
    TargetClass = target_ct.model_class()
    return render_to_response(
        'rubberstamp/object_list.html',
        {'objects': TargetClass.objects.all()},
        RequestContext(request)
    )


def type_perms(request, app, code, target_app, target_model, obj_pk=None):
    """
    Takes the same arguments as ``object_list``, but returns a form to specify
    users and groups to assign/unassign the given permission to.
    
    Also accepts an option argument, the primary key of an object of the given
    type; if given, then the permissions will be assigned for that specific
    object instead of the type.
    
    Renders the template ``'rubberstamp/type_perms.html'``, with context
    containing ``assign_form``, a Django form to select users and groups.
    """
    
    target_ct = get_object_or_404(
        ContentType, app_label=target_app, model=target_model)
    perm = get_object_or_404(AppPermission,
        app_label=app, codename=code, content_types=target_ct)
    TargetClass = target_ct.model_class()
    if obj_pk:
        obj = get_object_or_404(TargetClass, pk=obj_pk)
    else:
        obj = None
    if request.method == 'POST':
        assign_form = PermissionAssignForm(request.POST)
        if assign_form.is_valid():
            perm_name = '%s.%s.%s.%s' % (app, code, target_app, target_model)
            perm_filter = {
                'permission': perm,
                'content_type': target_ct,
            }
            perms = AssignedPermission.objects.filter(
                **perm_filter).select_related('user', 'group')
            current_users = set(User.objects.filter(
                id__in=perms.filter(user__isnull=False).values_list('user')))
            current_groups = set(Group.objects.filter(
                id__in=perms.filter(group__isnull=False).values_list('group')))
            selected_users = set(assign_form.cleaned_data['users'])
            selected_groups = set(assign_form.cleaned_data['groups'])
            for user in selected_users - current_users:
                AppPermission.objects.assign(perm_name, user, obj=obj)
            for group in selected_groups - current_groups:
                AppPermission.objects.assign(perm_name, group, obj=obj)
            for user in current_users - selected_users:
                AppPermission.objects.remove(perm_name, user, obj=obj)
            for group in current_groups - selected_groups:
                AppPermission.objects.remove(perm_name, group, obj=obj)
    else:
        assign_form = PermissionAssignForm()
    context_dict = {'assign_form': assign_form}
    return render_to_response(
        'rubberstamp/type_perms.html',
        context_dict,
        RequestContext(request)
    )
