# Generated by Django 4.0.5 on 2022-06-20 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0006_alter_shopuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='good',
            name='image',
            field=models.ImageField(blank=True, upload_to='img'),
        ),
    ]