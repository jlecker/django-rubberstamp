from django import forms

from django.contrib.auth.models import User, Group


class PermissionAssignForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        required=False, queryset=User.objects.all())
    groups = forms.ModelMultipleChoiceField(
        required=False, queryset=Group.objects.all())
