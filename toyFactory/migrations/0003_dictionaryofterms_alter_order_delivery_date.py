# Generated by Django 4.2.4 on 2024-10-27 00:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toyFactory', '0002_alter_order_delivery_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='DictionaryOfTerms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.TextField()),
                ('summary', models.CharField(default='', max_length=40)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 30, 0, 58, 58, 536231, tzinfo=datetime.timezone.utc)),
        ),
    ]