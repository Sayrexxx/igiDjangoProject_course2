# Generated by Django 4.2.4 on 2024-10-25 13:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toyFactory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 28, 13, 59, 1, 876088, tzinfo=datetime.timezone.utc)),
        ),
    ]