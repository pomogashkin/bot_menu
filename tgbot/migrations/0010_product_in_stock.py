# Generated by Django 3.2.18 on 2023-02-27 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0009_alter_product_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='in_stock',
            field=models.BooleanField(default=True, verbose_name='В наличии'),
        ),
    ]
