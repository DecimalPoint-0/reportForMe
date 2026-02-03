"""
Migration to remove github_token field and make it a property
Depends on: 0001_initial
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userconfig',
            name='github_token',
        ),
    ]
