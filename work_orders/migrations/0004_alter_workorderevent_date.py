# Generated by Django 5.0 on 2024-01-01 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_orders', '0003_workorderevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorderevent',
            name='date',
            field=models.DateTimeField(),
        ),
    ]