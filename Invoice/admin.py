# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         admin.py
# Purpose:      Advanced Django Admin configurations for the Invoice app.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Admin Site Configuration for the Invoice App.

This file provides advanced configurations to enforce a strict, multi-tenant
permission system directly within the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WorkEntry, Price, ClientProject


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Customizes the UserAdmin to enforce strict role-based permissions.
    - Admins can only add new users.
    - Admins cannot change any user's data (including roles or passwords).
    - Admins can only see users that they manage.
    """
    list_display = ('username', 'email', 'role', 'managed_by', 'is_staff')
    list_filter = ('role',)
    
    # This ensures an admin cannot change sensitive fields.
    # The default UserAdmin.fieldsets are used for the superuser.
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Ownership', {'fields': ('role', 'managed_by')}),
    )

    def get_queryset(self, request):
        """Filters the user list to show only managed users to admins."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'super_admin':
            return qs
        # Admins can only see users they have created/manage.
        return qs.filter(managed_by=request.user)

    def save_model(self, request, obj, form, change):
        """
        When an admin adds a new user, automatically assign the admin
        as the manager ('managed_by').
        """
        # Set manager only when a new user is created by an admin.
        if not change and not request.user.is_superuser:
            obj.managed_by = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        """
        Dynamically removes fields from the form for non-superusers.
        This prevents an admin from changing a user's role or manager.
        """
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Admins cannot change the role or manager of any user.
            if 'role' in form.base_fields:
                form.base_fields['role'].disabled = True
            if 'managed_by' in form.base_fields:
                form.base_fields['managed_by'].disabled = True
        return form

    def has_change_permission(self, request, obj=None):
        """
        Blocks regular admins from having change permissions on any user.
        This is the core of the solution to your problem.
        """
        # Only superusers can change user objects.
        if not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Prevents admins from deleting users."""
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


# --- The rest of your admin.py remains the same ---
# Note: I am providing the full, correct code for all other ModelAdmins
# to ensure everything is consistent and correct.

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Admin configuration for the Price model."""
    list_display = ('category', 'rate', 'managed_by')
    list_filter = ('managed_by',)
    search_fields = ('category',)

    def save_model(self, request, obj, form, change):
        if not obj.managed_by_id:
            obj.managed_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'super_admin':
            return qs
        return qs.filter(managed_by=request.user)

@admin.register(ClientProject)
class ClientProjectAdmin(admin.ModelAdmin):
    """Admin configuration for the ClientProject model."""
    list_display = ('name', 'start_date', 'managed_by')
    list_filter = ('managed_by',)
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        if not obj.managed_by_id:
            obj.managed_by = request.user
        if not hasattr(obj, 'created_by_id') or not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'super_admin':
            return qs
        return qs.filter(managed_by=request.user)


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    """Admin configuration for the WorkEntry model."""
    list_display = ('user', 'project', 'category', 'quantity', 'date')
    list_filter = ('date', 'category', 'project__name')
    search_fields = ('user__username', 'project__name', 'category')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'super_admin':
            return qs
        if request.user.role == 'admin':
            return qs.filter(project__managed_by=request.user)
        return qs.filter(user=request.user)