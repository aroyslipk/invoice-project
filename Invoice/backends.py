# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         backends.py
# Purpose:      Custom authentication backend to allow users to log in
#               using their email address instead of a username.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Custom Django Authentication Backends.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Authenticates a user via their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the default authenticate method to use email.
        The 'username' argument here is expected to be an email address.
        """
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Overrides the default get_user method.
        """
        UserModel = get_user_model()
        # .first() returns the object or None, elegantly handling the try/except.
        return UserModel.objects.filter(pk=user_id).first()