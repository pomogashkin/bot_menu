# Generated by Django 3.2.18 on 2023-02-27 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0004_auto_20230227_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
    ]
