def autodiscover():
    """
    Auto-discover INSTALLED_APPS permission.py modules, failing silently when
    not present, and create all permissions defined by them if not created
    already.
    """

    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    
    from django.contrib.contenttypes.models import ContentType
    from rubberstamp.models import AppPermission

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        if module_has_submodule(mod, 'permissions'):
            app_label = app.split('.')[-1]
            perm_module = import_module('%s.permissions' % app)
            permissions = getattr(perm_module, 'permissions', [])
            for (Model, (codename, name)) in permissions:
                AppPermission.objects.get_or_create(
                    app_label=app_label,
                    content_type=ContentType.objects.get_for_model(Model),
                    codename=codename,
                    name=name
                )