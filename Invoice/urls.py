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
# LogoutView এবং অন্যান্য প্রয়োজনীয় ভিউ import করা হয়েছে
from django.contrib.auth.views import LogoutView
from .views import (
    home_view,
    CustomLoginView,
    work_entry_form_view,
    my_work_entries_view,
    dashboard_template_view,
    admin_panel_view,
    my_team_view,
    manage_projects_view,
    delete_project_view,
    manage_prices_view,
    price_edit_view,
    delete_price_view,
    export_page_view,
    generate_invoice,
)

urlpatterns = [
    # --- Core & Authentication ---
    path('', home_view, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # --- নতুন Logout URL টি এখানে যোগ করা হয়েছে ---
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # --- User-Specific Pages ---
    path('submit-work/', work_entry_form_view, name='submit_work_entry'),
    path('my-work/', my_work_entries_view, name='my_work_entries'),

    # --- Admin Dashboards ---
    path('dashboard/', dashboard_template_view, name='dashboard'),
    path('admin-panel/', admin_panel_view, name='admin_panel'),
    path('my-team/', my_team_view, name='my_team'),

    # --- Management Pages ---
    path('manage/projects/', manage_projects_view, name='manage_projects'),
    path('manage/projects/delete/<int:project_id>/', delete_project_view, name='delete_project'),
    path('manage/prices/', manage_prices_view, name='manage_prices'),
    path('manage/prices/<int:id>/edit/', price_edit_view, name='price_edit'),
    path('manage/prices/delete/<int:id>/', delete_price_view, name='delete_price'),
    
    # --- Reporting & Invoices ---
    path('export-page/', export_page_view, name='export_page'),
    path('invoice/generate/<int:project_id>/', generate_invoice, name='generate_invoice'),
]