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

This file contains forms used for creating and updating data, such as
work entries and prices. It includes logic to handle permissions and
filter querysets based on the user's role.
"""

from django import forms
from .models import WorkEntry, ClientProject, Price


class WorkEntryForm(forms.ModelForm):
    """A form for users to submit their daily work entries."""

    class Meta:
        model = WorkEntry
        fields = ['project', 'category', 'quantity', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and filters the 'project' queryset based
        on the user's role and ownership to ensure data security.
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not user:
            self.fields['project'].queryset = ClientProject.objects.none()
            return

        # Security fix: Filter projects based on user's manager.
        # This ensures a user can only select projects owned by their admin.
        if user.role == 'user' and hasattr(user, 'managed_by') and user.managed_by:
            self.fields['project'].queryset = ClientProject.objects.filter(managed_by=user.managed_by)
        elif user.role == 'admin':
            self.fields['project'].queryset = ClientProject.objects.filter(managed_by=user)
        elif user.role == 'super_admin':
            self.fields['project'].queryset = ClientProject.objects.all()
        else:
            self.fields['project'].queryset = ClientProject.objects.none()


class PriceForm(forms.ModelForm):
    """A simple form for creating and updating prices."""

    class Meta:
        model = Price
        fields = ['category', 'rate']