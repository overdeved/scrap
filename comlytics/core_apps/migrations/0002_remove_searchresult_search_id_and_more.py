# Generated by Django 5.0.2 on 2024-02-13 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_apps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchresult',
            name='search_id',
        ),
        migrations.AlterField(
            model_name='searchresult',
            name='item_price',
            field=models.CharField(max_length=20),
        ),
    ]