# Generated by Django 3.1.13 on 2021-08-11 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0036_device_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='management_ip',
            field=models.GenericIPAddressField(
                blank=True,
                db_index=True,
                help_text='IP address used by OpenWISP to reach the device when '
                'performing any type of push operation or active check. The '
                'value of this field is generally sent by the device and hence '
                'does not need to be changed, but can be changed or cleared '
                'manually if needed.',
                null=True,
            ),
        ),
    ]