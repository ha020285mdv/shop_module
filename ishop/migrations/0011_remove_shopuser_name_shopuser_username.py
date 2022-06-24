# Generated by Django 4.0.5 on 2022-06-24 12:18

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0010_alter_good_options_alter_refund_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopuser',
            name='name',
        ),
        migrations.AddField(
            model_name='shopuser',
            name='username',
            field=models.CharField(default='dimon', error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
            preserve_default=False,
        ),
    ]
