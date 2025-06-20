# -*- coding: utf--8 -*-
# -----------------------------------------------------------------------------
# Name:         serializers.py
# Purpose:      Defines API serializers for the Invoice application's models.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
API Serializers for the Invoice application.

These serializers convert complex data types, such as Django model instances,
to native Python datatypes that can then be easily rendered into JSON, XML
or other content types for use in the REST API.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, WorkEntry, Price, ClientProject


class UserSerializer(serializers.ModelSerializer):
    """Serializer for viewing user profile information."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] # Role is intentionally removed for security

    def create(self, validated_data):
        """
        Creates a new user, always assigning the 'user' role by default
        to prevent privilege escalation through the public registration API.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='user'  # Security: Always register new users with the default 'user' role.
        )
        return user


class WorkEntrySerializer(serializers.ModelSerializer):
    """Serializer for creating and listing work entries."""
    class Meta:
        model = WorkEntry
        fields = ['id', 'user', 'project', 'category', 'quantity', 'date']
        read_only_fields = ['user']


class WorkDashboardSerializer(serializers.ModelSerializer):
    """A read-only serializer for displaying work entries on an admin dashboard."""
    username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = WorkEntry
        fields = ['id', 'username', 'project_name', 'category', 'quantity', 'date']


class PriceSerializer(serializers.ModelSerializer):
    """Serializer for managing prices, intended for admin use."""
    class Meta:
        model = Price
        fields = ['id', 'category', 'rate', 'managed_by']
        read_only_fields = ['managed_by'] # Owner is set automatically in the view.


class ClientProjectSerializer(serializers.ModelSerializer):
    """Serializer for creating and viewing client projects."""
    class Meta:
        model = ClientProject
        fields = ['id', 'name', 'start_date', 'end_date', 'attachment', 'created_by', 'managed_by']
        read_only_fields = ['created_by', 'managed_by'] # Owners are set in the view.