# Generated by Django 5.0.2 on 2024-02-13 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_apps', '0002_remove_searchresult_search_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchresult',
            name='search_id',
            field=models.CharField(default='0', max_length=20),
        ),
    ]