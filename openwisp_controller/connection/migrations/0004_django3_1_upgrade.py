# Generated by Django 3.1 on 2020-08-18 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('connection', '0003_default_group_permissions')]

    operations = [
        migrations.AlterField(
            model_name='deviceconnection',
            name='is_working',
            field=models.BooleanField(blank=True, default=None, null=True),
        )
    ]
