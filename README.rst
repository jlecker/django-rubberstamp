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


Creating Permissions
====================

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