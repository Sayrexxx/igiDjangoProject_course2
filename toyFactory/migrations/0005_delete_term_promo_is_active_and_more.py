# Generated by Django 4.2.4 on 2024-10-27 01:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toyFactory', '0004_remove_companyinfo_text_companyinfo_certificate_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Term',
        ),
        migrations.AddField(
            model_name='promo',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 30, 1, 53, 44, 142717, tzinfo=datetime.timezone.utc)),
        ),
    ]