# Generated by Django 3.2.18 on 2023-02-26 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_product_cost'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Favourite',
        ),
        migrations.DeleteModel(
            name='Poem',
        ),
    ]