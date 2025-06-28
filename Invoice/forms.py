# Invoice/forms.py (সংশোধিত এবং চূড়ান্ত সংস্করণ)
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         forms.py
# Purpose:      Defines Django forms for the Invoice application.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Django Forms for the Invoice application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, WorkEntry, ClientProject, Price


class WorkEntryForm(forms.ModelForm):
    """A form for users to submit their daily work entries."""
    class Meta:
        model = WorkEntry
        fields = ['project', 'category', 'quantity', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Initializes the form and filters the 'project' queryset."""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not user:
            self.fields['project'].queryset = ClientProject.objects.none()
            return

        if user.role == 'user' and hasattr(user, 'managed_by') and user.managed_by:
            self.fields['project'].queryset = ClientProject.objects.filter(managed_by=user.managed_by)
        elif user.role == 'admin':
            self.fields['project'].queryset = ClientProject.objects.filter(managed_by=user)
        elif user.role == 'super_admin':
            self.fields['project'].queryset = ClientProject.objects.all()
        else:
            self.fields['project'].queryset = ClientProject.objects.none()


class PriceForm(forms.ModelForm):
    """A simple form for creating and updating prices with a custom label."""
    class Meta:
        model = Price
        fields = ['category', 'rate']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Initializes the form and changes the 'category' field's label."""
        super().__init__(*args, **kwargs)
        self.fields['category'].label = "Folder Name"


class AdminUserCreationForm(UserCreationForm):
    """A form for admins to create new users under their management."""
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


# --- ClientProjectForm ক্লাসটিকে নিচের কোড দিয়ে প্রতিস্থাপন করুন ---
class ClientProjectForm(forms.ModelForm):
    """A form for creating and updating client projects."""
    class Meta:
        model = ClientProject
        fields = ['name', 'start_date', 'end_date', 'attachment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }