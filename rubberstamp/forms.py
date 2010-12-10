from django import forms

from django.contrib.auth.models import User, Group


class PermissionAssignForm(forms.Form):
    """A form to choose users and groups, to assign perms to them."""
    
    users = forms.ModelMultipleChoiceField(
        required=False, queryset=User.objects.order_by('username'))
    groups = forms.ModelMultipleChoiceField(
        required=False, queryset=Group.objects.order_by('name'))
