# Generated by Django 4.0.5 on 2022-06-21 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0007_alter_good_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='good',
            old_name='quantity',
            new_name='in_stock',
        ),
    ]