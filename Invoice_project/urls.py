# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         urls.py (Project Level)
# Purpose:      Root URL configuration for the entire Invoice_project.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Root URL Configuration for Invoice_project.
This file routes top-level URLs to the appropriate applications.
- '/admin/'   -> Django admin site.
- '/api/'     -> All API endpoints, handled by 'Invoice.api_urls'.
- '/'         -> All web pages, handled by 'Invoice.urls'.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Invoice.api_urls')),
    path('', include('Invoice.urls')),
]

# Serves media files during development (when DEBUG is True).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)