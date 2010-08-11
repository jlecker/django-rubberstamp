Permissions management and backend.

Requires Django 1.2, including `auth` and `contenttypes` from `contrib`.


What does it do?
* Permissions are generic words (actions) that can (conceivably) be applied to
  objects of any type. Like Django auth permissions "change", "delete", etc,
  but without each permission being tied to a specific model.
* Any app can define permissions with a list of types (models) that they apply
  to, including (or especially) models in other apps.
* Supports model (table-level) and object (row-level) permissions.
* Works as a backend for Django 1.2.



Settings
========


Add to Installed Apps
---------------------

Add ``'rubberstamp'`` to your ``INSTALLED_APPS`` in ``settings.py``.


Add the Backend
---------------

The backend is located at ``rubberstamp.backends.AppPermissionBackend``. It is
needed to check permissions via `User` instances (the normal Django way). To
use it, simply add it to your ``AUTHENTICATION_BACKENDS`` in ``settings.py``.
If you are not adding any additional backends, it would look like this::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'rubberstamp.backends.AppPermissionBackend',
    )

That is, assuming you are continuing to use Django's default `ModelBackend`.
The default backend is not a requirement for `django-rubberstamp`, but other
apps in your project may depend on it (e.g. Django admin).



Permissions
===========


Create Permissions
------------------

A method similar to that in Django's admin is used to discover permissions.
Simply add the following lines to the top of your URLconf::

    import rubberstamp
    rubberstamp.autodiscover()

The ``autodiscover()`` method looks for permissions in a module named
`permissions` within each installed app. That means, to add permissions for an
app, simply place them in a file called `permissions.py` in your app
directory. This file should contain a list of tuples called ``permissions``,
where each tuple defines a permission. Each tuple should be in the format
``('codename', 'description', Model)``. For example, here are the contents of
a `permissions` module used in the test application in the test suite::

    from rubberstamp.tests.testapp.models import TestModel
    
    permissions = [
        ('use', 'Use this object', TestModel),
    ]

Here, the test application defines a single permission `use` which can be
applied to the model `TestModel` (also from `testapp`). To allow a permission
to apply to more than one model, use a tuple as the last item in the
definition, like so: ``('codename', 'description', (Model1, Model2))``.
Remember that a permission can apply to models from any app; just include each
model in your permission definition.


Assign Permissions
------------------

Assigning permissions is done via the ``assign()`` manager method on the
``AppPermission`` model, like so::

    from rubberstamp.models import AppPermission
    
    AppPermission.objects.assign('testapp.use.testapp.testmodel', user_object)

This would assign the `use` permission on the model `TestModel` to the user
represented by `user_object`. The format of the permission string is
``<app label>.<codename>.<target app label>.<target model>``.

To assign object-level permissions, pass a ``obj`` keyword argument, like so::

    AppPermission.objects.assign('testapp.use.testapp.testmodel', user_object, obj=target_object)

When assigning object permissions, you can leave the `target` information out
of the permission string, since it can be extracted from the passed object.
This example would work exactly the same as the previous::

    AppPermission.objects.assign('testapp.use', user_object, obj=target_object)

Without the ``obj`` parameter, the type cannot be automatically determined, so
the full permission string must be user to assign model-level permissions, as
in the first example in this section.


Check Permissions
-----------------

Checking permissions works as it always has in Django, with the `has_perm()`
method on the User model::

    user_object.has_perm('testapp.use.testapp.testmodel')

As with ``assign()``, this method accepts an optional ``obj`` parameter to
check permissions for a specific object. Also like ``assign()``, when an
object is passed, the shorter form of the permission string can be used::

    user_object.has_perm('testapp.use', obj=target_object)


Remove Permissions
------------------

Removing permissions is done via the ``remove()`` manager method on the
``AppPermission`` model, with similar syntax to ``assign()``::

    AppPermission.objects.remove('testapp.use.testapp.testmodel', user_object)

This remove the `use` permission on the model `TestModel` from the user
represented by `user_object`. The ``remove()`` method accepts the same syntax
variations as ``assign()``.