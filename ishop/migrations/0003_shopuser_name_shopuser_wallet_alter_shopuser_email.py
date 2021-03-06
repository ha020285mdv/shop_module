# Generated by Django 4.0.5 on 2022-06-20 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0002_remove_shopuser_name_remove_shopuser_wallet_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopuser',
            name='name',
            field=models.CharField(default='admin', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shopuser',
            name='wallet',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shopuser',
            name='email',
            field=models.EmailField(blank=True, max_length=150, unique=True),
        ),
    ]
