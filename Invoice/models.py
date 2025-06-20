# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         models.py
# Purpose:      Defines the database models for the Invoice application.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""Defines the database schema for the Invoice application."""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model with role-based access control."""
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    managed_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL, # Prevents deleting users if their manager is deleted
        null=True,
        blank=True,
        related_name='managed_users'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ClientProject(models.Model):
    """Represents a client project owned by an admin."""
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='project_attachments/', null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='projects_created', on_delete=models.CASCADE)
    managed_by = models.ForeignKey(User, related_name='managed_projects', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Price(models.Model):
    """Defines the rate for a work category, owned by an admin."""
    category = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    managed_by = models.ForeignKey(User, related_name='managed_prices', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        # A category name must be unique per admin.
        unique_together = ('managed_by', 'category')
        verbose_name_plural = "Prices"

    def __str__(self):
        owner = self.managed_by.username if self.managed_by else "System"
        return f"({owner}) {self.category}: ${self.rate}"


class WorkEntry(models.Model):
    """A single log of work done by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(ClientProject, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        project_name = self.project.name if self.project else "No Project"
        return f"{self.user.username} | {self.quantity} of {self.category} for {project_name}"