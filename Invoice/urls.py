# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         urls.py (App Level)
# Purpose:      URL routing for the Invoice application's web pages.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""URL configuration for the web-facing pages of the 'Invoice' app."""

from django.urls import path
from .views import (
    home_view, CustomLoginView, work_entry_form_view, my_work_entries_view,
    dashboard_template_view, admin_panel_view, price_manage_view,
    price_edit_view, price_delete_view, export_page_view, generate_invoice,
)

urlpatterns = [
    # --- Home & Core ---
    path('', home_view, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),

    # --- User-facing pages ---
    path('submit-work/', work_entry_form_view, name='submit_work_entry'),
    path('my-work/', my_work_entries_view, name='my_work_entries'),

    # --- Dashboards & Admin ---
    path('dashboard/', dashboard_template_view, name='dashboard'),
    path('admin-panel/', admin_panel_view, name='admin_panel'),

    # --- Price Management Pages ---
    path('manage/prices/', price_manage_view, name='price_manage'),
    path('manage/prices/<int:id>/edit/', price_edit_view, name='price_edit'),
    path('manage/prices/<int:id>/delete/', price_delete_view, name='price_delete'),
    
    # --- Reporting & Invoices---
    path('export-page/', export_page_view, name='export_page'),
    path('invoice/generate/<int:project_id>/', generate_invoice, name='generate_invoice'),
]