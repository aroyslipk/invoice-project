from django.contrib import admin
from .models import User, Client, Folder Name, Pricing, WorkLog, Invoice, AuditLog
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Client)
admin.site.register(Folder Name)
admin.site.register(Pricing)
admin.site.register(WorkLog)
admin.site.register(Invoice)
admin.site.register(AuditLog)
