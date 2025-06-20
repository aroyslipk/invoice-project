# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         apps.py
# Purpose:      Declares the application configuration for the Invoice app.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Application configuration for the 'Invoice' app.
"""

from django.apps import AppConfig

class InvoiceConfig(AppConfig):
    """
    Configuration class for the 'Invoice' application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Invoice'