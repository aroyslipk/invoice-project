# Generated by Django 5.2.1 on 2025-06-28 07:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Invoice', '0004_alter_price_options_alter_clientproject_attachment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name of the template (e.g., 'Standard Photo Editing')", max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('managed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_templates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text="e.g., 'Main Folder Retouch' or 'Sub-folder Color Correction'", max_length=255)),
                ('default_quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Invoice.jobtemplate')),
            ],
        ),
    ]
