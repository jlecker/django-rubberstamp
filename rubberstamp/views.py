from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rubberstamp.models import AppPermission, AssignedPermission
from rubberstamp.forms import PermissionAssignForm


def app_list(request):
    app_codes = AppPermission.objects.order_by('app_label', 'codename') \
        .values_list('app_label', 'codename')
    on_app = None
    app_perms = []
    for (app, code) in app_codes:
        if app != on_app:
            on_app = app
            app_perms.append((app, [])) # add app and empty perm list
        app_perms[-1][1].append(code) # add this code to the current app's list
    
    return render_to_response(
        'rubberstamp/app_list.html',
        {'app_perms': app_perms}
    )


def type_list(request, app_label, codename):
    perm = get_object_or_404(
        AppPermission, app_label=app_label, codename=codename)
    return render_to_response(
        'rubberstamp/type_list.html',
        {'types': perm.content_types.all()}
    )


def type_perms(request, app, code, target_app, target_model, obj_pk=None):
    target_ct = get_object_or_404(
        ContentType, app_label=target_app, model=target_model)
    perm = get_object_or_404(AppPermission,
        app_label=app, codename=code, content_types=target_ct)
    TargetClass = target_ct.model_class()
    if obj_pk:
        object = get_object_or_404(TargetClass, pk=obj_pk)
    else:
        object = None
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
                AppPermission.objects.assign(perm_name, user, obj=object)
            for group in selected_groups - current_groups:
                AppPermission.objects.assign(perm_name, group, obj=object)
            for user in current_users - selected_users:
                AppPermission.objects.remove(perm_name, user, obj=object)
            for group in current_groups - selected_groups:
                AppPermission.objects.remove(perm_name, group, obj=object)
    else:
        assign_form = PermissionAssignForm()
    context_dict = {'assign_form': assign_form}
    if not obj_pk:
        context_dict['objects'] = TargetClass.objects.all()
    return render_to_response('rubberstamp/type_perms.html', context_dict)
