# Generated by Django 4.0.5 on 2022-06-26 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0011_remove_shopuser_name_shopuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopuser',
            name='wallet',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
