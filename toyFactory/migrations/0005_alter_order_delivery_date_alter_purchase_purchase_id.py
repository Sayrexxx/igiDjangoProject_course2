# Generated by Django 4.2.4 on 2024-05-22 07:58

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toyFactory', '0004_alter_order_delivery_date_alter_purchase_purchase_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 25, 7, 58, 33, 499173, tzinfo=datetime.timezone.utc), validators=[django.core.validators.MinValueValidator(datetime.datetime(2024, 5, 25, 7, 58, 33, 499184, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='purchase_id',
            field=models.IntegerField(default=63601),
        ),
    ]
