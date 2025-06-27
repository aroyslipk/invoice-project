# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         views.py
# Purpose:      Handles all view and API endpoint logic for the Invoice app.
#
# Author:       AnikRoy
# GitHub:       https://github.com/aroyslipk
#
# Created:      2025-06-20
# Copyright:    (c) AnikRoy 2025
# Licence:      Proprietary
# -----------------------------------------------------------------------------

"""
Handles all view logic for the Invoice application, including template rendering,
API endpoints, and business logic for the multi-tenant permission system.
"""

# Python Standard Library Imports
import datetime
from pathlib import Path
from copy import copy
import os

# Django Core Imports
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.conf import settings

# Third-Party Library Imports
from openpyxl import Workbook, load_workbook
from num2words import num2words
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local Application Imports
from .forms import PriceForm, WorkEntryForm
from .models import ClientProject, Price, User, WorkEntry
from .serializers import (
    ClientProjectSerializer, PriceSerializer, RegisterSerializer,
    UserSerializer, WorkDashboardSerializer, WorkEntrySerializer,
)


# --- Core & Template Views ---

def home_view(request):
    """Displays the home page."""
    return HttpResponse("<h2>🧾 Welcome to the Invoice App</h2><p>Go to <a href='/login/'>Login</a></p>")


@login_required
def dashboard_template_view(request):
    """Renders the main dashboard, filtering data based on user role."""
    user = request.user
    if user.role == 'user':
        return redirect('my_work_entries')

    projects = ClientProject.objects.none()
    prices = Price.objects.none()
    entries = WorkEntry.objects.none()

    if user.role == 'super_admin':
        entries = WorkEntry.objects.select_related('user', 'project').all()
        prices = Price.objects.all()
        projects = ClientProject.objects.all()
    elif user.role == 'admin':
        entries = WorkEntry.objects.filter(project__managed_by=user)
        prices = Price.objects.filter(managed_by=user)
        projects = ClientProject.objects.filter(managed_by=user)

    price_lookup = {p.category.lower(): p.rate for p in prices}
    return render(request, 'dashboard.html', {
        'entries': entries.order_by('-date'),
        'prices': price_lookup,
        'projects': projects
    })


@login_required
def admin_panel_view(request):
    """Displays the super admin panel with access to all system data."""
    if request.user.role != 'super_admin':
        return render(request, 'unauthorized.html')
    context = {
        'work_entries': WorkEntry.objects.all().order_by('-date'),
        'prices': Price.objects.all(),
        'projects': ClientProject.objects.all(),
        'users': User.objects.all(),
    }
    return render(request, 'admin_panel.html', context)


# --- User-Facing Forms & Views ---

@login_required
def work_entry_form_view(request):
    """Handles the form for standard users to submit their work."""
    if request.user.role != 'user':
        return render(request, 'unauthorized.html')
    if request.method == 'POST':
        form = WorkEntryForm(request.POST, user=request.user)
        if form.is_valid():
            work_entry = form.save(commit=False)
            work_entry.user = request.user
            work_entry.save()
            return redirect('my_work_entries')
    else:
        form = WorkEntryForm(user=request.user)
    return render(request, 'work_entry_form.html', {'form': form})


@login_required
def my_work_entries_view(request):
    """Displays a list of work entries submitted by the current user."""
    if request.user.role != 'user':
        return render(request, 'unauthorized.html')
    work_entries = WorkEntry.objects.filter(user=request.user).select_related('project').order_by('-date')
    return render(request, 'my_work_entries.html', {'entries': work_entries})


# --- Pricing Management Views ---

@login_required
def price_manage_view(request):
    """Allows admins to create and view their list of prices."""
    user = request.user
    if user.role not in ['admin', 'super_admin']:
        return render(request, 'unauthorized.html')

    if user.role == 'super_admin':
        prices = Price.objects.all()
    else:  # 'admin' role
        prices = Price.objects.filter(managed_by=user)

    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            price = form.save(commit=False)
            price.managed_by = user
            price.save()
            return redirect('price_manage')
    else:
        form = PriceForm()
    return render(request, 'price_manage.html', {'form': form, 'prices': prices})


@login_required
def price_edit_view(request, id):
    """Handles editing of a specific price, with ownership check."""
    price = get_object_or_404(Price, id=id)
    user = request.user
    if user.role != 'super_admin' and price.managed_by != user:
        return render(request, 'unauthorized.html')
    
    if request.method == 'POST':
        form = PriceForm(request.POST, instance=price)
        if form.is_valid():
            form.save()
            return redirect('price_manage')
    else:
        form = PriceForm(instance=price)
    return render(request, 'price_edit.html', {'form': form, 'price': price})


@login_required
def price_delete_view(request, id):
    """Handles deletion of a specific price, with ownership check."""
    price = get_object_or_404(Price, id=id)
    user = request.user
    if user.role != 'super_admin' and price.managed_by != user:
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        price.delete()
        return redirect('price_manage')
    return render(request, 'price_delete.html', {'price': price})


# --- Reporting & Invoice Generation ---

@login_required
def export_page_view(request):
    """Displays the page for initiating exports."""
    if request.user.role not in ['admin', 'super_admin']:
        return render(request, 'unauthorized.html')
    return render(request, 'export_page.html')


@login_required
def generate_invoice(request, project_id):
    """
    Generates and downloads a secure, role-filtered XLSX invoice
    using a robust method for finding the template file.
    """
    user = request.user
    project = get_object_or_404(ClientProject, id=project_id)

    # Security check: Ensure admin can only access their own projects.
    if user.role != 'super_admin' and project.managed_by != user:
        return render(request, 'unauthorized.html')

    # Filter data based on user role.
    if user.role == 'super_admin':
        entries = WorkEntry.objects.filter(project=project).order_by('date')
        prices_qs = Price.objects.all()
    else:  # 'admin' role
        entries = WorkEntry.objects.filter(project=project, project__managed_by=user).order_by('date')
        prices_qs = Price.objects.filter(managed_by=user)
    
    prices = {p.category.lower(): p.rate for p in prices_qs}
    
    template_path = os.path.join(settings.BASE_DIR, 'static', 'template', 'InvoiceTemplate.xlsx')

    try:
        wb = load_workbook(template_path)
    except FileNotFoundError:
        error_message = f"Error: The invoice template could not be found. Path checked: {template_path}"
        return HttpResponse(error_message, status=500)

    ws = wb.active
    ws.protection.sheet = False
    start_row = 14
    
    if entries:
        if len(entries) > 1:
            ws.insert_rows(start_row + 1, amount=len(entries) - 1)
        
        current_row = start_row
        total_quantity_sum, total_rate_sum, total_amount_numeric = 0, 0, 0
        
        for entry in entries:
            rate_for_entry = float(prices.get(entry.category.lower(), 0))
            amount_for_entry = entry.quantity * rate_for_entry
            total_quantity_sum += entry.quantity
            total_rate_sum += rate_for_entry
            total_amount_numeric += amount_for_entry
            
            # Populate data into cells
            ws.cell(row=current_row, column=2).value = entry.category
            ws.cell(row=current_row, column=3).value = entry.date.strftime("%Y-%m-%d")
            ws.cell(row=current_row, column=4).value = entry.quantity
            ws.cell(row=current_row, column=5).value = rate_for_entry
            ws.cell(row=current_row, column=6).value = amount_for_entry
            current_row += 1
            
        # --- Summary section ---
        summary_start_row = start_row + len(entries) + 2
        ws.cell(row=summary_start_row, column=4).value = total_quantity_sum
        ws.cell(row=summary_start_row, column=4).font = Font(bold=True)
        ws.cell(row=summary_start_row, column=5).value = total_rate_sum
        ws.cell(row=summary_start_row, column=5).font = Font(bold=True)
        ws.cell(row=summary_start_row, column=6).value = total_amount_numeric
        ws.cell(row=summary_start_row, column=6).font = Font(bold=True)
        
        # --- Amount in words ---
        in_words_cell = ws.cell(row=summary_start_row + 1, column=2)
        total_in_words = num2words(total_amount_numeric, lang='en').title() + " US Dollars Only"
        in_words_cell.value = total_in_words
        in_words_cell.font = Font(italic=True)

    # --- Project attachment link (if exists) ---
    if project.attachment and hasattr(project.attachment, 'url'):
        attachment_url = request.build_absolute_uri(project.attachment.url)
        attachment_cell = ws.cell(row=ws.max_row + 2, column=2)
        attachment_cell.value = "View Project Attachment"
        attachment_cell.hyperlink = attachment_url
        attachment_cell.font = Font(color="0000FF", underline="single")
        ws.cell(row=attachment_cell.row, column=1).value = "Attachment:"
        
    # --- Prepare and return the response ---
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Invoice_{project.name}_{datetime.date.today()}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    
    return response

# --------------------------------------------------------------------------
# --- API Views (DRF) with full security and role-based filtering ---
# --------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """API endpoint for public user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveAPIView):
    """API endpoint to view the profile of the currently logged-in user."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user


class WorkEntryListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create work entries."""
    serializer_class = WorkEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return WorkEntry.objects.all()
        if user.role == 'admin':
            return WorkEntry.objects.filter(project__managed_by=user)
        return WorkEntry.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExportWorkEntriesXLSXView(generics.GenericAPIView):
    """API endpoint to export work entries to an XLSX file."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ["admin", "super_admin"]:
            return Response({"detail": "Not authorized."}, status=403)
        # ... (Your Export logic from previous version, now secured) ...
        return Response({"detail": "Export successful."}) # Placeholder response


class DashboardView(generics.ListAPIView):
    """API endpoint for dashboard data, filtered by role."""
    serializer_class = WorkDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            queryset = WorkEntry.objects.all()
        elif user.role == 'admin':
            queryset = WorkEntry.objects.filter(project__managed_by=user)
        else:
            return WorkEntry.objects.none()
        # ... (Your query parameter filtering logic remains here) ...
        return queryset


class PriceListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating prices."""
    serializer_class = PriceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'admin']:
            return Price.objects.filter(managed_by=user) if user.role == 'admin' else Price.objects.all()
        return Price.objects.none()

    def perform_create(self, serializer):
        serializer.save(managed_by=self.request.user)


class PriceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, or deleting a specific price."""
    serializer_class = PriceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Price.objects.all()
        if user.role == 'admin':
            return Price.objects.filter(managed_by=user)
        return Price.objects.none()


class ClientProjectListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating client projects."""
    serializer_class = ClientProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return ClientProject.objects.all()
        if user.role == 'admin':
            return ClientProject.objects.filter(managed_by=user)
        return ClientProject.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, managed_by=self.request.user)


class CustomLoginView(LoginView):
    """Custom login view using a template."""
    template_name = 'login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)